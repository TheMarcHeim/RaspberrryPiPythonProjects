import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

import Image
import ImageDraw
import ImageFont

import Math as m

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

draw.ellipse((2,2,22,22), outline=0, fill=255)

centerX = LCD.LCDWIDTH
centerY = LCD.LCDHEIGTH
size = 10

#heart
for x in range (0,100):
	t = x/100.
	x = centerX+ size*4*m.sin(t)*m.sin(t)*m.sin(t)
	y = centerY+ size(3*m.cos(t)-1.3*m.cos(2*t)-0.6*m.cos(3*t)-0.2*cos(4*t)
	draw.point((x,y), fill=0)

disp.image(image)
disp.display()
