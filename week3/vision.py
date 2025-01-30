import cv2
import numpy as np
from picamera2 import Picamera2
from controller import Controller

class LineFollower:

    def __init__(self, scalar=35, speed=50):
        self.controller = Controller(scalar=scalar, speed=speed)

    def follow_line(self, frame):
        height, width, _ = frame.shape
        roi = frame[int(height * 0.9):, int(width * 0.175):int(width * 0.825)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

        # Ensure width is divisible by 5
        adjusted_width = binary.shape[1] - (binary.shape[1] % 5)
        binary = binary[:, :adjusted_width]

        fifths = np.hsplit(binary, 5)
        counts = [cv2.countNonZero(section) for section in fifths]

        if counts[2] > max(counts):
            turn_prop = 0  # Center
        elif counts[1] > max(counts[0], counts[3], counts[4]):
            turn_prop = -0.5  # Slight left
        elif counts[3] > max(counts[0], counts[1], counts[4]):
            turn_prop = 0.5  # Slight right
        elif counts[0] > max(counts[1:]):
            turn_prop = -1  # Full left
        elif counts[4] > max(counts[:4]):
            turn_prop = 1  # Full right
        else:
            turn_prop = 0  # Default to straight if no strong signal

        self.controller.move(turn_prop)
        return binary

if __name__ == "__main__":
    cam = Picamera2()
    cam.configure(cam.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    cam.start()

    follower = LineFollower(scalar=35, speed=50)

    try:
        while True:
            frame = cam.capture_array()
            binary = follower.follow_line(frame)

            cv2.imshow("Line Following", binary)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.stop()
        cv2.destroyAllWindows()
