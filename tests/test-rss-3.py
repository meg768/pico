

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

class XMLParser:


    def __init__(self, debug = True):



        self.filter = None
        self.debug = debug
        self.setXML('')
        self.setFilter(None)
        

    def setXML(self, xml = ''):
        self.xml = xml
        self.index = 0
        self.length = len(self.xml)

    def setFilter(self, filter):
        self.filter = filter

    

    def print(self, *args):
        if self.debug:
            print(*args)
            
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
            self.raiseError("Expected '{text}'. Got '{xml}'...".format(text = text, xml = self.xml[self.index:self.index+5]))
      
   
      
    def peek(self, text):

        if True:
            # This is faster
            length = len(text)

            for index in range(length):
                if self.index+index >= self.length:
                    return False
                
                if self.xml[self.index+index] != text[index]:
                    return False
                
            self.index += length
            return True

        else:
            
            peek = self.xml[self.index:self.index+len(text)]

            if peek == text:
                self.index += len(text)  
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


    def getTextBefore(self, stopText, ignoreChars = False):

        text = None
        index = self.xml.find(stopText, self.index)

        if index >= 0:
            if not ignoreChars:
                text = self.xml[self.index:index]
            self.index = index
        else:
            if not ignoreChars:
                text = self.xml[self.index:]
            self.index = len(self.xml)     

        return text

  


    def parseHeader(self, path):
        
        attributes = self.getAttributes()
        self.expect('?>')
        
        return attributes


    def parseComment(self, path):
        
        self.skipTextBefore('-->')
    
 

    def isValidPath(self, path):
        
        if self.filter == None:
            return True
        
        if path in self.filter:
            return True
        
        return False
    
        
    def parseContent(self, path):
        
        return self.getTextBefore('<', not self.isValidPath(path))
    
    
         
    def parseCDATA(self, path):
        
        data = self.getTextBefore(']]>', not self.isValidPath(path))
        self.index += 3
        
        return data;
    
    
        
        
    def parse(self, path = ''):
        

        xml = None


        def setContent(content):
            nonlocal xml
            
            if content != None and content != '':
                if xml == None:
                    xml = content
                    
                elif isinstance(xml, list):
                    xml.append(content)
                    
                else:
                    xml = [xml, content]
                
        def setTagContent(tag, content):
            nonlocal xml

            if content != None:
                if xml == None:
                    xml = Dictionary()

                if xml.get(tag) == None:
                    xml[tag] = content

                elif isinstance(xml[tag], list):
                    xml[tag].append(content)
                        
                else:
                    xml[tag] = [xml[tag], content]            
  
  
        while self.index < self.length:
            self.skipWS()


            if self.peek('<!--'):
                self.parseComment(path)

            elif self.peek('<![CDATA['):
                setContent(self.parseCDATA(path))

            elif self.peek('<?xml'):
                self.parseHeader(path)

            elif self.peek('</'):
                self.getNamespaceIdentifier()
                self.expect('>')        
                break

            elif self.peek('<'):
                tag = self.getNamespaceIdentifier()
                attributes = self.getAttributes()        
                content = None
                
                if path == '':
                    xpath = tag
                else:
                    xpath = path + '.' + tag

                
                if self.match('>'):
                    content = self.parse(xpath)

                elif self.match('/>'):
                    content = None
                    
                else:
                    self.raiseError('Syntax error. Expected end of tag.')
                
                setTagContent(tag, content)
                        
                
            else:
                setContent(self.parseContent(path))
                
            
                
        return xml
                    


    def parseXML(self, xml, filter = None):
        
        import time

        self.setXML(xml)
        self.setFilter(filter)

        startTime = time.ticks_ms()
        content = self.parse()
        endTime = time.ticks_ms()
        
        self.print("Parsed XML in {seconds} seconds".format(seconds = (endTime-startTime) / 1000))
        
        return content
                

 



        
    
class App:
    
    
    def __init__(self, debug = True):
        self.debug = debug
        self.connectToWiFi()
        
        self.cache = {}

        self.feeds = [
            #{'name':'Dagens Industri', 'url':'https://digital.di.se/rss'},
            {'name':'Expressen', 'url':'https://feeds.expressen.se/nyheter'},
            {'name':'Aftonbladet', 'url':'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt'},
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
            'accept': 'application/xml',
            'content-type': 'application/xml'
        }
        
        startTime = time.ticks_ms()
        response = request.get(url, headers = headers)
        xml = response.text
        endTime = time.ticks_ms() 
        
        self.print("Fetched RSS in {seconds} seconds.".format(seconds = (endTime-startTime) / 1000))

        print(len(xml))

        parser = XMLParser(debug = self.debug)
        
        
        return parser.parseXML(xml = xml, filter = filter)



    def getSortKey(self, date):
            
        #		https://www.w3.org/Protocols/rfc822/#z28
            
        # "^(.+),\s+(\d+)\s+(.+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(.+)$"gm
        # "^(\S+),\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\S+)$"gm
                
        # ^(?:\s*(Sun|Mon|Tue|Wed|Thu|Fri|Sat),\s*)?(0?[1-9]|[1-2][0-9]|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(19[0-9]{2}|[2-9][0-9]{3}|[0-9]{2})\s+(2[0-3]|[0-1][0-9]):([0-5][0-9])(?::(60|[0-5][0-9]))?\s+([-\+][0-9]{2}[0-5][0-9]|(?:UT|GMT|(?:E|C|M|P)(?:ST|DT)|[A-IK-Z]))(\s*\((\\\(|\\\)|(?<=[^\\])\((?<C>)|(?<=[^\\])\)(?<-C>)|[^\(\)]*)*(?(C)(?!))\))*\s*$

        # "^(\S+),\s(\d+)\s(\S+)\s(\d+)\s(\d+):(\d+):(\d+)\s+(\S+)$"gm

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

            



    def readFile(self, fileName):
        
        content = ''

        with open(fileName, 'r') as file:
            content = file.read()
            file.close()
        
 
        return content
        
        
    def run(self):
        

        import json

        parser = XMLParser()
        filter = ['rss.channel.item.title', 'rss.channel.item.pubDate', 'rss.channel.title']
        #filter = None
        xml = self.readFile('google.xml')
        parsed = parser.parseXML(xml, filter)
        print(json.dumps(parsed))
        print('Done')
        
        
    def runx(self):

        import gc
        
    
        for feed in self.feeds:
            gc.collect()
            entry = self.getLatestRSS(feed)
            self.print('{name}: {date} - {title}'.format(name = feed['name'], date = entry['date'], title = entry['title']))

 






App().run()

#tokenizer = XMLTokenizer()
#tokens = tokenizer.parse('test.xml')

#parser = XMLParser(debug = True)
#tokens = parser.parse(xml = 'test.xml')
#for token in tokens:
#    print(token)
