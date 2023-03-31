import machine
 
class OnboardLED:

    def __init__(self):
        self.timer = machine.Timer()
        self.led = machine.Pin('LED', machine.Pin.OUT)
    
    def on(self):
        self.stop()
        self.led.on()

    def off(self):
        self.stop()
        self.led.off()

    def flash(self, freq=10):
        def toggle(timer):
            self.led.toggle()
        
        self.stop()
        self.timer.init(freq=freq, mode=machine.Timer.PERIODIC, callback=toggle) 
