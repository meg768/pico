
class WiFi:


    def __init__(self, debug = True):
        self.debug = debug


    def print(self, *args):
        if self.debug:
            print(*args)
            
    def debug(self, *args):
        print(*args)
            
    
    def connect(self, ssid, password, timeout = 20, timezone = None):

        import ntptime, time, network, machine, utime

        def setTime():
            ntptime.settime()

            if (timezone != None):
                rtc = machine.RTC()

                (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time() + 3600 * timezone)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                time.sleep_ms(100)

            now = time.localtime()
            self.print('Local time is {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = now[0], month = now[1], day = now[2], hour = now[3], minute = now[4]))
            
            

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
        
        setTime()

        return ip

    
