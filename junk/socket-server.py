import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import secrets
import websocket


def _acceptWebSocketCallback(webSocket, httpClient) :
  print("WS ACCEPT")
  webSocket.RecvTextCallback   = _recvTextCallback
  webSocket.RecvBinaryCallback = _recvBinaryCallback
  webSocket.ClosedCallback     = _closedCallback

def _recvTextCallback(webSocket, msg) :
  print("WS RECV TEXT : %s" % msg)
  webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
  print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
  print("WS CLOSED")


                         # Starts server in a new thread

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip



try:
    ip = connect()
except KeyboardInterrupt:
    machine.reset()
    
    
    
from microWebSrv import MicroWebSrv
mws = MicroWebSrv(bindIP=ip)                                    # TCP port 80 and files in /flash/www
mws.MaxWebSocketRecvLen     = 256                      # Default is set to 1024
mws.WebSocketThreaded       = False                    # WebSockets without new threads
mws.AcceptWebSocketCallback = _acceptWebSocketCallback # Function to receive WebSockets
mws.Start(threaded=False)



while True:
    print('Serving...')
    sleep(10)
