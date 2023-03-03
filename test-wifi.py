from picoled import PicoLED
from wifi import WiFi

import urequests

led = PicoLED()
led.blink()

wifi = WiFi()
wifi.connect(ssid="Julia", password="potatismos")

print("Fetching astronauts...")
astronauts = urequests.get("http://api.open-notify.org/astros.json").json()

number = astronauts['number']

for i in range(number):
    print(astronauts['people'][i]['name'])

while(True):
    machine.idle()
    