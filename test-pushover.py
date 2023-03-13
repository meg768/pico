
# Hämta lösenord etc från en modul secrets.py
from secrets import WIFI_SSID, WIFI_PASSWORD, PUSHOVER_TOKEN, PUSHOVER_USER
import time

from pushover import Pushover
from  settime import setTime




class WiFi:


    def __init__(self, debug = True):
        self.debug = debug


    def print(self, *args):
        if self.debug:
            print(*args)
            
    def debug(self, *args):
        print(*args)
            

   
    def connect(self, ssid, password, timeout = 20):

        import network, machine, utime

            

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        self.print("Connecting to network '" + ssid + "' with password '" + password + "'...")
        wlan.connect(ssid, password)

        iterations = timeout

        while iterations > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break

            iterations -= 1
            
            self.print('Waiting for WiFi connection...')
            time.sleep(1)

        if wlan.status() != 3:
            raise RuntimeError('Network connection failed.')

        status = wlan.ifconfig()
        ip = status[0]

        self.print('Connected to WiFi with ip = ' + ip)

        return ip

    

# Koppla upp WiFi hur du vill
wifi = WiFi()
wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)


setTime()
setTime()

now = time.localtime()
text = '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = now[0], month = now[1], day = now[2], hour = now[3], minute = now[4])
print(text)
pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN)
result = pushover.send(message = text, title = "Aktuell tid")
print(result)
