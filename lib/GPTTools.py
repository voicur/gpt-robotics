import aiohttp
import asyncio
import time
import json
import csv
import sys
import os

from Controller import Controller as new_Controller

#### bad
# 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
# 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
# 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

#### good
# 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
# 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


async def preflight_test(keys, control):
    for key in keys:
        response = await control.chat(
            "gpt-4",
            [{"role": "user", "content": "Hello, how are you?"}],
            override_headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(key),
            },
            override_response_data=True,
        )
        print(key, response)


async def main():
    attempt_name = input("What to catalogue this attempt as?: ")

    keys = [
        "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",
        "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",
    ]

    controller = new_Controller(
        keys,
        worker_amt=len(keys) * 2,
    )

    await controller.start_workers()

    # await preflight_test(keys, controller)

    prompt = "Please fly up 6 feet, then turn in a circle with radius 10 feet with the intial point being the center of the circle, but before you do anything else takeoff the drone please"

    models = {"gpt-4": 10, "gpt-3.5-turbo-16k": 10}

    queue = []
    index = 0

    # split_prompt = await controller.split_prompt(prompt)
    split_prompt = [prompt]

    for model, count in models.items():
        for _ in range(count):
            queue.append(
                asyncio.ensure_future(
                    controller.designate(
                        split_prompt, model, split_prompt=True, iteration=index
                    )
                )
            )
            index += 1

    responses_bunched = await asyncio.gather(*queue)

    responses = []
    for resp in responses_bunched:
        responses += resp

    filename = f"./data/data_{attempt_name}_{int(time.time()) }.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "Iteration",
            "Model",
            "Request Time",
            "Safety Check Time",
            "Total Time",
            "Safety Rating",
            "Code",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for response in responses:
            request_time = float(response["request_time"])

            code = response["response"]
            model = response["model"]
            iteration = response["iteration"]

            total_time = request_time

            if "safety_check_time" in response:
                safety_check_time = float(response["safety_check_time"])
                safety_rating = response["safety_check_response"]

                total_time += safety_check_time
            else:
                safety_check_time = "N/A"
                safety_rating = "N/A"

            writer.writerow(
                {
                    "Iteration": iteration,
                    "Model": model,
                    "Request Time": round(request_time, 2),
                    "Safety Check Time": safety_check_time,
                    "Total Time": round(total_time, 2),
                    "Safety Rating": safety_rating,
                    "Code": code,
                }
            )

            print(f"{model} in {round(total_time, 2)} ")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
