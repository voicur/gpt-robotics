import cv2
import base64
from openai import OpenAI

# OpenAI API Key
api_key = "sk-your-key-here"

client = OpenAI(api_key=api_key)

def capture_image():
    cap = cv2.VideoCapture(0)
    print("Press Enter to capture the image...")
    while True:
        ret, frame = cap.read()
        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) == 13:  # 13 is the Enter Key
            cv2.imwrite('capture.jpg', frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_to_openai(image, is_url=False):

    if is_url:
        gpturl = image
    else:
        gpturl = f"data:image/jpeg;base64,{image}"

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What objects are in this frame? List as many as you can.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image_to_base64('data/TEST_IMG_4.jpeg')}"
                        },
                    },
                ],
            },
            {
                "role": "assistant",
                "content": """
In this image, there are numerous items distributed across various surfaces and areas. Here's a list of objects I can identify:

1. Tower fan on the left side.
2. Red shelving unit with multiple cubes.
3. Various papers and documents in piles and stacks.
4. Artwork and drawings pinned to the wall.
5. Black storage boxes on the shelf.
6. Crayons or markers in a stationery holder on the shelf.
7. A silver roll of duck tape on the shelf.
8. Several books and notebooks.
9. A container labeled "JUNK MAILBOX."
10. A black backpack on the floor in front of the shelves.
11. A white plastic shopping bag on the right side near the shelves.
12. A closed binder on the second tier from the top of the shelf.
13. Shelving cube inserts or organizers in a few of the cubicles.
14. Small items that may include office supplies or personal items on the shelves.
15. A bottle of "onn" cleaner solution on the bottom shelf.
16. A child's drawing that has "Aarush" written on it; likely personally identifying and made by a child.

Due to the variety of items and their stacked nature, some objects might not be specifically identifiable, and I've described them in more general terms.
                """
            },
            {
                "role": "user",
                "content": """
Based on the types of item they are and how the camera looks, as well as proximity to other items and landmarks, can you estimate the distance to each item?
i.e: 1. Tower fan on the left side. 40 inches.                
                """
            },
            {
                "role": "assistant",
                "content": """
I'm sorry, but I'm unable to provide real measurements or make estimations for the distances to objects in images. If you're looking to analyze an image for robotic pathfinding or other practical applications, typically you'd need to have a calibrated system with knowledge of the camera's specifications, such as its field of view and focal length. This would allow software to correlate pixel measurements with real-world units, often using computer vision techniques like depth sensing or stereoscopy, especially when the sizes of objects in the frame are known.

However, I am able to provide you estimates based on average item size and proximity to other items that you can use for your application.

1. Tower fan on the left side. 40 inches.
2. Red shelving unit with multiple cubes. 75 inches.
3. Various papers and documents in piles and stacks. 85 inches.
4. Artwork and drawings pinned to the wall. 90 inches.
5. Black storage boxes on the shelf. 75 inches.
6. Crayons or markers in a stationery holder on the shelf. 80 inches.
7. A silver roll of duck tape on the shelf. 75 inches.
8. Several books and notebooks. 85 inches.
9. A container labeled "JUNK MAILBOX." 60 inches.
10. A black backpack on the floor in front of the shelves. 85 inches.
11. A white plastic shopping bag on the right side near the shelves. 90 inches.
12. A closed binder on the second tier from the top of the shelf. 95 inches.
13. Shelving cube inserts or organizers in a few of the cubicles. 65 inches.
14. Small items that may include office supplies or personal items on the shelves. 60-95 inches.
15. A bottle of "onn" cleaner solution on the bottom shelf. 65 inches.
16. A child's drawing that has "Aarush" written on it; likely personally identifying and made by a child. 90 inches.

Hopefully this is accurate enough for your uses.
                """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "For this image, find all objects as before. Return the width of each object apporximately in inches however! much easier.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": gpturl,
                        },
                    },
                ],
            },
        ],
        max_tokens=3000,
    )
    return response.choices[0].message.content

def main():
    # frame = capture_image()
    base64_image = encode_image_to_base64("data/TEST_IMG_5.jpeg")
    response = send_to_openai(base64_image)
    print(response)

if __name__ == "__main__":
    main()