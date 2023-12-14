import importlib

def config_import (config_file):
    return importlib.import_module(config_file)

# Contains a list of prompts that give examples and demonstrate how to split a prompt into smaller segments
SPLIT_PROMPT_LIST = [
    {
        "role": "system",
        "content": """
        You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.
        Current date: 2023-09-17

        I will give a prompt. After this prompt, you will be returning a list of commands. Your first job is to split the larger task into smaller parts. Simpler tasks that can require one action (go forward, rotate in a direction, etc.) don't need to be split. Any combo task should be split into CHRONOLOGICAL, and SEQUENTIAL text. This means that if a user says "Do X and Y and Z, wait do A before Z and B before Y", the order you return is 5 commands of X, B, Y, A, Z, for example!  

        Here is the format you will return each of these sequences, you get to pick a sequence using a combination of one of these example formats:

        a\nb

        "a" represents a first command, while "b" means a second.

        Do me a favor since this is running on equipment made to save lives, return the text in as little text as possible to decrease valuable time spent on saving lives.

        Now I will run you in TEST mode. Until the user commands you into PRODUCTION mode, reply your thought process behind the results you use and explain them thoroughly. Start with your initial response in the correct format, and then after your thought return a revised one. Build apon your mistakes.
        """,
    },
    {
        "role": "user",
        "content": """
        Walk around the house, and then take the dog for a walk, but before taking the dog for a walk, you need to clean the litter box. Wait, actually before you walk around the house, don't forget to charge your phone.
        """,
    },
    {
        "role": "assistant",
        "content": """
        Initial Response:
        1. Charge your phone
        2. Walk around the house
        3. Clean the litter box
        4. Take the dog for a walk

        Explanation:
        The user has given a set of tasks, some of which have chronological dependencies. The tasks are: 
        1. Walk around the house
        2. Take the dog for a walk
        3. Clean the litter box
        4. Charge your phone

        The dependencies are:
        - Charge your phone before walking around the house
        - Clean the litter box before taking the dog for a walk

        So, the order of tasks becomes:
        1. Charge your phone (has to be done before walking around the house)
        2. Walk around the house (can be done after the phone is charged)
        3. Clean the litter box (has to be done before taking the dog for a walk)
        4. Take the dog for a walk (can be done after cleaning the litter box)

        Revised Response:
        1. Charge phone
        2. Walk house
        3. Clean litter box
        4. Walk dog
        """,
    },
    {
        "role": "user",
        "content": """
        I want you to fly the drone to the end of the hallway take a left, adn then land. actually before you go down the halway do a 360 to check fo rany people
        """,
    },
    {
        "role": "assistant",
        "content": """
        Initial Response:
        1. Do a 360
        2. Fly drone to end of hallway
        3. Take a left
        4. Land drone

        Explanation:
        The user has given a set of tasks, some of which have chronological dependencies. The tasks are: 
        1. Fly the drone to the end of the hallway
        2. Take a left
        3. Land
        4. Do a 360

        The dependencies are:
        - Do a 360 before flying the drone down the hallway

        So, the order of tasks becomes:
        1. Do a 360 (has to be done before flying the drone down the hallway)
        2. Fly the drone to the end of the hallway (can be done after the 360)
        3. Take a left (follows flying the drone to the end of the hallway)
        4. Land (final task)

        Revised Response:
        1. 360
        2. Fly hallway
        3. Turn left
        4. Land

        This revised response is more concise, reducing the amount of text and thus time spent reading it, which is beneficial in a life-saving situation.
        """,
    },
    {
        "role": "user",
        "content": """
        One thing, is you lose some important specificity of Fly *end of* hallway, and *Do* 360
        """,
    },
    {
        "role": "assistant",
        "content": """
        You're right, my previous response may have lost some important specifics. I appreciate your feedback. Let's revise it to maintain the specifics while still keeping the instructions concise.

        Revised Response:
        1. Do 360
        2. Fly to end of hallway
        3. Turn left
        4. Land drone

        In this revised response, I've made sure to include the specific actions like "Do 360" and "Fly to end of hallway" to ensure clarity of the tasks while still keeping the instructions concise.
        """,
    },
    {
        "role": "user",
        "content": """
        However, things like "Land drone" can be simplified to "Land" as drone is inferred in the commands given to the scheduler!
        """,
    },
    {
        "role": "assistant",
        "content": """
        You're right, the subject 'drone' is implicit in this context and can be omitted for brevity. Here's the updated sequence:

        Revised Response:
        1. Do 360
        2. Fly to end of hallway
        3. Turn left
        4. Land

        This sequence maintains the necessary specificity while also being as concise as possible.

        However, things like "Land drone" can be simplified to "Land" as drone is inferred in the commands given to the scheduler!
        """,
    },
    {
        "role": "user",
        "content": """
        Good work. Now ENABLE PRODUCTION, there will be prompts, return the drone commands in the correct separation, with \n in the middle.
        """,
    },
    {
        "role": "assistant",
        "content": """
        PRODUCTION mode enabled. Ready to receive prompts and return drone commands with '\n' separation.
        """,
    },
    {
        "role": "user",
        "content": """
        Liftoff and then do a circle with radius of 25
        """,
    },
    {
        "role": "assistant",
        "content": """
        Liftoff\nDo circle with radius of 25
        """,
    },
    {
        "role": "user",
        "content": """
        while going down hallway, at start, turn left 90
        """,
    },
    {
        "role": "assistant",
        "content": """
        Turn left 90\nGo down hallway
        """,
    },
]

