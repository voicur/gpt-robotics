import aiohttp
import asyncio
import time
import json
import csv
import sys

from prompts.gpt_prompts import MAIN_GPT_PROMPT, CONSTANTS, SAFETY_MODEL_PROMPT

controller = APIController("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")

async def fetch(session, url, headers, data):
    start = time.time()
    async with session.post(url, headers=headers, data=data) as response:
        r = await response.text()
        return r, time.time() - start

with open("prompts/docs_prompt.txt", "r") as promptFile:
    SYS_PROMPT = promptFile.read()

with open("prompts/safety_prompt.txt", "r") as promptFile:
    SAFETY_SYS_PROMPT = promptFile.read()

chat_history = [
    {"role": "system", "content": SYS_PROMPT},
]





async def main():
    api_key = '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'
    # api_key = "sk-sVfooF2RmxYEFzyazniAT3BlbkFJUEDoRmKuWcTuxvPr9E4"
    prompt = 'Please fly up 6 feet, then turn in a circle with radius 10 feet with the intial point being the center of the circle, but before you do anything else takeoff the drone please'

    models = {
        'gpt-4': 15,
        'gpt-3.5-turbo-16k': 40
    }

    queue = []
    for model, count in models.items():
        for _ in range(count):
            queue.append(asyncio.ensure_future(commander(api_key, prompt, model, split_prompt=True)))
    for model, count in models.items():
        for _ in range(count):
            queue.append(asyncio.ensure_future(commander(api_key, prompt, model)))

    responses = await asyncio.gather(*queue)
    
    with open('model_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['Model', 'Request Time', 'Safety Check Time', 'Total Time', 'Safety Rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for response in responses:
            print(response["response"])
            request_time = response["request_time"]
            model = response["model"]

            total_time = request_time
            
            if "safety_check_time" in response:
                safety_check_time = response["safety_check_time"]
                safety_rating = float(json.loads(response["safety_check_response"])["choices"][0]["message"]["content"])
                
                total_time += safety_check_time
            else:
                safety_check_time = "N/A"
                safety_rating = "N/A"

            writer.writerow({'Model': model, 'Request Time': round(request_time, 2), 'Safety Check Time': safety_check_time, 'Total Time': round(total_time, 2), 'Safety Rating': safety_rating})

            print(f"{model} in {round(total_time, 2)} ")
        
loop = asyncio.get_event_loop()
loop.run_until_complete(main())