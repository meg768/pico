import time, request, gc, machine, re, json
import uasyncio as asyncio



class App():
    
    
    def __init__(self, debug = True):
     
        feeds = [
            #{'name':'Dagens Industri', 'url':'https://digital.di.se/rss'},
            {'name':'SVT', 'url':'https://www.svt.se/nyheter/rss.xml'},
            {'name':'Sydsvenskan', 'url':'https://www.sydsvenskan.se/feeds/feed.xml'},
            {'name':'Expressen', 'url':'https://feeds.expressen.se/nyheter'},
            {'name':'Aftonbladet', 'url':'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'},
            {'name':'SvD', 'url':'https://www.svd.se/?service=rss'},
            {'name':'Google', 'url':'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'}
        ]
        
        
#        from mqtt import MQTTClient
        

        from feedreader import FeedReader
        from pushover import Pushover
        from mqtt import MQTTClient
        from wifi import WiFi
        from picoled import PicoLED
        
        from config import PUSHOVER_USER, PUSHOVER_TOKEN_NEWS
        from config import WIFI_SSID, WIFI_PASSWORD
        from config import MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC, MQTT_PORT
        from config import OPEN_WEATHER_APPID

        self.debug = debug
        self.loop = 0


        wifi = WiFi(debug = self.debug)
        wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

        self.pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN_NEWS)
        self.led = PicoLED()
        self.mqtt = MQTTClient(client_id = 'MEG', server = MQTT_HOST, user = MQTT_USERNAME, password = MQTT_PASSWORD, port = MQTT_PORT, keepalive = 60)
        self.reader = FeedReader(feeds = feeds, debug = self.debug)


    def print(self, *args):
        if self.debug:
            print(*args)

        
        
        
    def blink(self):
        try:
            while True:
                self.led.toggle()
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        
        self.led.off()

          
        
    def push(self, title, message, url = None):

        try:
            self.pushover.push(title = title, message = message, url = url)

        except Exception as error:
            self.print('Could not push -', error)
            pass
        

    def publish(self, payload):
        

        try:
            if not isinstance(payload, str):
                payload = json.dumps(payload)
              
            self.print("Publishing '{payload}'.".format(payload = payload))
                       
            self.mqtt.connect()
            self.mqtt.publish(topic = 'matrix/64x32', msg = payload.encode('utf-16'), retain = True)
            self.mqtt.disconnect()
            
        except Exception as error:
            self.print('Could not publish -', error)
            pass
            




    def fetchWeather(self):
        from config import OPEN_WEATHER_APPID
        from openweathermap import OpenWeatherMap

        weather = OpenWeatherMap(OPEN_WEATHER_APPID, lat = 55.71, long = 13.19)
        
        weather.fetch()

        text = 'Just nu {A} och {B}°'
        text = text.format(A = weather.current.weatherDescription(), B = weather.current.temperature())
        yield text

        text = 'Soluppgång {A} - solnedgång {B}'
        text = text.format(A = weather.current.sunrise(), B = weather.current.sunset())
        yield text

        text = 'I morgon {A} och {B}° ({C}°)'
        text = text.format(A = weather.daily[1].weatherDescription(), B = weather.daily[1].maxTemperature(), C = weather.daily[1].minTemperature())
        yield text

        text = 'I övermorgon {A} och {B}° ({C}°)'
        text = text.format(A = weather.daily[2].weatherDescription(), B = weather.daily[2].maxTemperature(), C = weather.daily[2].minTemperature())
        yield text


    def fetchNews(self):
        yield from self.reader.fetch()
        
    def run(self):

        if True:
            
            while True:
            
                self.loop += 1
                self.led.on()
                
                for entry in self.fetchNews():
                    self.print(entry)
            
                    payload = {
                        'text': '{A} - {B}'.format(A = entry['name'], B = entry['title']),
                        'textColor': 'auto'
                    }
                         
                    self.publish(payload)
                    self.push(title = entry['name'], message = entry['title'], url = entry['link'])
                                            

                if (self.loop % 5) == 0:
                    for entry in self.fetchWeather():
                        self.print(entry)
                        
                        payload = {
                            'text': entry,
                            'textColor': 'auto'
                        }                    

                        self.publish(payload)
                        
                    
                self.led.flash(10)                    
                time.sleep(60)

#        except Exception as error:
#             self.print('Error: {error}'.format(error = error))
#             self.push(title = 'Error', message = error)




app = App(debug = True)

app.run()






