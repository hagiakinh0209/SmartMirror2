import cv2
import time,  math, numpy as np
from . import HandTrackingModule as htm
import os
class HandGesture:
    def __init__(self, playAndPauseCommand, nextSongCommand, previousSongCommand, isRealsenseCamera = False):
        self.playAndPauseCommand = playAndPauseCommand
        self.nextSongCommand = nextSongCommand
        self.previousSongCommand = previousSongCommand
        self.stopFlag = False
        self.isRealsenseCamera = isRealsenseCamera
        self.curCmd = "firstCurCmd"
        self.preCmd = "firstPreCmd"
    def setStop(self):
        self.stopFlag = True
    def run(self):
        if self.isRealsenseCamera :
            import pyrealsense2 as rs
            # Create a pipeline
            pipeline = rs.pipeline()

            # Create a config and configure the pipeline to stream
            #  different resolutions of color and depth streams
            config = rs.config()

            # Get device product line for setting a supporting resolution
            pipeline_wrapper = rs.pipeline_wrapper(pipeline)
            pipeline_profile = config.resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            found_rgb = False
            for s in device.sensors:
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    found_rgb = True
                    break
            if not found_rgb:
                print("The demo requires Depth camera with Color sensor")
                exit(0)

            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

            # Start streaming
            profile = pipeline.start(config)

            # Getting the depth sensor's depth scale (see rs-align example for explanation)
            depth_sensor = profile.get_device().first_depth_sensor()
            depth_scale = depth_sensor.get_depth_scale()
            print("Depth Scale is: " , depth_scale)

            # We will be removing the background of objects more than
            #  clipping_distance_in_meters meters away
            clipping_distance_in_meters = 1 #1 meter
            clipping_distance = clipping_distance_in_meters / depth_scale

            # Create an align object
            # rs.align allows us to perform alignment of depth frames to others frames
            # The "align_to" is the stream type to which we plan to align depth frames.
            align_to = rs.stream.color
            align = rs.align(align_to)


        
        else:
            wCam, hCam = 640, 480
            cap = cv2.VideoCapture(0)
            cap.set(3,wCam)
            cap.set(4,hCam)
        pTime = 0

        detector = htm.handDetector()


        minVol = 0
        maxVol = 100
        hmin = 50
        hmax = 200
        volBar = 400
        volPer = 0
        vol = 0
        color = (0,215,255)

        tipIds = [4, 8, 12, 16, 20]
        mode = ''
        active = 0

        while True:
            if(self.stopFlag):
                self.stopFlag = False
                break
            try:
                if self.isRealsenseCamera:
                    # Get frameset of color and depth
                    frames = pipeline.wait_for_frames()
                    # frames.get_depth_frame() is a 640x360 depth image

                    # Align the depth frame to color frame
                    aligned_frames = align.process(frames)

                    # Get aligned frames
                    aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
                    color_frame = aligned_frames.get_color_frame()

                    # Validate that both frames are valid
                    if not aligned_depth_frame or not color_frame:
                        continue

                    depth_image = np.asanyarray(aligned_depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())

                    # Remove background - Set pixels further than clipping_distance to grey
                    grey_color = 153
                    depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
                    # img is background removed image
                    img = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

            
                else:
                    success, img = cap.read()
                img = detector.findHands(img)
                lmList = detector.findPosition(img, draw=False)
                fingers = []

                if len(lmList) != 0:

                    #Thumb
                    if lmList[tipIds[0]][1] > lmList[tipIds[0 -1]][1]:
                        if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    elif lmList[tipIds[0]][1] < lmList[tipIds[0 -1]][1]:
                        if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                    for id in range(1,5):
                        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                            fingers.append(1)
                        else:
                            fingers.append(0)


                #  print(fingers)
                    if (fingers == [0,0,0,0,0]) & (active == 0 ):
                        mode='N'
                    elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0 ):
                        mode = 'NextOrPrev'
                        active = 1
                    elif (fingers == [1, 1, 0, 0, 0] ) & (active == 0 ):
                        mode = 'Volume'
                        active = 1
                    elif (fingers == [1 ,1 , 1, 1, 1] ) & (active == 0 ):
                        mode = 'playAndPause'
                        active = 1

            ############# NextOrPrev 👇👇👇👇##############
                if mode == 'NextOrPrev':
                    active = 1
                #   print(mode)
                    putText(mode)
                    cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
                    if len(lmList) != 0:
                        if fingers == [0,1,0,0,0]:
                        #print('up')
                        #time.sleep(0.1)
                            putText(mode = 'N', loc=(200, 455), color = (0, 255, 0))
                            self.curCmd = "nextCmd"
                            if (self.curCmd == self.preCmd):
                                continue
                            self.nextSongCommand()

                        if fingers == [0,1,1,0,0]:
                            #print('down')
                        #  time.sleep(0.1)
                            putText(mode = 'P', loc =  (200, 455), color = (0, 0, 255))
                            self.curCmd = "preCmd"
                            if (self.curCmd == self.preCmd):
                                continue
                            self.previousSongCommand()
                        elif fingers == [0, 0, 0, 0, 0]:
                            active = 0
                            mode = 'N'
            ################# Volume 👇👇👇####################
                if mode == 'Volume':
                    active = 1
                #print(mode)
                    putText(mode)
                    if len(lmList) != 0:
                        if fingers[-1] == 1:
                            active = 0
                            mode = 'N'
                        

                        else:

                            x1, y1 = lmList[4][1], lmList[4][2]
                            x2, y2 = lmList[8][1], lmList[8][2]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                            cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)
                            cv2.line(img, (x1, y1), (x2, y2), color, 3)
                            cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)

                            length = math.hypot(x2 - x1, y2 - y1)
                            # print(length)

                            # hand Range 50-300
                            # Volume Range 0-100
                            vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
                            volBar = np.interp(vol, [minVol, maxVol], [400, 150])
                            volPer = np.interp(vol, [minVol, maxVol], [0, 100])
                            vol = vol if vol >=30 else 30
                            os.system("amixer -D pulse sset Master " + str(int(vol)) + "%")

                            if length < 50:
                                cv2.circle(img, (cx, cy), 11, (0, 0, 255), cv2.FILLED)

                            cv2.rectangle(img, (30, 150), (55, 400), (209, 206, 0), 3)
                            cv2.rectangle(img, (30, int(volBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                            cv2.putText(img, f'{int(volPer)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 3)


            #######################################################################
                if mode == 'playAndPause':
                    active = 1
                    #print(mode)
                    putText(mode)

                    if fingers[1:] == [0,0,0,0]: #thumb excluded
                        active = 0
                        mode = 'N'
                        print(mode)
                    else:
                        if len(lmList) != 0:
                            if fingers[0] == 0:
                                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                                self.curCmd = "playAndPauseCmd"
                                if (self.curCmd == self.preCmd):
                                    continue
                                self.playAndPauseCommand()

                self.preCmd = self.curCmd
                self.curCmd = "noCmd"
                cTime = time.time()
                fps = 1/((cTime + 0.01)-pTime)
                pTime = cTime

                cv2.putText(img,f'FPS:{int(fps)}',(480,50), cv2.FONT_ITALIC,1,(255,0,0),2)
                cv2.imshow('Hand LiveFeed',img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                def putText(mode,loc = (250, 450), color = (0, 255, 255)):
                    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                3, color, 3)
            except:
                pass
        print("destroy")
        cap.release()
        cv2.destroyAllWindows()
        
