#!/usr/bin/python3
import sys
sys.path.append("/home/conor/RobotSystems/rossros")

import rossros as rr
import cv2
import numpy as np
import time
import queue
import threading

from picamera2 import Picamera2
from controller import Controller
from picarx_improved import Picarx




frame_queue = queue.Queue()
cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
cam.start()
picarx = Picarx()
controller = Controller(scalar=35, speed=30, picarx=picarx)

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
        bus.set_message(turn_prop, _name="LineFollower")
        return binary

follower = LineFollower(scalar=35, speed=30, picarx=picarx)
sensor_bus = rr.Bus(None, "Sensor Bus")
interpreter_bus = rr.Bus(0, "Interpreter Bus")
bTerminate = rr.Bus(0, "Termination Bus")

def sensor_producer():
    frame = cam.capture_array()
    frame_queue.put(("Camera Feed", frame))
    return frame

def interpreter_function(frame):
    if frame is None:
        return 0
    binary = follower.follow_line(frame, interpreter_bus)
    frame_queue.put(("Processed Binary", binary))
    return interpreter_bus.get_message("Interpreter Function")

def control_function(turn_prop):
    if turn_prop is None:
        return 0
    controller.move(turn_prop)
    return 0

def display_frames(frame_queue):
    while True:
        try:
            window_name, frame = frame_queue.get(timeout=0.1)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            term_val = bTerminate.get_message("Display")
            if term_val and term_val >= 0:
                break

sensorProducer = rr.Producer(
    sensor_producer,
    sensor_bus,
    delay=0.1,
    termination_buses=bTerminate,
    name="Sensor Producer"
)

interpreterCP = rr.ConsumerProducer(
    interpreter_function,
    input_buses=sensor_bus,
    output_buses=interpreter_bus,
    delay=0.1,
    termination_buses=bTerminate,
    name="Interpreter"
)

controlConsumer = rr.Consumer(
    control_function,
    input_buses=interpreter_bus,
    delay=0.1,
    termination_buses=bTerminate,
    name="Control"
)

terminationTimer = rr.Timer(
    bTerminate,
    duration=60,
    delay=0.01,
    termination_buses=bTerminate,
    name="Termination Timer"
)

if __name__ == "__main__":
    display_thread = threading.Thread(target=display_frames, args=(frame_queue,))
    display_thread.start()
    producer_consumer_list = [sensorProducer, interpreterCP, controlConsumer, terminationTimer]
    try:
        rr.runConcurrently(producer_consumer_list)
    except KeyboardInterrupt:
        bTerminate.set_message(1, _name="KeyboardInterrupt Handler")
    finally:
        display_thread.join()
        cv2.destroyAllWindows()
        controller.move(0)
        picarx.stop()
        cam.stop()
