



class XML2JSON:
    def __init__(self, f):
        print("init")
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

    def parse(self):
        print("parsing")
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




file = open("test.xml")
parser = XML2JSON(file)
print("parsing")
parser.parse()

