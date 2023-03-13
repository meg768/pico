# class App:
# 
#     def run(self):
#         import time
#         import machine
#         
#         led = machine.Pin('LED', machine.Pin.OUT)
# 
#         try:
#             while True:
#                 led.toggle()
#                 time.sleep(0.1)
# 
#         except KeyboardInterrupt:
#             pass
# 
# 
# app = App()
# app.run()

# Hämta lösenord etc från en modul secrets.py
from secrets import WIFI_SSID, WIFI_PASSWORD, PUSHOVER_TOKEN, PUSHOVER_USER
import time

from pushover import Pushover
from settime import setTime



class WiFi:


    def __init__(self, debug = True):
        self.debug = debug


    def print(self, *args):
        if self.debug:
            print(*args)
            
    def debug(self, *args):
        print(*args)
            
    
    def connect(self, ssid, password, timeout = 20, timezone = None):

        import network, machine, utime

        def setTime(timezone = 1):
            
            import ntptime
            
            ntptime.settime()

            if (timezone != None):
                import time
                rtc = machine.RTC()

                (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time() + 3600 * timezone)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                time.sleep_ms(100)         
            

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
        
        if (timezone != None):
            setTime(timezone)

        now = time.localtime()
        (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time())
        self.print('Local time is {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = now[0], month = now[1], day = now[2], hour = now[3], minute = now[4]))

        return ip

    

# Koppla upp WiFi hur du vill
wifi = WiFi()
wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD, timezone = 3)

setTime()


now = time.localtime()
text = '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = now[0], month = now[1], day = now[2], hour = now[3], minute = now[4])
print(text)
pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN)
result = pushover.send(message = text, title = "Aktuell tid")
print(result)

