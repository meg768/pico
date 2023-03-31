
class App:
    
    
    def __init__(self, debug = True):
        self.debug = debug
        self.connectToWiFi()
        
        self.cache = {}

        self.feeds = [
            #{'name':'Dagens Industri', 'url':'https://digital.di.se/rss'},
            {'name':'Sydsvenskan', 'url':'https://www.sydsvenskan.se/feeds/feed.xml'},
            {'name':'Expressen', 'url':'https://feeds.expressen.se/nyheter'},
            {'name':'Aftonbladet', 'url':'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'},
            {'name':'SvD', 'url':'https://www.svd.se/?service=rss'},
            {'name':'Google', 'url':'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'}
        ]


    def print(self, *args):
        if self.debug:
            print(*args)
    
    
    def connectToWiFi(self):

        from secrets import WIFI_SSID, WIFI_PASSWORD
        from wifi import WiFi

        wifi = WiFi(debug = self.debug)
        wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

        
                
    def parseRSS(self, xml):
        

        result = []
        
        xml = xml
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
            import re
            
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
            
            pubDate = getAttribute(item, 'pubDate')
            title = getAttribute(item, 'title')
            
            result.append({'title':title, 'pubDate':pubDate})
            

        return result;                    


            

    def fetchRSS(self, url):


        import time, request, gc, machine
        
        gc.collect()
        
        led = machine.Pin('LED', machine.Pin.OUT)
        led.on()

        self.print("Fetching RSS from '{url}'".format(url = url))

        headers = {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }
        
        startTime = time.ticks_ms()
        response = request.get(url, headers = headers)
        xml = response.text
        endTime = time.ticks_ms() 
        
        self.print("Fetched RSS in {seconds} seconds.".format(seconds = (endTime-startTime) / 1000))
        
        led.off()
        
        return xml
        


    def getLatestRSS(self, url):

        def sortKey(value):
            return value['key']
        

        def getSortKey(date):
                
            # https://www.w3.org/Protocols/rfc822/#z28
            
            import ure
            import time

            regex = "^(\S+),\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)$"
            match = ure.match(regex, date)
            
            try:
                weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                weekday = weekdays.index(match.group(1))+1
                day     = int(match.group(2))
                month   = months.index(match.group(3))+1
                year    = int(match.group(4))
                hour    = int(match.group(5))
                minute  = int(match.group(6))
                second  = int(match.group(7))
                
                datetime = '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}.{second:02d}'.format(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
                         
                return datetime

            except:
                raise Exception("Invalid date: '{date}'".format(date = text))
                




        xml = self.fetchRSS(url)
        items = self.parseRSS(xml)
        
        for item in items:
            item['key'] = getSortKey(item['pubDate'])


        items.sort(key = sortKey, reverse = True)
        
        return items[0]

            



    def readFile(self, fileName):
        
        content = ''

        with open(fileName, 'r') as file:
            content = file.read()
            file.close()
        
 
        return content
        
        
    def run(self):
        

        import json, re


        #xml1 = self.readFile('google.xml')
        #print(self.parseRSS(xml1))
        
        #xml = self.fetchRSS('https://www.sydsvenskan.se/rss.xml?latest')

        #xml = self.fetchRSS('https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv')
        xml = self.fetchRSS('https://digital.di.se/rss')
        #xml = self.fetchRSS('https://www.sydsvenskan.se/feeds/feed.xml')
        #xml = self.fetchRSS('https://www.svd.se/?service=rss')
        

        print(xml)
        print(self.parseRSS(xml))
        #print(self.parseRSS(xml))
        
        

        
        
    def run(self):


            
        def blink():
            import time, machine
            
            led = machine.Pin('LED', machine.Pin.OUT)

            try:
                while True:
                    led.toggle()
                    time.sleep(0.1)

            except KeyboardInterrupt:
                pass
            
            led.off()
            
            
        try:
            import gc, time
            from pushover import Pushover
            from secrets import PUSHOVER_USER, PUSHOVER_TOKEN_NEWS
            

            pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN_NEWS)
            latest = {}
            
            
            def notify(feed, entry):
                print('{name}: {date} - {title}'.format(name = feed['name'], date = entry['pubDate'], title = entry['title']))
                
                try:
                    pushover.send(entry['title'], title = feed['name'])
                    
                except:
                    pass
                
            while True:
                for feed in self.feeds:
                    gc.collect()

                    feedName = feed['name']
                    feedURL = feed['url']
                    
                    
                    entry = self.getLatestRSS(feedURL)
                    
                    
                    if latest.get(feedName) == None or latest[feedName]['title'] != entry['title']:
                        latest[feedName] = entry
                        notify(feed, entry)
                        
                time.sleep(60)
                            
                    
        except Exception:
            blink()
                
 




App(debug = False).run()

