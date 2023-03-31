import time, request, gc, machine, re, json
import uasyncio as asyncio

class RSSParser:
    
    
    def __init__(self, feeds):
        
        from led import OnboardLED 

        self.cache = []
        self.feeds = feeds
        self.latest = {}
        self.led = OnboardLED()
       



    def print(self, *args):
        print(*args)
        
                
    def parseRSS(self, xml):
        

        rss = []
        index = 0
        length = len(xml)
        
        def getItem():
            nonlocal xml, index, length
            
            item = None
            
            startTag = '<item'
            endTag = '</item>'
            
            startIndex = xml.find(startTag, index)
            endIndex = xml.find(endTag, index)
            
            if startIndex < endIndex:
                item = xml[startIndex:endIndex + len(endTag)]
                index = endIndex + len(endTag)
            else:
                index = length
                
            return item
        
        
        def getAttribute(item, name):
            
            text = None
            regex = r"<{name}>(.*?)</{name}>".format(name = name)
            match = re.search(regex, item)
            
            if match:
                regex = '<!\[CDATA\[(.*?)\]\]>'
                
                text = match.group(1)
                match = re.search(regex, text)
                
                if match:
                    text = match.group(1)
                    
            return text
                
                
                

        while True:
            
            item = getItem()
            
            if item == None:
                break
            
            entry = {

                # Get pubDate and convert date format to GMT
                'date': self.formatRFC822ToTZ(getAttribute(item, 'pubDate')),

                # Get title
                'title': getAttribute(item, 'title'),
                
                # Get link
                'link': getAttribute(item, 'link')
                
            }
            
            rss.append(entry)

        return rss;                    


            

    def fetchRSS(self, url):

        try:
            gc.collect()
            
            self.print("Fetching RSS from '{url}'".format(url = url))

            headers = {
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }
            
            startTime = time.ticks_ms()
            response = request.get(url, headers = headers)
            xml = response.text
            response.close()
            endTime = time.ticks_ms() 
            
            self.print("Fetched RSS in {seconds} seconds.".format(seconds = (endTime-startTime) / 1000))
            
            return xml
        
        except:
            raise
        
        


    def getLatestRSS(self, url):

        def sortKey(value):
            return value['date']
        

        rss = self.fetchRSS(url)
        items = self.parseRSS(rss)
        
        items.sort(key = sortKey, reverse = True)

        return items[0]

            

    # Parses a RFC822 date/time to GMT time
    def parseRFC822(self, date):
            
        # https://www.w3.org/Protocols/rfc822/#z28
        
        try:

            regex = "^(\S+),\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)$"
            match = re.match(regex, date)
            
            weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            weekday  = weekdays.index(match.group(1))+1
            day      = int(match.group(2))
            month    = months.index(match.group(3))+1
            year     = int(match.group(4))
            hour     = int(match.group(5))
            minute   = int(match.group(6))
            second   = int(match.group(7))
            timezone = match.group(8)

            tm = time.mktime((year, month, day, hour, minute, second, 0, 0))
            offset = 0
            
            regex = "^([+-])(\d\d)(\d\d)$"
            match = re.match(regex, timezone)
            
            if match:
                sign = -1 if match.group(1) == '+' else 1
                offset = int(match.group(2)) * sign
            
            elif timezone != 'GMT':
                raise
                
            return tm + offset  * 3600
        
              
        except:
            raise Exception("Invalid date: '{date}'".format(date = date))
            

    def formatRFC822ToTZ(self, date):
        
        tm = self.parseRFC822(date)
        
        (year, day, month, hour, minute, second, weekday, yearday) = time.gmtime(tm)
        datetime = '{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.000Z'.format(year = year, month = month, day = day, hour = hour, minute = minute, second = second)

        return datetime
        
        

        
    def notify(self, name, date, title):
        self.print('{name}: {date} - {title}'.format(name = name, date = date, title = title))


    def error(self, message):
        self.print(message)        
        
        
    def poll(self):

                
        self.led.on()

        for feed in self.feeds:

            try:
                gc.collect()
                self.print('Amount of memory available: {}'.format(gc.mem_free()))

                time.sleep(1)

                feedName = feed['name']
                feedURL  = feed['url']
                
                
                self.led.flash(100)
                entry = self.getLatestRSS(feedURL)
                self.led.off()
                                  
                if entry != None:
                    
                    if self.latest.get(feedName) == None or self.latest[feedName]['title'] != entry['title']:
                        self.latest[feedName] = entry
                        
                        if not entry['title'] in self.cache:
                            self.cache.insert(0, entry['title'])

                            self.notify(name = feed['name'], date = entry['date'], title = entry['title'])
                        else:
                            self.print('Duplicate message: "{text}"'.format(text = entry['title']))
                        
                        while len(self.cache) > 10:
                            self.cache.pop()

                    self.led.flash(1)
                    time.sleep(10)
                    self.led.off()

            except Exception as error:
                self.error("Error parsing feed '{name}' - {error}".format(name = feed['name'], error = error))
                pass
            
 


class App(RSSParser):
    
    
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
        
        from umqtt.simple2 import MQTTClient
        from led import OnboardLED
        
        super().__init__(feeds)
        
        from wifi import WiFi
        from pushover import Pushover

        from secrets import PUSHOVER_USER, PUSHOVER_TOKEN_NEWS
        from secrets import WIFI_SSID, WIFI_PASSWORD
        from secrets import MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC, MQTT_PORT

    
        self.debug = debug
        self.pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN_NEWS)
        self.led = OnboardLED()
     
     
        wifi = WiFi(debug = self.debug)
        wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

        self.mqtt = MQTTClient(client_id = 'MEG', server = MQTT_HOST, user = MQTT_USERNAME, password = MQTT_PASSWORD, port = MQTT_PORT, keepalive = 60)


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

          
        
    def push(self, title, message):

        try:
            self.pushover.push(title = title, message = message)
        except:
            pass
        

    def publish(self, payload):
        

        try:
            if not isinstance(payload, str):
                payload = json.dumps(payload)
              
            self.print("Publishing '{payload}'.".format(payload = payload))
                       
            self.mqtt.connect()
            self.mqtt.publish(topic = 'Matrix/64x32', msg = payload.encode('utf-16'), retain = True)
            self.mqtt.disconnect()
            
        except Exception as error:
            self.print('Could not publish.', error)
            
                    
                
    def notify(self, name, date, title):
        
        try:
            super().notify(name = name, date = date, title = title)
            
            payload = {
                'text': '{name} - {title}'.format(name = name, title = title),
                'textColor': 'auto'
            }
                       
            self.publish(payload)
            self.push(message = title, title = name)
            
        except Exception as error:
            self.print('Problem notifying -', error)
            pass
                


    def error(self, message):


        try:
            super().error(message)
            self.send(title = 'Error', message = message)
            
        except:
            pass
                
        
    def run(self):


        self.led.off()
        
        try:
            
            while True:
            
                self.poll()                
                        
                for index in range(60 * 1):
                    self.led.toggle()
                    time.sleep(1)

        except Exception as error:
            self.print('Error: {error}'.format(error = error))
            self.send(title = 'Error', message = error)
            
        finally:
            self.blink()
 



app = App(debug = True)

app.run()





