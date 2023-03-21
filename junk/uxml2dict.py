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
            print('"text"'.format(text = text))
        elif tok[0] == START_TAG:
            print('{')
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
            print('}')
            return iter_tok
        else:
            raise NotImplementedError('Token %s not support' % tok[0])


def parse(iter_tok, lesslist=True):
    parsed = OrderedDict()
    parseitem(iter_tok, parsed, lesslist)
    return parsed


if __name__ == '__main__':
    import json
    import xmltok
    iter_tok = xmltok.tokenize(open('vector-text.svg'))
    parsed = parse(iter_tok)
    try:
        print(json.dumps(parsed, indent=4))
    except TypeError: # json in micropython does not support keyword argument indent
        print(json.dumps(parsed))