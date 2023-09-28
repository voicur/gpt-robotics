import aiohttp
import asyncio
import time
import json
import atexit
from itertools import cycle

# Prompts and Intermediate Lists
from prompts.gpt_prompts import *
with open("prompts/docs_prompt.txt", "r") as promptFile: SYS_PROMPT = promptFile.read()
with open("prompts/safety_prompt.txt", "r") as promptFile: SAFETY_SYS_PROMPT = promptFile.read()

class Controller:
    def __init__(self, keys, worker_amt=1):
        self.key_cycle = cycle(keys)

        self.api_key = keys[0]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }
        self.queue = asyncio.Queue()
        self.worker_amt = worker_amt
        self.time_delay = 0.001
        self.results = {}
        self.workers = []
        self.last_api_key_time = time.time()

        atexit.register(self.cleanup)
        
    async def start_workers (self):
        self.workers = [asyncio.create_task(self.worker()) for _ in range(self.worker_amt)]

    async def chat(
        self,
        model,
        messages,
        temperature=0.7,
        override_headers=None,
        override_response_data=None,
    ):

        
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
        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.fetch(session, url, override_headers, data)
        if override_response_data is True:
            return json.loads(response)
        response_text = json.loads(response)["choices"][0]["message"]["content"]
        return response_text, elapsed_time

    # Ask GPT to split the prompt into individual commands
    async def split_prompt(self, prompt):
        messages = SPLIT_PROMPT
        messages.append({"role": "user", "content": prompt})

        response, _ = await self.chat("gpt-4", messages, 0.5)

        # Get each prompt
        commands = [i for i in response.split("\n") if i]

        return commands

    # async def rate_complexity(self, commands):
    #     # Assign a complexity rating to each command based on the GPT model's response
    #     rated_commands = []
    #     for command in commands:
    #         complexity_check_prompt = f"On a scale of 0-10, how complex is the following command: '{command}'? Please provide a number."
    #         complexity_str = await self.chat(
    #             complexity_check_prompt, "gpt-3.5-turbo-16k"
    #         )
    #         complexity = float(complexity_str)
    #         rated_commands.append((command, complexity))
    #     return rated_commands

    # def assign_models(self, rated_commands):
    #     # Assign each command to a GPT model based on its complexity rating
    #     assigned_commands = [
    #         (command, "gpt-3.5-turbo-16k" if complexity <= 5 else "gpt-4")
    #         for command, complexity in rated_commands
    #     ]
    #     return assigned_commands

    # async def execute_tasks(self, assigned_commands):
    #     # Execute each command using the assigned GPT model
    #     tasks = []
    #     for command, model in assigned_commands:
    #         tasks.append(self.chat(command, model))

    #     responses = await asyncio.gather(*tasks)

    #     # Handle the responses here
    #     for command, response in zip(assigned_commands, responses):
    #         print(f"Executed '{command[0]}' using {command[1]}: {response}")

    async def designate (self, prompt, model, split_prompt=False, iteration=-1):
        if split_prompt:
            split_prompts = prompt
        else:
            split_prompts = [prompt]
        
        queue = []
        for each_prompt in split_prompts:
            messages = await self.generate_messages(SYS_PROMPT, MAIN_GPT_PROMPT, each_prompt)
            queue.append(asyncio.ensure_future(self.get_full_data(model, messages, each_prompt, iteration=iteration)))

        responses = await asyncio.gather(*queue)
        print(responses)

        return responses

    async def get_full_data (self, model, messages, prompt, iteration=-1):
        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.chat(model, messages)
            safety_messages = await self.generate_messages(SAFETY_SYS_PROMPT, SAFETY_MODEL_PROMPT, f"Prompt: {prompt}\n\n{response}")            
            safety_check_response, safety_check_time = await self.chat("gpt-4", safety_messages)

            return {
                "iteration": iteration,
                "response": response,
                "request_time": elapsed_time,
                "safety_check_response": safety_check_response,
                "safety_check_time": safety_check_time,
                "model": model,
            }

    async def generate_messages (self, SYSTEM_PROMPT, PROMPT_HISTORY_INTERMEDIARY, request_content, constants=CONSTANTS):
        # Intermediary gives a good overview of what it does
        PROMPT_HISTORY = PROMPT_HISTORY_INTERMEDIARY
        
        generated_messages = [
            {"role": "system", "content": SYSTEM_PROMPT + constants}
        ] + PROMPT_HISTORY

        generated_messages.append(
            {"role": "user", "content": request_content}
        )

        return generated_messages

    async def fetch_internal(self, session, url, headers, data):
        start = time.time()
        async with session.post(url, headers=headers, data=data) as request_response:
            response = await request_response.text()
            elapsed_time = time.time() - start
            return response, elapsed_time

    async def fetch(self, session, url, headers, data):
        task_id = id(asyncio.current_task())

        await self.queue.put((task_id, session, url, headers, data))

        while task_id not in self.results:
            await asyncio.sleep(0.001)  # Wait for the result
        result = self.results.pop(task_id)
        return result

    async def worker(self):
        while True:
            task_id, session, url, headers, data = await self.queue.get()
            response, elapsed_time = await self.fetch_internal(session, url, headers, data)
            if "error" in response:
                print("Delayed", response)
                if self.time_delay < 5:
                    self.time_delay *= 2

                # TODO, CHECK IF THIS MAY BE BETTER AFTER THE SLEEP.
                await self.shift_api_key(time_recieved=time.time())

                await asyncio.sleep(self.time_delay)
                await self.queue.put((task_id, session, url, headers, data))  # Put the task back in the queue
            else:
                print("On Time")
                self.time_delay = 0.001  # Reset the delay
                self.results[task_id] = (response, elapsed_time)
            self.queue.task_done()

    async def shift_api_key (self, time_recieved):
        if (time_recieved - self.last_api_key_time) > 0.05:
            self.api_key = next(self.key_cycle)
            self.last_api_key_time = time_recieved
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }

    def cleanup(self):
        for worker in self.workers:
            worker.cancel()
