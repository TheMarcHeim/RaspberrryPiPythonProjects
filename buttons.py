import RPi.GPIO as GPIO
import time
from threading import Thread

BUTTON = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, GPIO.PUD_UP)

REDLEDS = [21,26,13,6]
GREENLEDS = [20,16,19,5]

stopped = False




def buttonThread():
    oldState = False
    while not stopped:
      button_state = GPIO.input(BUTTON)
      if button_state == GPIO.HIGH:
        oldState = False
        time.sleep(0.01)
      else:
        if oldState == False:
            print("PUSH")
        oldState = True
        time.sleep(0.2)



def ledThread():
    for led in REDLEDS+GREENLEDS:
        GPIO.setup(led, GPIO.OUT)
    while not stopped:
        #sample program
        for led in REDLEDS+GREENLEDS:
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(led, GPIO.LOW)
        


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