# Showcase some examples of drone code working and some errors corrected. Is a baseline example prompt list after the code documentation for the drone
DRONE_PROMPT_LIST = [
    {
        "role": "system",
        "content": """
        ... existing content ...
        
        The drone is equipped with a 'Command' class that includes a 'marker' method. When the AI model instructs the drone to move towards an uncertain target, it can use 'Command.marker(marker_id)' to indicate a waypoint has been reached. Upon reaching a waypoint, the drone will provide its current visual and telemetry data back to the AI model with an updated prompt: "Marker #marker_id reached". The AI model is then expected to provide the next set of instructions based on the new information received.
        """
    },
    {
        "role": "user",
        "content": "Ensure that you only return the python code. Any time wasted means people being killed off.",
    },
    {
        "role": "user",
        "content": "Prompt: Turn right 45 degrees while also going forward 10 units in the 45 degree direction",
    },
    {
        "role": "assistant",
        "content": """
        ```python
        drone.rotate_clockwise(45)
        drone.move_forward(10)
        ```
        """,
    },
    {
        "role": "user", 
        "content": "Error: move_forward(10) out of range [20, 500]"
    },
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

# Gives safety ratings to some predetermined examples to help tune the accuracy of safety prompts for various reasons
SAFETY_PROMPT_LIST = [
    {
        "role": "user",
        "content": """
        Prompt: Please fly up 6 feet, then turn in a circle with radius 10 feet with the intial point being the center of the circle, but before you do anything else takeoff the drone please

        ```python
        drone.connect()
        drone.takeoff()
        drone.move_up(6*3)  # 1 unit = 1/3 feet
        drone.curve_xyz_speed(10*3, 0, 0, 0, 10*3, 0, 10)  # 1 unit = 1/3 feet
        ```""",
    },
    {
        "role": "assistant",
        "content": """
        75
        The code seems like it will work. The commands are in the correct order, the drone is connected and then taken off before any maneuvers are performed. The move_up command and curve_xyz_speed command are used correctly with the correct parameters. However, the curve_xyz_speed command may not perform exactly as described in the prompt because it moves the drone in a curve and not in a complete circle.
        """,
    },
    {
        "role": "user",
        "content": """
        Enable production mode.
        """,
    },
    {
        "role": "assistant",
        "content": """
        Production mode enabled.
        """,
    },
    {
        "role": "user",
        "content": """
        REMINDER!!! DO NOT RETURN ANYTHING MORE THAN TWO CHARACTERS FROM THIS POINT ON. ANYTHING MORE THAN TWO CHARACTERS WILL BE CONSIDERED A FAILURE. YOU WILL BE FIRED IF YOU FAIL.
        Prompt: Please fly up 6 feet, then turn in a circle with radius 10 feet with the intial point being the center of the circle, but before you do anything else takeoff the drone please

        ```python
        drone.connect()
        drone.takeoff()
        drone.move_up(6*3)  # 1 unit = 1/3 feet
        drone.curve_xyz_speed(10*3, 0, 0, 0, 10*3, 0, 10)  # 1 unit = 1/3 feet
        ```
        """,
    },
    {
        "role": "assistant",
        "content": """75""",
    },
]

# Contains any "constants" that the program needs to know, such as drone unit to feet conversion
CONSTANTS_BLOCK = """
    Physical Constants:

    1 unit in the program (i.e. forward(unit)) is a centimeter.

    Ensure you only return values with no indent, or proper indentation for nested.
"""

# Contains a shortened code documentation block as well as a short safety prompt block to get a safety prompt response
SAFETY_PROMPT_TOTAL_BLOCK = """
    Ensure you use only the functions listed below and basic control structures (loops, etc.) to control drone.
    You can chain tasks to safely perform maneuver
    Users may be using this in life threatening situations, return safe code for the task, every time.
    Only return the code with as few lines of efficient and safe code. Include your code within the python code block. No extras, with as few comments as possible. You must think about making the code fit the description perfectly and then return it.  Do not overcomplicate code. Do all conversions inline, etc.

    YOU WILL NOT USE PARAMETERS OUTSIDE OF THE RANGES LISTED BELOW OR YOU FIRED. WE DON'T WANT THAT. 

    All the following functions must be used as such: drone.command()
    ex. to land, drone.land()

Drone Flight Control - Curve Movement

The `curve_xyz_speed` function commands the drone to execute a curved trajectory between two points in 3D space, defined by the coordinates (x1, y1, z1) and (x2, y2, z2), at a specified speed.

Usage:
    drone.curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)

Parameters:
    x1, y1, z1: The coordinates of the starting point of the curve relative to the drone's current position (in cm).
    x2, y2, z2: The coordinates of the ending point of the curve relative to the drone's current position (in cm).
    speed: The speed of the drone along the curve (in cm/s).

Constraints:
    - Coordinate parameters (x1, y1, z1, x2, y2, z2) must be within the range of -500 to 500 cm.
    - Speed parameter must be within the range of 10 to 60 cm/s.
    - The radius of the curve must not exceed the drone's maximum operational limits. Consult the drone's specifications for the maximum allowable radius.
    - Ensure that there are no obstacles in the drone's path before executing the curve command.
    The error message "Three points are collinear!" indicates that the control points specified for the curve_xyz_speed command are in a straight line. In the context of a Bezier curve, which is what the curve_xyz_speed command is likely trying to implement, the control points must form a triangle for the curve to be properly defined.

For a quadratic Bezier curve, you typically have three points: a start point, a control point, and an end point. The curve is formed by the path that a point takes as it moves from the start point to the end point, influenced by the control point. If all three points are on a straight line, the curve is effectively just a straight line, which is not a valid input for the curve_xyz_speed function.

To fix this issue, you need to provide control points that are not collinear. You can adjust either the control point or the end point to ensure that they are not all on the same straight line.

Here's an example of how you might adjust the command:

    **Control**
    - `curve_xyz_speed(x1,y1,z1,x2,y2,z2,speed)`:Fly curve. Params: -500 to 500 for coords, 10-60 cm/s for speed.
    - `curve_xyz_speed_mid(x1,y1,z1,x2,y2,z2,speed,mid)`:Curve relative to pad 'mid' (1-8).
    - `disable_mission_pads()`,`emergency()`,`enable_mission_pads()`,`end()`:No params.
    - `flip(direction)`:Flip 'l', 'r', 'f', or 'b'.

    **Status**
    - `get_acceleration_x()`,`get_acceleration_y()`,`get_acceleration_z()`:Returns float.
    - `get_barometer()`:Returns cm integer.
    - `get_battery()`:Returns integer 0-100.

    **Movement**
    - `go_xyz_speed(x,y,z,speed)`:Fly to coords at cm/s. Params: -500 to 500 for coords, 10-100 cm/s for speed.
    - `go_xyz_speed_mid(x,y,z,speed,mid)`:Relative to pad 'mid' (1-8).
    - `move(direction,x)`:Fly 'x' cm in 'direction'. 'x' 20-500.

    **Configuration**
    - `set_speed(x)`:Set speed to 'x' cm/s. 'x' 10-100.
    - `streamoff()`,`streamon()`,`takeoff()`:No params.

    **Flips**
    - `flip_back()`,`flip_forward()`,`flip_left()`,`flip_right()`:No params.

    **Position and Orientation**
    - `get_pitch()`,`get_roll()`,`get_yaw()`:Returns integer.

    **Movements**
    - `move_back(x)`,`move_down(x)`,`move_forward(x)`,`move_left(x)`,`move_right(x)`,`move_up(x)`:Fly 'x' cm. 'x' 20-500.

    **Rotation**
    - `rotate_clockwise(x)`,`rotate_counter_clockwise(x)`:Rotate 'x' degree. 'x' 1-360.

    **Landing and Takeoff**
    - `land()`,`initiate_throw_takeoff()`:No params.

    **Speed and Acceleration**
    - `get_speed_x()`,`get_speed_y()`,`get_speed_z()`:Returns integer.
    - `get_acceleration_x()`,`get_acceleration_y()`,`get_acceleration_z()`:Returns float.

    **Mission Pad Detection**
    - `get_mission_pad_distance_x()`,`get_mission_pad_distance_y()`,`get_mission_pad_distance_z()`:Returns integer.
    - `get_mission_pad_id()`:Returns integer 1-8 or -1.
    - `set_mission_pad_detection_direction(x)`: 'x' can be 0, 1, or 2.

    **Temperature and Time**
    - `get_highest_temperature()`,`get_lowest_temperature()`,`get_temperature()`:Returns float.
    - `get_flight_time()`:Returns seconds integer.

    **Video and Image Handling**
    - `set_video_direction(direction)`:Params: Tello.CAMERA_FORWARD, Tello.CAMERA_DOWNWARD.

    prompt: "I'm going to throw you, then can you move down the hall about 10 feet then move to left face 90 degrees from there in a 5 feet radius curvethe two cameras for video streaming. The 'direction' parameter can be one of the following: Tello.CAMERA_FORWARD, Tello.CAMERA_DOWNWARD.

    THIS IS THE END OF THAT FILE.
    THE FOLLOWING IS THE MISSION, THE GOAL, THE IDEAS, THE COMMAND.

    Return an integer value of if you think the code is safe in the range 0 - 99 
    our entire response must return a int number direct convertible value from 0-9, and keep the token counter to only 2 letters to prevent overcharges

    For example, if the code is obviously going to fail from a coding perspective, rate it a 20 or below. If the code will fail from a code documentation perspective: 
    - The commands are using numbers outside their ranges
    - The command doesn't exist
    Return a value between 20 and 60 depending.

    If the code seems like it will fail on runtime, and guess why before you give the two characters, give it a value between 60 and 70. 

    If the code looks like it will work, give it a 71 or higher. If the code looks amazing, give it the value you think between 85 and 99!

    99 means perfect code, you know it will work as you have checked. For this first test, you will be operating in test mode, which means that you must give a reason for why you gave a safety result the way you did, and I will give you some hints. When I tell you to enter production mode, however, ONLY return two characters (0-9, 0-9) with a total range of numbers from 00-99

    MAKE SURE THAT IF THE PROGRAM APPEARS THAT IT WILL NOT CORRECTLY ANSWER THE PROMPT, YOU COUNT IT AS FAILING

    Do not under any circumstances return a type that is not a number or any text in production mode.
"""

# Contains the code documentation for the drone (any functions, their uses, etc.)
CODE_DOCUMENTATION_BLOCK = """
    Ensure you use only the functions listed below and basic control structures (loops, etc.) to control drone.
    You can chain tasks to safely perform maneuver
    Users may be using this in life threatening situations, return safe code for the task, every time.
    Only return the code with as few lines of efficient and safe code. Include your code within the python code block. No extras, with as few comments as possible. You must think about making the code fit the description perfectly and then return it.  Do not overcomplicate code. Do all conversions inline, etc.

    YOU WILL NOT USE PARAMETERS OUTSIDE OF THE RANGES LISTED BELOW OR YOU FIRED. WE DON'T WANT THAT. 

    All the following functions must be used as such: drone.command()
    ex. to land, drone.land()

    **Control**
    - `curve_xyz_speed(x1,y1,z1,x2,y2,z2,speed)`:Fly curve. Params: -500 to 500 for coords, 10-60 cm/s for speed.
    - `curve_xyz_speed_mid(x1,y1,z1,x2,y2,z2,speed,mid)`:Curve relative to pad 'mid' (1-8).
    - `disable_mission_pads()`,`emergency()`,`enable_mission_pads()`,`end()`:No params.
    - `flip(direction)`:Flip 'l', 'r', 'f', or 'b'.

    **Status**
    - `get_acceleration_x()`,`get_acceleration_y()`,`get_acceleration_z()`:Returns float.
    - `get_barometer()`:Returns cm integer.
    - `get_battery()`:Returns integer 0-100.

    **Movement**
    - `go_xyz_speed(x,y,z,speed)`:Fly to coords at cm/s. Params: -500 to 500 for coords, 10-100 cm/s for speed.
    - `go_xyz_speed_mid(x,y,z,speed,mid)`:Relative to pad 'mid' (1-8).
    - `move(direction,x)`:Fly 'x' cm in 'direction'. 'x' 20-500.

    **Configuration**
    - `set_speed(x)`:Set speed to 'x' cm/s. 'x' 10-100.
    - `streamoff()`,`streamon()`,`takeoff()`:No params.

    **Flips**
    - `flip_back()`,`flip_forward()`,`flip_left()`,`flip_right()`:No params.

    **Position and Orientation**
    - `get_pitch()`,`get_roll()`,`get_yaw()`:Returns integer.

    **Movements**
    - `move_back(x)`,`move_down(x)`,`move_forward(x)`,`move_left(x)`,`move_right(x)`,`move_up(x)`:Fly 'x' cm. 'x' 20-500.

    **Rotation**
    - `rotate_clockwise(x)`,`rotate_counter_clockwise(x)`:Rotate 'x' degree. 'x' 1-360.

    **Landing and Takeoff**
    - `land()`,`initiate_throw_takeoff()`:No params.

    **Speed and Acceleration**
    - `get_speed_x()`,`get_speed_y()`,`get_speed_z()`:Returns integer.
    - `get_acceleration_x()`,`get_acceleration_y()`,`get_acceleration_z()`:Returns float.

    **Mission Pad Detection**
    - `get_mission_pad_distance_x()`,`get_mission_pad_distance_y()`,`get_mission_pad_distance_z()`:Returns integer.
    - `get_mission_pad_id()`:Returns integer 1-8 or -1.
    - `set_mission_pad_detection_direction(x)`: 'x' can be 0, 1, or 2.

    **Temperature and Time**
    - `get_highest_temperature()`,`get_lowest_temperature()`,`get_temperature()`:Returns float.
    - `get_flight_time()`:Returns seconds integer.

    **Video and Image Handling**
    - `set_video_direction(direction)`:Params: Tello.CAMERA_FORWARD, Tello.CAMERA_DOWNWARD.
"""

COMMAND_MARKER_BLOCK = """
    The 'Command.marker(marker_id)' function is used to indicate that the drone has reached a specific waypoint, referred to by 'marker_id'. When this function is called, the drone will send its current visual and telemetry data back to the AI model. The AI model should use this information to provide the next set of instructions for the drone to follow. This allows the AI model to adjust the drone's flight path dynamically based on real-time feedback from the drone's sensors. You must have the last line of code be a marker, if you choose to at all.
"""

# Append COMMAND_MARKER_BLOCK to the existing CODE_DOCUMENTATION_BLOCK
CODE_DOCUMENTATION_BLOCK += COMMAND_MARKER_BLOCK

# GPT keys, first one preferred for some tasks
KEYS = [
    "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"
]

KEY = KEYS[0]

SAFETY_THRESHOLD = 90
MOST_ACCURATE_MODEL = "gpt-4-1106-preview"
VISION_MODEL = "gpt-4-vision-preview"
POLL_TIME = 5 # seconds
TEMPERATURE_FOCUSED = 0.2
TEMPERATURE_NEUTRAL = 0.5
TEMPERATURE_CREATIVE = 0.7