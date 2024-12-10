
class WiFi:



    def __init__(self, debug = True):
        self.debug = debug


    def print(self, *args):
        if self.debug:
            print(*args)
            
    
    
    def connect(self, ssid, password, timeout = 20, timezone = 1):


        import time, network, machine, utime            
            
        def setTime(timezone):
            
            import ntptime, utime, time
            
            ntptime.settime()

            rtc = machine.RTC()

            (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time() + 3600 * timezone)
            rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
            time.sleep_ms(100)
            
            (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time())
            
            self.print('Local time is {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = year, month = month, day = day, hour = hour, minute = minute))


        if ssid == None:
            raise Exception('No WiFi network name specified.')
        
        if password == None:
            raise Exception('No password specified.')

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        self.print("Connecting to network '" + ssid + "' with password '" + password + "'...")
        wlan.connect(ssid, password)

        iterations = timeout

        led = machine.Pin('LED', machine.Pin.OUT)
        led.off()
        
        while iterations > 0:
            led.toggle()
            
            if wlan.status() < 0 or wlan.status() >= 3:
                break

            iterations -= 1
            
            self.print('Waiting for WiFi connection...')
            time.sleep(1)

        led.off()

        if wlan.status() != 3:
            raise RuntimeError('Network connection failed.')

        status = wlan.ifconfig()
        ip = status[0]

        self.print('Connected to WiFi with ip = ' + ip)        
        setTime(timezone = timezone)
        
        
        return ip


def connectToWiFi(ssid, password, debug = False):
    
    wifi = WiFi(debug = debug)
    wifi.connect(ssid = ssid, password = password)
    
    
    
if __name__ == '__main__':

    from config import WIFI_SSID, WIFI_PASSWORD
    connectToWiFi(ssid = WIFI_SSID, password = WIFI_PASSWORD, debug = True)
    
    