from models.whisper_rt import OnlineVoiceDetector
import config.native as conf
import openai
from config.native import KEYS as keys, VISION_MODEL as model_to_use, KEY as gpt_key
import requests
import asyncio
from controllers.Controller import Controller
from controllers.Video import Video
from controllers.Application import colors
from djitellopy import Tello
import base64
import re
import cv2
import os
import sys
from controllers.Application import app as App
import threading
import numpy as np


# ----------------------------- VARIABLES DEFINITIONS ----------------------------- #

# ----------------------------- MAIN START ----------------------------- #

def main ():
    session_chat_history = None
    voice_detector = OnlineVoiceDetector(api_key=gpt_key)
    openai.api_key = gpt_key

    drone = Tello()    
    video_tools = Video("config.native", drone)
    app = App("config.native", drone, video_tools)

    app.drone.connect()
    app.video_tools.initializePipe()
    drone.takeoff()
    app.start_active_daemon()
    

    try:
        os.system('reset')
        while True:
            # insert the voice commander here!
            try: 
                question = input(colors.YELLOW + "AirSim> " + colors.ENDC)
            except KeyboardInterrupt:
                drone.emergency()
                app.cleanup

            # Shortcuts without AI
            if question == "quit" or question == "exit":
                print("exiting")
                video_tools.cleanup()
                cv2.destroyAllWindows()
                sys.exit(0)

            if question == "stop" or question == "land":
                drone.land()
                continue

            if question == "clear":
                os.system("cls")
                continue

            # Error catching
            if question == "emstop" or question == "emergency" or question == "terminate" or question == "stop!":
                drone.emergency()
                break

            base64_image = app.get_wait_for_b64_image()

            image_bytes = base64.b64decode(base64_image)

            # Convert the bytes to a NumPy array
            nparr = np.frombuffer(image_bytes, np.uint8)

            # Decode the NumPy array into an image
            new_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
            cv2.imshow('Image Window', new_image)
            cv2.waitKey(1)

            # # response, session_chat_history = ask(question, b64_image_or_url=getPreviewFrameB64("capture.jpg"), prev_chat_history=session_chat_history)
            response = app.ask(question, b64_image_or_url=base64_image)
            print(f"\n{response}\n")
            code = app.extract_python_code(response)
            app.execute_commands(code)

            response = app.ask("Do you think that you have finished the task? If not and it has not completed the task CORRECTLY or otherwise, INCLUDE more python code to finish based on the image! If you see the code works, DO NOT MOVE, but if the image asks to go a place and you are not at the place/endpoint, further movement is required, you must move.", b64_image_or_url=base64_image, system=True)
            print(f"\n{response}\n")
            code = app.extract_python_code(response)
            if (code != ""):
                app.execute_commands(code)


    except KeyboardInterrupt:
        app.cleanup()
        drone.emergency();
        is_running = False
        thread.join()
        # drone.emergency();
        print("quitting")
        video_tools.cleanup()
        sys.exit(0)

main()

