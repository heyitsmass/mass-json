import re

'''
  <expression_a> | 
    => <expression_a> is optional but atleast one is required 

  <expression_a> + 
    => <expression_a> is required 

  

  

  
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
            #self.rules[id] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1])
            args[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1])
            #print(arg) 
        
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


if __name__ == '__main__': 
  rule_set = [ 
    ('json', r':=object|,array|=:+'),
    ('object', r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,whitespace?,comma?,whitespace?=:+\}+'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+')
  ]

  rules = Rules(rule_set) 
