'''Important library installation
cv2 library: for graphical functions and webcam access
numpy : for kernel calculation i.e. images' pixel manipulation and to adjust their range accordingly
math : to perform math functions such as distance and Pythagoras theorem
mediapipe : to access functions related to hand gesture and screen coordinates 
pycaw and comtypes: to import Audio control abilities
'''
import cv2
import numpy as np
import mediapipe as mp
import time 
import pyautogui
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
'''class of handi_cap which makes it a little more organized to access mediapipe hand coorindates features'''
class handi_cap():
    def __init__(self) :    
        '''mediapipe object creation'''
        self.sol=mp.solutions
        '''object creation for hands within mediapip'''
        self.mphand=self.sol.hands
        '''calls Hands Function'''
        self.hands=self.mphand.Hands()
        '''creates drawing object to display on screen'''
        self.mpdraw=self.sol.drawing_utils
    '''Trace function takes images as input and traces hand on the webcam frame'''
    def trace(self,img,connections=True):
        '''converts the image to RGB format'''
        self.img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        '''processes images and draws the hand on the images using medpipe function'''
        self.result=self.hands.process(self.img)
        '''draws hands only when hands are shown'''
        if self.result.multi_hand_landmarks:
            for i in self.result.multi_hand_landmarks:
                if connections:
                    self.mpdraw.draw_landmarks(img,i,self.mphand.HAND_CONNECTIONS)
                else:
                    self.mpdraw.draw_landmarks(img,i)
        return img
    '''return landmarks that are coordinates on the screen where hands are present'''
    def lmarks(self,img):
        points=[]
        self.img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.result=self.hands.process(self.img)
        if self.result.multi_hand_landmarks:
                for id,lm in enumerate(self.result.multi_hand_landmarks[0].landmark):
                    h,w,c=img.shape
                    xc=int(lm.x*w)
                    yc=int(lm.y*h)
                    points.append([id,xc,yc])
        return points
       
def main():
    '''creates camera object to start video capture'''
    cap=cv2.VideoCapture(0)
    '''object creation for hand'''
    h1=handi_cap()
    '''object creation to control volume functions'''
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    #volume.GetMute()
    #volume.GetMasterVolumeLevel()
    '''function to get volume range'''
    volrange=volume.GetVolumeRange()
    minvol=volrange[0]
    maxvol=volrange[1]
    vol=0
    volvb=400
    volper=0
    #volume.SetMasterVolumeLevel(-20.0, None)
    '''backbone function that displays images'''
    while True:
        '''reads each frame'''
        works,image=cap.read()
        '''flip images'''
        image=cv2.flip(image,1)
        '''return camera error if there is no camera'''
        if works==False:
            print("Camera error")
            break
        '''traces hand on screen'''
        fine=h1.trace(image)
        '''stores landsmarks'''
        lmlist=h1.lmarks(image)
        if len(lmlist)!=0:
            '''stores coordinates for thumb and index finger'''
            x1,y1=lmlist[4][1],lmlist[4][2]
            x2,y2=lmlist[8][1],lmlist[8][2]
            cx,cy=(x1+x2)//2,(y1+y2)//2
            '''creates a specific landmarks to recognize them'''
            cv2.circle(fine,(x1,y1),15,(255,0,255),cv2.FILLED)
            cv2.circle(fine,(x2,y2),15,(255,0,255),cv2.FILLED)
            cv2.circle(fine,(cx,cy),15,(255,0,255),cv2.FILLED)
            '''draws lines between them'''
            cv2.line(fine,(x1,y1),(x2,y2),(255,0,255),3)
            '''finds distance between them'''
            length=math.hypot(x2-x1,y2-y1)
            '''maps volume range within that range'''
            vol=np.interp(length,[50,250],[minvol,maxvol])
            volvb=np.interp(length,[50,250],[400,150])
            volper=np.interp(length,[50,250],[0,100])
            '''changes volume'''
            volume.SetMasterVolumeLevel(vol, None)
            print(vol)
            '''when distance is too small makes one circle'''
            if length<50:
                cv2.circle(fine,(cx,cy),15,(0,255,0),cv2.FILLED)    
        '''draws rectangles to draw volume on screen'''
        cv2.rectangle(fine,(50,150),(85,400),(0,255,0),3)
        cv2.rectangle(fine,(50,int(volvb)),(85,400),(0,255,0),cv2.FILLED)
        '''shows volume in text'''
        cv2.putText(fine,f'{int(volper)}%',(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(0,250,0),3)
        '''shows frame on screen'''
        cv2.imshow("Hand",fine)
        '''difines key to stop the function'''
        key=cv2.waitKey(1)
        if key==27:
            break
    '''stops execution'''
    cap.release()
    cv2.destroyAllWindows()
    
if __name__=="__main__":
    main()
