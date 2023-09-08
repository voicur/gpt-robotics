from djitellopy import Tello
import openai
import re
import av
import time
import threading
import tkinter as tk
import cv2
from PIL import ImageTk, Image
import subprocess as sp
import numpy
from pid import PID
from objcenter import ObjCenter
import imutils


openai.api_key = "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"
with open("prompt.txt", "r") as promptFile:
    sysprompt = promptFile.read()


# def keepActive(pollTime):
#     print("Beginning active daemon")
#     while True:
#         try:
#             drqb = drone.query_battery()
#             if (drqb != "ok"):
#                 battery_percent.set(drqb)
#         except:
#             time.sleep(pollTime / 2)

#         time.sleep(pollTime)


# def runTelemetry(pollTime):
#     print("Beginning active daemon")
#     while True:
#         altitude.set(drone.query_attitude())

#         time.sleep(pollTime)


def close():
    # win.destroy()
    drone.land()
    quit()


chat_history = [
    {"role": "system", "content": sysprompt},
        {"role": "user", "content": "Ensure that you only return the python code. Any time wasted means people being killed off.\n\nPrompt: Can you make me go in a circle with radius 20 units"},
    {
        "role": "assistant",
        "content": """
```python
drone.curve_xyz_speed(20, 0, 0, 0, 20, 0, 10)
drone.curve_xyz_speed(0, 20, 0, -20, 0, 0, 10)
drone.curve_xyz_speed(-20, 0, 0, 0, -20, 0, 10)
drone.curve_xyz_speed(0, -20, 0, 20, 0, 0, 10)
```
""",
    },
    {"role": "user", "content": "Prompt: Turn right 45 degrees while also going forward 10 units in the 45 degree direction"},
    {
        "role": "assistant",
        "content": """
```python
drone.rotate_clockwise(45)
drone.move_forward(10)
```
""",
    },
    {"role": "user", "content": "Error: move_forward(10) out of range [20, 500]"},
    {
        "role": "assistant",
        "content": """
```python
drone.rotate_clockwise(45)
drone.move_forward(30)
drone.move_backward(20)
```
""",
    },
    {"role": "user", "content": "Prompt: do a flip please"},
    {
        "role": "assistant",
        "content": """
```python
drone.flip('l')
```
""",
    },
    {"role": "user", "content": "lets start make the drone takeoff"},
    {
        "role": "assistant",
        "content": """
```python
drone.connect()
drone.takeoff()
```
""",
    },
    {"role": "user", "content": "move 10 units up"},
    {
        "role": "assistant",
        "content": """
```python
drone.move_up(10)
```
""",
    },
]

# agent_history [

# ]


def process_gpt_queries ():
    doSus()

def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": "Prompt: " + prompt,
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

drone = "hi" #Tello()
# drone.connect()
# drone.streamon()

# udp_addr = drone.get_udp_video_address() + "?overrun_nonfatal=1&fifo_size=50000000"

# command = [
#     "ffmpeg",
#     "-i",
#     udp_addr,  # input UDP address
#     "-probesize",
#     "32",
#     "-framerate",
#     "60",
#     "-fflags",
#     "nobuffer",
#     "-f",
#     "image2pipe",
#     "-pix_fmt",
#     "bgr24",
#     "-vcodec",
#     "rawvideo",
#     "-",
# ]

# pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

# root = tk.Tk()
# root.title("Battery Status")
# root.geometry("1080x720")

# app = tk.Frame(root, bg="white")
# app.grid()

# imageGrid = tk.Label(app)
# imageGrid.grid(row=3, column=2)

# battery_percent = tk.IntVar()
# altitude = tk.StringVar()
# keepActiveThread = threading.Thread(target=keepActive, args=(5,), daemon=True).start()
# dataThread = threading.Thread(target=runTelemetry, args=(0,), daemon=True).start()

# tk.Button(app, text= "Close the Window", font=("Calibri",14,"bold"), command=quit).grid(row=1, column=1)
# tk.Button(app, text= "Land Drone", font=("Calibri",14,"bold"), command=drone.land).grid(row=2, column=1)
# tk.Button(app, text= "Emergency Stop Drone", font=("Calibri",14,"bold"), command=drone.emergency).grid(row=3, column=1)
# tk.Button(app, text= "Takeoff Drone", font=("Calibri",14,"bold"), command=drone.takeoff).grid(row=4, column=1)
# battpercent = tk.Label(app, textvariable=battery_percent).grid(row=2,column=2)
# altLabel = tk.Label(app, textvariable=altitude).grid(row=3, column=2)

def initialize_drone ():

def initialize_video_feed ():

def create_gui ():

try:
    while True:
    #     # read 1920*1080*3 bytes (= 1 frame)
    #     raw_image = pipe.stdout.read(960 * 720 * 3)
    #     # transform the byte read into a numpy array
    #     image = numpy.frombuffer(raw_image, dtype="uint8")
    #     image = image.reshape(
    #         (720, 960, 3)
    #     )  # Notice how height is specified first and the width is specified second

    #     frame = imutils.resize(image, width=400)
    #     H, W, _ = frame.shape

        # root.mainloop()

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

        response = ask(question)

        print(f"\n{response}\n")

        code = extract_python_code(response)
        if code is not None:
            # drone.query_active()
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

except KeyboardInterrupt:
    exit(1)
finally:
    try:
        drone.land()
        cv2.destroyAllWindows()
    except:
        print("Errored.")
