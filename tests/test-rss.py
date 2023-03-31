#from xmltokenizer import XMLTokenizer
#from xmlparser import XMLParser


###########################################################################################



class XMLTokenizer:

    START_TAG         = 'start-tag'
    END_TAG           = 'end-tag'
    HEADER            = 'header'
    COMMENT           = 'comment'
    CONTENT           = 'content'
    

    def __init__(self, xml = ""):

        self.setXML(xml)
        

    def setXML(self, xml = ''):
        self.xml = xml
        self.index = 0
        self.length = len(self.xml)


    def raiseError(self, message):
        raise Exception(message)
            
  

    
    def skipWS(self):
        
        while self.index < self.length:
            if not self.xml[self.index].isspace():
                return
            
            self.index += 1





    def getIdentifier(self):

        identifier = ""
        
        self.skipWS()
        
        while self.index < self.length:
            char = self.xml[self.index]
            
            if not (char.isalpha() or char.isdigit() or char in "_-."):
                break
            
            identifier += char
            self.index += 1
            
        return identifier

    def getNamespaceIdentifier(self):

        namespace = self.getIdentifier()

        if self.xml[self.index] != ':':
            return namespace

        # Skip colon
        self.index += 1
        
        identifier = self.getIdentifier()
        
        if len(identifier) == 0:
            self.raiseError('Invalid namespace')
                        
        return namespace + ':' + identifier


    def expect(self, text):
        if not self.match(text):
            raiseError("Expected '{text}'".format(text = text))
      
      
    def peek(self, text):

        if True:
            # This is faster
            length = len(text)

            for index in range(length):
                if self.xml[self.index+index] != text[index]:
                    return False
                
            self.index += length
            return True

        else:
            
            peek = self.xml[self.index:self.index+len(text)]

            if peek == text:
                self.skipChars(len(text))    
                return True
            
            return False
        
        
    def match(self, text):
        
        self.skipWS()        
        return self.peek(text)



    
    
    def getAttributes(self):

        attributes = {}
        
        while self.index < self.length:
            attribute = self.getNamespaceIdentifier()
            value = ""
            
            if attribute == "":
                break
            
            self.expect("=")
            self.expect('"')
            
            while self.index < self.length:
                char = self.xml[self.index]
                self.index += 1
                
                if char == '"':
                    break;

                value += char
                

            attributes[attribute] = value

        return attributes


    def getTextBefore(self, stopText):

        text = ''
        index = self.xml.find(stopText, self.index)

        if index >= 0:
            text = self.xml[self.index:index]
            self.index = index
        else:
            text = self.xml[self.index:]
            self.index = len(self.xml)     

        return text


    def parseHeader(self):
        
        yield (self.HEADER, {'attributes':self.getAttributes()})

        self.expect('?>')


    def parseComment(self):
        
        comment = self.getTextBefore('-->')
        self.skipChars(3)

        if comment != '':
            yield (self.COMMENT, {'text':comment})
    
 
    def parseStartTag(self):

        identifier = self.getNamespaceIdentifier()
        
        yield (self.START_TAG, {'name':identifier, 'attributes':self.getAttributes()})

        if self.match('/>'):
            yield (self.END_TAG, {'name':identifier})
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        
        identifier = self.getNamespaceIdentifier()

        yield (self.END_TAG, {'name':identifier})
        self.expect('>')        
        
    
  
        
    def parseContent(self):
        
        self.skipWS()
        
        content = self.getTextBefore('<')
        
        yield (self.CONTENT, {'text':content.strip()})
    
        
    def parseCDATA(self):
        
        data = self.getTextBefore(']]>')
        self.index += 3
                        
        yield (self.CONTENT, {'text':data})
    
    
    def parse(self, xml):
        

        try:
            with open(xml, 'r') as file:
                xml = file.read()
        except:
            pass
     
        self.setXML(xml)

        while True:

            self.skipWS()

            if self.index >= self.length:
                break
                    


            if self.peek('<!--'):
                yield from self.parseComment()

            elif self.peek('<![CDATA['):
                yield from self.parseCDATA()

            elif self.peek('<?xml'):
                yield from self.parseHeader()

            elif self.peek('</'):
                yield from self.parseEndTag()

            elif self.peek('<'):
                yield from self.parseStartTag()
                
            else:
                yield from self.parseContent()
                    
            




###########################################################################################

        
class XMLParser:

    def __init__(self, filter = None, debug = True):
        
        self.filter = filter
        self.debug = debug
    
    

    def print(self, *args):
        if self.debug:
            print(*args)
            
            
    def parse(self, xml):


        import time


        try: 
            from collections import OrderedDict as Dictionary
        except ImportError: 
            try:
                from ordereddict import OrderedDict as Dictionary
            except ImportError:
                try:
                    from ucollections import OrderedDict as Dictionary
                except ImportError:
                    Dictionary = dict

