import re
from typing import NamedTuple

__FILENAME__ = 'sample-4.json'

rules = [ 
  #('object', r'\{!(:whitespace?pair!comma?:)*\}!'),
  ('pair', r'(:string!colon!whitespace?string!comma$whitespace?:)*'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'), 
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('colon', r':'), 
  ('comma', r',') 
]

class RuleScanner(object): 
  def __init__(self, rules): 

    self._rules = dict() 
    delims = ['|', '*', '+', '!', '?', '$']

    for id, rule in rules: 
      if '(:' in rule: 
        rule = self._remove(re.split(r'(\(:)|:\)([!|+*?$])?', rule), ('', None))
        for i, par in enumerate(rule): 
          if par == '(:': 
            rule.remove(par)
            rule[i] = self._remove(re.split(r'([!|+*?$])', rule[i]), '') 
            for j, child in enumerate(rule[i]): 
              if j+1 < len(rule[i]): 
                rule[i][j] = child + rule[i][j+1]
                rule[i].remove(rule[i][j+1]) 
              else: 
                if j-1 >= 0 and rule[i][j-1][-1] == '|': 
                  rule[i][j] = child + rule[i][j-1][-1]
                else: 
                  raise Exception("Missing Delimiter")  
            if i+1 < len(rule): 
              if rule[i+1] in delims: 
                rule[i].append(rule[i+1]) 
                rule.remove(rule[i+1]) 
              else: 
                raise Exception("Missing Delimiter") 
            else: 
              rule[i].append('!') 
            rule[i] = tuple(rule[i]) 
          if par != '(:': 
            rule[i] = '(?P<%s>%s)%s' % (id, par[:-1], par[-1]) 
        self._rules[id] = rule[0] if len(rule) == 1 else tuple(rule) 
      else: 
        self._rules[id] = '(?P<%s>%s)' % (id, rule)


  def _remove(self, rule:list, delims): 
    if type(delims) == str: 
      while delims in rule: 
        rule.remove(delims) 
    elif type(delims) in [list, tuple]: 
      for arg in delims: 
        while arg in rule: 
          rule.remove(arg) 
    else: 
      raise Exception("Unsupported type '%s'" % type(delims))
    return rule 


  def __iter__(self): 
    return iter(self._rules) 


  def __getitem__(self, key): 
    return self._rules[key] 


  def __setitem__(self, key, value): 
    self._rules[key] = value 
  

  def keys(self): 
    return self._rules.keys() 
  

  def values(self): 
    return self._rules.values() 
  

  def items(self): 
    return self._rules.items() 



class Info(Exception): 
  def __init__(self, locals): 

    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str

class Token(NamedTuple): 
  kind:str
  value:str
  lineno:int
  column:int

class Scanner(object): 
  def __init__(self, data, rules): 
    self.rules = RuleScanner(rules)  
    self.data = data 
    self.ids = [id for id in self.rules]
    self.delims = ['|', '*', '+', '!', '?', '$']
    self.lineno = self.column = 0 
    match = self.__scan(self.rules[self.ids[0]], self.ids[0])

    if not match[0]: 
      raise Exception("Invalid Token: '%s'" % match[1]) 

    #print(match) 


  def __scan(self, input, id, delim = None, _delim=None, _match=None, prev_delim=None): 
    if type(input) == tuple:
      if input[-1] in self.delims: 
        _delim = input[-1] 

      tmp = input[:-1] if input[-1] in self.delims else input
      final = ''
      for i, arg in enumerate(tmp): 
        next = tmp[i+1] if i+1 < len(tmp) else None 
        rule = arg[:-1] 
        delim = arg[-1] 

        ret = self.__scan(rule, id, delim, _delim) 
        match = ret[0]
        tok_regex = ret[1] 

        if match: 

          #_match = match 

          #kind = match.lastgroup 
          #value = match.group()
          final += match.group() 
          #print(Token(kind, value, self.lineno, self.column), prev_delim)
          self.data = re.sub(tok_regex, '', self.data, 1) 

          if prev_delim == '$':
            if match.lastgroup == 'whitespace': 
              continue 
            if not _match:

              return (None, final)
            else: 
              #prev_delim = None
              raise Info(locals())

          _match = match 

        else: 

          if delim == '?': 
            continue 
          
          if delim == '$':
            _match = match 
            prev_delim = delim 
            continue 
          
          #return None
          raise Info(locals())
      match = True 
      print(Token(id, final, self.lineno, self.column))

      if _delim == '*' and len(self.data) > 0: 
        return self.__scan(input, id, None, None, _match, prev_delim) 
      #raise Info(locals()) 

    elif type(input) == str: 
      #print(input)
      if input in self.ids: 
        tok_regex = self.rules[input]
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, input, delim, _delim, _match, prev_delim) 
      elif '?P' in input: 
        tok_regex = input 
    else: 
      raise Info(locals()) 

    return (re.match(tok_regex, self.data), tok_regex) 






scanner = Scanner(open(__FILENAME__, 'r').read(), rules)






