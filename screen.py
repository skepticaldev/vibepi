
from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import sys, getopt

maxAmp = 0
maxFreq = 0
spd = 0

i2c = busio.I2C(SCL, SDA)
width = 128
height = 64
font = ImageFont.truetype('retro-gaming.ttf',11)

padding = 0
top = padding
bottom = height - padding
x=2

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"a:f:s:")
    except getopt.GetoptError:
        print('ledscreen.py -a <amplitude> -f <frequency> -s <speed>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-a':
            global maxAmp
            maxAmp = arg
        elif opt == '-f':
            global maxFreq 
            maxFreq = arg
        elif opt == '-s':
            global spd 
            spd = arg
        
    display = adafruit_ssd1306.SSD1306_I2C(width,height,i2c)
    display.fill(0)
    display.show()
    image = Image.new("1",(width, height))
    draw = ImageDraw.Draw(image)

    draw.text((x, top+0), "Max", font=font, fill=255)
    draw.text((x+50, top+0), str(maxAmp)+" g", font=font, fill=255)
    draw.text((x+50, top+15), str(maxFreq)+" Hz", font=font, fill=255)
    draw.text((x, top+30), "Vel.", font=font, fill=255)
    draw.text((x+50, top+30), str(spd)+" rpm", font=font, fill=255)
    display.image(image)
    display.show()

if __name__ == "__main__":
    main(sys.argv[1:])
