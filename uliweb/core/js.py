import re
import datetime
import decimal

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

def encode_basestring(s):
    """Return a JSON representation of a Python string

    """
    def replace(match):
        return ESCAPE_DCT[match.group(0)]
    return '"' + ESCAPE.sub(replace, s) + '"'
  
def encode_unicode(s):
    """Return a JSON representation of a Python unicode

    """
    return '"' + s.encode('unicode_escape') + '"'

def simple_value(v):
    from uliweb.i18n.lazystr import LazyString
    
    if callable(v):
        v = v()
    elif isinstance(v, LazyString):
        return str(v)
    else:
        return v

class JSONEncoder(object):
    def __init__(self, encoding='utf-8', unicode=False, default=None):
        self.encoding = encoding
        self.unicode = unicode
        self.default = default
        
    def iterencode(self, obj):
        if self.default:
            x = self.default(obj)
            obj = x or obj
        if isinstance(obj, str):
            if self.unicode:
                yield encode_unicode(unicode(obj, self.encoding))
            else:
                yield encode_basestring(obj)
        elif isinstance(obj, unicode):
            if self.unicode:
                yield encode_unicode(obj)
            else:
                yield encode_basestring(obj.encode(self.encoding))
        elif obj is None:
            yield 'null'
        elif obj is True:
            yield 'true'
        elif obj is False:
            yield 'false'
        elif isinstance(obj, (int, long)):
            yield str(obj)
        elif isinstance(obj, float):
            yield repr(obj)
        elif isinstance(obj, (list, tuple)):
            yield '['
            first = True
            for x in obj:
                if not first:
                    yield ','
                for y in self.iterencode(x):
                    yield y
                first = False
            yield ']'
        elif isinstance(obj, dict):
            yield '{'
            first = True
            for k, v in obj.iteritems():
                if not first:
                    yield ','
                yield encode_basestring(k) + ':'
                for y in self.iterencode(v):
                    yield y
                first = False
            yield '}'
        elif isinstance(obj, decimal.Decimal):
            yield str(obj)
        elif isinstance(obj, datetime.datetime):
            yield '"' + obj.strftime('%Y-%m-%d %H:%M:%S') + '"'
        elif isinstance(obj, datetime.date):
            yield '"' + obj.strftime('%Y-%m-%d') + '"'
        elif isinstance(obj, datetime.time):
            yield '"' + obj.strftime('%H:%M:%S') + '"'
        else:
            raise TypeError(repr(obj) + " can't be serialized to JSON")
        
    def encode(self, obj):
        return ''.join(self.iterencode(obj))
    
def json_dumps(obj, unicode=False, **kwargs):
    return JSONEncoder(unicode=unicode, default=simple_value, **kwargs).encode(obj)
