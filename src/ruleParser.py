import re 
from typing import Union

class RuleError(Exception): 
  
  def __init__(self, id, rule): 
    self.str = f'Unable to parse {id=}, {rule=} -> (invalid format?)' 

  def __str__(self): 
    return self.str 


class Rule_parser(object): 
  def __init__(self, rules): 
    self.delims = ['!', '+', '*', '|', '?'] 
    self.ids = [id for id, rule in rules]

    self.rules = self._scan(rules) 


  def _sanitize(self, input:list, delims:Union[str, tuple, list]) -> list:
    if type(delims) in [tuple, list]: 
      for arg in delims: 
        while arg in input: 
          input.remove(arg) 
    elif type(delims) == str: 
      while delims in input: 
        input.remove(delims)
    else: 
      raise TypeError(type(delims)) 
    return input 


  def _scan(self, rules:list) -> dict: 
    tok_regex = r'(?:[^\n(:)]+[?+|*$!]?)?(?:(?:\(:(?:[a-zA-Z]+[?+|*$!]?)+:\)[?+|*$!]?)+(?:[^\n):(]+[?+|*$!]?)?)+'
    tmp=dict()
    for id, rule in rules: 
      if '(:' in rule and ':)' in rule: 
        match = re.match(tok_regex, rule) 
        if match: 
          match = re.split(r'(\(:)([^\n(:)]+?):\)([?!|+*$]?)', rule)
          match = self._sanitize(match, (None, ''))

          tmp[id] = self._parse(match, id) 

        else: 
          raise RuleError(id, rule)
      else: 
        tmp[id] = '(?P<%s>%s)' % (id, rule)
    return tmp 


  def _parse(self, input:list, id:str) -> Union[list, str]: 
    _parsed = list()
    for i, arg in enumerate(input): 
      next = input[i+1] if i+1 < len(input) else None 
      if arg != '(:': 
        if arg not in self.delims: 
          tmp = self._sanitize(re.split(r'(.+?[?!|+*$])', arg), '') 
          if next in self.delims: 
            tmp.append(next)
          else: 
            if len(tmp) > 1: 
              for sub in tmp: 
                if sub[:-1] not in self.ids: 
                  _parsed.append('(?P<%s>%s)%s' % (id, sub[:-1], sub[-1]))
                  continue          # else:
                _parsed.append(sub)  
            else: 
              if arg[:-1] not in self.ids: 
                _parsed.append('(?P<%s>%s)%s' % (id, arg[:-1], arg[-1]))
                continue          # else 
              _parsed.append(arg)
          continue                # else:
        _parsed.append(tuple(tmp))                 
    return tuple(_parsed) if len(_parsed) > 1 else _parsed[0]

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