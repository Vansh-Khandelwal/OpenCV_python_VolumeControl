import cv2
import time
import numpy as np
import HandTracking_Module as Htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# __all__ = [cast, cv2.line]


#
# devices = AudioUtilities.GetSpeakers()
# interface = devices.Activate(
#     IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20.0, None)


######################################
wCam, hCam = 1288, 720
######################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

detector = Htm.handDetector(detectionCon=0.7, trackCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-20.0, None)
volBar = 600
volPerc = 0

minVol = volRange[0]
maxVol = volRange[1]

length = 0

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:

        x1, y1 = lmList[4][1], lmList[4][2]
        # thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]
        # index finger tip

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (x2, y2), (x1, y1), (255, 0, 0), 3)

        length = math.hypot(x2-x1, y1-y2)
        # print(length)
        # calculate length between two points by calculating hypotenuse

        #   finger distance range of 20 - 230
        #   Volume Range of -65 to 0

        vol = np.interp(length, [20, 230], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)

        volBar = np.interp(length, [20, 230], [600, 300])
        volPerc = np.interp(length, [20, 230], [0, 100])

        cv2.rectangle(img, [60, 600], [80, int(volBar)], (255, 0, 255), -1)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (48, 58), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.putText(img, f'Volume: {int(volPerc)}%', (48, 158), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # volume bar
    cv2.rectangle(img, [60, 600], [80, 300], (255, 255, 255), 2)


    cv2.imshow("img", img)
    cv2.waitKey(1)
