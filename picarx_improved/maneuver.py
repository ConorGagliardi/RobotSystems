import time
import logging
from picarx_improved import Picarx

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")

logging.getLogger().setLevel(logging.DEBUG)

def forward(car, speed=50, duration=1, angle=0):
    car.set_dir_servo_angle(angle)
    car.forward(speed)
    logging.info(f"move forward at {speed} speed, {angle} angle, for {duration} seconds")
    time.sleep(duration)
    car.stop()

def backward(car, speed=50, duration=1, angle=0):
    car.set_dir_servo_angle(angle)
    car.backward(speed)
    logging.info(f"move backward at {speed} speed, {angle} angle, for {duration} seconds")
    time.sleep(duration)
    car.stop()

def forward(car, speed=50, duration=1, angle=0):
    car.set_dir_servo_angle(angle)
    car.forward(speed)
    logging.info(f"move forward at {speed} speed, {angle} angle, for {duration} seconds")
    time.sleep(duration)
    car.stop()

def parallel_park(car, speed=50, duration=2, direction=0):
    left = 30
    right = -30
    if(direction == 1):
        left = left * -1
        right = right * -1

    forward(car, speed, duration=2)
    backward(car, speed, duration=1, angle=left)
    backward(car, speed, duration=1, angle=right)
    car.stop()

def three_pt(car, speed=50, duration=2, direction=0):
    left = 30
    right = -30
    if(direction == 1):
        left = left * -1
        right = right * -1

    forward(car, speed, duration, angle=left)
    backward(car, speed, duration, angle=right)
    forward(car,speed, duration, angle=0)
    car.stop()

def main():
    car = Picarx()

    moves = {
        "w": lambda: forward(car),
        "a": lambda: forward(car, angle=-30),
        "s": lambda: backward(car),
        "d": lambda: forward(car, angle=30),
        "o": lambda: parallel_park(car),
        "p": lambda: parallel_park(car, direction=1),
        "k": lambda: three_pt(car),
        "l": lambda: three_pt(car, direction=1),
        "q": lambda: logging.info("EXIT PROGRAM")
        
        }

    while True:
        cmd = input("enter cmd wasd for basic move, o/p for left/right parallel parking k/l for left/right 3pt turn").lower()
        if cmd in moves:
            if cmd == "q":
                break
            moves[cmd]()
        else:
            logging.warning(f"incorrect cmd")

    car.stop()
    logging.info("STOPPED PROGRAMA")

if __name__ == "__main__":
    main()
