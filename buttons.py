import RPi.GPIO as GPIO
import time
from threading import Thread
from threading import Event



#REDLEDS = [21,26,19,6]
#GREENLEDS = [20,16,13,5]
GREENLEDS = [26,13,6,20,12]
REDLEDS = [16,19,5,21,25]

PULLDOWNPINS = [17,18,27,23,24]
oldState = [False,False,False,False,False]

RELAYPINS = [2,4,3,22]
DOORRELAY = 2

lastCode = []
correctCode = [0,1,2,3,4]

newPassword = []

currentInput = -1
lastCurrentInput = 0

blinkStopEvent = None
pushAction = None

open = False

stopped = False

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

def setHigh(pins):
	for pin in pins:
		GPIO.output(pin, GPIO.HIGH)

def setLow(pins):
	for pin in pins:
		GPIO.output(pin, GPIO.LOW)
    
def lightFire(leds):
    time.sleep(0.1)
    for x in range(0,15):
        for led in leds:
            GPIO.output(led, GPIO.HIGH)
        time.sleep(0.05)
        for led in leds:
            GPIO.output(led, GPIO.LOW)
        time.sleep(0.05)

def slowLightFire(leds):
    for x in range(0,2):
        for led in leds:
            GPIO.output(led, GPIO.HIGH)
        time.sleep(2)
        for led in leds:
            GPIO.output(led, GPIO.LOW)
        time.sleep(1)
        
def lightRun(leds):
    for led in leds:
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.1)

def successRelay():
	global open
	GPIO.output(DOORRELAY, GPIO.LOW)
	print("OPEN THE DOOR!")
	open = True
	time.sleep(5)
	GPIO.output(DOORRELAY, GPIO.HIGH)
	open = False
	print("CLOSING AGAIN!")

def relayDemo():
	for relay in RELAYPINS:
		time.sleep(1)
		GPIO.output(relay, GPIO.HIGH)
	blinkTrough(RELAYPINS)
	lightFire(RELAYPINS)
	for relay in RELAYPINS:
		time.sleep(1)
		GPIO.output(relay, GPIO.HIGH)

def buttonThread():
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
	if not open:
		lastCode=lastCode[-4:]+[input]
		if not lastCode[-5:]==correctCode:
			Thread(target=inputActivationThread, args=(REDLEDS[input],)).start()
		print(lastCode)
	if lastCode[-5:]==correctCode and not open:
		actSuccess()
		lastCode = []

def actSuccess():
	Thread(target=successRelay).start()
	Thread(target=ledSucces).start()
	

def inputActivationThread(led):
    for i in range(0,5):
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.1)
	GPIO.output(led, GPIO.LOW)
        time.sleep(0.1)

def passwordDemo():
	global open
	open = True
	time.sleep(1)
	lightFire(GREENLEDS)
	time.sleep(1)
	for inp in correctCode:
		GPIO.output(GREENLEDS[inp], GPIO.HIGH)
        	time.sleep(1)
		GPIO.output(GREENLEDS[inp], GPIO.LOW)
        	time.sleep(0.5)
	open = False
	lightFire(REDLEDS)

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

def ledSucces():
	slowLightFire(REDLEDS)

        
def passwordBlinking(stopEvent):
	setLow(GREENLEDS)
	while not stopEvent.is_set():
		setHigh(GREENLEDS)
		#fastblinking
		for i in range(1,5):
			inp = currentInput#-> has to be thread safe
			if not inp == -1:
				setHigh([GREENLEDS[inp]])
			else:
				setHigh(GREENLEDS)			
			stopEvent.wait(0.1)
			if not inp == -1:
				setLow([GREENLEDS[inp]])			
			stopEvent.wait(0.1)	
			if stopEvent.is_set():
				break
		setLow(GREENLEDS)
		#fastblinking
		for i in range(1,5):
			inp = currentInput
			if not inp == -1:
				setHigh([GREENLEDS[inp]])				
			stopEvent.wait(0.1)
			if not inp == -1:
				setLow([GREENLEDS[inp]])
			else:
				setLow(GREENLEDS)			
			stopEvent.wait(0.1)	
			if stopEvent.is_set():
				break

def passwordInputPush(input):
	global newPassword, currentInput, lastCurrentInput
	print "input: "+str(input)
	newPassword = newPassword + [input]
	currentInput = input
	lastCurrentInput = time.time()
	Thread(target=deactivateCurrentInputAsync).start()
	if len(newPassword)==5:
		#set new password
		setPassword(newPassword)
		endPasswordInput()

def deactivateCurrentInputAsync():
	global currentInput
	time.sleep(1)
	if time.time()-lastCurrentInput >= 1:
		currentInput = -1
	
def startPasswordInput():
	global blinkStopEvent, pushAction, newPassword
	blinkStopEvent = Event()
	newPassword = []
	pushAction = passwordInputPush
	bt = Thread(target=passwordBlinking, args = (blinkStopEvent,))
	currentInput = -1
	bt.start()

def endPasswordInput():
	global pushAction
	blinkStopEvent.set()
	pushAction = normalPush

def setPassword(password):
	global correctCode
	correctCode = password
	print("new password: "+str(correctCode))
	Thread(target=passwordDemo).start()
	

def run():
	global pushAction
	init()
	#start reading thread
	global t1, t2, t3, stopped
	stopped = 0
	pushAction = normalPush
	t1 = Thread(target=buttonThread)
	t1.start()
	print('started threads')
	#while True:
	#	x = raw_input('Command? ')
	#	if x == "set password":
	startPasswordInput()


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