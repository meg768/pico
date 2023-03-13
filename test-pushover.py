
# Hämta lösenord etc från en modul secrets.py
from secrets import WIFI_SSID, WIFI_PASSWORD, PUSHOVER_TOKEN, PUSHOVER_USER

import time
from pushover import Pushover
from wifi import WiFi

# Koppla upp WiFi hur du vill
wifi = WiFi()
wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)


(year, month, day, hour, minute, second, weekday, yearday) = time.localtime()

now = '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = year, month = month, day = day, hour = hour, minute = minute)
print(now)

pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN)
result = pushover.send(message = now, title = "Aktuell tid")
print(result)
