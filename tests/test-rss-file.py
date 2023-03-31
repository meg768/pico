#from xmltokenizer import XMLTokenizer
#from xmlparser import XMLParser


###########################################################################################



class XMLParser:

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
        
        print('ERROR', self.xml[self.index:self.index+10])
        raise Exception(message)
            
  

    
    def skipWS(self):
        
        while self.index < self.length:
            if not self.xml[self.index].isspace():
                return
            
            self.index += 1


    def skipChars(self, chars):
        self.index += chars


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

        if False:
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

    def skipTextBefore(self, stopText):

        index = self.xml.find(stopText, self.index)

        if index >= 0:
            self.index = index
        else:
            self.index = len(self.xml)     





 
    def parseTag(self, path):

        print('******', self.xml[self.index:])
        
        self.expect('<')
        
        content = None
        tag = self.getNamespaceIdentifier()
        attributes = self.getAttributes()

        if tag == '':
            self.raiseError('Tag name expected.')

        self.expect('>')

        if not self.match('/>'):
            
            if path == '':
                xpath = path
            else:
                xpath = path + '.' + tag
                
            parsed = self.parse(xpath)
                
            if parsed != None:
                content = {tag:parsed}


        else:
            self.raiseError ('Syntax error.')
        
        return content
    

    
    def parse(self, path = ''):
        
        content = None
        
        while self.index < self.length:
            
            print('***', self.xml[self.index:], '***')
            
            parsed = None
            
            if self.match('<'):
                tag = self.getNamespaceIdentifier()
                        
                if tag == '':
                    self.raiseError('Tag name expected.')                
                
                self.expect('>')

                if path == '':
                    xpath = path
                else:
                    xpath = path + '.' + tag
                    
                parsed = self.parse(xpath)
                    
                if parsed != None:
                    parsed = {tag:parsed}
                    
                self.getNamespaceIdentifier()
                self.expect('</')
                
                if tag != self.getNamespaceIdentifier():
                    self.raiseError('End tag not  matching')
                    
                self.expect('>') 

            else:
                parsed = self.getTextBefore('<')

            if parsed != None:
                if content == None:
                    content = parsed

                elif isinstance(content, list):
                     content.append(parsed)
                     
                else:
                    content = [content, parsed]


        return content
            


        
    def parseXML(self, xml):
        
        self.setXML(xml)
        
        if self.match('<?xml'):
            attributes = self.getAttributes()
            self.expect('?>')
                      
        return self.parse()



    
class App:
    
    
    def __init__(self, debug = True):
        self.debug = debug
        #self.connectToWiFi()
        
    def print(self, *args):
        if self.debug:
            print(*args)
    
    
    def connectToWiFi(self):

        from secrets import WIFI_SSID, WIFI_PASSWORD
        from wifi import WiFi

        wifi = WiFi(debug = self.debug)
        wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)

        



    def readFile(self, fileName):
        
        content = ''

        with open(fileName, 'r') as file:
            content = file.read()
            file.close()
        
 
        return content

    def run(self):
        
        a1 = """<hej>FOO!</hej>"""


        a2 = """
            ÅÄÖlksdjlkdfj
        """

        a3 = """
            <kalle> 
                <  nisse>
                    NISSE3
                </nisse  >
            </kalle >
        """
        
        
        parser = XMLParser()

        a4 = '<   kalle   a = "55">  < nisse  >   NISSE3   </nisse>    </kalle>'
        import json
        filter = ['rss.channel.item.title']
        xml = self.readFile('test.txt')
        xml = '<olle>1</olle>'

        xml = xml
        parser.setXML(xml)        
#        print('CONTENT', parser.parseXML('<hej>KALLE</hej>'))
        print(json.dumps(parser.parseXML(xml)))



App().run()
