"""
  Delimiter rules: [|, +, ?, (:=, =:)]
  
  <expression_a><delimiter><expression_b> +
    => b is required and must follow a unless a does not exist or its delimiter is a ?
  
  <expression_a> ?
    => a is not required

  <expression_a> | <expression_b>
    => either a or b must exist 

  := <expression list> =: <delimiter> 
    => expressions to be repeated followed by it's necessity
    => expression list is comma seperated 
      => <expression_1><delimiter>, <expression_2><delimiter>, ... <expression_n><delimiter> , n <= 100 

  <expression> ! 
    => expression is terminal, once found the function can return 

  #<expression_a><delimiter><expression_b> ! <expression_c> 
  # => c can follow a but cannot follow b 

"""

from typing import NamedTuple

import re 

class MissingRuleError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "Error: Missing rule '%s'" % self.rule 


class MissingTokenError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "Error: Missing token '%s'" % self.rule 


class UnknownTypeError(Exception): 
  def __init__(self, type, rule): 
    self.type = type 
    self.rule = rule 
  
  def __str__(self): 
    return "Error: Unknown type '%s' within rule\n\t'%s'"% (self.type, str(self.rule)) 


class DelimiterError(Exception): 
  def __init__(self, delim): 
    self.delim = delim 

  def __str__(self): 
    return "Error: Unknown delimiter '%s'" % self.delim 


class ParseError(Exception): 
  def __init__(self, rule): 
    self.rule = rule

  def __str__(self): 
    return "Error: Unable to parse rule\n\t'%s'" % self.rule 

class Token(NamedTuple): 
  type:str 
  value:str 


class Rules(object): 
  def __init__(self, rules): 
    self.rules = dict() 

    for id, rule in rules: 

      arg = re.split(r'(:=|=:[?+|])', rule) 
      ids = [id for id, rule in rules] 

      # print(id, rule, '\n', arg if len(arg) > 1 else '') 

      if len(arg) > 1:
        if '' in arg: 
          while '' in arg: 
            arg.remove('') 

        for i, sub_arg in enumerate(arg): 
          if sub_arg == ':=': 
            arg[i+1] = re.split(r'\,', arg[i+1])
            arg.remove(':=') 
            arg[i].append(arg[i+1][-1])
            arg.remove(arg[i+1])
            arg[i] = tuple(arg[i]) 
          else: 
            tmp = sub_arg[:-1] 
            delim = sub_arg[-1]
            if tmp not in ids: 
              arg[i] = '(?P<%s>%s)%s' % (id, tmp, delim) 

        if len(arg) <= 1: 
          self.rules[id] = arg[0]
        else: 
          self.rules[id] = tuple(arg) 

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

class Scanner(object): 
  def __init__(self, rules, data): 
    self.rules = Rules(rules) 
    self.data = data

    self.tokens = list() 

    self.ids = [id for id in self.rules] 


    self.__scan(self.rules[list(self.rules.keys())[0]])

  def __scan(self, input, _delim=None): 

    for i, arg in enumerate(input): 

      rule = arg[:-1] 
      delim = arg[-1] 

      if rule not in self.ids: 
        if '?P' in rule: 
          #print(i, rule, delim) 
          tok_regex = rule 
        elif type(rule) == tuple: 

          match = self.__scan(rule, delim) 
          if delim == '?' and match: 
            return match 
          if delim == '?' and not match: 
            continue
          elif _delim == '|' and not match or not _delim: 
            continue 

          #print(rule, delim, input, input[i+1]) 
          raise Exception('A', i, rule, delim, _delim, input[i], match) 
          #print(i, rule) 
      elif rule in self.ids: 
        tok_regex = self.rules[rule] 
      else: 
        raise ParseError(rule) 

      
      if type(tok_regex) == str: 
        match = re.match(tok_regex, self.data) 

      elif type(tok_regex) == tuple: 
        match = self.__scan(tok_regex, delim) 
        
        if delim == '+' and i+1 < len(input): 
          continue 
        elif delim == '|' and not match: 
          continue 

        print(rule, delim, input, input[i+1])
        raise Exception('B', match)

      if match: 
        kind = match.lastgroup 
        value = match.group() 

        print(Token(kind, value)) 

        self.data = re.sub(tok_regex, '', self.data, 1) 

        if delim == '|': 
          return match

      else: 
        if delim == '?': 
          continue 
        elif delim == '|' and i+1 < len(input): 
          continue 
        elif delim == '+' and i <= 1: 
          return match
        elif delim == '|': 
          return match 
        elif _delim in ['?']: 
          return match 
        else: 
          raise MissingTokenError(rule) 

    if match: 
      match = self.__scan(input, delim) 
      return match  

if __name__ == '__main__': 
  rules = [

      ('object', r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,whitespace?,comma?,whitespace?=:|\}+'),
      ('value', r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:?whitespace?'), 
      ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:?\]+'),   
      ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
      ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
      ('boolean', r'true|false'),
      ('_null', r'null'),
      ('colon', r':'),
      ('comma', r','),
      ('mismatch', r'.')
  ]

  data = open('sample.json', 'r').read() 

  scanner = Scanner(rules, data) 