#         try:
#             from xmltokenizer import XMLTokenizer
#         except ImportError:
#             raise Exception('XMLParser needs XMLTokenizer to work.')
#         

        
        def parse(tokens, path = ''):
            
            result = None

            while True:
                try:
                    token, params = next(tokens)
                except StopIteration:
                    return result
                
                if (token == XMLTokenizer.CONTENT):
                    
                    if self.filter == None or path in self.filter:
                        result = params['text']
            
                    
                if (token == XMLTokenizer.START_TAG):
                    tag = params['name']


                    if path == '':
                        xpath = tag
                    else:
                        xpath = path + '.' + tag
                        
                    parsed = parse(tokens, xpath)

                    if result == None:
                        result = Dictionary()

                    if parsed != None:
                        if result.get(tag) == None:
                            result[tag] = parsed

                        elif isinstance(result[tag], list):
                            result[tag].append(parsed)
                                
                        else:
                            result[tag] = [result[tag], parsed]
                        

                if (token == XMLTokenizer.END_TAG):
                    return result



        tokenizer = XMLTokenizer()
        tokens = tokenizer.parse(xml)

        self.print('Parsing XML...')

        startTime = time.ticks_ms()
        result = parse(tokens)
        endTime = time.ticks_ms()
        
        self.print("Parsed XML in {seconds} seconds".format(seconds = (endTime-startTime) / 1000))

        return result





###########################################################################################



#         let feeds = {
#             "BBC": "http://feeds.bbci.co.uk/news/uk/rss.xml#",
#             "CNN": "http://rss.cnn.com/rss/edition.rss",
#             "Google": "https://news.google.com/rss?gl=US&ceid=US:en&hl=en-US",
#             "SDS" :'https://www.sydsvenskan.se/rss.xml?latest',
#             "Di": 'https://digital.di.se/rss',
#             "SvD": 'http://www.svd.se/?service=rss',
#             "Experssen":'https://feeds.expressen.se/nyheter',
#             "Aftonbladet": 'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'
# 
#         };
#         
        
    
class App:
    
    
    def __init__(self, debug = True):
        self.debug = debug
        self.connectToWiFi()
        
        self.cache = {}

        self.feeds = [
#            {'name':'Expressen', 'url':'https://feeds.expressen.se/nyheter'},
#            {'name':'Aftonbladet', 'url':'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'},
#            {'name':'Google', 'url':'https://news.google.com/rss?gl=US&ceid=US:en&hl=en-US'},
#            {'name':'Dagens Industri', 'url':'https://digital.di.se/rss'},
            {'name':'Sydsvenskan', 'url':'https://www.sydsvenskan.se/rss.xml?latest'}
        ]


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
        import gc
        
        gc.collect()
        
        filter = ['rss.channel.item.title', 'rss.channel.item.pubDate']
        
        self.print("Fetching RSS from '{url}'".format(url = url))

        headers = {
            'accept': 'application/text',
            'content-type': 'application/xml'
        }
        
        startTime = time.ticks_ms()
        response = request.get(url, headers = headers)
        endTime = time.ticks_ms() 
        
        self.print("Fetched RSS in {seconds} seconds".format(seconds = (endTime-startTime) / 1000))

        parser = XMLParser(filter = filter, debug = self.debug)
        
        return parser.parse(response.text)  



    def getSortKey(self, date):
            
#		https://www.w3.org/Protocols/rfc822/#z28

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
            


    def getLatestRSS(self, feed):

        def sortKey(value):
            return value['key']


        rss = self.fetchRSS(feed['url'])

        items = rss
        items = items['rss']
        items = items['channel']
        items = items['item']
        

        list = []
        
        for item in items:
            entry = {
                'key': self.getSortKey(item['pubDate']),
                'date':item['pubDate'],
                'title':item['title']
            }

            list.append(entry)

        list.sort(key = sortKey, reverse = True)
        
        return list[0]

            
        
    # "^(.+),\s+(\d+)\s+(.+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(.+)$"gm
    # "^(\S+),\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)$"gm
            
# ^(?:\s*(Sun|Mon|Tue|Wed|Thu|Fri|Sat),\s*)?(0?[1-9]|[1-2][0-9]|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(19[0-9]{2}|[2-9][0-9]{3}|[0-9]{2})\s+(2[0-3]|[0-1][0-9]):([0-5][0-9])(?::(60|[0-5][0-9]))?\s+([-\+][0-9]{2}[0-5][0-9]|(?:UT|GMT|(?:E|C|M|P)(?:ST|DT)|[A-IK-Z]))(\s*\((\\\(|\\\)|(?<=[^\\])\((?<C>)|(?<=[^\\])\)(?<-C>)|[^\(\)]*)*(?(C)(?!))\))*\s*$

# "^(\S+),\s(\d+)\s(\S+)\s(\d+)\s(\d+):(\d+):(\d+)\s+(\S+)$"gm

# https://www.w3.org/Protocols/rfc822/#z28


    def testRSS(self):

        import gc
        
        SDS = 'https://www.sydsvenskan.se/feeds/feed.xml'
        expressen = 'https://feeds.expressen.se/nyheter'
        google = 'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'
        CNN = 'http://rss.cnn.com/rss/edition.rss'
        DI = 'https://digital.di.se/rss'


#        feed = self.feeds[2]
#        entry = self.getLatestRSS(feed)
#        self.print('{name}: {date} - {title}'.format(name = feed['name'], date = entry['date'], title = entry['title']))

    
        for feed in self.feeds:
            gc.collect()
            entry = self.getLatestRSS(feed)
            self.print('{name}: {date} - {title}'.format(name = feed['name'], date = entry['date'], title = entry['title']))

 


    def run(self):
        self.testRSS()



App().run()

#tokenizer = XMLTokenizer()
#tokens = tokenizer.parse('test.xml')

#parser = XMLParser(debug = True)
#tokens = parser.parse(xml = 'test.xml')
#for token in tokens:
#    print(token)