try:
    from robot_hat import Pin, ADC, PWM, Servo, fileDB
    from robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = True
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    from sim_robot_hat import Pin, ADC, PWM, Servo, fileDB
    from sim_robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = False
import time
import os

class Sensor:
    
    def __init__(self, adc_structs):
                
        self.sensors = [ADC(adc_structs[i]) for i in range(3)]
        
    def read(self):
        return [sensor.read() for sensor in self.sensors]
    
if __name__ == "__main__":

    adc_sensors = ["A0", "A1", "A2"]  

    sensor = Sensor(adc_sensors)
    while True:
        vals = sensor.read()
        print(f"ADC Values: {vals}")
        time.sleep(0.01)