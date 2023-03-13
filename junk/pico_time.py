import socket
import time
import struct
import machine


def SetTime():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    host = "pool.ntp.org"
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = 1
    while(t > 0 and t < 10):
        try:
            t = t + 1
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
   
 
        except OSError as exc:
            if exc.args[0] == 110: # ETIMEOUT
                time.sleep(0.5)
                continue
        else:
            t=0
            
   
    s.close()
    if(t == 0):
        val = struct.unpack("!I", msg[40:44])[0]
        NTP_DELTA = 2208985200 # GMT - 3600
        t = val - NTP_DELTA    
        tm = time.gmtime(t)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))



def TimeNow():
    now = time.localtime()
    return(now[3], now[4]) # hour,minute



