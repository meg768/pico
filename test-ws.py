from ws import WebSocketServer, WebSocketClient


class MeasureDistance(WebSocketClient):

    def __init__(self, connection, debug = True):
        
        from vl53l1x import VL53L1X
        from machine import I2C, Pin

        super().__init__(connection)
        
        self.i2c = I2C(0,  freq = 400000, sda = Pin(8), scl = Pin(9))
        self.vl53l1x = VL53L1X(self.i2c)
        self.value = -1
        self.debug = debug


    def print(self, *args):
        if self.debug:
            print(*args)

    def process(self):
        import json
        
        try:
            value = round(self.vl53l1x.read() / 10)
                            
            if value != self.value:
                self.value = value
                
                percent = round(self.value / 4)
                
                if percent > 100:
                    percent = 100

                data = {}
                data["value"] = value;
                data["percent"] = percent;
                
                self.print(json.dumps(data))
                self.connection.write(json.dumps(data))
            
        except:
            self.print("Client closed. Disconnecting.")
            self.connection.close()



class Server(WebSocketServer):
    
    def __init__(self):
        super().__init__("test-ws.html")

    # Return a new instance of a client
    def _make_client(self, connection):
        return MeasureDistance(connection = connection, debug = False)



class App:

    def run(self):
        from wifi import WiFi
        from machine import Pin
        from pushover import Pushover        
        import secrets, time

        wifi = WiFi()
        wifi.connect(secrets.SSID, secrets.PASSWORD)

        server = Server()
        server.start(3000)
        
        pushover = Pushover(user = secrets.PUSHOVER_USER, token = secrets.PUSHOVER_TOKEN)
        pushover.send('Websocket server started.')
        
        led = Pin('LED', Pin.OUT)

        try:
            while True:
                led.toggle()
                server.process_all()
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        
        server.stop()
        led.off();



app = App()
app.run()