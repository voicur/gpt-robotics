import subprocess as sp
import numpy as np
import cv2
import threading
import queue
import imutils
import base64
from config.native import config_import

class Video:
    def __init__(self, config_file, drone):
        self.drone = drone
        self.CONFIG = config_import(config_file)
        
        self.frame_queue = queue.Queue(maxsize=1)  # Queue with a max size of 1
        self.pipe_thread = None
        self.stop_event = threading.Event()

    def initializePipe(self):
        self.drone.streamon()
        udp_addr = self.drone.get_udp_video_address() + "?overrun_nonfatal=1&fifo_size=50000000"
        self.command = [
            "ffmpeg",
            "-i", udp_addr,
            "-probesize", "32",
            "-framerate", "60",
            "-fflags", "nobuffer",
            "-f", "image2pipe",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo",
            "-",
        ]

        self.pipe = sp.Popen(self.command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=10**8)
        self.pipe_thread = threading.Thread(target=self.read_from_pipe)
        self.pipe_thread.daemon = True
        self.pipe_thread.start()

    def read_from_pipe(self):
        while True:
            raw_image = self.pipe.stdout.read(960 * 720 * 3)
            if not raw_image:
                break
            if not self.frame_queue.full():
                # Try to put the new frame in the queue; if the queue is full, it means the previous frame
                # hasn't been processed yet, so we just skip putting the new frame in the queue.
                try:
                    self.frame_queue.put_nowait(raw_image)
                except queue.Full:
                    pass
            else:
                # If the queue is full, remove the old frame and put the new one
                self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(raw_image)

    def cleanup(self):
        self.stop_event.set()
        if self.pipe:
            self.pipe.terminate()
        if self.pipe_thread and self.pipe_thread.is_alive():
            self.pipe_thread.join()
        self.frame_queue.queue.clear()

    def getImage(self):
        if self.pipe_thread is None:
            self.initializePipe()
        try:
            # Wait for the most recent frame with a timeout
            raw_image = self.frame_queue.get(timeout=1.0)  # Timeout of 1 second
            frame = self.processFrame(raw_image)
            H, W, _ = frame.shape
            return (frame, H, W)
        except queue.Empty:
            return None, None, None

    def getImgB64(self, already_has_this_image=None):
        if already_has_this_image is None:
            frame, H, W = self.getImage()
            if frame is None:
                return None
        else:
            frame, H, W = already_has_this_image

        # Convert the image to a format suitable for encoding (e.g., PNG or JPEG)
        success, buffer = cv2.imencode('.png', frame)
        if not success:
            raise ValueError("Could not encode image to PNG")

        # Convert the buffer to a byte string
        byte_data = buffer.tobytes()

        # Encode the byte string to a base64 string
        b64_str = base64.b64encode(byte_data).decode('utf-8')

        return b64_str

    def processFrame(self, raw_image):
        # Read a frame and run general processing
        image = np.frombuffer(raw_image, dtype="uint8")

        # Notice how height is specified first and the width is specified second
        image = image.reshape((720, 960, 3))

        frame = imutils.resize(image, width=400)

        return frame

# Example usage:
# Assuming 'drone' is an object with necessary methods like 'streamon' and 'get_udp_video_address',
# and 'config_file' is the path to your configuration file.

# video = Video(config_file, drone)
# frame, height, width = video.getImage()
# if frame is not None:
#     cv2.imshow("Drone", frame)
#     cv2.waitKey(1)
# video.cleanup()