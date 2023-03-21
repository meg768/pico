

class XMLTokens:

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
        
        yield {'token':HEADER_BEGIN}
        yield from self.parseAttributes(HEADER_ATTRIBUTE)
        yield {'token':HEADER_END}

        self.expect('?>')


    def parseComment(self):
        
        comment = ""
        
        while not self.eof():
            if self.peek('-->'):
                break
                          
            comment += self.getChar()
        
        yield {'token':COMMENT, 'text':comment}
    
 
    def parseStartTag(self):

        identifier = self.getNamespaceIdentifier()
        
        yield {'token':TAG_BEGIN, 'tag':identifier}
        yield from self.parseAttributes(TAG_ATTRIBUTE)

        if self.match('/>'):
            yield {'token':TAG_END, 'tag':identifier}
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        

        identifier = self.getNamespaceIdentifier()

        yield {'token':TAG_END, 'tag':identifier}
        self.expect('>')        
        
        
    def parseContent(self):
        
        self.skipWS()
        
        content = ""
        
        while not self.eof():
            if self.currentChar() == '<':
                break;
            
            content = content + self.getChar()
        
        if (len(content) > 0):
            yield {'token':CONTENT, 'text':content.strip()}
    
        
    def parseCDATA(self):
        
        data = ""
        
        while not self.eof():
            if self.peek(']]>'):
                break
                          
            data += self.getChar()
        
        yield {'token':CONTENT, 'text':data}
    
    
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
        

