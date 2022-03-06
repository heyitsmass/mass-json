import argparse
import re

args = argparse.ArgumentParser(
         description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")

args = vars(args.parse_args())
__FILENAME__ = args['filename']


class _Rules(object):
  def __init__(self, rules: list) -> None:
    self.__rules = dict()

    for id, rule in rules:
      tmp = re.split(r'(:=|=:)', rule)
      ids = [id for id, rule in rules]
      if type(tmp) == list and len(tmp) > 1:
        for i, cap in enumerate(tmp, 0):
          if cap == ':=' and i+1 < len(tmp):
            tmp[i+1] = tuple(tmp[i+1].split(','))
            delims = [':=', '=:']
            [tmp.remove(e) for e in delims]
            continue
          cap = re.split(r'([|+?])', cap)[:-1]
          if cap[0] not in ids:
            cap[0] = '(?P<%s>%s)' % (id, cap[0])
            tmp[i] = cap[0] + cap[1]
            self.__rules[id] = tuple(tmp)
      else: 
        self.__rules[id] = '(?P<%s>%s)' % (id, rule)

  def __iter__(self):
    return iter(self.__rules)

  def __getitem__(self, key: any) -> any:
    return self.__rules[key]

  def __setitem__(self, key: any, value: any) -> any:
    self.__rules[key] = value

  def keys(self):
    return self.__rules.keys()

  def values(self):
    return self.__rules.values()

  def items(self):
    return self.__rules.items()


class Scanner(object): 
  def __init__(self, data, rules): 
    self.__data = data
    self.__rules = _Rules(rules) 

    for id in self.__rules: 
      print(id, ':', self.__rules[id]) 




rules = [
    ('object',
     r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,comma?,whitespace?=:\}+'),
    ('value',
        r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:whitespace?'),
    ('string',
        r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:\]+'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
]

data = open(__FILENAME__, 'r').read()
scanner = Scanner(data, rules) 
