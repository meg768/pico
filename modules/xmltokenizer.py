

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
                    
            

