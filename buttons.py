import RPi.GPIO as GPIO
import time
from threading import Thread



#REDLEDS = [21,26,19,6]
#GREENLEDS = [20,16,13,5]
GREENLEDS = [26,13,6,20,12]
REDLEDS = [16,19,5,21,25]

PULLDOWNPINS = [17,18,27,23,24]
oldState = [False,False,False,False,False]

RELAYPINS = [2,4,3,22]
DOORRELAY = 2

lastCode = []
correctCode = [3,3,3,3,3]

open = False

stopped = False
oldState

def init():
	GPIO.setmode(GPIO.BCM)
	for relay in RELAYPINS:
		GPIO.setup(relay, GPIO.OUT)
		GPIO.output(relay, GPIO.HIGH)
	for button in PULLDOWNPINS:
        	GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
	for led in REDLEDS+GREENLEDS:
        	GPIO.setup(led, GPIO.OUT)
		GPIO.output(led, GPIO.LOW)

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

def successRelay():
	global open
	GPIO.output(DOORRELAY, GPIO.LOW)
	open = True
	time.sleep(2)
	GPIO.output(DOORRELAY, GPIO.HIGH)
	open = False

def relayDemo():
	for relay in RELAYPINS:
		time.sleep(1)
		GPIO.output(relay, GPIO.HIGH)
	blinkTrough(RELAYPINS)
	lightFire(RELAYPINS)
	for relay in RELAYPINS:
		time.sleep(1)
		GPIO.output(relay, GPIO.HIGH)
	

def buttonThread(pushAction):
	global oldState, lastCode
	oldState = [False,False,False,False,False]
	alreadyPushed = [False,False,False,False,False]
	while not stopped:
		i = 0
		for button in PULLDOWNPINS:
			alreadyPushed[i] = alreadyPushed[i] or oldState[i]
			button_state = GPIO.input(button)
			if button_state == GPIO.HIGH:
				oldState[i] = False
				time.sleep(0.01)
			else:
				if oldState[i] == False:
					pushAction(i)
					#break
				oldState[i] = True
				time.sleep(0.2)
			i=i+1


def normalPush(input):
	#append input to lastCode and test code
	global lastCode
	Thread(target=inputActivationThread, args=(REDLEDS[input],)).start()
	lastCode=lastCode[-4:]+[input]
	print(lastCode)
	if lastCode[-5:]==correctCode and not open:
		actSuccess()
		lastCode = []

def passwordInputMode(input):
	print "password" #todo

def actSuccess():
	Thread(target=successRelay).start()#switch to successRelay() in deployment
	Thread(target=ledDemo).start()
	

def inputActivationThread(led):
    for i in range(0,5):
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.1)
	GPIO.output(led, GPIO.LOW)
        time.sleep(0.1)

def ledDemo():
	time.sleep(0.1)
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
	init()
	#start reading thread
	global t1, t2, t3, stopped
	stopped = 0
	t1 = Thread(target=buttonThread, args = (normalPush,))
	t1.start()
	print('started threads')
	#while True:
		



def stop():
	global stopped
	stopped = 1
	t1.join()
	#t2.join()
	#t3.join()
	print('stopped threads')
	GPIO.cleanup()



try:
    run()
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    stop()