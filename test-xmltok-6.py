
class Tokens:
    TAG_BEGIN         = '<tag>'
    TAG_END           = '</tag>'
    XML_HEADER        = '<?xml?>'
    COMMENT           = 'comment'
    CONTENT           = 'content'
    


class XMLTokenizer:



    def __init__(self, xml = ""):

        self.setXML(xml)
        

    def setXML(self, xml = ''):
        self.xml = xml
        self.index = 0
        self.length = len(self.xml)
        self.optimize = True
        
    def raiseError(self, message):
        raise Exception(message)
            

        
    def eof(self):
        return self.index >= self.length
    
    def skipWS(self):
        while self.currentChar().isspace():
            self.nextChar()
        
    def nextChar(self):
        char = ''
        
        if self.index < self.length:
            char = self.xml[self.index]
            self.index += 1
            
        return char

    def currentChar(self):
        if self.eof():
            return ''
        else:
            return self.xml[self.index]
        
    def getChar(self):
        char = self.currentChar()
        self.nextChar()
        return char


    def getIdentifier(self):

        identifier = ""
        
        self.skipWS()
        
        while True:
            char = self.currentChar()
            
            if not (char.isalpha() or char.isdigit() or char in "_-."):
                break
            
            identifier += self.getChar()
            
        return identifier

    def getNamespaceIdentifier(self):

        namespace = self.getIdentifier()

        if self.currentChar() != ':':
            return namespace

        self.nextChar()
        identifier = self.getIdentifier()
        
        if len(identifier) == 0:
            self.raiseError('Invalid namespace')
                        
        return namespace + ':' + identifier


    def expect(self, text):
        if not self.match(text):
            raise Exception("Expected '{text}'".format(text = text))
      
      
    def peek(self, text):

        if self.optimize:
            if self.xml[self.index] != text[0]:
                return False
        
        peek = self.xml[self.index:self.index+len(text)]

        if peek == text:
            self.skipChars(len(text))    
            return True
        
        return False
        
        
    def match(self, text):
        
        self.skipWS()        
        return self.peek(text)


    def skipChars(self, number):
        self.index += number
    
    
    def getAttributes(self):

        attributes = {}
        
        while not self.eof():
            attribute = self.getNamespaceIdentifier()
            value = ""
            
            if attribute == "":
                break
            
            self.expect("=")
            self.expect('"')
            
            while self.currentChar() != '"':
                value += self.getChar()
                
            self.expect('"')
            
            attributes[attribute] = value

        return attributes


    def getText(self, stopText):

        text = ''
        index = self.xml.find(stopText, self.index)

        if index >= 0:
            text = self.xml[self.index:self.index+index]
            self.index = index + len(stopText)
        else:
            text = self.xml[self.index:]
            self.index = len(self.xml)     

        return text


    def parseHeader(self):
        
        yield (Tokens.XML_HEADER, {'attributes':self.getAttributes()})

        self.expect('?>')


    def parseComment(self):
        

        comment = ''
        
        if self.optimize:
            comment = self.getText('-->')        
        else:
            while not self.eof():
                if self.currentChar() == '<':
                    break;
                
                comment = comment + self.getChar()        
        
        
        if comment != '':
            yield (Tokens.COMMENT, {'text':comment})
    
 
    def parseStartTag(self):

        identifier = self.getNamespaceIdentifier()
        
        yield (Tokens.TAG_BEGIN, {'name':identifier, 'attributes':self.getAttributes()})

        if self.match('/>'):
            yield (Tokens.TAG_END, {'name':identifier})
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        

        identifier = self.getNamespaceIdentifier()

        yield (Tokens.TAG_END, {'name':identifier})
        self.expect('>')        
        
    
  
        
    def parseContent(self):
        
        self.skipWS()

        content = ""
        
        if self.optimize:
            index = self.xml.find('<', self.index)

            if index >= 0:
                content = self.xml[self.index:self.index+index]
                self.index = index + 1
            else:
                content = self.xml[self.index:]
                self.index = len(self.xml)
                
        else:
            while not self.eof():
                if self.currentChar() == '<':
                    break;
                
                content = content + self.getChar()
        
        if (len(content) > 0):
            yield (Tokens.CONTENT, {'text':content.strip()})
    
        
    def parseCDATA(self):
        
        data = ""
        
        while not self.eof():
            if self.peek(']]>'):
                break
                          
            data += self.getChar()
        
        yield (Tokens.CONTENT, {'text':data})
    
    
    def parse(self, xml):
        

        try:
            with open(xml, 'r') as file:
                xml = file.read()
        except:
            pass
     
        self.setXML(xml)

        while True:

            self.skipWS()

            if self.eof():
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
            except StopIteration:
                return result
            
            if (token == Tokens.CONTENT):
                result = params['text']
        
                
            if (token == Tokens.TAG_BEGIN):
                tag = params['name']


                parsed = parse(tokens)


                if result.get(tag) == None:
                    result[tag] = parsed

                elif isinstance(result[tag], list):
                    result[tag].append(parsed)
                        
                else:
                    result[tag] = [result[tag], parsed]
                    

            if (token == Tokens.TAG_END):
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
    xml = parseXML('test.xml')
    print(json.dumps(xml))







        
testFile()