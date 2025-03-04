#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import Camera
import cv2
from vision import Vision
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

def main():
    vision = Vision()
    vision.start()
    cam = Camera.Camera()
    cam.camera_open()
    while True:
        frame = cam.frame
        if frame is not None:
            annotated = vision.run(frame, color_range)
            cv2.imshow('Frame', annotated)
            key = cv2.waitKey(1)
            if key == 27:
                break
    cam.camera_close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
