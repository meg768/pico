

from xmlparser import XMLParser
from xmltokenizer import XMLTokenizer


class App:
    
    
    def __init__(self, debug = True):
        self.debug = debug
        self.connectToWiFi()


    def print(self, *args):
        if self.debug:
            print(*args)
    
    def connectToWiFi(self):

        from secrets import WIFI_SSID, WIFI_PASSWORD
        from wifi import WiFi

        wifi = WiFi(debug = self.debug)
        wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

        

    def fetchRSS(self, url):


        import time
        import request
        
        self.print("Fetching RSS from '{url}'".format(url = url))

        startTime = time.ticks_ms()
        response = request.get(url)
        endTime = time.ticks_ms() 
        
        self.print("Fetched RSS in {seconds} seconds".format(seconds = (endTime-startTime) / 1000))

        return response.text


    def printRSS(self, rss):


        items = rss
        items = items['rss']
        items = items['channel']
        items = items['item']
        

        for item in items:
            x = item['title']
            print(x)
        
            

    def testRSS(self):


        filter = ['rss.channel.item.title', 'rss.channel.item.pubDate']

        SDS = 'https://www.sydsvenskan.se/feeds/feed.xml'
        expressen = 'https://feeds.expressen.se/nyheter'
        google = 'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'

        xml = self.fetchRSS(google)
        parser = XMLParser(filter = filter, debug = self.debug)
        rss = parser.parse(xml)

        self.printRSS(rss)





    def run(self):
        self.testRSS()



        
App().run()

