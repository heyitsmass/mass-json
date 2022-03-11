import argparse
import re
from typing import NamedTuple

args = argparse.ArgumentParser(
         description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")

args = vars(args.parse_args())
__FILENAME__ = args['filename']


class ParseError(Exception): 
  def __init__(self, capture, operand): 
    self.capture = capture 
    self.operand = operand

  def __str__(self): 
    return ("Error capturing rule: %s\n\t"
              "Unsupported operand: %s\n\t\t"
                "Supported operands: | (or) + (req.) ? (opt.)" % (self.capture, self.operand)) 


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

          if len(cap) <= 0: 
            raise ParseError(id, tmp[i][-1])

          if cap[0] not in ids:
            cap[0] = '(?P<%s>%s)' % (id, cap[0])
            tmp[i] = cap[0] + cap[1]
            self.__rules[id] = tuple(tmp)
            continue    

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


class DelimiterError(Exception):

  def __init__(self, delim): 
    self.delim = delim 

  def __str__(self): 
    return "Error: Unsupported delimiter '%s'" % self.delim 


class TokenError(Exception): 

  def __init__(self, regex, delim): 
    self.regex = regex 
    self.delim = delim 

  def __str__(self): 
    return 'Error: Missing token value %s' % self.regex 


class Token(NamedTuple): 
  type:str 
  value:str
  line:int 

class RuleError(Exception): 
  def __init__(self, id): 
    self.id = id 

  def __str__(self): 
    return "Error: repeated rules should have a matching definition, raw strings should be avoided %s" % self.id


class Scanner(object): 
  def __init__(self, data, rules): 
    self.__data = data
    self.__rules = _Rules(rules)
    self.__lineno = 0

    #for id in self.__rules: 
      #print(id, ':', self.__rules[id]) 
    self.__ids = [id for id in self.__rules] 
    default = self.__rules[self.__ids[0]] 

    for arg in default: 
      if type(arg) == str:

        tok_regex = arg[:-1]
        delim = arg[-1]
        match = re.match(tok_regex, self.__data) 

        if match: 
          kind = match.group() 
          value = match.lastgroup 

          print(Token(kind, value, self.__lineno)) 

          self.__data = re.sub(tok_regex, '', self.__data, 1) 

        else: 
          raise TokenError(tok_regex, delim) 

      elif type(arg) == tuple: 

        self.__scan(arg) 

    '''
    for r in default: 
        if type(r) == str: 
          delim = r[-1:] 
          rule = r[:-1]
          if delim not in ['|', '?', '+']: 
            raise DelimiterError(delim) 

          if rule not in self.__ids:  # rule is a regex pattern 
            tok_regex = rule 
            match = re.match(tok_regex, self.__data) 

          else:     # rule is some placeholder value 
            
            tok_regex = self.__rules[rule] 
            match = re.match(tok_regex, self.__data) 

            print(tok_regex) 
            ...  

          if match:                 # found a match 
            kind = match.group() 
            value = match.lastgroup 

            print(Token(kind, value, self.__lineno)) 
            self.__data = re.sub(tok_regex, '', self.__data, 1) 

          elif not match:         
            if delim == '+':        # if not match and required, file has a grammatical error 
              raise TokenError(tok_regex, delim) 
            elif delim == '?':      # if not match and not required, skip 
              continue 
            elif delim == '|':      # if not match and or, then if not match is found by the last or, then raise an exception (wip) 
              raise Exception   
            
            print(tok_regex) 

        elif type(r) == tuple: 
          self.__scan(r) 
        #print(r) 
      '''



  def __scan(self, input): 

    i = 0
    while i < len(input): 
      id = input[i][:-1] 
      delim = input[i][-1] 

      if id not in self.__ids: 
        print(id) 
        if type(id) == tuple: 
          self.__scan(id)
          print("HERE 1", tok_regex) 
          return 

          i+=1 
          continue 
        if '?P' in id: 
          tok_regex = id 
      else: 

        tok_regex = self.__rules[id]
        
      if type(tok_regex) == tuple: 
        self.__scan(tok_regex)
        print("HERE 2", tok_regex) 
        if delim == '|': 
          return 

        i+=1   
        continue  
        #return 

      match = re.match(tok_regex, self.__data) 

      if match: 
        value = match.group() 
        kind = match.lastgroup 

        print(Token(kind, value, self.__lineno)) 

        self.__data = re.sub(tok_regex, '', self.__data, 1)

        print(delim)
        if delim == '|': 
          return  

      elif not match: 
        if delim == '?':
          #match = True 
          i+=1 
          continue

        if delim == '|' and i+1 >= len(input): 
          raise TokenError(id, delim)
        elif delim == '|': 
          i+=1 
          continue 

        raise TokenError(id, delim) 

      else: 

        raise Exception 

      if i+1 >= len(input) and match: 
        i=0 
        continue 


      i+=1 
      continue 

  

rules = [
    ('object',
     r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,comma?,whitespace?=:\}+'),
    ('value',
        r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:whitespace?'),
    ('string',
        r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:\]+'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
]

data = open(__FILENAME__, 'r').read()
scanner = Scanner(data, rules) 
