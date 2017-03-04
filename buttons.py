import RPi.GPIO as GPIO
import time
from threading import Thread

BUTTON = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, GPIO.PUD_UP)

#REDLEDS = [21,26,19,6]
#GREENLEDS = [20,16,13,5]
GREENLEDS = [26,13,6,20,12]
REDLEDS = [16,19,5,21,25]

PULLDOWNPINS = [17,18,27,23,24]
oldState = [False,False,False,False,False]

lastCode = []
correctCode = [0,1,2,3,4]

success = False
stopped = False
oldState

def blinkTrough(leds):
    for led in leds:
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led, GPIO.LOW)
    
def lightFire(leds):
    time.sleep(0.1)
    for x in range(0,15):
        for led in leds:
            GPIO.output(led, GPIO.HIGH)
        time.sleep(0.05)
        for led in leds:
            GPIO.output(led, GPIO.LOW)
        time.sleep(0.05)
        
def lightRun(leds):
    for led in leds:
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.1)

def testCode():
    global success
    if lastCode[-5:]==correctCode:
	success = True

def buttonThread():
    global oldState, success, lastCode
    for button in PULLDOWNPINS:
        GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
        
    oldState = [False,False,False,False,False]
    alreadyPushed = [False,False,False,False,False]
    while not stopped:
      i = 0
      all = True
      for button in PULLDOWNPINS:
        alreadyPushed[i] = alreadyPushed[i] or oldState[i]
	all = all and alreadyPushed[i]
	button_state = GPIO.input(button)
        if button_state == GPIO.HIGH:
          oldState[i] = False
          time.sleep(0.01)
        else:
          if oldState[i] == False:
	      #start blinkerthread
              bt = Thread(target=inputActivationThread, args=(REDLEDS[i],))
              bt.start()
              print("PUSH:"+str(i))
              lastCode=lastCode[-4:]+[i]
              print(lastCode)
          oldState[i] = True
          time.sleep(0.2)
        i=i+1
      testCode()

def inputActivationThread(led):
    for i in range(0,5):
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.1)
	GPIO.output(led, GPIO.LOW)
        time.sleep(0.1)

def ledThread():
    for led in REDLEDS+GREENLEDS:
        GPIO.setup(led, GPIO.OUT)
	GPIO.output(led, GPIO.LOW)
    while not success and not stopped:
	time.sleep(0.1)
    while not stopped:
        #sample program
        #print("red")
        blinkTrough(REDLEDS)
        lightRun(REDLEDS)
        lightFire(REDLEDS)
        #print("green")
        blinkTrough(GREENLEDS)
        lightRun(GREENLEDS)
        lightFire(GREENLEDS)
        


def run():
    #start reading thread
    global t1, t2, stopped
    stopped = 0
    t1 = Thread(target=buttonThread)
    t2 = Thread(target=ledThread)
    t1.start()
    t2.start()
    print('started threads')


def stop():
    global stopped
    stopped = 1
    t1.join()
    t2.join()
    print('stopped threads')
    GPIO.cleanup()



try:
    run()
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    stop()