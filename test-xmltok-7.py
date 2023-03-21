

class XMLTokenizer:

    TAG_BEGIN         = 'tag'
    TAG_END           = '/tag'
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
        
        yield (self.TAG_BEGIN, {'name':identifier, 'attributes':self.getAttributes()})

        if self.match('/>'):
            yield (self.TAG_END, {'name':identifier})
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        
        identifier = self.getNamespaceIdentifier()

        yield (self.TAG_END, {'name':identifier})
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
                    
            




        


def parseXML(xml):


    import time
    debug = False

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

    
    def parse(tokens):
        result = Dictionary()

        while True:
            try:
                token, params = next(tokens)
                if debug:
                    print(token, params)
            except StopIteration:
                return result
            
            if (token == XMLTokenizer.CONTENT):
                result = params['text']
        
                
            if (token == XMLTokenizer.TAG_BEGIN):
                tag = params['name']


                parsed = parse(tokens)


                if result.get(tag) == None:
                    result[tag] = parsed

                elif isinstance(result[tag], list):
                    result[tag].append(parsed)
                        
                else:
                    result[tag] = [result[tag], parsed]
                    

            if (token == XMLTokenizer.TAG_END):
                return result




    
    tokenizer = XMLTokenizer()
    tokens = tokenizer.parse(xml)
        
    time1 = time.ticks_ms()
    result = parse(tokens)
    time2 = time.ticks_ms()
    print("Parsed XML in {seconds} seconds".format(seconds = (time2-time1) / 1000))

    return result




    
##################################################################


def testXML():
    
    xml = """
        <!-- A top comment !--->
        <?xml version="1.0" encoding  =   "UTF-8"  ?>
        <rss xmlns:dc = "http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"/>

        <data>
          <![CDATA[Sydsvenskan RSS ÅÄÖ]]>
        </data>
        
        <foo xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
            <kalle>
                foo ÅÄÖ
            </kalle>
            <!-- COMENRT -->
            
            
        </foo>
        
        <!-- This is a comment!! -->
        <html>
            <kalle>
                KALLE
                OLLE     
            </kalle>
            <x:olle a:esdf="33">
                OLLE
            </x:olle>
        </html>
    """
    
    xxml = """
        <?xml version="1.0" encoding="UTF-8"  ?>
        <rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"/>


        <foo xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
            <kalle foo="skdjfh">
                foo
            </kalle>
        </foo>
        <foo xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
            <kalle>
                foo
            </kalle>
        </foo>


    """
    
    xml = "<!--ABCD--><foo/>"
    
    result = parseXML(xml)
    print(result)





def connectToWiFi():

    from secrets import WIFI_SSID, WIFI_PASSWORD
    from wifi import WiFi

    # Koppla upp WiFi hur du vill
    wifi = WiFi()
    wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

    

def fetchRSS(url):


    connectToWiFi()

    import gc
    import time
    import request



    headers = {
        'accept': 'application/rss+xml'
    }

    SDS = 'https://www.sydsvenskan.se/feeds/feed.xml'
    Expressen = 'https://feeds.expressen.se/nyheter'
    Google = 'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'
    print("Fetching...")
    response = request.get(Expressen)

    print("Parsing...")
    parseXML(response.text)

    print("Generating dict...")

    time1 = time.ticks_ms()
    dict = parseXML(tokens)
    time2 = time.ticks_ms()
    
    
    print("Finished in {seconds} seconds".format(seconds = (time2-time1) / 1000))
#    print(json.dumps(dict))




def testRSS():


    import gc
    import time
    import request
    from wifi import WiFi

    connectToWiFi()

    headers = {
        'accept': 'application/rss+xml'
    }

    print("Fetching...")
    response = request.get('https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv')

    print("Parsing...")
    news = parseXML(response.text)

    print("Done!")

def testFile():


    import json
    xml = parseXML('google.xml')
#    print(json.dumps(xml))







        
testFile()
