
import re 
import argparse
from typing import NamedTuple 


args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args = vars(args.parse_args())
__FILENAME__ = args['filename'] 

class Rules(object): 
  def __init__(self, rules, *args): 
    self.rules = dict() 
    _WS = 'ws' in args 
    delims = ['+', '!', '?', '*', '|'] 

    for id, rule in rules: 
      if '(:' in rule: 
        rule = re.split(r'\(:|:\)([|?|+*])', rule) 
        rule = self.__remove(self.__remove(rule, ''), None) 

        for i, arg in enumerate(rule): 
          if arg not in delims: 
            arg = re.split(r'([+|!*?])', arg) 
            arg = self.__remove(arg, '') 

            if len(arg) == 2: 
              rule[i] = '(?P<%s>%s)%s' % (id, arg[0], arg[1]) 
            else: 
              if arg[len(arg)-1] not in delims: 
                arg.append(arg[len(arg)-2]) 
              for j, sub in enumerate(arg): 
                arg[j] = sub+arg[j+1] 
                arg.remove(arg[j+1]) 
              arg.append(rule[i+1]) 
              rule.remove(rule[i+1]) 
              rule[i] = tuple(arg) 
        if _WS: 
          rule.insert(0, 'whitespace?') 
          rule.append('whitespace?') 
        self.rules[id] = tuple(rule) if len(rule) > 1 else rule[0] 
      else: 
        self.rules[id] = '(?P<%s>%s)' % (id, rule) 
  
  def __remove(self, rule:list, delim): 
    if delim in rule: 
      while delim in rule: 
        rule.remove(delim) 
    return rule 

  def __iter__(self): 
    return iter(self.rules) 

  def __getitem__(self, key): 
    return self.rules[key] 

  def __setitem__(self, key, value): 
    self.rules[key] = value 
  
  def keys(self): 
    return self.rules.keys() 
  
  def values(self): 
    return self.rules.values() 
  
  def items(self): 
    return self.rules.items() 
  

class Token(NamedTuple): 
  type:str 
  value:str
  line:int 
  column:int
  numchars:int

class MissingTokenError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "\n\tError, missing token: '%s'" % self.rule 


class Info(Exception): 
  def __init__(self, locals): 

    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str


class InputScanner(object): 
  def __init__(self, data, rules): 
    self.rules = Rules(rules) 
    self.data = data 
    self.tokens = list()
    self.lineno = 0
    self.col = 0
    self.numchars = 0

    self.ids = [key for key in self.rules] 

    self.__scan(self.rules[self.ids[0]]) 

    for token in self.tokens: 
      print(token) 


  def __scan(self, input, delim=None, _delim=None, _match=None, p_delim=None):
    if type(input) == tuple: 
      p_delim = delim 
      for index, arg in enumerate(input): 
        _delim = delim 
        next = input[index+1] if index+1 < len(input) else None 
        length = len(input) 
        rule = arg[:-1] 
        delim = arg[-1] 

        match = self.__scan(rule, delim) 

        if match: 
          _match = match 
          kind = match.lastgroup 
          value = match.group()  
          
          if delim == '|' and input[len(input)-1] == '*' or delim == '!' and _delim == '*':
            #raise Exception  
            return match 
          
          if delim == '*': 
            continue 

          if kind == 'whitespace' and '\n' in value: 
            self.lineno += 1
            self.col = 0          

          print(Token(kind, value, self.lineno, self.col, self.numchars)) #, delim, _delim, p_delim, next)
          #self.tokens.append(Token(kind, value, self.lineno, self.col))

          self.col += match.span()[1]
          self.numchars += match.span()[1]

          if '\\' in value: 
            value = value.replace('\\', '\\\\')

          if value == '[': 
            value = '\\'+value 

          if kind in self.ids and kind not in ['json', 'object', 'array', 'value']: 
            value = self.rules[kind]  


          self.data = re.sub(value, '', self.data, 1) 


          if delim in ['!', '?'] and next: 
            continue

          if not next: 
            return self.__scan(input, _delim) 

          if delim == '|': 
            #raise Exception 
            return match

          raise Info(locals())
        else: 

          if delim in ['?', '|'] and next or _match and delim == '*':
            continue 

          if delim == '?':
            return _match 

          if delim == '!' and _delim == '|' or delim == '*' and _delim == '|': 
            return 

          if delim == '!' and p_delim == '*': 
            if not _match: 
              return 
            raise Info(locals()) 
          
          raise Info(locals())
      
    
    else: 
      if '?P' in input: 
        tok_regex = input 
      elif input in self.ids: 
        tok_regex = self.rules[input] 
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, delim) 
      else: 
        return 
    
    return re.match(tok_regex, self.data) 

   
rule_set = [ 
  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:whitespace?string!whitespace?colon!whitespace?value!whitespace?comma?:)*\}!'), 
  ('array', r'\[!(:whitespace?value!whitespace?comma?:)*\]!'), 
  ('value', r'(:string|number|object|array|boolean|NULL:)*'), 
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('NULL', r'null'),
  ('colon', r':'),
  ('comma', r','),
  ('mismatch', r'.')
]



scanner = InputScanner(open(__FILENAME__).read(), rule_set)
