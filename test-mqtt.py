#Native libs
from machine import Pin, I2C
import network
import time
from time import sleep


#Third Party
from umqtt.robust import MQTTClient


# Internal libs
import constants


def connectMQTT():
    '''Connects to Broker'''
    # Client ID can be anything
    client = MQTTClient(
        client_id=b"mahmood",
        server=constants.SERVER_HOSTNAME,
        port=1883,
        user=constants.USER,
        password=constants.PASSWORD,
        keepalive=7200
    )
    client.connect()
    return client


def connect_to_internet(ssid, password):
    # Pass in string arguments for ssid and password

    # Just making our internet connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('waiting for connection...')
      time.sleep(1)
    # Handle connection error
    if wlan.status() != 3:
       print(wlan.status())
       raise RuntimeError('network connection failed')
    else:
      print('connected')
      print(wlan.status())
      status = wlan.ifconfig()


# Connect to internet and set MPU to start taking readings
connect_to_internet(constants.INTERNET_NAME, constants.INTERNET_PASSWORD)
client = connectMQTT()


def publish(topic, value):
    '''Sends data to the broker'''
    print(topic)
    print(value)
    client.publish(topic, value, retain = True)
    print("Publish Done")


while True:
    # Publish to broker
    publish('picow/ax', str(time.ticks_ms()))
    sleep(3)
    
    