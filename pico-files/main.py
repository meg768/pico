class App:

    def run(self):
        import time
        import machine
        
        led = machine.Pin('LED', machine.Pin.OUT)

        try:
            while True:
                led.toggle()
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        
        led.off()


app = App()
app.run()

