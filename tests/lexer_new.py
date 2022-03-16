import re

'''
  <expression_a> | 
    => <expression_a> is optional but atleast one is required 

  <expression_a> + 
    => <expression_a> is required 
  
  <expression_a> ? 
    => <expression_a> is not necessary 



  

  

  
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
            args[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1])
        
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



class Scanner(object): 
  def __init__(self, data, rules): 
    self.rules = Rules(rules) 
    self.data = data 
    self.ids = [id for id in self.rules]

    self.default = self.rules[self.ids[0]][:-1]
    self.delim = self.rules[self.ids[0]][-1] 


    self.__scan(self.default, self.delim) 

  def __scan(self, input, _delim=None): 
    
    or_var = None 
    match = None 

    i = 0
    while i < len(input): 
      rule = input[i][:-1]
      delim = input[i][-1] 

      #print(rule, delim) 

      if rule in self.ids: 
        tok_regex = self.rules[rule]
        if type(tok_regex) == tuple: 
          match = self.__scan(tok_regex, delim)
          if match: 
            if i+1 < len(input): 
              i += 1 
            else: 
              i = 0
            continue 
          #print(input[i+1]) 
          raise Exception(tok_regex, match, input, delim) 
      else: 
        if '?P' in rule: 
          tok_regex = rule 
        elif type(rule) == tuple: 
          match = self.__scan(rule, delim)

          if match and delim == '?': 

            #print(delim) 

            return match 
          
          

          raise Exception(input[i], rule, delim, match) 

      

      match = re.match(tok_regex, self.data) 

    
      if match: 
        print(match) 

        self.data = re.sub(tok_regex, '', self.data, 1) 

        if delim == '|': 
          return match 
        
      else: 
        if delim == '+': 
          raise Exception(tok_regex, delim) 
        elif delim == '?': 
          i+=1
          continue 
        elif delim == '|':
          if i+1 >= len(input): 
            raise Exception("Unable to find or variable")
          else: 
            i+=1
            continue  

        raise Exception(input, rule, delim, i) 
      
      if match and i+1 >= len(input):
        i = 0
        continue 

      i+=1 
      #print(rule, i) 

    return 




if __name__ == '__main__': 
  rule_set = [ 
    ('json', r':=object|,array|=:+'),
    ('object', r'\{+:=whitespace?,string+,whitespace?,colon+,whitespace?,value+,whitespace?,comma?,whitespace?=:?\}+'),
    ('value', r'whitespace?:=string|,number|,object|,array|,boolean|,_null|=:?whitespace?'),
    ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array', r'\[+:=whitespace?,value+,comma?,whitespace?=:?\]+'),
    ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
    ('boolean', r'true|false'),
    ('_null', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
  ]

  scanner = Scanner(open('sample.json', 'r').read(), rule_set) 