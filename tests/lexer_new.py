import argparse

'''
  object ending cannot be after a comma 
  string beginning cannot be after a comma 

'''

from typing import NamedTuple

args = argparse.ArgumentParser(
         description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")

args = vars(args.parse_args())
__FILENAME__ = args['filename']

rules = [
    ('object',
     r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,comma?,whitespace?=:?\}+'),
    ('value',
        r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:?whitespace?'),
    ('string',
        r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:?\]+'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
]

import re 

class MissingRuleError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "Error: Missing rule '%s'" % self.rule 


class Token(NamedTuple): 
  type:str 
  value:str 


class MissingTokenError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "Error: Missing token '%s'" % self.rule 


class ParseError(Exception): 
  def __init__(self, rule): 
    self.rule = rule

  def __str__(self): 
    return "Error: Unable to parse rule\n\t'%s'" % self.rule 


class DelimiterError(Exception): 
  def __init__(self, delim): 
    self.delim = delim 

  def __str__(self): 
    return "Error: Unknown Delimiter '%s'" % self.delim 


class Rules(object):
  def __init__(self, rules): 

    self.__rules = dict() 

    for id, rule in rules: 

      tmp_rule = re.split(r'(:=|=:[|+?])', rule) 
      ids = [id for id, rule in rules] 

      if 'whitespace' not in ids: 
        raise MissingRuleError('whitespace') 
      
      if len(tmp_rule) > 1: 
        for i, arg in enumerate(tmp_rule): 
          if arg != ':=': 
            tmp_arg = arg.split(',') 
            if len(tmp_arg) > 1: 
              tmp_arg.append(tmp_rule[i+1][-1])
              tmp_rule.remove(tmp_rule[i+1])
              tmp_rule[i] = tuple(tmp_arg) 
            else: 
              if arg[:-1] not in ids: 
                tmp_rule[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1]) 
        tmp_rule.remove(':=')
        self.__rules[id] = tuple(tmp_rule) 

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


class UnknownTypeError(Exception): 
  def __init__(self, type, rule): 
    self.type = type 
    self.rule = rule 
  
  def __str__(self): 
    return "Exception; Unknown type '%s' within rule:\n\t%s"% (self.type, str(self.rule)) 


class Scanner(object): 
  def __init__(self, filename, rules):
    # Parse the inputted rules 
    self.rules = Rules(rules) 
    # Open the inputted data (should be already read on input, will be modified)
    self.data = open(filename, 'r').read() 
    # Read the ids from the input 
    self.ids = [id for id in self.rules] 
    # Token list 
    self.tokens = list()
    # Scan the inputted data 
    self.__scan(self.rules[list(self.rules.keys())[0]]) 
  
  def __iter__(self): 
    for e in self.tokens: 
      yield e 

  def __scan(self, input, _delim=None):
   

    '''
      
      # raise an error if the delimiter is not in the allowed delimiter range 
      if delim not in ['|', '?', '+']: 
        raise DelimiterError(delim) 
      # Recursively analyize the rule 
      if type(rule) == tuple: 
        self.__scan(rule) 
        # Delimiter support tertiary -> modifications allowed here 
        if delim == '?': 
          continue 
        # Any Exception raised is a parse error 
        raise ParseError(input) 
      else: 
        # Check if the rule is already a regex pattern 
        if '?P' in rule: 
          tok_regex = rule 
        else: 
          # Check if the rule is a rule within the parsable rules
          if rule in self.ids: 
            tok_regex = self.rules[rule] 
            # Check if the regex rule is a tuple (nested rule) 
            if type(tok_regex) == tuple: 
              self.__scan(tok_regex) 
              # Delimiter support secondary -> modifications allowed here
              if delim == '+': 
                continue 
              elif delim == '|' and i+1 < len(input): 
                continue 
              raise ParseError(input) 
          else: 
            raise ParseError(input) 
        # Check if the regex token matches a value in the data stream 
        match = re.match(tok_regex, self.data) 
        if match: 
          # If there's a match, output the match (save the match) 
          kind = match.lastgroup 
          value = match.group() 
          # Shrink the data stream accordingly 
          self.data = re.sub(tok_regex, '', self.data, 1) 
          # If output is necessary, uncomment to ignore whitespace tokens
          #if kind in ['whitespace']:
            #continue 
          # Print the token if necessary (uncomment for use)
          #print(Token(kind, value)) 
          self.tokens.append(Token(kind, value)) 
          # Delimiter support quarternary -> modifications allowed here 
          if delim == '|': 
            return 
        else: 
        # Demiliter support singular -> modifications allowed here 
          if delim == '?': 
            continue 
          elif delim == '|' and i+1 <= len(input): 
            continue 
          elif delim == '+' and i <= 1: 
            
            return 
          # Output the errored rule 
          raise MissingTokenError(rule) 
    # While there's a match, continue searching for the required input 
    if match: 
      self.__scan(input) 
    '''

scanner = Scanner(__FILENAME__, rules)

prev = None 
for t in scanner:

  if t.type != 'whitespace': 

    print(t, '\n\t', prev) 
    if (prev and prev.type == 'comma' and t.value in ['}', ']'] or
        prev and prev.value in ['{', '['] and t.type == 'comma' or
        prev and prev.type == 'colon' and t.type == 'comma'):
      
      raise Exception 

       
    prev = t 
  


