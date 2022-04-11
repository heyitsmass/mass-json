import re 
import argparse
from typing import NamedTuple 


args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args = vars(args.parse_args())
__FILENAME__ = args['filename'] 

rule_set = [ 
  ('json', r'(:object|array:)'),
  ('object', r'\{!(:whitespace?pair!comma?:)*\}!'),
  ('pair', r'(:whitespace?string!whitespace?colon!whitespace?value!whitespace?:)'),
  ('value', r'(:string|number|object|array|boolean|null|true|false:)'), 
  ('array', r'\[!(:whitespace?value!whitespace?comma?:)*\]!'), 
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('colon', r':'),
  ('comma', r',')
]

class RuleScanner(object): 
  def __init__(self, rules): 

    self._rules = dict() 
    delims = ['|', '*', '+', '!', '?']

    for id, rule in rules: 
      if '(:' in rule: 
        rule = self._remove(re.split(r'(\(:)|:\)([!|+*?])?', rule), ('', None))
        for i, par in enumerate(rule): 
          if par == '(:': 
            rule.remove(par)
            rule[i] = self._remove(re.split(r'([!|+*?])', rule[i]), '') 
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


class Token(NamedTuple): 
  kind:str
  value:str
  lineno:int
  column:int

class Info(Exception): 
  def __init__(self, locals): 

    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str
  
class InputScanner(object):
  def __init__(self, data, rule_set): 
    self.rules = RuleScanner(rule_set) 
    self.ids = [id for id in self.rules] 
    self.data = data 
    self.lineno = self.column = 0

    self.__scan(self.rules[self.ids[0]], self.rules[self.ids[0]][-1])

  def __scan(self, input, delim=None, _delim=None): 
    if type(input) == tuple: 
      for i, arg in enumerate(input): 
        next = input[i+1] if i+1 < len(input) else None 
        rule = arg[:-1] 
        delim = arg[-1] 
        
        ret = self.__scan(rule, delim)
        match = ret[0] 
        tok_regex = ret[1] 
        if match: 
          kind = match.lastgroup 
          value = match.group() 
          print(Token(kind, value, self.lineno, self.column)) 
          self.data = re.sub(tok_regex, '', self.data, 1)

          raise Info(locals()) 
        else: 
          raise Info(locals()) 
    else: 
      if '?P' in input: 
        tok_regex = input
      elif input in self.ids: 
        tok_regex = self.rules[input] 
        if type(tok_regex) == tuple: 
          return (self.__scan(tok_regex, delim), tok_regex)  
      else: 
        raise Info(locals())
    return (re.match(tok_regex, self.data), tok_regex) 


if __name__ == '__main__': 
  scanner = InputScanner(open(__FILENAME__, 'r').read(), rule_set)


