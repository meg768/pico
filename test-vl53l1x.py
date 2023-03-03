
import utime
from machine import Pin, I2C
from vl53l1x import VL53L1X
from picoled import PicoLED

PicoLED().blink()
        
i2c = I2C(0,  freq=400000, sda=Pin(8), scl=Pin(9))
test = VL53L1X(i2c)

while(True):
    print("Distance in mm: ", test.read() )
    utime.sleep(0.05)
        
