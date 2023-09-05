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

try:
    # face_center = ObjCenter("./facedet.xml")
    # pan_pid = PID(kP=0.7, kI=0.0001, kD=0.1)
    # tilt_pid = PID(kP=0.7, kI=0.0001, kD=0.1)

    # forward_tilt_pid = PID(kP=0.2, kI=0.0001, kD=0.1)

    # pan_pid.initialize()
    # tilt_pid.initialize()
    # forward_tilt_pid.initialize()

    # drone.takeoff()
    # time.sleep(5)
    # drone.move_up(70)

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

    #     # calculate the center of the frame as this is (ideally) where
    #     # we will we wish to keep the object
    #     centerX = W // 2
    #     centerY = H // 2

    #     # draw a circle in the center of the frame
    #     cv2.circle(
    #         frame, center=(centerX, centerY), radius=5, color=(0, 0, 255), thickness=-1
    #     )

    #     # find the object's location
    #     frame_center = (centerX, centerY)
    #     objectLoc = face_center.update(frame, frameCenter=None)
    #     # print(centerX, centerY, objectLoc)
    #     max_speed_threshold = 40

    #     ((objX, objY), rect, d) = objectLoc
    #     if d > 25 or d == -1:
    #         # then either we got a false face, or we have no faces.
    #         # the d - distance - value is used to keep the jitter down of false positive faces detected where there
    #         #                   were none.
    #         # if it is a false positive, or we cannot determine a distance, just stay put
    #         # print(int(pan_update), int(tilt_update))
    #         # if track_face and fly:
    #         drone.send_rc_control(0, 0, 0, 0)
    #         continue  # ignore the sample as it is too far from the previous sample

    #     if rect is not None:
    #         (x, y, w, h) = rect
    #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #         print(w, " x ", h)

    #         # draw a circle in the center of the face
    #         cv2.circle(
    #             frame, center=(objX, objY), radius=5, color=(255, 0, 0), thickness=-1
    #         )

    #         # Draw line from frameCenter to face center
    #         cv2.arrowedLine(
    #             frame, frame_center, (objX, objY), color=(0, 255, 0), thickness=2
    #         )

    #         # calculate the pan and tilt errors and run through pid controllers
    #         pan_error = centerX - objX
    #         pan_update = pan_pid.update(pan_error, sleep=0)

    #         forward_error = 40 - int(w)
    #         if forward_error > 30:
    #             forward_error = 30 + forward_error / 6
    #         forward_tilt = forward_tilt_pid.update(forward_error, sleep=0)

    #         tilt_error = centerY - objY
    #         tilt_update = tilt_pid.update(tilt_error, sleep=0)

    #         # print(pan_error, int(pan_update), tilt_error, int(tilt_update))
    #         cv2.putText(
    #             frame,
    #             f"X Error: {pan_error} PID: {pan_update:.2f}",
    #             (20, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX,
    #             1,
    #             (0, 255, 0),
    #             2,
    #             cv2.LINE_AA,
    #         )

    #         cv2.putText(
    #             frame,
    #             f"Y Error: {tilt_error} PID: {tilt_update:.2f}",
    #             (20, 70),
    #             cv2.FONT_HERSHEY_SIMPLEX,
    #             1,
    #             (0, 0, 255),
    #             2,
    #             cv2.LINE_AA,
    #         )

    #         if pan_update > max_speed_threshold:
    #             pan_update = max_speed_threshold
    #         elif pan_update < -max_speed_threshold:
    #             pan_update = -max_speed_threshold

    #         # NOTE: if face is to the right of the drone, the distance will be negative, but
    #         # the drone has to have positive power so I am flipping the sign
    #         pan_update = pan_update * -1

    #         if tilt_update > max_speed_threshold:
    #             tilt_update = max_speed_threshold
    #         elif tilt_update < -max_speed_threshold:
    #             tilt_update = -max_speed_threshold

    #         if forward_tilt > max_speed_threshold:
    #             forward_tilt = max_speed_threshold
    #         elif forward_tilt < -max_speed_threshold:
    #             forward_tilt = -max_speed_threshold

    #         print(int(pan_update), int(tilt_update))
    #         drone.send_rc_control(
    #             int(pan_update) // 3, int(forward_tilt), int(tilt_update) // 2, 0
    #         )
    #     pipe.stdout.flush()
    #     cv2.imshow("Drone Face Tracking", frame)
    #     cv2.waitKey(1)
    #     if cv2.waitKey(1) & 0xFF == ord("q"):
    #         exit_event.set()
        # throw away the data in the pipe's buffer.

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
