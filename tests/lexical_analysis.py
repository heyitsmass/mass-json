import re 
from typing import Union

__FILENAME__ = 'sample.json' 

data = open(__FILENAME__, 'r').read() 


raw_rules = [('json', r'(:object|array:)'), 
             ('object', r'(:\{!whitespace?pair*whitespace?,$whitespace?\}!:)'), 
             ('array', r'(:\[!whitespace?value*whitespace?,$whitespace?\]!:)'), 
             ('value', r'(:string|number|true|false|null|array|object:)'),  
             ('pair', r'(:string!whitespace?:!whitespace?value!:)'), 
             ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'), 
             ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'), 
             ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+')]


class Rule(object): 
  def __init__(self):  
    ...



class RuleParser(object): 
  def __init__(self, raw_rules):  

    self.rules = self._parse(raw_rules, [id for id, rule in raw_rules])


  def _verify(self, input:list): 
    # Not currently implemented 
    ... 
            
  def _parse(self, input:list, ids:list) -> dict:

    tmp = dict() 

    for id, rule in input: 
      if '(:' in rule and ':)' in rule: 
        rule = re.split(r'([?|!*$])', rule.strip('(:)'))
        rule = self._sanitize(rule, '')  

        for i, tmp in enumerate(rule):  
          if i+1 < len(rule): 
            if rule[i] not in ids:
              rule[i] = ('(?P<%s>%s)%s' % (id, tmp, rule[i+1]))
            else: 
              rule[i] += rule[i+1]  
            rule.remove(rule[i+1]) 
          else: 
            if i-1 >= 0: 
              if rule[i-1][-1] != '|': 
                raise Exception(f"Unknown delimiter '{rule[i-1][-1]}'")
              rule[i] += rule[i-1][-1]
            else: 
              raise Exception(f"Unable to parse '{id}' -> '{rule}'")
        

        tmp[id] = tuple(rule) 
      else: 
        tmp[id] = ('(?P<%s>%s)' % (id, rule))

    return tmp 
    


  def _sanitize(self, input:list, delim:str): 
    while delim in input: 
      input.remove(delim)  
    return input 
    
      
      



rules = RuleParser(raw_rules) 


      
  


