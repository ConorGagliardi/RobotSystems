import cv2
import numpy as np
import concurrent.futures
import time
import threading
import queue
from picamera2 import Picamera2
from controller import Controller
from bus import Bus  
from picarx_improved import Picarx  
class LineFollower:
    def __init__(self, scalar=35, speed=50, picarx=None):
        self.controller = Controller(scalar=scalar, speed=speed, picarx=picarx)

    def follow_line(self, frame, bus):
        height, width, _ = frame.shape
        roi = frame[int(height * 0.9):, int(width * 0.175):int(width * 0.825)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        
        adjusted_width = binary.shape[1] - (binary.shape[1] % 5)
        binary = binary[:, :adjusted_width]
        fifths = np.hsplit(binary, 5)
        counts = [cv2.countNonZero(section) for section in fifths]

        if counts[2] > max(counts):
            turn_prop = 0
        elif counts[1] > max(counts[0], counts[3], counts[4]):
            turn_prop = -0.5
        elif counts[3] > max(counts[0], counts[1], counts[4]):
            turn_prop = 0.5
        elif counts[0] > max(counts[1:]):
            turn_prop = -1
        elif counts[4] > max(counts[:4]):
            turn_prop = 1
        else:
            turn_prop = 0

        bus.write(turn_prop)
        return binary

def sensor_function(cam, sensor_bus, frame_queue, delay):
    while True:
        frame = cam.capture_array()
        sensor_bus.write(frame)
        frame_queue.put(("Camera Feed", frame))  # Send frame to the main thread
        time.sleep(delay)

def interpreter_function(sensor_bus, interpreter_bus, frame_queue, delay, follower):
    while True:
        frame = sensor_bus.read()
        if frame is None:
            continue
        binary = follower.follow_line(frame, interpreter_bus)
        frame_queue.put(("Processed Binary", binary))  # Send processed frame to main thread
        time.sleep(delay)

def control_function(interpreter_bus, controller, delay):
    while True:
        turn_prop = interpreter_bus.read()
        if turn_prop is None:
            continue
        controller.move(turn_prop)
        time.sleep(delay)

def display_frames(frame_queue):
    while True:
        if not frame_queue.empty():
            window_name, frame = frame_queue.get()
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)  # Required for OpenCV windows to update

def stop_robot_on_exit(picarx):
    print("Stopping robot...")
    picarx.stop()
    cv2.destroyAllWindows()
    exit()

if __name__ == "__main__":
    cam = Picamera2()
    cam.configure(cam.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    cam.start()

    sensor_bus = Bus()
    interpreter_bus = Bus()
    frame_queue = queue.Queue()  # Thread-safe queue for OpenCV frame updates
    picarx = Picarx()  # Ensure Picarx instance is created
    follower = LineFollower(scalar=35, speed=50, picarx=picarx)
    controller = Controller(scalar=35, speed=50, picarx=picarx)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.submit(sensor_function, cam, sensor_bus, frame_queue, 0.1)
            executor.submit(interpreter_function, sensor_bus, interpreter_bus, frame_queue, 0.1, follower)
            executor.submit(control_function, interpreter_bus, controller, 0.1)
            executor.submit(display_frames, frame_queue)  # Run OpenCV display in main thread

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Stopping...")
    finally:
        stop_robot_on_exit(picarx)
