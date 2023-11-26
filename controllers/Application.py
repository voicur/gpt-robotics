from config.native import config_import
import re
import time
import threading
# from Command import Command

import openai

import requests
import asyncio

import base64
import re
import cv2
import os
import sys


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"        

class app:
    def __init__(self, config_file, drone, video_tools):
        self.drone = drone
        self.video_tools = video_tools
        self.prev_chat_history = None
        self.reg_code = re.compile(r"```(.*?)```", re.DOTALL)

        cfg = config_import(config_file)

        self.conf = cfg
        self.keepActiveThread = threading.Thread(target=self.keepActive, args=(self.conf.POLL_TIME, ), daemon=True)

    def keepActive(self, pollTime):
        print("Beginning active daemon")
        while True:
            try:
                battery_query_info = self.drone.query_battery()
                if (battery_query_info != "ok"):
                    pass
            except:
                time.sleep(pollTime / 2)

            time.sleep(pollTime)

    def start_active_daemon (self):
        self.keepActiveThread.start()

    def cleanup (self):
        self.keepActiveThread.join()
    # ----------------------------- FUNCTIONS DEFINITIONS ----------------------------- #

    def is_b64_image(self, b64_image_or_url):
        base64_pattern = r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
        url_pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        
        if re.match(base64_pattern, b64_image_or_url):
            return True
        
        if re.match(url_pattern, b64_image_or_url):
            return False

    def validate_keys(self, keys, models):
        valid_keys = []
        for key in keys:
            # OpenAI API URL for listing engines
            api_url = "https://api.openai.com/v1/models"
            
            # Prepare headers for authentication
            headers = {
                "Authorization": f"Bearer {key}"
            }
            
            try:
                # Make the GET request to the API
                response = requests.get(api_url, headers=headers)
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    
                    # response.json()["data"] contains a dict with a lot of models
                    # getting just the model from the id, gives us just the key i.e. gpt-3.5-turbo-16k
                    # the, it is a list of ids, so we can make it a set
                    # woohoo!!                 
                    model_set = set([model['id'] for model in response.json()['data']])

                    # if the models the program uses are accessible with the api_key, continue!
                    if (all(model_name in model_set for model_name in models)):
                        valid_keys.append(key)

                elif (response.status_code == 401):
                    print("whoops it bad key")        
                else:
                    # Print the error message
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                # Handle exceptions (e.g., network issues)
                print(f"An error occurred: {e}")

        return valid_keys

    def extract_python_code(self, content):
        code_blocks = self.reg_code.findall(content)
        if code_blocks:
            full_code = "\n".join(code_blocks)

            if full_code.startswith("python"):
                full_code = full_code[7:]

            return full_code
        else:
            return None

    def ask(self, prompt, b64_image_or_url=None, system=False):
        conf = self.conf

        # the system prompt, gives code context and a basic training combo.
        chat_history = [
            {
                "role": "system",
                "content": conf.CODE_DOCUMENTATION_BLOCK + conf.CONSTANTS_BLOCK,
            }
        ] + conf.DRONE_PROMPT_LIST

        # if not first attempt, just use the last successful attempt to overwrite
        if (self.prev_chat_history is not None):
            chat_history = self.prev_chat_history

        # content is to store multiple types of input, image and text
        content = []
        content.append({
            "type": "text", 
            "text": f"{prompt}"
        })

        if (b64_image_or_url is not None):
            if (self.is_b64_image(b64_image_or_url)):
                b64_image_or_url = f"data:image/jpeg;base64,{b64_image_or_url}"
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": b64_image_or_url,
                    },
                })

        # add it to the history so the assistant knows what its doing
        if (system):
            chat_history.append(
                {
                    "role": "system",
                    "content": content,
                }
            )
        else:
            chat_history.append(
                {
                    "role": "user",
                    "content": content,
                }
            )

        # get the results
        completion = openai.chat.completions.create(
            model=conf.VISION_MODEL, messages=chat_history, temperature=conf.TEMPERATURE_FOCUSED, max_tokens=4096, seed=123456
        )

        # trim the results down
        the_content = completion.choices[0].message.content
        chat_history.append(
            {
                "role": "assistant",
                "content": the_content,
            }
        )
        
        self.prev_chat_history = chat_history

        # return the results and the chat history to overwrite in the main (how to global var?)
        return the_content
        
    def execute_commands(self, commands):
        drone = self.drone

        commands = self.dedent_code(commands)
        # Validate and execute the commands safely
        try:
            exec(commands)
        except Exception as e:
            print(f"Error executing commands: {e}")

    def dedent_code(self, code):
        if (code is None):
            return None
        # Split the code into lines
        lines = code.split('\n')
        
        # Find the minimum indentation of non-empty lines
        min_indent = None
        for line in lines:
            if line.strip():  # Ignore empty lines
                indent = len(line) - len(line.lstrip())
                if min_indent is None or indent < min_indent:
                    min_indent = indent
        
        # Dedent all lines by the minimum indentation
        if min_indent is not None:
            dedented_lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]
        else:
            dedented_lines = lines
        
        # Rejoin the lines into a single string
        dedented_code = '\n'.join(dedented_lines)
        
        return dedented_code

    def get_wait_for_image (self):
        frame, height, width = self.video_tools.getImage()
        while (frame is None):
            frame, height, width = self.video_tools.getImage()
            pass
        return (frame, height, width)

    def get_wait_for_b64_image (self):
        base64_image = self.video_tools.getImgB64(already_has_this_image=self.get_wait_for_image())
        return base64_image