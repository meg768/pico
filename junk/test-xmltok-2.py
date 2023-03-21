


TEXT = "TEXT"
START_TAG = "START_TAG"
# START_TAG_DONE = "START_TAG_DONE"
END_TAG = "END_TAG"
PI = "PI"
# PI_DONE = "PI_DONE"
ATTR = "ATTR"
# ATTR_VAL = "ATTR_VAL"


class XMLSyntaxError(Exception):
    pass


class XMLTokenizer:
    def __init__(self, f):
        self.f = f
        self.nextch()

    def curch(self):
        return self.c

    def getch(self):
        c = self.c
        self.nextch()
        return c

    def eof(self):
        return self.c == ""

    def nextch(self):
        self.c = self.f.read(1)
#        if not self.c:
#            raise StopIteration
        return self.c

    def skip_ws(self):
        while self.curch().isspace():
            self.nextch()

    def isident(self):
        self.skip_ws()
        return self.curch().isalpha()

    def getident(self):
        self.skip_ws()
        ident = ""
        while True:
            c = self.curch()
            if not (c.isalpha() or c.isdigit() or c in "_-."):
                break
            ident += self.getch()
        return ident

    def getnsident(self):
        ns = ""
        ident = self.getident()
        if self.curch() == ":":
            self.nextch()
            ns = ident
            ident = self.getident()
        return (ns, ident)

    def match(self, c):
        self.skip_ws()
        if self.curch() == c:
            self.nextch()
            return True
        return False

    def expect(self, c):
        if not self.match(c):
            raise XMLSyntaxError

    def lex_attrs_till(self):
        while self.isident():
            attr = self.getnsident()
            # yield (ATTR, attr)
            self.expect("=")
            self.expect('"')
            val = ""
            while self.curch() != '"':
                val += self.getch()
            # yield (ATTR_VAL, val)
            self.expect('"')
            yield (ATTR, attr, val)

    def tokenize(self):
        while not self.eof():
            if self.match("<"):
                if self.match("/"):
                    yield (END_TAG, self.getnsident())
                    self.expect(">")
                elif self.match("?"):
                    yield (PI, self.getident())
                    yield from self.lex_attrs_till()
                    self.expect("?")
                    self.expect(">")
                elif self.match("!"):
                    self.expect("-")
                    self.expect("-")
                    last3 = ""
                    while True:
                        last3 = last3[-2:] + self.getch()
                        if last3 == "-->":
                            break
                else:
                    tag = self.getnsident()
                    yield (START_TAG, tag)
                    yield from self.lex_attrs_till()
                    if self.match("/"):
                        yield (END_TAG, tag)
                    self.expect(">")
            else:
                text = ""
                while self.curch() != "<":
                    text += self.getch()
                if text:
                    yield (TEXT, text)




def tokenizeXML(file):
    return XMLTokenizer(file).tokenize()






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

TEXT = "TEXT"
START_TAG = "START_TAG"
#START_TAG_DONE = "START_TAG_DONE"
END_TAG = "END_TAG"
PI = "PI"
#PI_DONE = "PI_DONE"
ATTR = "ATTR"
#ATTR_VAL = "ATTR_VAL"


def parseitem(iter_tok, parsed, lesslist):
    while True:
        try:
            tok = next(iter_tok)
        except StopIteration:
            return iter_tok
        if tok[0] == PI:
            pass
        elif tok[0] == ATTR:
            _, (namespace, attr), value = tok
            if namespace:
                attr = namespace + ':' + attr
            parsed['@' + attr] = value
#            print('"{attr}"={value}'.format(attr = attr, value = value))
        elif tok[0] == TEXT:
            _, text = tok
            parsed['#text'] = text
        elif tok[0] == START_TAG:
            _, (namespace, tag) = tok
            if namespace:
                tag = namespace + ':' + tag
            d = OrderedDict()
            iter_tok = parseitem(iter_tok, d, lesslist)
            if not d:
                d = None
            parsed.setdefault(tag, [])
            if lesslist and not isinstance(parsed[tag], list):
                parsed[tag] = [parsed[tag], d]
            else:
                parsed[tag].append(d)
            if lesslist and len(parsed[tag]) == 1:
                parsed[tag] = parsed[tag][0]
        elif tok[0] == END_TAG:
            return iter_tok
        else:
            raise NotImplementedError('Token %s not support' % tok[0])


def parse(iter_tok, lesslist=True):
    parsed = OrderedDict()
    parseitem(iter_tok, parsed, lesslist)
    return parsed





def parseXML(tokens):

    result = OrderedDict()

    while True:
        try:
            token = next(tokens)
        except StopIteration:
            return result
            
        print(token)
        
        if (token[0] == 'TEXT'):
            _, text = token
            result = text
    
            
        if (token[0] == 'START_TAG'):
            _, (namespace, tag) = token

            if namespace:
                tag = namespace + ':' + tag


            parsed = parseXML(tokens)


            if result.get(tag) == None:
                result[tag] = parsed

            elif isinstance(result[tag], list):
                result[tag].append(parsed)
                    
            else:
                result[tag] = [result[tag], parsed]
                

        if (token[0] == 'END_TAG'):
            return result
            
    


import json, ujson
file = open("test.xml")
tokens = tokenizeXML(file)
dict = parseXML(tokens)
print(ujson.dumps(dict))
#parseXML(tokens)



# parsed = parse(tokens)
 
# try:
#     print(json.dumps(parsed, indent=4))
# except TypeError: # json in micropython does not support keyword argument indent
#     print(json.dumps(parsed))