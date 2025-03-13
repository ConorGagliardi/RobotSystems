#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
from LABConfig import *
from vision import Vision
from motion import Motion

def main():
    camera = Camera.Camera()
    camera.camera_open()
    
    vision = Vision()
    vision.start()
    
    motion = Motion()
    motion.init_move()
    motion.start()
    
    vision._Vision__target_color = ('red', 'green', 'blue')
    
    try:
        while True:
            frame = camera.frame
            if frame is None:
                continue
            
            frame_processed = vision.run(frame, color_range)
            
            if vision.detect_color != 'None' and vision.start_pick_up:
                motion.set_target(vision.detect_color, vision.world_X, vision.world_Y, vision.rotation_angle)
                vision.start_pick_up = False
            
            cv2.imshow('Motion Test', frame_processed)
            
            key = cv2.waitKey(1)
            if key == 27:
                break
    
    except KeyboardInterrupt:
        print("stop")
    finally:
        motion.stop()
        vision.stop()
        camera.camera_close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
