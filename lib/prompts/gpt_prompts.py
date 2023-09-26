SPLIT_PROMPT = [
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

MAIN_GPT_PROMPT = [
    {
        "role": "user",
        "content": "Ensure that you only return the python code. Any time wasted means people being killed off.\n\nPrompt: Can you make me go in a circle with radius 20 units",
    },
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

SAFETY_MODEL_PROMPT = [
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

CONSTANTS = """

PROGRAM CONSTANTS MODULE:

1/3 of a foot = 1 unit in the program

"""
