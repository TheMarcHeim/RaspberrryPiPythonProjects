import RPi.GPIO as GPIO
import time
from threading import Thread
from threading import Event
import os
from random import randint
import datetime as dt


#REDLEDS = [21,26,19,6]
#GREENLEDS = [20,16,13,5]
#GREENLEDS = [26,13,6,20,12]
#REDLEDS = [16,19,5,21,25]

GREENLEDS = [5,13,19,20,16]
REDLEDS = [6,21,25,12,26]

PASSWORTSETPIN = 10
DOOROPENPIN = 9
OPENLED = 11

MORNINGHOUR = 7
EVENINGHOUR = 22

NOPASSSOUNDS = 8
PASSSOUNDS = 1
OPENSOUNDS = 5

RESETTIME = 60

OPENLEDLIGHTTIME = 300


PULLDOWNPINS = [23,18,27,24,17]
#oldState = [False,False,False,False,False]

RELAYPINS = [2,4,3,22]
DOORRELAY = 2

lastCode = []
correctCode = [0,1,2,3,4]

newPassword = []

currentInput = -1
lastCurrentInput = 0

lastInputTime = 0

blinkStopEvent = None
pushAction = None

tries = 0

playing = False

open = False

stopped = False

def init():
	GPIO.setmode(GPIO.BCM)
	for relay in RELAYPINS:
		GPIO.setup(relay, GPIO.OUT)
		GPIO.output(relay, GPIO.HIGH)
	for button in PULLDOWNPINS:
        	GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
	GPIO.setup(PASSWORTSETPIN, GPIO.IN, GPIO.PUD_UP)
	GPIO.setup(DOOROPENPIN, GPIO.IN, GPIO.PUD_UP)
	for led in REDLEDS+GREENLEDS+[OPENLED]:
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
    #for x in range(0,2):
        for led in leds:
            GPIO.output(led, GPIO.HIGH)
        time.sleep(5)
        for led in leds:
            GPIO.output(led, GPIO.LOW)
        #time.sleep(1)
        
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
	oldState = [False,False,False,False,False,False,False]
	while not stopped:
		i = 0
		for button in PULLDOWNPINS+[PASSWORTSETPIN]+[DOOROPENPIN]:
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
		setOpenLed()
		setReset()


def normalPush(input):
	#append input to lastCode and test code
	global tries
	tries = tries + 1
	print tries


	global lastCode, lastInputTime
	GPIO.output(OPENLED, GPIO.HIGH)
	lastInputTime = time.time()
	if input == 5:
		startPasswordInput()
		print "passwordinput"
	elif input == 6:
		actOpen()
	else:
		if not open:
			lastCode=lastCode[-4:]+[input]
			#if not lastCode[-5:]==correctCode:
				#Thread(target=inputActivationThread, args=(REDLEDS[input],)).start()
			print(lastCode)
		if lastCode[-5:]==correctCode and not open:
			actSuccess()
			lastCode = []
			tries = 0
		if tries == 5 and not lastCode[-5:]==correctCode:
			playsound("nopass"+str(randint(1,NOPASSSOUNDS)))
			tries = 0

def actSuccess():
	Thread(target=successRelay).start()
	Thread(target=ledSucces).start()
	playsound("pass"+str(randint(1,PASSSOUNDS)))

def actOpen():
	global tries
	tries = 0
	Thread(target=successRelay).start()
	Thread(target=ledSucces).start()
	playsound("open"+str(randint(1,OPENSOUNDS)))
	

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
	global newPassword, currentInput, lastCurrentInput, lastInputTime
	lastInputTime = time.time()
	if input < 5:
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

def playsound(sound):
	Hour = dt.datetime.today().hour
	if Hour >=MORNINGHOUR and Hour<EVENINGHOUR:
		t = Thread(target=playsoundthread, args = (sound,))
		t.start()

def playsoundthread(sound):
	global playing
	while(playing):
		time.sleep(0.1)
	playing = True
	#os.system('mpg321 -g 200 '+sound+'.mp3')
	os.system('mplayer '+sound+'.mp3')
	playing = False

def endPasswordInput():
	global pushAction
	blinkStopEvent.set()
	pushAction = normalPush

def setPassword(password):
	global correctCode
	correctCode = password
	#with open('passw.txt', 'w') as file:
	#	for inp in correctCode:
	#		file.write(str(inp)+"\n")

	print("new password: "+str(correctCode))
	Thread(target=passwordDemo).start()

def loadPassword():
	global correctCode
	correctCode = [0,1,2,3,4]
	#WTF why does this not work?
	#for line in open("passw.txt"):
		#correctCode = correctCode+[int(line)]
	#print "code: "+ str(correctCode)
	
def setOpenLed():
	if time.time()-lastInputTime >= OPENLEDLIGHTTIME:
		GPIO.output(OPENLED, GPIO.LOW)
	else:
		GPIO.output(OPENLED, GPIO.HIGH)

def setReset():
	global lastCode, tries
	if tries > 0 and time.time()-lastInputTime >= RESETTIME:
		print "Reset after timeout..."
		lastCode = []
		tries = 0

def run():
	global pushAction, lastInputTime
	init()
	#start reading thread
	global t1, t2, t3, stopped
	stopped = 0
	pushAction = normalPush
	t1 = Thread(target=buttonThread)
	t1.start()
	print('started threads')
	lastInputTime = time.time()
	#while True:
	#	x = raw_input('Command? ')
	#	if x == "set password":
	#startPasswordInput()
	loadPassword()


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
