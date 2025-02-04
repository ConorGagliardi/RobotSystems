import sys
sys.path.append("..") 
from picarx_improved import Picarx
from sensor import *
from interpreter import *
import time
import os


def constrain(x, min_val, max_val):
    '''
    Constrains value to be within a range.
    '''
    return max(min_val, min(max_val, x))

class Controller:
        
    def __init__(self, scalar=35, speed=50, picarx=None):
        self.scalar = scalar
        self.speed = speed
        self.picarx = picarx  

    def move(self, turn_prop):
        steering_angle = self.scalar * turn_prop
        self.picarx.set_dir_servo_angle(steering_angle)
        self.picarx.forward(self.speed)
        
        
if __name__ == "__main__":
    adc_sensors = ["A0", "A1", "A2"]
    sensor = Sensor(adc_sensors)
    interpreter = Interpreter(sensitivity=500, polarity=False)
    controller = Controller(scalar=35, speed=30)

    while True:
        vals = sensor.read()
        turn = interpreter.think(vals)
        angle = controller.move(turn)
        print(f"Sensor Values: {vals}, Turn: {turn}, Steering Angle: {angle}")
        time.sleep(0.01)