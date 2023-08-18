from djitellopy import Tello
import openai
import re
import time
import threading
import tkinter as tk

openai.api_key = "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"
with open("prompt.txt", "r") as promptFile:
    sysprompt = promptFile.read()

battery_percent = 100

def keepActive (pollTime):
    print("Beginning active daemon")
    while True:
        battery_percent = drone.query_battery()
        time.sleep(pollTime)

chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "lets start make the drone takeoff"
    },
    {
        "role": "assistant",
        "content": """
```python
drone.connect()
drone.takeoff()
```

This code uses the `drone.connect()` function to connect to the drone on its interface, and `drone.takeoff()` to let the drone takeoff at its current position."""
    },
    {
        "role": "user",
        "content": "move 10 units up"
    },
    {
        "role": "assistant",
        "content": """
```python
drone.move_left(100)
```

This code uses the `move_left()` function to move the drone to a new position that is 100 units left from the current position."""
    }
]



def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history,
        temperature=0
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]

code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_python_code(content):
    code_blocks = code_block_regex.findall(content)
    if code_blocks:
        full_code = "\n".join(code_blocks)

        if full_code.startswith("python"):
            full_code = full_code[7:]

        return full_code
    else:
        return None


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


print("Welcome to the AirSim chatbot! I am ready to help you with your AirSim questions and commands.")

drone = Tello()
drone.connect()

root = tk.Tk()
root.title("Battery Status")
root.geometry("300x100")
label = tk.Label(root, textvariable=battery_percent)
label.pack()

drone.takeoff()


guiThread = threading.Thread(target=root.mainloop, daemon=True).start()
keepActiveThread = threading.Thread(target=keepActive, args=(5,), daemon=True).start()


while True:
    question = input(colors.YELLOW + "AirSim> " + colors.ENDC)

    if question == "quit" or question == "exit":
        break

    if question == "emstop" or question == "emergency" or question == "terminate":
        drone.emergency()
        break
    
    if question == "stop" or question == "land":
        drone.land()
        continue

    if question == "clear":
        os.system("cls")
        continue

    response = ask(question)

    print(f"\n{response}\n")

    code = extract_python_code(response)
    if code is not None:
        drone.query_active()
        print(code)
        shouldRun = input(">>> is the code ok to run? (yes/*) <<< ")
        if (shouldRun == "yes"):
            print("Please wait while I run the code in AirReal...")
            try:
                exec(code)
            except Exception as e:
                print(e)
                a = input("Shutdown? ")
                if (a == "yes"): 
                    drone.emergency()
                break
        print("Done!\n")

drone.land()

