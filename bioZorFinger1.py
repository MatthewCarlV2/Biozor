import serial
import adafruit_fingerprint as af
import time
import RPi.GPIO as GPIO
import adafruit_ssd1306
import board
import busio
from PIL import Image, ImageDraw, ImageFont

#Init for Screen
i2c = busio.I2C(board.SCL, board.SDA)
oledWidth = 128
oledHeight = 64
oled = adafruit_ssd1306.SSD1306_I2C(oledWidth,oledHeight, i2c)
oled.fill(0)
oled.show
image = Image.new("1",(oledWidth, oledHeight))
draw = ImageDraw.Draw(image)
size = 12 #text size
font = ImageFont.truetype("/usr/share/fonts/truetype/quicksand/Quicksand-Medium.ttf", size) #font path



#Init for Fingerprint Sesnsor
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
sensor = af.Adafruit_Fingerprint(uart)
#FingerPin = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.setup(FingerPin, GPIO.IN)

#Button Config
ButtonL = 16
ButtonR = 6
GPIO.setup(ButtonR, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(ButtonL, GPIO.IN,pull_up_down=GPIO.PUD_UP)

def ButtonController():
    printText("Left Button: Scan Finger | Right Button: Reset Print",1)
  
    while True:
        
        if GPIO.input(ButtonL)==GPIO.LOW:
            return True
        elif GPIO.input(ButtonR)==GPIO.LOW:
            printText("Verify Fingerprint To Reset",2)
            return False

#prints text 
def printText(text,sleep):
    textW, textH = draw.textsize(str(text), font)

    lines = wrap(text, font, oledWidth)
    lineH = font.getsize("A")[1]
    y = (oledHeight - (len(lines) * lineH)) // 2
    draw.rectangle((0,0,oledWidth, oledHeight),outline = 0,fill=0)

    for line in lines:
        lineW, _ = draw.textsize(line, font = font)
        x = ((oledWidth - lineW) // 2)
        draw.text((x,y), line, font = font, fill = 255)
        y+=lineH

    oled.image(image)
    oled.show()
    time.sleep(sleep)


#wraps text if its too long for the width of the screen
def wrap(text, font, maxW):
    lines = []
    words = text.split(" ")
    curLine = ""
    
    for word in words:
        
        tempLine = f"{curLine} {word}".strip()
        textW, _ = draw.textsize(tempLine, font = font)
        
        if textW <= maxW:
            curLine = tempLine
        else:
            lines.append(curLine)
            curLine = word
    if curLine:
        lines.append(curLine)
        
    return lines
    
    

def get_fingerprint(val):
    printText("Place Finger",1)
    
    while sensor.get_image() != af.OK:
        pass
        
    if(sensor.image_2_tz(val)!= af.OK):
       return False
       
    return True

def search():
    if(sensor.finger_search() != af.OK):
        printText("Finger Not Found, Please Try Again",2)
        return False

    return True

def enroll():
    printText("Welcome to BioZor!",2)
    
    for i in range(1,3):
        
        if not get_fingerprint(i):
            printText("Error Reading Fingerprint, Try Again",0.5)
            return

        while sensor.get_image() != af.OK:
            pass
        
        if (i == 1):
            printText("Remove Finger",1.5)
        
    
    if(sensor.create_model() != af.OK):
        printText("Error Creating Model",2.5)
        return
    
    if(sensor.store_model(11) != af.OK):
        printText("Error Storing Model",2.5)
        return
        
    printText("Finger Added Successfully!", 2)

if __name__ == "__main__":
    sensor.empty_library()
    while True:
        sensor.count_templates()
        while(sensor.template_count == 0):
            enroll()
            sensor.count_templates()

        time.sleep(1)
        toRun = ButtonController()
        
        while(True):
            get_fingerprint(1)
            if(search() == True):
                break
        
        if(toRun):
            printText("Verified! Launching Trezor Software!",3)
            break
            #launch pytrezor
        else:
            printText("Verified! Fingerprint Removed",1)
            sensor.empty_library()
    

