
class Tokens:
    TAG_BEGIN         = 'tag-begin'
    TAG_END           = 'tag-end'
    TAG_ATTRIBUTE     = 'tag-attribute'
    HEADER_BEGIN      = 'header-begin'
    HEADER_END        = 'header-end'
    HEADER_ATTRIBUTE  = 'header-attribute'
    COMMENT           = 'comment'
    CONTENT           = 'content'
    CDATA             = 'cdata'
    


class XMLTokenizer:

    TAG_BEGIN         = 'tag-begin'
    TAG_END           = 'tag-end'
    TAG_ATTRIBUTE     = 'tag-attribute'
    HEADER_BEGIN      = 'header-begin'
    HEADER_END        = 'header-end'
    HEADER_ATTRIBUTE  = 'header-attribute'
    COMMENT           = 'comment'
    CONTENT           = 'content'
    CDATA             = 'cdata'
    

    def __init__(self, xml = ""):

        self.setXML(xml)
        

    def setXML(self, xml = ''):
        self.xml = xml
        self.index = 0
        self.length = len(self.xml)
        
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
    
    
    def parseAttributes(self, name):

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
            
            yield {'token':name, 'attribute':attribute, 'value':value}


    def parseHeader(self):
        
        yield {'token':Tokens.HEADER_BEGIN}
        yield from self.parseAttributes(Tokens.HEADER_ATTRIBUTE)
        yield {'token':Tokens.HEADER_END}

        self.expect('?>')


    def parseComment(self):
        
        comment = ""
        
        while not self.eof():
            if self.peek('-->'):
                break
                          
            comment += self.getChar()
        
        yield {'token':Tokens.COMMENT, 'text':comment}
    
 
    def parseStartTag(self):

        identifier = self.getNamespaceIdentifier()
        
        yield {'token':Tokens.TAG_BEGIN, 'tag':identifier}
        yield from self.parseAttributes(Tokens.TAG_ATTRIBUTE)

        if self.match('/>'):
            yield {'token':Tokens.TAG_END, 'tag':identifier}
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        

        identifier = self.getNamespaceIdentifier()

        yield {'token':Tokens.TAG_END, 'tag':identifier}
        self.expect('>')        
        
        
    def parseContent(self):
        
        self.skipWS()
        
        content = ""
        
        while not self.eof():
            if self.currentChar() == '<':
                break;
            
            content = content + self.getChar()
        
        if (len(content) > 0):
            yield {'token':Tokens.CONTENT, 'text':content.strip()}
    
        
    def parseCDATA(self):
        
        data = ""
        
        while not self.eof():
            if self.peek(']]>'):
                break
                          
            data += self.getChar()
        
        yield {'token':Tokens.CONTENT, 'text':data}
    
    
    def parseXML(self, xml):
     
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
                    
            
            
    def parseFile(self, fileName):
        
        with open(fileName, 'r') as file:
            xml = file.read()

        yield from self.parseXML(xml)


    def parse(self):
        yield from self.parseXML(self.xml)
        


def parseXML(tokens):


    import time

    try:  # pragma no cover
        from collections import OrderedDict
    except ImportError:  # pragma no cover
        try:
            from ordereddict import OrderedDict
        except ImportError:
            try:
                from ucollections import OrderedDict  # micropython
            except ImportError:
                OrderedDict = dict

    def parse(tokens):
        result = OrderedDict()

        while True:
            try:
                token = next(tokens)
            except StopIteration:
                return result
                
            
            if (token['token'] == Tokens.CONTENT):
                result = token['text']
        
                
            if (token['token'] == Tokens.TAG_BEGIN):
                tag = token['tag']


                parsed = parse(tokens)


                if result.get(tag) == None:
                    result[tag] = parsed

                elif isinstance(result[tag], list):
                    result[tag].append(parsed)
                        
                else:
                    result[tag] = [result[tag], parsed]
                    

            if (token['token'] == Tokens.TAG_END):
                return result


    print('Parsing...')
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
    
    import json
    
    tokenizer = XMLTokenizer()
    tokens = tokenizer.parseXML(xml)     

    dict = parseXML(tokens)
    print(json.dumps(dict))

##################################################################

def testHeader():
   
    text = """
        <?xml
        version =   "1.0"    encoding  =
             "UTF-8" kalle:olle = "32"   ?>
    
    """

    tokenizer = XMLTokenizer(text)
    tokenizer.parseHeader()      
   
##################################################################
   


def testStartTag():
   
    xml = """
        <kalle
        version =   "1.0"    encoding  =
             "UTF-8" kalle:olle = "32" >
    """

    xml = """
        <  kalle >
    """

    tokenizer = XMLTokenizer(xml)
    tokenizer.parseStartTag()      
   
##################################################################

def testComment():

    xml = """
        <!-- this
            is a comment

        -->
    """

    tokenizer = XMLTokenizer(xml)
    print("---")
    print(tokenizer.currentChar())
    print("---")
    print(tokenizer.xml)
    print("---")
    tokenizer.parseComment()    
    
##################################################################

def testRSS():

    from secrets import WIFI_SSID, WIFI_PASSWORD, PUSHOVER_TOKEN, PUSHOVER_USER

    import time
    import request
    from wifi import WiFi

    # Koppla upp WiFi hur du vill
    wifi = WiFi()
    wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)



    headers = {
        'accept': 'application/rss+xml'
    }

    SDS = 'https://www.sydsvenskan.se/feeds/feed.xml'
    Expressen = 'https://feeds.expressen.se/nyheter'
    Google = 'https://news.google.com/rss?hl=sv&gl=SE&ceid=SE:sv'
    print("Fetching...")
    response = request.get(Google)

    print("Parsing...")
    tokenizer = XMLTokenizer()
    tokens = tokenizer.parseXML(response.text)

    import json
    
    print("Generating dict...")

    time1 = time.ticks_ms()
    dict = parseXML(tokens)
    time2 = time.ticks_ms()
    
    
    print("Finished in {seconds} seconds".format(seconds = (time2-time1) / 1000))
#    print(json.dumps(dict))


    
##################################################################

def testFile():


    tokenizer = XMLTokenizer()
    tokens = tokenizer.parseFile('expressen.xml')

    xml = parseXML(tokens)
        
testFile()