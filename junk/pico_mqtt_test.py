import time
import pico_mqtt
import pico_time


ssid = 'Ljunggren'
pwd = 'Windy9800'
broker = '192.168.1.37' 


def main():

    mqtt = pico_mqtt.MQTT(ssid, pwd, broker)

    pico_time.SetTime()
    (h,m) = pico_time.TimeNow()
    s = 'Pico has started '+ str(h)+':'+ str(m)
    mqtt.Publish(s)
    
    while True:
        time.sleep(5)
        
        (h,m) = pico_time.TimeNow()
        
        s = 'Pico time: ' + str(h)+':'+ str(m)
        mqtt.Publish(s)






main()






