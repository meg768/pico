import machine
 
class PicoLED:

    def __init__(self):
        self.timer = machine.Timer()
        self.led = machine.Pin('LED', machine.Pin.OUT)
    
    def cancel(self):
        self.timer.deinit()
        
    def on(self):
        self.cancel()
        self.led.on()

    def off(self):
        self.cancel()
        self.led.off()

        
    
    def flash(self, freq=10):
        def toggle(timer):
            self.led.toggle()
            
        self.timer.init(freq=freq, mode=machine.Timer.PERIODIC, callback=toggle) 

        
if __name__ == '__main__':
    
    led = PicoLED();
    led.flash(1)
    