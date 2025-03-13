def move():
    # coordinates for each color
    coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }
    while True:
        if __isRunning:
            # first time block found and pick up triggered
            if first_move and start_pick_up:
                action_finish = False
                set_rgb(detect_color)
                setBuzzer(0.1)
                # move arm to block location (adjust height)
                result = AK.setPitchRangeMoving((world_X, world_Y - 2, 5), -90, -90, 0)
                if result == False:
                    unreachable = True
                else:
                    unreachable = False
                time.sleep(result[2]/1000)
                start_pick_up = False
                first_move = False
                action_finish = True
            # other blocks found
            elif not first_move and not unreachable:
                set_rgb(detect_color)
                if track:
                    if not __isRunning:
                        continue
                    # move arm to track block
                    AK.setPitchRangeMoving((world_x, world_y - 2, 5), -90, -90, 0, 20)
                    time.sleep(0.02)
                    track = False
                if start_pick_up:
                    action_finish = False
                    if not __isRunning:
                        continue
                    # open end effector
                    Board.setBusServoPulse(1, servo1 - 280, 500)
                    # compute end effector rotation
                    servo2_angle = getAngle(world_X, world_Y, rotation_angle)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    # lower arm to pick block
                    AK.setPitchRangeMoving((world_X, world_Y, 2), -90, -90, 0, 1000)
                    time.sleep(2)
                    
                    if not __isRunning:
                        continue
                    # close end effector
                    Board.setBusServoPulse(1, servo1, 500)
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    # reset servo
                    Board.setBusServoPulse(2, 500, 500)
                    # raise arm with block
                    AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    # move arm to color assorted goal
                    result = AK.setPitchRangeMoving((coordinate[detect_color][0],
                                                     coordinate[detect_color][1], 12),
                                                    -90, -90, 0)
                    time.sleep(result[2]/1000)
                    
                    if not __isRunning:
                        continue
                    # move servo angle for placement
                    servo2_angle = getAngle(coordinate[detect_color][0],
                                            coordinate[detect_color][1], -90)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)
                    
                    if not __isRunning:
                        continue
                    # lower arm to place block
                    AK.setPitchRangeMoving((coordinate[detect_color][0],
                                             coordinate[detect_color][1],
                                             coordinate[detect_color][2] + 3),
                                            -90, -90, 0, 500)
                    time.sleep(0.5)
                    
                    if not __isRunning:
                        continue
                    # move to exact color goal
                    AK.setPitchRangeMoving((coordinate[detect_color]), -90, -90, 0, 1000)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    # open end effector
                    Board.setBusServoPulse(1, servo1 - 200, 500)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    # move arm up
                    AK.setPitchRangeMoving((coordinate[detect_color][0],
                                             coordinate[detect_color][1], 12),
                                            -90, -90, 0, 800)
                    time.sleep(0.8)
                    
                    # return arm to home
                    initMove()
                    time.sleep(1.5)
                    
                    # reset flags
                    detect_color = 'None'
                    first_move = True
                    get_roi = False
                    action_finish = True
                    start_pick_up = False
                    set_rgb(detect_color)
                else:
                    time.sleep(0.01)
        else:
            if _stop:
                _stop = False
                Board.setBusServoPulse(1, servo1 - 70, 300)
                time.sleep(0.5)
                Board.setBusServoPulse(2, 500, 500)
                AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                time.sleep(1.5)
            time.sleep(0.01)
