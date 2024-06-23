import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self):
       

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False,
                                        max_num_hands=1,
                                        min_detection_confidence=0.95,
                                        min_tracking_confidence=0.90)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks and self.results.multi_handedness[0].classification[0].score>0.9:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
            # print("find pos", self.results.multi_handedness[0].classification[0].score)

                                               
        return img

    def findPosition(self, img, handNo=0, draw=True, color =  (255, 0, 255), z_axis=False):

        lmList = []
        if self.results.multi_hand_landmarks and  self.results.multi_handedness[0].classification[0].score>0.9:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
             #   print(id, lm)
                h, w, c = img.shape
                if z_axis == False:
                   cx, cy = int(lm.x * w), int(lm.y * h)
                    # print(id, cx, cy)
                   lmList.append([id, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z,3)
                    # print(id, cx, cy, cz)
                    lmList.append([id, cx, cy, cz])

                if draw:
                    cv2.circle(img, (cx, cy),5,color, cv2.FILLED)

        return lmList
