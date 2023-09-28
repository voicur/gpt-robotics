import aiohttp
import asyncio
import time
import json
import atexit
from itertools import cycle

# Prompts and Intermediate Lists
from prompts.gpt_prompts import *

with open("prompts/docs_prompt.txt", "r") as promptFile:
    SYS_PROMPT = promptFile.read()
with open("prompts/safety_prompt.txt", "r") as promptFile:
    SAFETY_SYS_PROMPT = promptFile.read()


# The controller classes encapsulates the process of splitting up requests and doing so efficiently
class Controller:
    def __init__(self, keys, worker_amt=1):
        # It works by having a queue of requests, and a set of workers that process the requests

        # One step the code takes to reduce time taken is to swap rate limited keys on the go.
        self.key_cycle = cycle(keys)

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
    ):
        # You can change this endpoint url for flexibility
        url = "https://api.openai.com/v1/chat/completions"

        if override_headers is None:
            override_headers = self.headers

        data = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
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
        messages = SPLIT_PROMPT
        messages.append({"role": "user", "content": prompt})

        # Get the response from the API, discard the time taken.
        response, _ = await self.chat("gpt-4", messages, 0.5)

        # Get each prompt
        commands = [i for i in response.split("\n") if i]

        return commands

    # This function takes in the split prompt and actually gets the return data for each instance of each model. (10 made for each 9 gpt-4 and 1 gpt-3.5-turbo)
    async def designate(self, prompt, model, split_prompt=False, iteration=-1):
        if split_prompt:
            split_prompts = prompt
        else:
            split_prompts = [prompt]

        queue = []
        for each_prompt in split_prompts:
            # Get the data for each part of the split prompt
            messages = await self.generate_messages(
                SYS_PROMPT, MAIN_GPT_PROMPT, each_prompt
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

    # This function uses the functions to get the data from each model, and then safety check them all.
    async def get_full_data(self, model, messages, prompt, iteration=-1):
        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.chat(model, messages)
            safety_messages = await self.generate_messages(
                SAFETY_SYS_PROMPT,
                SAFETY_MODEL_PROMPT,
                f"Prompt: {prompt}\n\n{response}",
            )
            safety_check_response, safety_check_time = await self.chat(
                "gpt-4", safety_messages
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
        constants=CONSTANTS,
    ):
        # Intermediary gives a good overview of what it does
        PROMPT_HISTORY = PROMPT_HISTORY_INTERMEDIARY

        generated_messages = [
            {"role": "system", "content": SYSTEM_PROMPT + constants}
        ] + PROMPT_HISTORY

        generated_messages.append({"role": "user", "content": request_content})

        return generated_messages

    # This function is the core part of the controller, it actually sends the request to the api.
    async def fetch_internal(self, session, url, headers, data):
        start = time.time()
        async with session.post(url, headers=headers, data=data) as request_response:
            response = await request_response.text()
            elapsed_time = time.time() - start
            return response, elapsed_time

    # Wrapper for the fetch (internal) function that uses the queueing system to prevent rate limiting.
    async def fetch(self, session, url, headers, data):
        task_id = id(asyncio.current_task())

        await self.queue.put((task_id, session, url, headers, data))

        # Polling to check if the result for the task is there yet (is done)
        while task_id not in self.results:
            await asyncio.sleep(0.001)  # Wait for the result
        result = self.results.pop(task_id)
        return result

    # Used to create a worker that processes requests in the queue.
    async def worker(self):
        while True:
            # queue.get removes the item from the queue, and then the function processes it.
            task_id, session, url, headers, data = await self.queue.get()
            response, elapsed_time = await self.fetch_internal(
                session, url, headers, data
            )

            # If it is rate limited, put it back in the queue after waiting for a bit (the bit is the global wait time for the rate limiter,
            # which is increased exponentially, so everything will halt after a rate limit, then spring back to life after the next queue (it resets the time after a successful request)
            if "error" in response:
                print("Delayed", response)
                if self.time_delay < 5:
                    self.time_delay *= 2
                print(self.time_delay)
                print(self.queue.qsize(), self.queue)

                # TODO, CHECK IF THIS MAY BE BETTER AFTER THE SLEEP.
                await self.shift_api_key(time_recieved=time.time())

                await asyncio.sleep(self.time_delay)
                await self.queue.put(
                    (task_id, session, url, headers, data)
                )  # Put the task back in the queue
            else:
                print("On Time")
                self.time_delay = 0.001  # Reset the delay
                self.results[task_id] = (response, elapsed_time)
            # Indicate that the task is done
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
