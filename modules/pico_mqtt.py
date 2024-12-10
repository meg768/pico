
from mqtt_as import MQTTClient, config
import uasyncio as asyncio



async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print((topic, msg, retained))

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('foo_topic', 1)  # renew subscriptions




       
MQTTClient.DEBUG = True  # Optional: print diagnostic messages

class MQTT:

    def __init__(self, ssid, pwd, broker):
        config['ssid'] = ssid  
        config['wifi_pw'] = pwd
        config['server'] = broker
        config["queue_len"] = 3 

        self.client = MQTTClient(config)
        asyncio.run(self.as_MQTTInit())

    def Publish(self, msg):
        asyncio.run(self.as_Publish('From_pico', msg))

    async def as_Publish(self, topic, msg):
        self.client.dprint('Publish ' + msg+ ' Topic='+topic)
        await self.client.publish(topic, msg, qos = 1)
    
    async def as_MQTTInit(self):
        await self.client.connect()
        
        
        





