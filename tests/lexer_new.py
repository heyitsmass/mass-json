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


class Rules(object): 

  def __init__(self, rules): 

    self.__rules = dict() 

    for id, rule in rules: 

      tmp_rule = re.split(r'(:=|=:[|+?])', rule) 
      ids = [id for id, rule in rules] 
      
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


new_rules = Rules(rules)

for id in new_rules: 
  print(id + ':', new_rules[id]) 