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
    pipeline_msgs = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Given an image, identify and describe all notable objects, including their relative positions to each other and any other interesting details that can be discerned.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": gpturl,
                    },
                },
            ],
        },
    ]

    if is_url:
        gpturl = image
    else:
        gpturl = f"data:image/jpeg;base64,{image}"

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=pipeline_msgs,
        max_tokens=3000,
    )

    pipeline_msgs.append({
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": response.choices[0].message.content,
            },
        ],
    })

    this_prompt = "Using the image and description above, draw bounding boxes over the objects in the image and label them with their corresponding dimensions."
    pipeline_msgs.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": this_prompt,
            },
        ],
    })

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=pipeline_msgs,
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