import cv2
import time,  math, numpy as np
from . import HandTrackingModule as htm
import os
from lib.ImgProvider.ImgProvider import  ImgProvider

class HandGesture:
    def __init__(self, playAndPauseCommand, nextSongCommand, previousSongCommand, onModeChange, isRealsenseCamera = False):
        self.playAndPauseCommand = playAndPauseCommand
        self.nextSongCommand = nextSongCommand
        self.previousSongCommand = previousSongCommand
        self.onModeChange = onModeChange
        self.stopFlag = False
        self.isRealsenseCamera = isRealsenseCamera
        self.curCmd = "firstCurCmd"
        self.preCmd = "firstPreCmd"
        self.commandEnable = False
        self.imgProvider = ImgProvider(isRealsenseCamera)
    def setStop(self):
        self.stopFlag = True
    def run(self):
        preNotificationText = ''
        notificationText = "Hãy đưa tay ra trước camera."

        self.imgProvider.runWithThread()
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
        def computeAngle(lmList, pointA,pointB, pointC, horizon = False):
            if (pointC != None) and (not horizon):
                points = np.asarray([lmList[pointA][1:], lmList[pointB][1:], lmList[pointC][1:]])
            else:
                points = np.asarray([lmList[pointA][1:], lmList[pointB][1:], [100000, lmList[pointB][2]]])
            d_ba = points[1] - points[0]
            d_ca = points[2] - points[0]
            cosineAngle = np.dot(d_ba, d_ca)   / (np.linalg.norm(d_ba)* np.linalg.norm(d_ca))             
            angle = np.arccos(cosineAngle)
            return angle
        while True:
            if(self.stopFlag):
                self.stopFlag = False
                break
            try:
                img = self.imgProvider.getImage()
              
                img = detector.findHands(img)
                lmList = detector.findPosition(img, draw=False)
                fingers = []
                # print(lmList)
                if len(lmList)>0:
                    angle5_0_17 = computeAngle(lmList, 0, 5, 17)*100
                    angle9_0_horizon = computeAngle(lmList , 9, 0, None, True)*180/np.pi
                    # print(angle9_0_horizon)
                    if angle5_0_17>55 and angle5_0_17 < 95 and angle9_0_horizon <120 and angle9_0_horizon>60:
                        self.commandEnable = True
                    else:
                        self.commandEnable = False
                

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

                    oldMode = mode
                #  print(fingers)
                    if (fingers == [0,0,0,0,0]) & (active == 0 ):
                        mode='N'
                    elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0 ):
                        mode = 'NextOrPrev'
                        active = 1
                    elif (fingers == [1, 1, 0, 0, 0] ) & (active == 0 ) & (lmList[12][2]>lmList[9][2]):
                        mode = 'Volume'
                        active = 1
                    elif (fingers == [1 ,1 , 1, 1, 1] ) & (active == 0 ):
                        mode = 'playAndPause'
                        active = 1

                     
                    if mode != oldMode and mode != 'N' and mode != 'P':
                        if mode == 'playAndPause':
                            notificationText = "Chế độ bật, tắt youtube audio"
                        elif mode == 'Volume' :
                            notificationText = "Chế độ điều chỉnh âm lượng"
                        elif mode == 'NextOrPrev' :
                            notificationText = "Chế độ tiến, lùi audio"
                    if mode=='N' or mode == 'P':    
                        notificationText = "Chế độ idle"
                    if preNotificationText != notificationText: 
                        self.onModeChange(notificationText)
                    preNotificationText = notificationText
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
                            if self.commandEnable:
                                self.nextSongCommand()

                        if fingers == [0,1,1,0,0]:
                            #print('down')
                        #  time.sleep(0.1)
                            putText(mode = 'P', loc =  (200, 455), color = (0, 0, 255))
                            self.curCmd = "preCmd"
                            if (self.curCmd == self.preCmd):
                                continue
                            if self.commandEnable:
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
                            if self.commandEnable:
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
                                if self.commandEnable:
                                    self.playAndPauseCommand()

                self.preCmd = self.curCmd
                self.curCmd = "noCmd"
                cTime = time.time()
                fps = 1/((cTime + 0.01)-pTime)
                pTime = cTime

                cv2.putText(img,f'FPS:{int(fps)}',(480,50), cv2.FONT_ITALIC,1,(255,0,0),2)
                # cv2.putText(img,f'angle:{int(angle5_0_17)}',(480,100), cv2.FONT_ITALIC,1,(255,0,0),2)
                cv2.imshow('Hand LiveFeed',img)
                # 15fps means period is 67ms, according to Nyquist's criteria, the wait period should be 67/2 =33
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    break

                def putText(mode,loc = (250, 450), color = (0, 255, 255)):
                    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                3, color, 3)
            except:
                # import traceback
                # traceback.print_exc()
                pass
        # print("destroy")
        # cap.release()
        # cv2.destroyAllWindows()
if __name__ == "__main__":
    import HandTrackingModule as htm
    import sys
    sys.path.append(r"/home/kinh/DoAn/SmartMirrorCapstoneProject2024/lib")
    from ImgProvider.ImgProvider import  ImgProvider

    hgt = HandGesture(playAndPauseCommand=None, nextSongCommand=None,previousSongCommand=None, isRealsenseCamera=True)
    hgt.run()
