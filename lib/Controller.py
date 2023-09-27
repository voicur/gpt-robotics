import aiohttp
import asyncio
import time
import json
import csv
import sys

from prompts.gpt_prompts import MAIN_GPT_PROMPT, CONSTANTS, SAFETY_MODEL_PROMPT

with open("prompts/docs_prompt.txt", "r") as promptFile:
    SYS_PROMPT = promptFile.read()

with open("prompts/safety_prompt.txt", "r") as promptFile:
    SAFETY_SYS_PROMPT = promptFile.read()


class Controller:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(api_key),
        }

    async def fetch(self, session, url, headers, data):
        start = time.time()
        async with session.post(url, headers=headers, data=data) as request_response:
            response = await request_response.text()
            elapsed_time = time.time() - start
            return response, elapsed_time

    async def chat(
        self,
        model,
        messages,
        temperature=0.7
    ):
        url = "https://api.openai.com/v1/chat/completions"

        data = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
        )
        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.keep_fetching(session, url, self.headers, data)
        response_text = json.loads(response)["choices"][0]["message"]["content"]
        return response_text, elapsed_time

    # Ask GPT to split the prompt into individual commands
    async def split_prompt(self, prompt):
        messages = SPLIT_PROMPT + CONSTANTS
        messages.append({"role": "user", "content": prompt})

        response = await self.chat_complex(prompt, "gpt-4", messages, 0.5)

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

    async def commander(api_key, prompt, model, split_prompt=False):
        url = "https://api.openai.com/v1/chat/completions"

        messages = await self.generate_messages(SYS_PROMPT, MAIN_GPT_PROMPT, prompt)

        async with aiohttp.ClientSession() as session:
            response, elapsed_time = await self.chat(model, messages)

            safety_messages = await self.generate_messages(SAFETY_SYS_PROMPT, SAFETY_MODEL_PROMPT, f"Prompt: {prompt}\n\n{response}")            

            safety_check_response, safety_check_time = await chat("gpt-4", safety_messages)

            print(safety_check_response)

            return {
                "response": response,
                "request_time": elapsed_time,
                "safety_check_response": safety_check_response,
                "safety_check_time": safety_check_time,
                "model": model,
            }

        async def generate_messages (SYSTEM_PROMPT, PROMPT_HISTORY_INTERMEDIARY, request_content, constants=CONSTANTS):
            # Intermediary gives a good overview of what it does
            PROMPT_HISTORY = PROMPT_HISTORY_INTERMEDIARY
            
            generated_messages = [
                {"role": "system", "content": SYSTEM_PROMPT + constants}
            ] + PROMPT_HISTORY

            generated_messages.append(
                {"role": "user", "content": request_content}
            )

            return generated_messages

        async def keep_fetching (session, url, headers, data):
            request_completed = False
            time_delay = 0.001
            while not request_completed:
                response, elapsed_time = await fetch(session, url, headers, data)
                if "error" in response:
                    request_completed = False
                    await asyncio.sleep(time_delay)
                    time_delay += 0.001
                else:
                    request_completed = True
            return response, elapsed_time


async def main():
    controller = APIController("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")
    prompt = "Run to end, turn left, before that fly up 60 feet and you fly up enable the speaker"
    commands = await controller.split_prompt(prompt)
    print(commands)
    # rated_commands = await controller.rate_complexity(commands)
    # assigned_commands = controller.assign_models(rated_commands)
    # await controller.execute_tasks(assigned_commands)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
