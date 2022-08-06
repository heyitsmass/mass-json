import re 

from typing import Union


class RuleError(Exception): 
  
  def __init__(self, id, rule): 

    self.str = f'Unable to parse {id=}, {rule=} -> (invalid format?)' 

  def __str__(self): 
    return self.str 


class RuleParser(object): 
  """ 
  """
  def __init__(self, rules): 
    """
    """
    self.delims = ['!', '+', '*', '|', '?'] 
    self.ids = [id for id, rule in rules]

    self.rules = self.scan(rules) 


  def sanitize(self, input:list, delims:Union[str, tuple, list]) -> list:
    """
    """
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


  def scan(self, rules:list) -> dict: 
    """
    """
    tok_regex = r'(?:[^\n(:)]+[?+|*$!]?)?(?:(?:\(:(?:[a-zA-Z]+[?+|*$!]?)+:\)[?+|*$!]?)+(?:[^\n):(]+[?+|*$!]?)?)+'
    tmp=dict()
    for id, rule in rules: 
      if '(:' in rule and ':)' in rule: 
        match = re.match(tok_regex, rule) 
        if match: 
          match = re.split(r'(\(:)([^\n(:)]+?):\)([?!|+*$]?)', rule)
          match = self.sanitize(match, (None, ''))

          tmp[id] = self.parse(match, id) 

        else: 
          raise RuleError(id, rule)
      else: 
        tmp[id] = '(?P<%s>%s)' % (id, rule)
    return tmp 


  def parse(self, match:list, id:str) -> Union[list, str]: 
    """
    """
    final = list()
    for i, arg in enumerate(match): 
      next = match[i+1] if i+1 < len(match) else None 
      if arg != '(:': 
        if arg not in self.delims: 
          tmp = self.sanitize(re.split(r'(.+?[?!|+*$])', arg), '') 
          if next in self.delims: 
            tmp.append(next)
          else: 
            if len(tmp) > 1: 
              for sub in tmp: 
                if sub[:-1] not in self.ids: 
                  final.append('(?P<%s>%s)%s' % (id, sub[:-1], sub[-1]))
                else: 
                  final.append(sub) 
            else: 
              if arg[:-1] not in self.ids: 
                final.append('(?P<%s>%s)%s' % (id, arg[:-1], arg[-1]))
              else: 
                final.append(arg) 
        else: 
          final.append(tuple(tmp))
      else: 
        continue 
    return tuple(final) if len(final) > 1 else final[0] 

rule_set = [ 
  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:pair!:)*\}!'), 
  ('value', r'(:string|number|object|array|boolean|Null?:)?'), 
  ('array', r'\[!(:whitespace?value!comma$whitespace?:)*\]!'),
  ('pair', r'(:whitespace?string!whitespace?colon!whitespace?value!whitespace?comma$whitespace?:)*'),
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('Null', r'null'),
  ('colon', r':'),
  ('comma', r','),
  ('mismatch', r'.') 
]

rules = RuleParser(rule_set) 