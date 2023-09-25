import aiohttp
import asyncio
import time
import json
from gpt_prompt_utils import SPLIT_PROMPT, CONSTANTS

with open("safety_prompt.txt", "r") as promptFile:
    SAFETY_PROMPT = promptFile.read()

class DroneController:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = {
            'gpt-4': 25,
            'gpt-3.5-turbo-16k': 25
        }

    async def fetch(self, session, url, headers, data):
        start = time.time()
        async with session.post(url, headers=headers, data=data) as response:
            r = await response.text()
            return r, time.time() - start

    async def chat(self, prompt, model):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key)
        }
        data = json.dumps({
            "model": model,
            "messages": [
                { "role": "user", "content": prompt }
            ],
            "temperature": 0.7,
        })
        async with aiohttp.ClientSession() as session:
            response, _ = await self.fetch(session, url, headers, data)
        return json.loads(response)["choices"][0]["message"]["content"]

    async def chat_complex(self, prompt, model, messages, temperature=0.7):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key)
        }
        data = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
        })
        async with aiohttp.ClientSession() as session:
            response, _ = await self.fetch(session, url, headers, data)
        return json.loads(response)["choices"][0]["message"]["content"]

    # Ask GPT to split the prompt into individual commands
    async def split_prompt(self, prompt):
        messages = SPLIT_PROMPT + CONSTANTS       
        messages.append({ "role": "user", "content": prompt })

        response = await self.chat_complex(prompt, 'gpt-4', messages, 0.5)

        # Get each prompt
        commands = [i for i in response.split("\n") if i]
        return commands

    async def rate_complexity(self, commands):
        # Assign a complexity rating to each command based on the GPT model's response
        rated_commands = []
        for command in commands:
            complexity_check_prompt = f"On a scale of 0-10, how complex is the following command: '{command}'? Please provide a number."
            complexity_str = await self.chat(complexity_check_prompt, 'gpt-3.5-turbo-16k')
            complexity = float(complexity_str)
            rated_commands.append((command, complexity))
        return rated_commands

    def assign_models(self, rated_commands):
        # Assign each command to a GPT model based on its complexity rating
        assigned_commands = [(command, 'gpt-3.5-turbo-16k' if complexity <= 5 else 'gpt-4') for command, complexity in rated_commands]
        return assigned_commands

    async def execute_tasks(self, assigned_commands):
        # Execute each command using the assigned GPT model
        tasks = []
        for command, model in assigned_commands:
            tasks.append(self.chat(command, model))

        responses = await asyncio.gather(*tasks)
        
        # Handle the responses here
        for command, response in zip(assigned_commands, responses):
            print(f"Executed '{command[0]}' using {command[1]}: {response}")

async def main():
    controller = DroneController('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')
    prompt = 'Run to end, turn left, before that fly up 60 feet and you fly up enable the speaker'
    commands = await controller.split_prompt(prompt)
    print(commands)
    # rated_commands = await controller.rate_complexity(commands)
    # assigned_commands = controller.assign_models(rated_commands)
    # await controller.execute_tasks(assigned_commands)

loop = asyncio.get_event_loop()
loop.run_until_complete(main()) 