#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import numpy as np
import math
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

range_rgb = {
    'red':   (0, 0, 255),
    'blue':  (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours: 
        contour_area_temp = math.fabs(cv2.contourArea(c))
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300: 
                area_max_contour = c

    return area_max_contour, contour_area_max

class Vision:
    def __init__(self, size=(640,480), square_length=1):
        self.size = size
        self.square_length = square_length
        self.__isRunning = False
        self.__target_color = ('red', 'green', 'blue')
        self.get_roi = False
        self.start_pick_up = False
        self.center_list = []
        self.count = 0
        self.last_x, self.last_y = 0, 0
        self.world_X, self.world_Y = 0, 0
        self.start_count_t1 = True
        self.t1 = 0
        self.detect_color = 'None'
        self.rotation_angle = 0

    def start(self):
        self.__isRunning = True
        self.reset()

    def stop(self):
        self.__isRunning = False

    def reset(self):
        self.get_roi = False
        self.start_pick_up = False
        self.center_list = []
        self.count = 0
        self.start_count_t1 = True
        self.detect_color = 'None'
        


    def preprocess(self, img):
        # copy frame and draw cross lines
        img_copy = img.copy()
        h, w = img.shape[:2]
        cv2.line(img, (0, int(h/2)), (w, int(h/2)), (0,0,200), 1)
        cv2.line(img, (int(w/2), 0), (int(w/2), h), (0,0,200), 1)
        # resize and blur image
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11,11), 11)
        # if ROI is set use that area
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.size)
        # convert to LAB
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        return frame_lab

    def detect_block(self, frame_lab, color_range):
        max_area = 0
        best_contour = None
        best_color = None
        # loop through target colors
        for col in color_range:
            if col in self.__target_color:
                mask = cv2.inRange(frame_lab, color_range[col][0], color_range[col][1])
                opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((6,6), np.uint8))
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6), np.uint8))
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
                contour, area = getAreaMaxContour(contours)
                if contour is not None and area > max_area:
                    max_area = area
                    best_contour = contour
                    best_color = col
        return best_contour, max_area, best_color

    def process_detection(self, img, best_contour, color_range):
        if best_contour is None:
            return img
        # get rotated rectangle and ROI
        rect = cv2.minAreaRect(best_contour)
        box = np.int0(cv2.boxPoints(rect))
        self.roi = getROI(box)
        self.get_roi = True
        # get center of block in image then in world coordinates
        img_centerx, img_centery = getCenter(rect, self.roi, self.size, self.square_length)
        world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size)
        # draw the contour and center info
        cv2.drawContours(img, [box], -1, range_rgb[color_range], 2)
        cv2.putText(img, f'({world_x},{world_y})', (min(box[0,0], box[2,0]), box[2,1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[color_range], 1)
        # update stability info
        distance = math.sqrt((world_x-self.last_x)**2+(world_y-self.last_y)**2)
        self.last_x, self.last_y = world_x, world_y
        if distance < 0.5:
            self.center_list.extend((world_x, world_y))
            self.count += 1
            if self.start_count_t1:
                self.start_count_t1 = False
                self.t1 = time.time()
            if time.time()-self.t1 > 1:
                self.rotation_angle = rect[2]
                self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(self.count,2), axis=0)
                self.center_list = []
                self.count = 0
                self.start_pick_up = True
        else:
            self.t1 = time.time()
            self.start_count_t1 = True
            self.center_list = []
            self.count = 0
        self.detect_color = color_range
        return img

    def run(self, img, color_range):
        if not self.__isRunning:
            return img
        frame_lab = self.preprocess(img)
        best_contour, area, best_color = self.detect_block(frame_lab, color_range)
        if area > 2500:
            img = self.process_detection(img, best_contour, best_color)
        cv2.putText(img, "Color: "+self.detect_color, (10, img.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, range_rgb.get(self.detect_color, (0,0,0)), 2)
        return img
