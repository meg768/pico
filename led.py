import machine

timer = machine.Timer()
led   = machine.Pin('LED', machine.Pin.OUT)

class OnboardLED:



    def on(self):
        timer.deinit()
        led.on()

    def off(self):
        timer.deinit()
        led.off()

    def toggle(self):
        timer.deinit()
        led.toggle()

    def flash(self, freq=10):
        def toggle(timer):
            led.toggle()
        
        self.off()
        timer.init(freq=freq, mode=machine.Timer.PERIODIC, callback=toggle) 
