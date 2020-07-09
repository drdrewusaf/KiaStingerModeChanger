import gc
gc.collect()

import time
import os
import board
import busio
import digitalio
import adafruit_ssd1306

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
driveModes = ["Smart", "Eco", "Comfort", "Sport", "Custom"]
autoISG = ["On", "Off"]
savedModes = []
buttonA = digitalio.DigitalInOut(board.D9)
buttonA.direction = digitalio.Direction.INPUT
buttonA.pull = digitalio.Pull.UP
buttonB = digitalio.DigitalInOut(board.D6)
buttonB.direction = digitalio.Direction.INPUT
buttonB.pull = digitalio.Pull.UP
buttonC = digitalio.DigitalInOut(board.D5)
buttonC.direction = digitalio.Direction.INPUT
buttonC.pull = digitalio.Pull.UP
driveModeRight = digitalio.DigitalInOut(board.A0)  # Brown wire/pin 5 on output
driveModeRight.direction = digitalio.Direction.OUTPUT
driveModeLeft = digitalio.DigitalInOut(board.A1)  # Grey wire/pin 4 on output
driveModeLeft.direction = digitalio.Direction.OUTPUT
# reserved1 = digitalio.DigitalInOut(board.A2)  # Black wire/pin 1 on output
# reserved1.direction = digitalio.Direction.OUTPUT
autoISGsw = digitalio.DigitalInOut(board.A3)  # Red wire/pin 2 on output
autoISGsw.direction = digitalio.Direction.OUTPUT
# reserved2 = digitalio.DigitalInOut(board.A4)  # Blue wire/pin 3 on output
# reserved2.direction = digitalio.Direction.OUTPUT

def writeFile():
    os.remove("/settings.dat")
    with open("/settings.dat", "w") as settingsFile:
        for i in savedModes:
            settingsFile.write('%s,' % i)
        return

def driveModeSelect(mode):
    if mode == "Smart":
        driveModeTurn(driveModeLeft, 2)
    elif mode == "Sport":
        driveModeTurn(driveModeRight, 1)
    elif mode == "Custom":
        driveModeTurn(driveModeRight, 2)

def driveModeTurn(direction, turns):
    for i in range(0, turns):
        direction.value = True
        time.sleep(.3)
        direction.value = False
        time.sleep(.3)

def oledWriter(line1, line2, line3):
    oled.fill(0)
    oled.text(line1, 0, 0, 1)
    oled.text(line2, 0, 10, 1)
    oled.text(line3, 0, 20, 1)
    oled.show()
    return

def driveModeMenu():
    menuPosition = 0
    modeSaved = False
    returnToMain = time.time() + 20
    for m in driveModes:
        if savedModes[0] == m:
            menuPosition = driveModes.index(m)
            oledWriter('(A) Up', '(B) Set Mode: '
                       + driveModes[menuPosition], '(C) Down')
    while modeSaved is False:
        while modeSaved is False:
            if time.time() < returnToMain:
                break
            modeSaved = True
        if not buttonA.value:
            returnToMain = time.time() + 20
            if menuPosition == 0:
                pass
            else:
                menuPosition = menuPosition - 1
                oledWriter('(A) Up', '(B) Set Mode: '
                           + driveModes[menuPosition], '(C) Down')
        elif not buttonC.value:
            returnToMain = time.time() + 20
            if menuPosition == 4:
                pass
            else:
                menuPosition = menuPosition + 1
                oledWriter('(A) Up', '(B) Set Mode: '
                           + driveModes[menuPosition], '(C) Down')
        if not buttonB.value:
            returnToMain = time.time() + 20
            savedModes[0] = driveModes[menuPosition]
            writeFile()
            oledWriter('', 'Drv Mode Saved', '')
            modeSaved = True
    main()

def mainMenu(buttonVal):
    if buttonVal == 1:
        driveModeMenu()
    elif buttonVal == 2:
        if savedModes[1] == "On":
            savedModes[1] = "Off"
            writeFile()
            main()
        else:
            savedModes[1] = "On"
            writeFile()
            main()

def main():
    buttonVal = 0
    buttonPressed = False
    screenOff = False
    screenTimer = time.time() + 15
    oledWriter('(A) Drv Mode: ' + savedModes[0],
               '(B) ISG: ' + savedModes[1], '')
    while buttonPressed is False:
        while screenOff is False:
            if time.time() < screenTimer:
                break
            screenOff = True
            oledWriter('', '', '')
        if not buttonA.value:
            buttonVal = 1
            mainMenu(buttonVal)
        elif not buttonB.value:
            buttonVal = 2
            mainMenu(buttonVal)

# Begin Startup #
settingsApplied = False
oledWriter('', '', '')
with open("/settings.dat", "r") as settingsFile:
    savedModes = settingsFile.read().split(',')

while settingsApplied is False:
    if savedModes[0] == "Comfort" or savedModes[0] == "Eco":
        oledWriter('Cannot autoset ' + savedModes[0], 'Manually set car.', '')
    else:
        driveModeSelect(savedModes[0])
        oledWriter('Drv Mode ' + savedModes[0] + ' Set', '', '')
    if savedModes[1] == "On":
        oled.text('ISG Left On', 0, 20, 1)
        oled.show()
        settingsApplied = True
    elif savedModes[1] == "Off":
        autoISGsw.value = True
        time.sleep(.3)
        autoISGsw.value = False
        oled.text('ISG Turned Off', 0, 20, 1)
        oled.show()
        settingsApplied = True
time.sleep(5)
main()
