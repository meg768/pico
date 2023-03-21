
from secrets import WIFI_SSID, WIFI_PASSWORD, PUSHOVER_TOKEN, PUSHOVER_USER

import time
import request
from wifi import WiFi

# Koppla upp WiFi hur du vill
wifi = WiFi()
wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)




headers = {
    'accept': 'application/rss+xml'
}

response = request.get('https://www.sydsvenskan.se/feeds/feed.xml', headers = headers)

print('Fetching')
print(response.text)