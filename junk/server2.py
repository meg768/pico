
import secrets
import json

import network
import socket
import time

from machine import Pin

led = Pin(15, Pin.OUT)

ssid = secrets.SSID
password = secrets.PASSWORD

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)

#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
#         print(cl.readline())
        
        request = cl.recv(1024).split(b'\r\n')        

        print(request);
        

        print("----")
        
        for line in request:
            line = str(line)
            print(line)
            line = line.split(':', 1)
            if len(line) == 2:                
                print(line[0].strip())
                print(line[1].strip())
                
            if len(line) == 1:
                print(line[0].strip())


        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        x = {
            "name": "John",
            "age": 30,
            "city": "New York"
        }
        cl.send(json.dumps(x))

        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')