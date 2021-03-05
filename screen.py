
from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import sys, getopt

ax = 0
ay = 0
az = 0
fx = 0
fy = 0
fz = 0
spd = 0

i2c = busio.I2C(SCL, SDA)
width = 128
height = 64
font = ImageFont.truetype('retro-gaming.ttf', 10)

padding = 0
top = padding
bottom = height - padding
x=2

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"s:", ["ax=", "ay=", "az=", "fx=", "fy=", "fz=", "spd="])
    except getopt.GetoptError:
        print('ledscreen.py -a <amplitude> -f <frequency> -s <speed>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--ax':
            global ax
            ax = arg
        elif opt == '--ay':
            global ay
            ay = arg
        elif opt == '--az':
            global az
            az = arg
        elif opt == '--fx':
            global fx 
            fx = arg
        elif opt == '--fy':
            global fy
            fy = arg
        elif opt == '--fz':
            global fz
            fz = arg
        elif opt in ("-s", "--spd"):
            global spd 
            spd = arg
        
    display = adafruit_ssd1306.SSD1306_I2C(width,height,i2c)
    display.fill(0)
    display.show()
    image = Image.new("1",(width, height))
    draw = ImageDraw.Draw(image)

    #draw.text((x, top+0), "Max", font=font, fill=255)
    #draw.text((x+50, top+0), str(maxAmp)+" g", font=font, fill=255)
    #draw.text((x+50, top+15), str(maxFreq)+" Hz", font=font, fill=255)
    #draw.text((x, top+30), "Vel.", font=font, fill=255)
    #draw.text((x+50, top+30), str(spd)+" rpm", font=font, fill=255)
    
    draw.text((x+34, top), "X", font=font, fill=255)
    draw.text((x+70, top), "Y", font=font, fill=255)
    draw.text((x+106, top), "Z", font=font, fill=255)

    draw.text((x, top+17), "G", font=font, fill=255)
    draw.text((x, top+34), "Hz", font=font, fill=255)
    draw.text((x, top+51), "R", font=font, fill=255)

    draw.text((x+16+2, top+17), str(ax), font=font, fill=255)
    draw.text((x+52+2, top+17), str(ay), font=font, fill=255)
    draw.text((x+88+2, top+17), str(az), font=font, fill=255)

    draw.text((x+16+2, top+34), str(fx), font=font, fill=255)
    draw.text((x+52+2, top+34), str(fy), font=font, fill=255)
    draw.text((x+88+2, top+34), str(fz), font=font, fill=255)

    draw.text((x+16+2, top+51), str(spd)+" rpm", font=font, fill=255)

    display.image(image)
    display.show()

if __name__ == "__main__":
    main(sys.argv[1:])
