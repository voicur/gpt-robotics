import aiohttp
import asyncio
import time
import json

async def fetch(session, url, headers, data):
    start = time.time()
    async with session.post(url, headers=headers, data=data) as response:
        r = await response.text()
        return r, time.time() - start

async def commander(api_key, prompt, model):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(api_key)
    }

    data = json.dumps({
        "model": model,
        "messages": [
            { "role": "user", "content": prompt }
        ],
        "temperature": 0.7,
    })

    async with aiohttp.ClientSession() as session:
        response, elapsed_time = await fetch(session, url, headers, data)

    # if model == 'gpt-3.5-turbo-16k':
        safety_check_prompt = 'Return an integer value of if you think the code is safe in the range 0 - 10 \nour entire response must return a int/float direct convertable value from 0-10, and keep the token counter under 10 to prevent overcharges: ' + response
        safety_check_data = json.dumps({
            "model": model,
            "messages": [
                { "role": "user", "content": safety_check_prompt }
            ],
            "temperature": 0.7,
        })

        safety_check_response, safety_check_time = await fetch(session, url, headers, safety_check_data)
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
    prompt = 'Write a program to move an RC car in a circle of 20 radians, with only turn_left(degrees), turn_right(degrees), forward(units), backwards(units)'

    models = {
        'gpt-4': 25,
        'gpt-3.5-turbo-16k': 25
    }

    tasks = []
    for model, count in models.items():
        for _ in range(count):
            tasks.append(asyncio.ensure_future(commander(api_key, prompt, model)))

    responses = await asyncio.gather(*tasks)
    
    model_times = {model: {"total_time": 0.0, "count": 0.0, "safety": 0.0} for model in models}

    for response in responses:
        total_time = 0
        request_time = response["request_time"]
        model = response["model"]

        
        model_times[model]["count"] += 1

        total_time += request_time
        
        if "safety_check_time" in response:
            safety_check_time = response["safety_check_time"]
            safety_rating = float(json.loads(response["safety_check_response"])["choices"][0]["message"]["content"])
            
            total_time += safety_check_time

        model_times[model]["total_time"] += request_time
        model_times[model]["safety"] += safety_rating
            
        print(f"{model} in {round(total_time, 2)} ")
    for model, data in model_times.items():
        avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
        avg_safety = data["safety"] / data["count"] if data["count"] > 0 else 0
        print(f"{model} is {round(avg_time, 2)} seconds ({avg_safety})")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())