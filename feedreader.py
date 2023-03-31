import time, request, gc, machine, re, json
import uasyncio as asyncio

class FeedReader:
    
    
    def __init__(self, feeds, debug):
        
        from led import OnboardLED 

        self.cache = []
        self.feeds = feeds
        self.latest = {}
        self.debug = debug
        self.led = OnboardLED()
       



    def print(self, *args):
        if self.debug:
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
        
        

        
    def fetch(self):

    
        for feed in self.feeds:

            try:
                gc.collect()
                self.print('Amount of memory available: {}'.format(gc.mem_free()))

                time.sleep(1)

                feedName = feed['name']
                feedURL  = feed['url']
                
                
                entry = self.getLatestRSS(feedURL)
                                  
                if entry != None:
                    
                    if self.latest.get(feedName) == None or self.latest[feedName]['title'] != entry['title']:
                        self.latest[feedName] = entry
                        
                        if not entry['title'] in self.cache:
                            name  = feed['name']
                            date  = entry['date']
                            title = entry['title']
                            
                            self.print('{name}: {date} - {title}'.format(name = name, date = date, title = title))
                            self.cache.insert(0, title)

                            yield {'name':name, 'date':date, 'title':title}
                        else:
                            self.print('Duplicate message: "{text}"'.format(text = entry['title']))
                        
                        while len(self.cache) > 10:
                            self.cache.pop()


            except Exception as error:
                self.print("Error parsing feed '{name}' - {error}".format(name = feed['name'], error = error))
                pass
            
 

if __name__ == '__main__':

    class App():


        def __init__(self, debug = True):
            from secrets import WIFI_SSID, WIFI_PASSWORD
            from wifi import WiFi
            
            self.debug = debug
            
            wifi = WiFi(debug = self.debug)
            wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)
        
        
        def run(self):


            feeds = [
                #{'name':'Dagens Industri', 'url':'https://digital.di.se/rss'},
                {'name':'SVT', 'url':'https://www.svt.se/nyheter/rss.xml'},
                {'name':'Sydsvenskan', 'url':'https://www.sydsvenskan.se/feeds/feed.xml'},
                {'name':'Expressen', 'url':'https://feeds.expressen.se/nyheter'},
                {'name':'Aftonbladet', 'url':'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'},
                {'name':'SvD', 'url':'https://www.svd.se/?service=rss'},
                {'name':'Google', 'url':'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'}
            ]
            
            
            reader = FeedReader(feeds, debug = self.debug)
            
            for entry in reader.fetch():
                print(entry)            



    App().run()







