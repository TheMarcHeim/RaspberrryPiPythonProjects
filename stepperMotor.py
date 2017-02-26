import RPi.GPIO as GPIO
from threading import Thread
import math as m
import time
import urllib.request
import re

GPIO.setmode(GPIO.BOARD)
coil1 = 11
coil2 = 13
coil3 = 16
coil4 = 18

GPIO.setup(coil1, GPIO.OUT)
GPIO.setup(coil2, GPIO.OUT)
GPIO.setup(coil3, GPIO.OUT)
GPIO.setup(coil4, GPIO.OUT)

UDP_IP = "127.0.0.1"
UDP_PORT = 5006

currentPosition = 0
currentStep = 0
wantedPosition = 1
positionOffset = 0
wantedSpeed = 0
computedSpeed = 0
gain = 1
shouldRelax = 1
istopped = 0
cstopped = 0
intervall = 2
t1 = None
t2 = None

def setNextStep(step):
    #go to one of the 8 steps
    cstep = step%8
    if cstep == 0:
        setStep(1, 0, 0, 0)
    elif cstep == 1:
        setStep(1, 1, 0, 0)
    elif cstep == 2:
        setStep(0, 1, 0, 0)
    elif cstep == 3:
        setStep(0, 1, 1, 0)
    elif cstep == 4:
        setStep(0, 0, 1, 0)
    elif cstep == 5:
        setStep(0, 0, 1, 1)
    elif cstep == 6:
        setStep(0, 0, 0, 1)
    elif cstep == 7:
        setStep(1, 0, 0, 1)
    else:
        relax()

def proceed():
    global currentStep
    global currentPosition
    currentStep = currentStep + 1
    currentPosition = currentStep/4076+positionOffset
    setNextStep(currentStep)

def retreat():
    global currentStep
    global currentPosition
    currentStep = currentStep - 1
    currentPosition = currentStep/4076+positionOffset
    setNextStep(currentStep)

def correct(value):
    global positionOffset
    positionOffset = positionOffset + value
    proceed()

def receiveDataThread():
    #should be in a separate thread
    global wantedPosition
    while not istopped:
        page = urllib.request.urlopen('http://masajudo.5gbfree.com/info.txt')
        readstring = str(page.read())
        oldWantedPosition = wantedPosition
        wantedPosition = float(re.findall(r"[-+]?\d*\.\d+|\d+", readstring)[0])
        if(wantedPosition!=oldWantedPosition):
            print("Update: "+str(wantedPosition))
        time.sleep(intervall)

def controlMotorThread():
    offset= wantedPosition-currentPosition
    while not cstopped:
        if abs(offset)>0.0005:
            if offset > 0:
                proceed()
            else:
                retreat()
            time.sleep(0.0008)
        else:
            relax()
            time.sleep(0.5)
        offset= wantedPosition-currentPosition

def run():
    #start reading thread
    global t1, t2, stopped
    istopped = 0
    cstopped = 0
    t1 = Thread(target=receiveDataThread)
    t2 = Thread(target=controlMotorThread)
    t1.start()
    t2.start()
    print('started threads')

def stop():
    global t1, t2, cstopped, istopped, wantedPosition
    istopped = 1
    t1.join()
    wantedPosition = 0
    print('go to start Position')
    while abs(wantedPosition-currentPosition)>0.0005:
        time.sleep(1)
    cstopped = 1
    t2.join()
    print('stopped threads')
        
def relax():
    setStep(0, 0, 0, 0)


def setStep(w1, w2, w3, w4):
  GPIO.output(coil1, w1)
  GPIO.output(coil2, w2)
  GPIO.output(coil3, w3)
  GPIO.output(coil4, w4)

