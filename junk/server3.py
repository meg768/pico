"""sample adapted from https://github.com/jczic/MicroWebSrv"""

import microWebSrv
import network
import machine
from time import sleep

import secrets
ssid = secrets.SSID
password = secrets.PASSWORD

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while wlan.isconnected() == False:
    print('Waiting for connection...')
    sleep(1)
        
ip = wlan.ifconfig()[0]
print(f'Connected on {ip}')
        
        
        
def handlerFunc_1(httpClient, httpResponse):
    print("handlerFunc_1")
    content   = """\
      <!DOCTYPE html>
      <html> 
        <head>
          <meta charset="UTF-8" />
          <title>TEST handlerFunc_1</title>
        </head>
        <body>
          <h1>TEST handlerFunc_1</h1>
          <div id='result'>...</div>
          Wait for websocket connect and get result printed above.
          <script>
            console.log("started");
            webSocket = new WebSocket("ws://192.168.86.52");
            
            webSocket.onopen = (event) => {
            
              webSocket.send("Here's some text that the server is urgently awaiting!");
            };
            webSocket.onmessage  = (event) => {
            console.log(event.data);
              document.getElementById("result").textContent = event.data;
            };
          </script>
        </body>
      </html>
    """ 
    httpResponse.WriteResponseOk( headers         = None,
                                  contentType     = "text/html",
                                  contentCharset  = "UTF-8",
                                  content         = content )
    
def handlerFunc_2(httpClient, httpResponse):
    print("handlerFunc_2")
    httpResponse.WriteResponseFile("www/test.html", contentType="text/html",  headers=None)


def handlerFunc_3(httpClient, httpResponse):
    print("handlerFunc_3")
    httpResponse.WriteResponseFile("www/test.html", contentType="text/html",  headers=None)


webSocket_ = None
def _acceptWebSocketCallback(webSocket, httpClient) :
  global webSocket_
  webSocket_ = webSocket
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
  global webSocket_
  webSocket_ = None
  
routeHandlers = [
  ( "/"    , "GET", handlerFunc_1 ),
  ( "/test", "GET", handlerFunc_2 ),
]

mws = microWebSrv.MicroWebSrv(routeHandlers=routeHandlers, port=80, bindIP='0.0.0.0', webPath="/www")

mws.MaxWebSocketRecvLen     = 1024                      # Default is set to 1024
mws.WebSocketThreaded       = False                    # WebSockets without new threads
mws.AcceptWebSocketCallback = _acceptWebSocketCallback # Function to receive WebSockets

cnt = 0
def timer_method(t):
    global cnt
    if webSocket_:
        webSocket_.SendText("cnt = " + str(cnt))
        cnt += 1

tim = machine.Timer(period=1000, mode=machine.Timer.PERIODIC, callback=timer_method)

mws.Start(threaded=False)

print("not threaded, there is no execution past this point")