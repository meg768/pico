import xmltok
import json
from uxml2dict import parse


def parseTokens(tokens):
    while True:
        try:
            token = next(tokens)
        except StopIteration:
            return tokens

        print(token)



file = open("test.xml")
tokens = xmltok.tokenize(file)
parseTokens(tokens)


# parsed = parse(tokens)
# 
# try:
#     print(json.dumps(parsed, indent=4))
# except TypeError: # json in micropython does not support keyword argument indent
#     print(json.dumps(parsed))