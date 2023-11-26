import cv2
from ultralytics import YOLO
import subprocess as sp
from djitellopy import Tello
import numpy
import imutils
import time

# IN MM
specs = {
    "FOCAL_LENGTH": 26,  # 25mm <-- on a 35mm equivalent i assume!
    # THIS MAY HAVE TO BE SWITCHED TO 2 as that is the actual sensor thinger
    "SENSOR_WIDTH": 6.8,  # mm
    "MODEL": "yolov8x.pt",
    "MINIMUM_CONFIDENCE": 0.5,
}

specs_drone = {
    "FOCAL_LENGTH": 25,  # 25mm <-- on a 35mm equivalent i assume!
    # THIS MAY HAVE TO BE SWITCHED TO 2 as that is the actual sensor thinger
    "SENSOR_WIDTH": 2.77,  # mm
    "MODEL": "yolov8x.pt",
    "MINIMUM_CONFIDENCE": 0.5,
}

realObjectsArray = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    5: "bus",
    6: "train",
    7: "truck",
    8: "boat",
    9: "traffic light",
    10: "fire hydrant",
    11: "stop sign",
    12: "parking meter",
    13: "bench",
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe",
    24: "backpack",
    25: "umbrella",
    26: "handbag",
    27: "tie",
    28: "suitcase",
    29: "frisbee",
    30: "skis",
    31: "snowboard",
    32: "sports ball",
    33: "kite",
    34: "baseball bat",
    35: "baseball glove",
    36: "skateboard",
    37: "surfboard",
    38: "tennis racket",
    39: "bottle",
    40: "wine glass",
    41: "cup",
    42: "fork",
    43: "knife",
    44: "spoon",
    45: "bowl",
    46: "banana",
    47: "apple",
    48: "sandwich",
    49: "orange",
    50: "broccoli",
    51: "carrot",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    61: "toilet",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    68: "microwave",
    69: "oven",
    70: "toaster",
    71: "sink",
    72: "refrigerator",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
    77: "teddy bear",
    78: "hair drier",
    79: "toothbrush",
}

realWidthArray = {
    "person": 457,
    "bicycle": 600,
    "car": 1800,
    "motorcycle": 700,
    "airplane": 27000,
    "bus": 2500,
    "train": 2820,
    "truck": 2500,
    "boat": 6000,
    "traffic light": 500,
    "fire hydrant": 600,
    "stop sign": 750,
    "parking meter": 300,
    "bench": 1600,
    "bird": 150,
    "cat": 180,
    "dog": 200,
    "horse": 2000,
    "sheep": 600,
    "cow": 2000,
    "elephant": 3000,
    "bear": 2000,
    "zebra": 1300,
    "giraffe": 800,
    "backpack": 450,
    "umbrella": 1000,
    "handbag": 400,
    "tie": 80,
    "suitcase": 500,
    "frisbee": 220,
    "skis": 100,
    "snowboard": 250,
    "sports ball": 220,
    "kite": 1000,
    "baseball bat": 60,
    "baseball glove": 200,
    "skateboard": 200,
    "surfboard": 500,
    "tennis racket": 270,
    "bottle": 70,
    "wine glass": 70,
    "cup": 80,
    "fork": 20,
    "knife": 20,
    "spoon": 20,
    "bowl": 180,
    "banana": 40,
    "apple": 80,
    "sandwich": 120,
    "orange": 80,
    "broccoli": 100,
    "carrot": 30,
    "hot dog": 30,
    "pizza": 200,
    "donut": 100,
    "cake": 200,
    "chair": 450,
    "couch": 2000,
    "potted plant": 200,
    "bed": 1500,
    "dining table": 1000,
    "toilet": 360,
    "tv": 1000,
    "laptop": 380,
    "mouse": 60,
    "remote": 50,
    "keyboard": 450,
    "cell phone": 70,
    "microwave": 540,
    "oven": 600,
    "toaster": 300,
    "sink": 500,
    "refrigerator": 800,
    "book": 150,
    "clock": 200,
    "vase": 200,
    "scissors": 150,
    "teddy bear": 300,
    "hair drier": 100,
    "toothbrush": 20
}

model = YOLO(specs["MODEL"])

# drone = Tello()
# drone.connect()
# drone.streamon()

def getTelloStream (drone):
    udp_addr = drone.get_udp_video_address() + "?overrun_nonfatal=1&fifo_size=50000000"
    command = [
        "ffmpeg",
        "-i",
        udp_addr,
        "-probesize",
        "32",
        "-framerate",
        "60",
        "-fflags",
        "nobuffer",
        "-f",
        "image2pipe",
        "-pix_fmt",
        "bgr24",
        "-vcodec",
        "rawvideo",
        "-",
    ]
    pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
    return pipe

cap = cv2.VideoCapture(0)

def main():
    # pipe = getTelloStream(drone)
    while True:
        # # read 1920*1080*3 bytes (= 1 frame)
        # # raw_image = pipe.stdout.read(960 * 720 * 3)
        # ret, raw_image = cap.read()
        # # transform the byte read into a numpy array
        # image = numpy.frombuffer(raw_image, dtype="uint8")
        # # image = image.reshape(
        # #     (720, 960, 3)
        # # )  # Notice how height is specified first and the width is specified second

        # # frame = imutils.resize(image, width=400)
        # # H, W, _ = frame.shape

        image = cv2.imread("TEST_IMG_9.jpeg")
        # image = cv2.resize(frame, (640, 480), interpolation = cv2.INTER_LINEAR)
        results = model(image, conf=specs["MINIMUM_CONFIDENCE"])

        img=image

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                classInt = int(box.cls)
                label = result.names.get(classInt)

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                width = x2 - x1
                height = y2 - y1

                realLabel = f"{label} | {width}x{height} | avg: {realWidthArray[label]} | distCalc: {round(getDistance(width, realWidthArray[label]), 2)}"

                cv2.putText(
                    img, realLabel, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2
                )

        cv2.imshow("Webcam", img)
        if cv2.waitKey(1) == ord('q'): 
            break



# d = (F * W * I) / P
def getPinholeDistance(focalLength, realWidth, sensorWidth, pixelWidth):
    distance = (focalLength * realWidth * sensorWidth) / (pixelWidth) * 2 # constant to offset
    return distance


def getDistance(pixelWidth, realWidth, specificationsDictionary=specs):
    spdict = specificationsDictionary
    distance = (spdict["FOCAL_LENGTH"] * realWidth * spdict["SENSOR_WIDTH"]) / (
        pixelWidth * 2 # offsetter
    )
    return distance




try:
    main()
except KeyboardInterrupt:
    exit(1)
finally:
    cv2.destroyAllWindows()
