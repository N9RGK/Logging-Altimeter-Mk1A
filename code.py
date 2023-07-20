import board
import time
from digitalio import DigitalInOut, Direction, Pull
import analogio
import asyncio
import busio
import storage
import adafruit_bmp280
import supervisor
import microcontroller

# define the Hardware for the board
sda1_pin = board.GP18
scl1_pin = board.GP19
sda0_pin = board.GP20
scl0_pin = board.GP21

sense1_pin = board.A0
sense2_pin = board.A1
pixel_pin = board.GP1
fire1_pin = board.GP9
fire2_pin = board.GP11
pyro_low_pin = board.GP10
led_pin = board.GP25

tx_pin = board.GP0
rx_pin = board.GP1

# configure the system
flying = False

sense1 = analogio.AnalogIn(sense1_pin)
sense2 = analogio.AnalogIn(sense2_pin)

pyro_low = DigitalInOut(pyro_low_pin)
pyro_low.switch_to_output(value = False)

fire1 = DigitalInOut(fire1_pin)
fire1.switch_to_output(value=False)

fire2 = DigitalInOut(fire2_pin)
fire2.switch_to_output(value=False)

i2c = busio.I2C(scl0_pin, sda0_pin)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x77)

bmp280.sea_level_pressure = 1013.25
bmp280.mode = adafruit_bmp280.MODE_NORMAL
bmp280.standby_period = adafruit_bmp280.STANDBY_TC_500
bmp280.iir_filter = adafruit_bmp280.IIR_FILTER_X16
bmp280.overscan_pressure = adafruit_bmp280.OVERSCAN_X16
bmp280.overscan_temperature = adafruit_bmp280.OVERSCAN_X2

altitude = bmp280.altitude * 3.28084 # initialize altitude to current measurement and convert to feet

launchSiteAltitude = altitude #set launch site altitude to start athte current measurement

agl = 0
newAltitude = bmp280.altitude * 3.28084
agl = newAltitude - altitude
waitToLog = 60
loopTime = 0
usb_status = supervisor.runtime.serial_connected


#Setup LED
led_pin = board.GP25
led = DigitalInOut(led_pin)
led.switch_to_output()

    
while(usb_status):
    print("Standing by for file transfer. To fly and log, remove USB cable.")
    led.value = True
    time.sleep(0.25)
    led.value = False
    time.sleep(0.25)
    time.sleep(0.1)
    


print("Starting Ground Phase")    
while(loopTime < waitToLog):

    newAltitude = bmp280.altitude * 3.28084
    agl = newAltitude - altitude
    altitude = newAltitude
    print(supervisor.ticks_ms(),", ", agl,", ", usb_status)
    loopTime = loopTime + 1
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)



logging = True
# open the file
file = open('data.csv','wt')
print("Log File Created")
# capture the time of the launch so we can subtract
launchTime = supervisor.ticks_ms()
print("Launch Time Set To: ", launchTime)

previous_sample_time = 0
led.value = True #turn on LED for the durration of the logging

while(logging == True):
    mission_time = supervisor.ticks_ms() - launchTime

    if(mission_time - previous_sample_time > 50): # sample every 100ms
        previous_sample_time = mission_time
        newAltitude = bmp280.altitude * 3.28084
        pressure = bmp280.pressure
        agl = newAltitude - altitude
        altitude = newAltitude
        data_string = '' + str((supervisor.ticks_ms()-launchTime)/100) + ', ' + str(agl) + ', ' + str(pressure)
        print('Flight Time: ' + str((supervisor.ticks_ms()-launchTime)/100) + ', Altitude: ' + str(agl) + ', Pressure: ' + str(pressure))
        file.write(data_string + '\n')
    # determine if our flight is over
    # currently 100 seconds.  But altitude stable is better.
    if mission_time > 30000: # keep logging for 10 minutes
        logging = False

file.close()
led.value = False #Turn off LED to indicate logging is complete

time.sleep(1000000) #Wait forever so there is time to find the rocket and get files

# microcontroller.reset()

