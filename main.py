from djitellopy import Tello
import openai
import re
import time
import threading
import tkinter as tk
from vidgear.gears import VideoGear
import cv2
from PIL import ImageTk, Image

openai.api_key = "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"
with open("prompt.txt", "r") as promptFile:
    sysprompt = promptFile.read()


def keepActive(pollTime):
    print("Beginning active daemon")
    while True:
        try:
            drqb = drone.query_battery()
            if (drqb != "ok"):
                battery_percent.set(drqb)
        except:
            time.sleep(pollTime / 2)

        time.sleep(pollTime)


def runTelemetry(pollTime):
    print("Beginning active daemon")
    while True:
        altitude.set(drone.query_attitude())

        time.sleep(pollTime)


def close():
    # win.destroy()
    drone.land()
    quit()


chat_history = [
    {"role": "system", "content": sysprompt},
    {"role": "user", "content": "lets start make the drone takeoff"},
    {
        "role": "assistant",
        "content": """
```python
drone.connect()
drone.takeoff()
```

This code uses the `drone.connect()` function to connect to the drone on its interface, and `drone.takeoff()` to let the drone takeoff at its current position.""",
    },
    {"role": "user", "content": "move 10 units up"},
    {
        "role": "assistant",
        "content": """
```python
drone.move_left(100)
```

This code uses the `move_left()` function to move the drone to a new position that is 100 units left from the current position.""",
    },
]


def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=chat_history, temperature=0
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


print(
    "Welcome to the AirSim chatbot! I am ready to help you with your AirSim questions and commands."
)

drone = Tello()
drone.connect()
drone.streamon()

# cap = cv2.VideoCapture(
#     drone.get_udp_video_address() + "?overrun_nonfatal=1&fifo_size=50000000",
#     cv2.CAP_FFMPEG,
#     # [cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY ]
# )

udp_addr=drone.get_udp_video_address() + "?overrun_nonfatal=1&fifo_size=50000000"

import av

container = av.open(udp_addr, options={'probesize': '32', 'fflags': 'nobuffer'})

# cap = VideoGear(source=udp_addr, stabilize=True,).start()

def video_stream():
    frame = cap.read()
    # cv2.putText(
    #     frame,
    #     "Before",
    #     (10, frame.shape[0] - 10),
    #     cv2.FONT_HERSHEY_SIMPLEX,
    #     0.6,
    #     (0, 255, 0),
    #     2,
    # )
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    imageGrid.imgtk = imgtk
    imageGrid.configure(image=imgtk)
    imageGrid.after(1, video_stream) 

root = tk.Tk()
root.title("Battery Status")
root.geometry("1080x720")

app = tk.Frame(root, bg="white")
app.grid()

imageGrid = tk.Label(app)
imageGrid.grid(row=3, column=2)


# drone.takeoff()

battery_percent = tk.IntVar()
altitude = tk.StringVar()
keepActiveThread = threading.Thread(target=keepActive, args=(5,), daemon=True).start()
dataThread = threading.Thread(target=runTelemetry, args=(0,), daemon=True).start()

tk.Button(app, text= "Close the Window", font=("Calibri",14,"bold"), command=quit).grid(row=1, column=1)
tk.Button(app, text= "Land Drone", font=("Calibri",14,"bold"), command=drone.land).grid(row=2, column=1)
tk.Button(app, text= "Emergency Stop Drone", font=("Calibri",14,"bold"), command=drone.emergency).grid(row=3, column=1)
tk.Button(app, text= "Takeoff Drone", font=("Calibri",14,"bold"), command=drone.takeoff).grid(row=4, column=1)
battpercent = tk.Label(app, textvariable=battery_percent).grid(row=2,column=2)
altLabel = tk.Label(app, textvariable=altitude).grid(row=3, column=2)

try:
    while True:
        video_stream()
        root.mainloop()

        question = input(colors.YELLOW + "AirSim> " + colors.ENDC)

        # Shortcuts without AI
        if question == "quit" or question == "exit":
            break

        if question == "stop" or question == "land":
            drone.land()
            continue

        if question == "clear":
            os.system("cls")
            continue

        # Error catching
        if question == "emstop" or question == "emergency" or question == "terminate":
            drone.emergency()
            break

        # response = ask(question)

        # print(f"\n{response}\n")

        # code = extract_python_code(response)
        # if code is not None:
        #     drone.query_active()
        #     print(code)
        #     shouldRun = input(">>> is the code ok to run? (yes/*) <<< ")
        #     if (shouldRun == "yes"):
        #         print("Please wait while I run the code in AirReal...")
        #         try:
        #             exec(code)
        #         except Exception as e:
        #             print(e)
        #             a = input("Shutdown? ")
        #             if (a == "yes"):
        #                 drone.emergency()
        #             break
        #     print("Done!\n")

except KeyboardInterrupt:
    exit(1)
finally:
    try:
        drone.land()
    except:
        print("Errored.")
