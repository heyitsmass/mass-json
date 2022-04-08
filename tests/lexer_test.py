import re 
from typing import NamedTuple, Union 
import argparse


args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args = vars(args.parse_args())
__FILENAME__ = args['filename'] 


class RuleScanner(object): 
  def __init__(self, rules): 

    self.__ids = [rule[0] for rule in rules]
    self.__rules = dict() 

    delims = ['!', '|', '+', '?', '*']

    for id, rule in rules: 
      if '(:' in rule: 
        rule = self.__remove(re.split(r'\(:|:\)([!?|+*])', rule), ('', None))

        for i, arg in enumerate(rule): 
          rule[i] = self.__remove(re.split(r'([!?|+*])', arg), '')

          if i+1 < len(rule): 
            if rule[i+1] in delims: 
              for j, r in enumerate(rule[i]): 
                if j+1 < len(rule[i]):
                  rule[i][j] = r + rule[i][j+1]
                  rule[i].remove(rule[i][j+1]) 
                else: 
                  if rule[i][j-1][-1] == '|': 
                    rule[i][j] = r + rule[i][j-1][-1]
                  else: 
                    raise Exception("Missing Delimiter") 
              rule[i].append(rule[i+1]) 
              rule.remove(rule[i+1])
              rule[i] = tuple(rule[i])
              continue 
          rule[i] ='(?P<%s>%s)%s' % (id, rule[i][0], rule[i][1])   
        if len(rule) <= 1: 
          self.__rules[id] = rule[0] 
        else: 
          self.__rules[id] = tuple(rule) 
      else: 
        self.__rules[id] = '(?P<%s>%s)' % (id, rule)

  def __remove(self, rule:list, delims:Union[str, tuple, list]): 
    if type(delims) == str: 
      while delims in rule: 
        rule.remove(delims) 
    elif type(delims) in [tuple, list]: 
      for arg in delims: 
        while arg in rule: 
          rule.remove(arg) 
    return rule 

  def __iter__(self): 
    return iter(self.__rules) 

  def __getitem__(self, key): 
    return self.__rules[key] 

  def __setitem__(self, key, value): 
    self.__rules[key] = value 
  
  def keys(self): 
    return self.__rules.keys() 
  
  def values(self): 
    return self.__rules.values() 
  
  def items(self): 
    return self.__rules.items() 


class Info(Exception): 
  def __init__(self, locals): 

    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str


class Token(NamedTuple): 
  type:str 
  value:str
  line:int 
  column:int
  numchars:int


class InputScanner(object): 
  def __init__(self, data, rules): 
    self.rules = RuleScanner(rules) 
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
          
          if delim == '|' and input[len(input)-1] == '*':
            #raise Exception  
            return match 
          
          if delim == '*': 
            continue 

          if delim == '!' and _delim == '*': 
            
            return match 

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


          if delim == '!' and next: 
            continue

          if delim == '?' and next: 
            continue 

          if not next: 
            return self.__scan(input, _delim) 

          if delim == '|': 
            #raise Exception 
            return match

          raise Info(locals())
        else: 

          if delim == '?' and next:
            continue 

          if delim == '|' and next: 
            continue 

          if delim == '?':
            return _match 

          if delim == '!' and _delim == '|': 
            return 

          if delim == '!' and p_delim == '*': 
            if not _match: 
              return 
            raise Info(locals()) 
          
          if _match and delim == '*': 
            continue 

          
          if delim == '*' and _delim == '|': 
            return 
        
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


if __name__ == '__main__': 
  rule_set = [ 

    ('json', r'(:object|array:)+'), 
    ('object', r'\{!(:whitespace?pair!comma?:)*\}!'), 
    ('value', r'(:string|number|object|array|boolean|Null:)?'), 
    ('array', r'\[!(:whitespace?value!comma?:)*\]!'),
    ('pair', r'(:whitespace?string!whitespace?colon!whitespace?value!whitespace?comma?:)?'),
    ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')  
  ]

  scanner = InputScanner(open(__FILENAME__, 'r').read(), rule_set) 

