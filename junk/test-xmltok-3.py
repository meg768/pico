
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
    
    def __init__(self, xml = ""):

        self.setXML(xml)
        

    def setXML(self, xml = ''):
        self.xml = xml
        self.index = 0
        self.length = len(self.xml)
        self.tokens = []
        
    def parseError(self, message):
        raise Exception(message)
            

    def addToken(self, value):
        print(value)
        self.tokens.append(value)
        
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
            self.parseError('Invalid namespace')
                        
        return namespace + ':' + identifier


    def expect(self, text):
        if not self.match(text):
            raise Exception("Expected '{text}'".format(text = text))
      
      
    def peek(self, text, skip = False):
        peek = self.xml[self.index:self.index+len(text)]

        if peek == text:
            if skip:
                self.skipChars(len(text))
                
            return True
        
        return False
        
        
    def match(self, text):
        
        self.skipWS()
        
        if self.peek(text, True):
            return True
        
        return False


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
            
            self.addToken((name, attribute, value))


    def parseHeader(self):
        
        
        self.expect('<?xml')

        self.addToken((Tokens.HEADER_BEGIN, '', ''))

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
            
            self.addToken((Tokens.HEADER_ATTRIBUTE, attribute, value))

        self.expect('?>')
        self.addToken((Tokens.HEADER_END, '', ''))


    def parseComment(self):
        
        self.expect('<!--')
        
        comment = ""
        
        while not self.eof():
            if self.peek('-->', skip = True):
                break
                          
            comment += self.getChar()
        
        if len(comment) > 0:
            self.addToken((Tokens.COMMENT, comment, ''))
    
            

    def parseStartTag(self):
        self.expect('<')
        identifier = self.getNamespaceIdentifier()
        
        if len(identifier) == 0:
            self.parseError('Tag name expected')
                
        self.addToken((Tokens.TAG_BEGIN, identifier, ''))

        self.parseAttributes(Tokens.TAG_ATTRIBUTE)

        if self.match('/>'):
            self.addToken((Tokens.TAG_END, identifier, ''))
        else:
            self.expect('>')
        
        
    def parseEndTag(self):
        
        self.expect('</')
        identifier = self.getNamespaceIdentifier()
        self.expect('>')
        
        self.addToken((Tokens.TAG_END, identifier, ''))
        
        
    def parseContent(self):
        
        self.skipWS()
        
        content = ""
        
        while not self.eof():
            if self.currentChar() == '<':
                break;
            
            content = content + self.getChar()
        
        if (len(content) > 0):
            self.addToken((Tokens.CONTENT, content.strip(), ''))
    
    def parseXML(self, xml):
     
        self.setXML(xml)

        while True:

            self.skipWS()

            if self.eof():
                break

            if self.peek('<!--'):
                self.parseComment()

            elif self.peek('<?xml'):
                self.parseHeader()

            elif self.peek('</'):
                self.parseEndTag()

            elif self.peek('<'):
                self.parseStartTag()
                
            else:
                self.parseContent()
                    
        return self.tokens
            
            
    def parseFile(self, fileName):
        
        with open(fileName, 'r') as file:
            xml = file.read()

        self.parseXML(xml)


    def parse(self):
        return self.parseXML(self.xml)
        

##################################################################


def testXML():
    
    xml = """
        <!-- A top comment !--->
        <?xml version="1.0" encoding  =   "UTF-8"  ?>
        <rss xmlns:dc = "http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"/>


        <foo xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
            <kalle>
                foo
            </kalle>
            <!-- COMENRT -->
            olle
            pelle
            
            
        </foo>
        
        <!-- This is a comment!! -->
        <html>
            <kalle>
                KALLE
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
    
    
    
    tokenizer = XMLTokenizer()
    tokenizer.parseXML(xml)     


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
    
#tokenizer = XMLTokenizer(comment)
#tokenizer.parseComment()
#print(tokenizer.peek('<?xml'))
testXML()