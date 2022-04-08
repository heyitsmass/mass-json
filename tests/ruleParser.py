
import re 
from typing import Union 

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

    for key in self.__rules: 
      print(key, self.__rules[key]) 


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

