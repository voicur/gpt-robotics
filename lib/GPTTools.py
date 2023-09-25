import aiohttp
import asyncio
import time
import json
import csv

from gpt_prompt_utils import MAIN_GPT_PROMPT, CONSTANTS, SAFETY_MODEL_PROMPT

async def fetch(session, url, headers, data):
    start = time.time()
    async with session.post(url, headers=headers, data=data) as response:
        r = await response.text()
        return r, time.time() - start

with open("prompt.txt", "r") as promptFile:
    SYS_PROMPT = promptFile.read()

with open("safety_prompt.txt", "r") as promptFile:
    SAFETY_SYS_PROMPT = promptFile.read()

chat_history = [
    {"role": "system", "content": SYS_PROMPT},
]
async def commander(api_key, prompt, model):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(api_key)
    }
    messages = [{ "role": "system", "content": SYS_PROMPT + CONSTANTS }] + MAIN_GPT_PROMPT 
    messages.append({ "role": "user", "content": prompt })

    data = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    })

    async with aiohttp.ClientSession() as session:
        response, elapsed_time = await fetch(session, url, headers, data)

        response_returned = json.loads(response)["choices"][0]["message"]["content"]

        safety_messages = [
            { "role": "system", "content": SAFETY_SYS_PROMPT + CONSTANTS }
        ] + SAFETY_MODEL_PROMPT

        safety_messages.append({ "role": "user", "content": f"Prompt: {prompt}\n\n{response_returned}" })

        safety_check_data = json.dumps({
            "model": model,
            "messages": safety_messages,
            "temperature": 0.7,
        })

        safety_check_response, safety_check_time = await fetch(session, url, headers, safety_check_data)
        print(safety_check_response)
        return {
            "response": response,
            "request_time": elapsed_time,
            "safety_check_response": safety_check_response,
            "safety_check_time": safety_check_time,
            "model": model
        }
        # return response, elapsed_time

async def main():
    api_key = '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'
    # api_key = "sk-sVfooF2RmxYEFzyazniAT3BlbkFJUEDoRmKuWcTuxvPr9E4"
    prompt = 'Please fly up 6 feet, then turn in a circle with radius 10 feet with the intial point being the center of the circle, but before you do anything else takeoff the drone please'

    models = {
        'gpt-4': 10,
        'gpt-3.5-turbo-16k': 10
    }

    tasks = []
    for model, count in models.items():
        for _ in range(count):
            tasks.append(asyncio.ensure_future(commander(api_key, prompt, model)))

    responses = await asyncio.gather(*tasks)
    
    model_times = {model: {"times": [], "safety_ratings": []} for model in models}

    for response in responses:
        print(response["response"])
        request_time = response["request_time"]
        model = response["model"]

        total_time = request_time
        
        if "safety_check_time" in response:
            safety_check_time = response["safety_check_time"]
            safety_rating = float(json.loads(response["safety_check_response"])["choices"][0]["message"]["content"])
            
            total_time += safety_check_time

        model_times[model]["times"].append(total_time)
        model_times[model]["safety_ratings"].append(safety_rating)
            
        print(f"{model} in {round(total_time, 2)} ")
    
    for model, data in model_times.items():
        if data["times"]:
            avg_time = sum(data["times"]) / len(data["times"])
            min_time = min(data["times"])
            max_time = max(data["times"])
        else:
            avg_time = min_time = max_time = 0

        if data["safety_ratings"]:
            avg_safety = sum(data["safety_ratings"]) / len(data["safety_ratings"])
            min_safety = min(data["safety_ratings"])
            max_safety = max(data["safety_ratings"])
        else:
            avg_safety = min_safety = max_safety = 0

        print(f"{model}: Avg Time: {round(avg_time, 2)} seconds, Min Time: {round(min_time, 2)} seconds, Max Time: {round(max_time, 2)} seconds, Avg Safety: {round(avg_safety, 2)}, Min Safety: {round(min_safety, 2)}, Max Safety: {round(max_safety, 2)}")

    with open('model_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['Model', 'Avg Time', 'Min Time', 'Max Time', 'Avg Safety', 'Min Safety', 'Max Safety']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for model, data in model_times.items():
            if data["times"]:
                avg_time = sum(data["times"]) / len(data["times"])
                min_time = min(data["times"])
                max_time = max(data["times"])
            else:
                avg_time = min_time = max_time = 0

            if data["safety_ratings"]:
                avg_safety = sum(data["safety_ratings"]) / len(data["safety_ratings"])
                min_safety = min(data["safety_ratings"])
                max_safety = max(data["safety_ratings"])
            else:
                avg_safety = min_safety = max_safety = 0

            writer.writerow({'Model': model, 'Avg Time': round(avg_time, 2), 'Min Time': round(min_time, 2), 'Max Time': round(max_time, 2), 'Avg Safety': round(avg_safety, 2), 'Min Safety': round(min_safety, 2), 'Max Safety': round(max_safety, 2)})

loop = asyncio.get_event_loop()
loop.run_until_complete(main())