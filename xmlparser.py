
        
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

        try:
            from xmltokenizer import XMLTokenizer
        except ImportError:
            raise Exception('XMLParser needs XMLTokenizer to work.')
        

        
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


