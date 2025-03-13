#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Motion:
    def __init__(self):
        self.AK = ArmIK()
        self.servo1 = 500
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        
        self.track = False
        self._stop = False
        self.get_roi = False
        self.first_move = True
        self.__isRunning = False
        self.unreachable = False
        self.action_finish = True
        self.start_pick_up = False
        
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.rotation_angle = 0
        self.detect_color = 'None'
        
        self.th = threading.Thread(target=self.__move)
        self.th.setDaemon(True)
        self.th.start()
    
    def init_move(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
    
    def start(self):
        self.reset()
        self.__isRunning = True
    
    def stop(self):
        self._stop = True
        self.__isRunning = False
    
    def reset(self):
        self.track = False
        self._stop = False
        self.get_roi = False
        self.first_move = True
        self.unreachable = False
        self.action_finish = True
        self.start_pick_up = False
        self.detect_color = 'None'
    
    def set_target(self, color, world_X, world_Y, rotation_angle):
        self.detect_color = color
        self.world_X = world_X
        self.world_Y = world_Y
        self.rotation_angle = rotation_angle
        self.start_pick_up = True
    
    def set_tracking_target(self, world_x, world_y):
        self.world_x = world_x
        self.world_y = world_y
        self.track = True
    
    def is_running(self):
        return self.__isRunning
    
    def is_action_finished(self):
        return self.action_finish
    
    def __move(self):
        while True:
            if self.__isRunning:
                if self.first_move and self.start_pick_up:
                    self.action_finish = False
                    result = self.AK.setPitchRangeMoving((self.world_X, self.world_Y - 2, 5), -90, -90, 0)
                    if result == False:
                        self.unreachable = True
                    else:
                        self.unreachable = False
                    time.sleep(result[2]/1000)
                    self.start_pick_up = False
                    self.first_move = False
                    self.action_finish = True
                elif not self.first_move and not self.unreachable:
                    if self.track:
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.world_x, self.world_y - 2, 5), -90, -90, 0, 20)
                        time.sleep(0.02)
                        self.track = False
                    if self.start_pick_up:
                        self.action_finish = False
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 280, 500)
                        servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)
                        time.sleep(2)
                        
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1, 500)
                        time.sleep(1)
                        
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)
                        time.sleep(1)
                        
                        if not self.__isRunning:
                            continue
                        result = self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0],
                                                         self.coordinate[self.detect_color][1], 12),
                                                        -90, -90, 0)
                        time.sleep(result[2]/1000)
                        
                        if not self.__isRunning:
                            continue
                        servo2_angle = getAngle(self.coordinate[self.detect_color][0],
                                                self.coordinate[self.detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)
                        
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0],
                                                 self.coordinate[self.detect_color][1],
                                                 self.coordinate[self.detect_color][2] + 3),
                                                -90, -90, 0, 500)
                        time.sleep(0.5)
                        
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 200, 500)
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0],
                                                 self.coordinate[self.detect_color][1], 12),
                                                -90, -90, 0, 800)
                        time.sleep(0.8)
                        
                        self.init_move()
                        time.sleep(1.5)
                        
                        self.detect_color = 'None'
                        self.first_move = True
                        self.get_roi = False
                        self.action_finish = True
                        self.start_pick_up = False
                    else:
                        time.sleep(0.01)
            else:
                if self._stop:
                    self._stop = False
                    Board.setBusServoPulse(1, self.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)

    def set_stacking_position(self, color, x_offset, y_offset, z_height):
        self.coordinate[color] = (x_offset, y_offset, z_height)
    
    def add_stacking_layer(self, color, z_increment):
        x, y, z = self.coordinate[color]
        self.coordinate[color] = (x, y, z + z_increment)
