import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

import Image
import ImageDraw
import ImageFont

import math as m

DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

disp.begin(contrast=60)

disp.clear()
disp.display()


image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

draw = ImageDraw.Draw(image)

draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

#draw.ellipse((2,2,22,22), outline=0, fill=255)

centerX = LCD.LCDWIDTH/2
centerY = LCD.LCDHEIGHT/2-7
size = -5

print (m.cos(1))

#heart
for i in range (0,30):
	t = 3.1415*i/30.0
	x = size*4*m.sin(t)*m.sin(t)*m.sin(t)
	y = centerY+ size*(3*m.cos(t)-1.3*m.cos(2*t)-0.6*m.cos(3*t)-0.2*m.cos(4*t))
	if (i!=0):
                draw.line((centerX+x,y,centerX+oldx,oldy), fill=0)
                draw.line((centerX-x,y,centerX-oldx,oldy), fill=0)
	oldx = x
	oldy = y
        #draw.rectangle(((int(x),int(y),int(x)+1,int(y)+1), outline=0, fill=0)

font = ImageFont.load_default()
draw.text((1,33), 'Ich liebe dech!', font=font)

disp.image(image)
disp.display()
