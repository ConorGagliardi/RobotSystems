try:
    from robot_hat import Pin, ADC, PWM, Servo, fileDB
    from robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = True
    from sensor import Sensor
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    from sim_robot_hat import Pin, ADC, PWM, Servo, fileDB
    from sim_robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = False
import time
import os

class Interpreter:
    
    def __init__(self, sensitivity = 200, polarity = True):
                
        self.sensitivity = sensitivity
        self.polarity = polarity
        
    def think(self, vals):
        left_diff = vals[0] - vals[1]
        right_side = vals[2] - vals[1]

        if self.polarity:
            position = (right_side - left_diff) / (vals[0] + vals[1] + vals[2])
        else:
            position = (left_diff - right_side) / (vals[0] + vals[1] + vals[2])

        return position * 2
    
if __name__ == "__main__":
    adc_sensors = ["A0", "A1", "A2"]
    sensor = Sensor(adc_sensors)
    interpreter = Interpreter()

    while True:
        vals = sensor.read()
        turn = interpreter.think(vals)
        print(f"vals: {vals}, turn: {turn}")
        time.sleep(0.01)