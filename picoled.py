import machine
 
class PicoLED:

    def __init__(self):
        self.foo = 1
        self.timer = machine.Timer()
        self.led = machine.Pin('LED', machine.Pin.OUT)
    

    def cancel(self):
        self.timer.deinit()
        
    def blink(self, freq=10):
        def toggle(timer):
            self.led.toggle()
            
        self.timer.init(freq=freq, mode=machine.Timer.PERIODIC, callback=toggle) 
