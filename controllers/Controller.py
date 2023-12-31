import aiohttp
import asyncio
import time
import json
import atexit
from itertools import cycle
from config.native import config_import
import logging


# The controller classes encapsulates the process of splitting up requests and doing so efficiently
class Controller:
    def __init__(self, config_file, worker_amt=1):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        config = config_import(config_file)
        # It works by having a queue of requests, and a set of workers that process the requests

        # One step the code takes to reduce time taken is to swap rate limited keys on the go.
        keys = config.KEYS
        self.key_cycle = cycle(keys)
        self.CONFIG_FILE = config

        self.CONSTANTS = config.CONSTANTS_BLOCK
        self.SAFETY_PROMPT = config.SAFETY_PROMPT_TOTAL_BLOCK
        self.SAFETY_PROMPT_LIST = config.SAFETY_PROMPT_LIST
        self.CODE_DOCUMENTATION_BLOCK = config.CODE_DOCUMENTATION_BLOCK

        self.DRONE_PROMPT = config.DRONE_PROMPT_LIST
        self.SPLIT_PROMPT = config.SPLIT_PROMPT_LIST
        
        self.api_key = keys[0]

        # Additionally, the python openai library does not allow you to use a certain api key for a request,
        # so we manually implement this functionality.
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }
        self.queue = asyncio.Queue()
        self.worker_amt = worker_amt

        # The keys are time restricted.
        self.time_delay = 0.001
        self.results = {}
        self.workers = []
        self.last_api_key_time = time.time()

        atexit.register(self.cleanup)

    # This simple function creates the workers (by default the loaded amount of api keys * 2 workers per key, to account for rate limiting)
    async def start_workers(self):
        self.workers = [
            asyncio.create_task(self.worker()) for _ in range(self.worker_amt)
        ]

    # One of the larger functions, just using the fetch function to "chat" with the openai api, with many parameters for flexibility.
    async def chat(
        self,
        model,
        messages,
        temperature=0.7,
        override_headers=None,
        override_response_data=None,
        override_url=None
    ):
        # You can change this endpoint url for flexibility
        
        url = "https://api.openai.com/v1/chat/completions"
        if (override_url is not None):  
            url = override_url

        if override_headers is None:
            override_headers = self.headers

        data = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096,
            }
        )

        # Asynchronously wait for a request to be completed
        async with aiohttp.ClientSession() as session:
            # Get the response using the worker queue
            response, elapsed_time = await self.fetch(
                session, url, override_headers, data
            )

        # If override_response_data is enabled, then we return the full response
        if override_response_data is True:
            return json.loads(response)

        # If the parameter is not enabled for override_response_data, then we return just the response text
        response_text = json.loads(response)["choices"][0]["message"]["content"]
        return response_text, elapsed_time

    # Ask GPT to split the prompt into individual commands
    async def split_prompt(self, prompt):
        # You will see many CAPS variables, these are long "system" prompts that accuratly describe what GPT should generate.
        messages = self.SPLIT_PROMPT
        messages.append({"role": "user", "content": prompt})

        # Get the response from the API, discard the time taken.
        response, _ = await self.chat("gpt-4", messages, 0.5)

        # Get each prompt
        commands = [i for i in response.split("\n") if i]

        return commands

    # This function takes in the split prompt and actually gets the return data for each instance of each model. (10 made for each 9 gpt-4 and 1 gpt-3.5-turbo)
    # Split prompt tells if it is a list or not
    async def designate(self, prompt, model, split_prompt=False, iteration=-1):
        if split_prompt:
            split_prompts = prompt
        else:
            split_prompts = [prompt]

        queue = []
        for each_prompt in split_prompts:
            # Get the data for each part of the split prompt
            messages = await self.generate_messages(
                self.CODE_DOCUMENTATION_BLOCK, self.DRONE_PROMPT, each_prompt, self.CONSTANTS
            )
            queue.append(
                asyncio.ensure_future(
                    self.get_full_data(
                        model, messages, each_prompt, iteration=iteration
                    )
                )
            )

        # Gather the data from each part of the split prompt and then get them
        responses = await asyncio.gather(*queue)

        return responses

    async def first_finished(self, queue, amount_to_collect=1):
        futures = [asyncio.create_task(coro) for coro in queue]
        results = []
        try:
            # Iterate over the futures as they complete
            for future in asyncio.as_completed(futures):
                print(future)
                response = await future
                safety_check_result = int(response[0]["safety_check_response"].split("\n")[0])

                print(safety_check_result)
                
                if safety_check_result >= self.CONFIG_FILE.SAFETY_THRESHOLD:
                    results.append(response)
                    # Break out of the loop once we've collected the desired amount of results
                    if len(results) == amount_to_collect:
                        break
        except asyncio.CancelledError:
            # If any future raises a CancelledError, it means we are shutting down.
            # No new results should be added and we should proceed to cancellation.
            pass
        finally:
            # Cancel any remaining tasks that are not done
            for remaining_future in futures:
                if not remaining_future.done():
                    remaining_future.cancel()

        return results
    # This function uses the functions to get the data from each model, and then safety check them all.
    async def get_full_data(self, model, messages, prompt, iteration=-1):
        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.chat(model, messages)
            safety_messages = await self.generate_messages(
                self.SAFETY_PROMPT,
                self.SAFETY_PROMPT_LIST,
                f"Prompt: {prompt}\n\n{response}",
                self.CONSTANTS
            )
            safety_check_response, safety_check_time = await self.chat(
                self.CONFIG_FILE.MOST_ACCURATE_MODEL, safety_messages
            )

            return {
                "iteration": iteration,
                "response": response,
                "request_time": elapsed_time,
                "safety_check_response": safety_check_response,
                "safety_check_time": safety_check_time,
                "model": model,
            }

    # Prompts require three things to work well, this function is what packages the following to be used:
    # A SYSTEM Prompt, a prompt that tells the api what they are working with and any documentation or description of the task
    # A PROMPT_HISTORY, where it shows a user (me) entering a prompt, and correcting its responses to improve its own response,
    # and the request_content, which is the actual prompt for the api.
    async def generate_messages(
        self,
        SYSTEM_PROMPT,
        PROMPT_HISTORY_INTERMEDIARY,
        request_content,
        constants,
    ):
        # Intermediary gives a good overview of what it does
        PROMPT_HISTORY = PROMPT_HISTORY_INTERMEDIARY

        generated_messages = [
            {"role": "system", "content": SYSTEM_PROMPT + constants}
        ] + PROMPT_HISTORY

        generated_messages.append({"role": "user", "content": request_content})

        return generated_messages

    # This function is the core part of the controller, it actually sends the request to the api.
    # async def fetch_internal(self, session, url, headers, data):
    #     start = time.time()
    #     async with session.post(url, headers=headers, data=data) as request_response:
    #         response = await request_response.text()
    #         elapsed_time = time.time() - start
    #         return response, elapsed_time

    # Wrapper for the fetch (internal) function that uses the queueing system to prevent rate limiting.
    async def fetch(self, session, url, headers, data):
        task_id = id(asyncio.current_task())

        await self.queue.put((task_id, session, url, headers, data))

        # Polling to check if the result for the task is there yet (is done)
        while task_id not in self.results:
            await asyncio.sleep(0.001)  # Wait for the result
        result = self.results.pop(task_id)
        return result

    # # Used to create a worker that processes requests in the queue.
    # async def worker(self):
    #     while True:
    #         # queue.get removes the item from the queue, and then the function processes it.
    #         task_id, session, url, headers, data = await self.queue.get()
    #         response, elapsed_time = await self.fetch_internal(
    #             session, url, headers, data
    #         )

    #         # If it is rate limited, put it back in the queue after waiting for a bit (the bit is the global wait time for the rate limiter,
    #         # which is increased exponentially, so everything will halt after a rate limit, then spring back to life after the next queue (it resets the time after a successful request)
    #         if "error" in response:
    #             print("Delayed", response)
    #             if self.time_delay < 5:
    #                 self.time_delay *= 2
    #             print(self.time_delay)
    #             print(self.queue.qsize(), self.queue)

    #             # TODO, CHECK IF THIS MAY BE BETTER AFTER THE SLEEP.
    #             await self.shift_api_key(time_recieved=time.time())

    #             await asyncio.sleep(self.time_delay)
    #             await self.queue.put(
    #                 (task_id, session, url, headers, data)
    #             )  # Put the task back in the queue
    #         else:
    #             print("On Time")
    #             self.time_delay = 0.001  # Reset the delay
    #             self.results[task_id] = (response, elapsed_time)
    #         # Indicate that the task is done
    #         self.queue.task_done()

    async def fetch_internal(self, session, url, headers, data):
        start = time.time()
        try:
            async with session.post(url, headers=headers, data=data) as request_response:
                response = await request_response.text()
                elapsed_time = time.time() - start
                # Log the response status and data for debugging
                # logging.info(f"API Response Status: {request_response.status}")
                # logging.info(f"API Response Data: {response}")
                return response, elapsed_time
        except Exception as e:
            # Log any exceptions that occur during the API request
            logging.error(f"An error occurred during the API request: {e}")
            raise

    async def worker(self):
        while True:
            task_id, session, url, headers, data = await self.queue.get()
            try:
                response, elapsed_time = await self.fetch_internal(session, url, headers, data)
                if "error" in response:
                    # Log the error response and delay information
                    # logging.warning(f"Delayed due to error response: {response}")
                    if self.time_delay < 5:
                        self.time_delay *= 2
                    # logging.info(f"Current delay time: {self.time_delay}")
                    # logging.info(f"Queue size: {self.queue.qsize()}")
                    await self.shift_api_key(time_received=time.time())
                    await asyncio.sleep(self.time_delay)
                    await self.queue.put((task_id, session, url, headers, data))
                else:
                    # Log successful response processing
                    # logging.info(f"Task {task_id} completed on time.")
                    self.time_delay = 0.001
                    self.results[task_id] = (response, elapsed_time)
                self.queue.task_done()
            except Exception as e:
                # Log any exceptions that occur while processing the task
                # logging.error(f"An error occurred while processing task {task_id}: {e}")
                self.queue.task_done()

    # This function changes the api key in use to prevent rate limiting.
    # Contains a built in debounce timer of 0.05 to prevent too many shifts in the api key, preventing the same one from being used twice in a row.
    async def shift_api_key(self, time_recieved, debounce_time=0.5):
        if (time_recieved - self.last_api_key_time) > debounce_time:
            self.api_key = next(self.key_cycle)
            self.last_api_key_time = time_recieved
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }   

    # Clear the workers after a program quit
    def cleanup(self):
        for worker in self.workers:
            worker.cancel()