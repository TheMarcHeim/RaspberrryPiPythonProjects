import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from threading import Thread

import RPi.GPIO as gpio

import Image
import ImageDraw
import ImageFont

import math as m

DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0


stopping = False
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

disp.begin(contrast=60)

disp.clear()
disp.display()

distance = 0


def measureThread():
        global distance
        TRIG = 3
        ECHO = 4
        gpio.setmode(gpio.BCM)
        gpio.setup(TRIG, gpio.OUT)
        gpio.setup(ECHO, gpio.IN)
        gpio.output(TRIG, False)
        while (!stopping):
                time.sleep(0.5)
                gpio.output(TRIG, True)
                time.sleep(0.5)
                gpio.output(TRIG, False)
                while gpio.input(echo) == 0:
                        start = time.time()
                while gpio.input(echo) == 1:
                        stop = time.time()
                elapsed = stop - start
                distance = round(elapsed*17000,2)


def drawThread():
        image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
        draw = ImageDraw.Draw(image)
        centerX = LCD.LCDWIDTH/2
        centerY = LCD.LCDHEIGHT/2-7
        size = -5
        while(!stopping):
                draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

                #draw.ellipse((2,2,22,22), outline=0, fill=255)




                #heart
                #for i in range (0,30):
                #        t = 3.1415*i/30.0
                #        x = size*4*m.sin(t)*m.sin(t)*m.sin(t)
                #        y = centerY+ size*(3*m.cos(t)-1.3*m.cos(2*t)-0.6*m.cos(3*t)-0.2*m.cos(4*t))
                #        if (i!=0):
                 #               draw.line((centerX+x,y,centerX+oldx,oldy), fill=0)
                #                draw.line((centerX-x,y,centerX-oldx,oldy), fill=0)
                 #       oldx = x
                 #       oldy = y
                        #draw.rectangle(((int(x),int(y),int(x)+1,int(y)+1), outline=0, fill=0)

                font = ImageFont.load_default()
                draw.text((1,33), distance, font=font)

                disp.image(image)
                disp.display()

def run():
    global t1, t2, stopped
    stopped = False
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
