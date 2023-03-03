import network
import ntptime

class WiFi:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self, ssid, password):
        self.wlan.connect(ssid, password)

        while(not self.wlan.isconnected()):
            utime.sleep(0.5)        

        ntptime.settime()


