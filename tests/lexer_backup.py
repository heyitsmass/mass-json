import re

'''
  <expression_a> | 
    => <expression_a> is optional but atleast one is required 

  <expression_a> + 
    => <expression_a> is required 
  
  <expression_a> ? 
    => <expression_a> is not necessary 

  :=<expression_list>=:<delimiter> 
    => <expression_1><delimiter>,<expression_2><delimiter>,...,<expression_n><delimiter>
'''

class Rules(object):
  def __init__(self, rules): 
    self.rules = dict() 

    for id, rule in rules: 
      args = re.split(r'(:=|=:[+!?|])', rule)
      ids = [id for id, rule in rules] 

      if '' in args: 
        while '' in args: 
          args.remove('') 
      
      if len(args) > 1: 
        for i, arg in enumerate(args):
          if arg == ':=': 
            if i+1 > len(args): 
              raise Exception 

            args[i+1] = re.split('\,', args[i+1]) 

            args.remove(args[i])

            args[i].append(args[i+1][-1])

            args.remove(args[i+1]) 

            if len(args) <= 1: 
              args = tuple(args[i]) 
            else: 
              args[i] = tuple(args[i]) 
            
          elif arg[:-1] not in ids: 
            args[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1])
        
        self.rules[id] = tuple(args) 
      else: 
        self.rules[id] = '(?P<%s>%s)' % (id, rule) 

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


class TempError(Exception): 
  def __init__(self, input, rule, match, delim, tok_regex=None, parent_delim = None): 
    self.input = str(input) 
    self.rule = str(rule) 
    self.tok_regex = str(tok_regex)
    self.match = str(match)
    self.delim = str(delim) 
    self.parent_delim = str(parent_delim) 

  def __str__(self): 
    return (("\n\tinput=%s\n\trule=%s\n\ttok_regex=%s\n\tmatch=%s\n\tdelim=%s\n\tparent_delim=%s") % 
            (self.input, self.rule, self.tok_regex, self.match, self.delim, self.parent_delim))

from typing import NamedTuple

class Token(NamedTuple): 
  type:str 
  value:str 

class Scanner(object): 
  def __init__(self, data, rules): 
    self.rules = Rules(rules) 
    self.data = data 
    self.ids = [id for id in self.rules]

    self.default = self.rules[self.ids[0]][:-1]
    self.delim = self.rules[self.ids[0]][-1]

    self.tokens=list() 

    self.__scan(self.default, self.delim) 



  def __scan(self, input, parent_delim=None): 

    i = 0
    while i < len(input): 
      
      rule = input[i][:-1] 
      delim = input[i][-1] 

      if rule in self.ids: 
        #print(rule, delim) 
        tok_regex = self.rules[rule] 

        if type(tok_regex) == tuple:
          match = self.__scan(tok_regex, delim)

          if (not match and delim == '|' and i+1 < len(input) or 
              not match and delim == '+' and parent_delim == '?' or 
              match and delim == '+'): 
            i+=1 
            continue

          elif match and delim == '|' and parent_delim in ['+', '?']: 
            return match 
          
          raise TempError(input, rule, match, delim, tok_regex, parent_delim)

      else: 
        if '?P' in rule: 
          tok_regex = rule 
        elif type(rule) == tuple: 
          match = self.__scan(rule, delim)
          if (not match and delim == '?' or 
              not match and delim == '|' and i+1 < len(input)): 
            i+=1 
            continue

          elif match: 
            return match 

          raise TempError(input, rule, match, delim, tok_regex, parent_delim) 

        
      match = re.match(tok_regex, self.data) 

      if match: 
        

        kind = match.lastgroup 
        value = match.group() 
        #print(Token(kind, value)) 

        if len(self.tokens) > 0: 

          if self.tokens[-1].type == 'comma' and value == '}': 
            return None         

        if kind != 'whitespace': 
          self.tokens.append(Token(kind, value))

        self.data = re.sub(tok_regex, '', self.data, 1) 

        if delim == '|' or delim == '|' and parent_delim != '?': 
          return match

      elif not match: 


        if (delim == '+' and parent_delim in ['|', '?'] or 
            delim == '|' and i+1 >= len(input) and parent_delim == '?'): 
        
          return match 

        
        if (delim == '?' or 
            delim == '|' and i+1 < len(input)):

          '''
          if delim == '?' and i+1 >= len(input) and parent_delim == '?': 
          print(rule, delim, parent_delim, i, i+1) 
          #return match 
          i = 0
          continue
          raise TempError(input, rule, match, delim, tok_regex, parent_delim)'''

          i+=1 
          continue 

        raise TempError(input, rule, match, delim, tok_regex, parent_delim)

      if i+1 >= len(input) and match and len(self.data) > 0: 
        i = 0
        continue  

      i+=1 
    return match 

  def __iter__(self): 
    for e in self.tokens: 
      yield e 



if __name__ == '__main__': 
  rule_set = [ 
    ('json', r':=object|,array|=:+'),
    ('object', r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,whitespace?,comma+,whitespace?=:?\}+'),
    ('value', r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:?whitespace?'),
    ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:?\]+'),
    ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
  ]

  scanner = Scanner(open('sample.json', 'r').read(), rule_set) 

  print("Scan Done") 

  for token in scanner: 
    print(token) 