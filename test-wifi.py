from picoled import PicoLED
from wifi import WiFi

import urequests
import secrets

led = PicoLED()
led.blink()

wifi = WiFi()
wifi.connect(ssid=secrets.SSID, password=secrets.PASSWORD)

print("Fetching astronauts...")
astronauts = urequests.get("http://api.open-notify.org/astros.json").json()

number = astronauts['number']

for i in range(number):
    print(astronauts['people'][i]['name'])

while(True):
    machine.idle()
    