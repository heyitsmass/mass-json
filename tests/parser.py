import argparse 
args = argparse.ArgumentParser(
          description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="set the name for the input file")
args.add_argument('--debug', metavar='N',
                  type=int, help="set the debug depth level N (default: 0)",
                  default=0)

args = vars(args.parse_args())

__depth__ = args['debug'] if args['debug'] else 0
__filename__ = args['filename']

class RuleScanner(object): 

  def __init__(self, data, rules):
    self.data = data 
    self.rules = rules

  
class CaptureError(Exception): 
  def __init__(self, id, rule): 
    self.id = id 
    self.rule = rule 

  def __str__(self): 
    return "Error capturing '%s':\n\t%s" % (self.id, self.rule)

class Capture(object): 
  def __init__(self, value, index): 
    self.value = value 
    self.index = index 

class Parser(object): 

  def __init__(self, rules): 
    self.rules = self.parse(rules)

  def __iter__(self): 
    return iter(self.rules) 

  def __getitem__(self, id):    
    return self.rules[id] 
  
  def __setitem__(self, key, value): 
    self.rules[key] = value  
    
  def keys(self):                     #return keys in rules 
    return self.rules.keys()    

  def values(self):                   #return values in rules 
    return self.rules.values()       

  def items(self):                    #return keys, values in rules 
    return self.rules.items() 

  def parse(self, rules): 

    capture_val = str 
    tmp = dict() 

    for id, rule in rules: 
      #print(id, ':', rule) 
      capture_val = '' 
      i = 0 
      while i < len(rule): 
        if i+1 < len(rule): 
          if rule[i] + rule[i+1] == '\(': 
            capture_ret = self.capture(id, rule, i)
            capture_val = capture_ret.value 
            i = capture_ret.index 
            #print('\t', capture_val)
            rule = rule.replace('\('+capture_val+'\)', '<capture>') #value 
            #print(rule) 

        i+=1 
      
      tmp[id] = dict() 

      print(id, ':', tmp[id], ': \''+rule+'\'', ':', capture_val) 
         
    return tmp 

  def capture(self, id, rule, index): 
    tmp = ''
    i = index+2
    while i < len(rule): 
      if i+1 < len(rule): 
        if rule[i]+rule[i+1] == '\(': 
          captured = self.capture(id, rule, i) 
          if __depth__ > 0: 
            print("[\x1b[33m\x1b[1m!!\x1b[0m]", captured) 
        elif rule[i]+rule[i+1] == '\)': 
          return Capture(tmp, i) 
        tmp += rule[i]
      i+=1 
    raise CaptureError(id, rule) 

  def tokenize(self): 
    return 

if __name__ == "__main__": 

  data = open(__filename__, 'r').read()
  rules = [
    ('object',
      r'{+\(whitespace+string+whitespace+colon+whitespace+value+comma+newline\)+}'),
    ('value',
      r'whitespace+\(string|number|object|array|boolean|null\)+whitespace'),
    ('string',
      r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
    ('array',
      r'\[+\(whitespace|value+comma\)+\]+newline'),
    ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]'),
    ('boolean', r'true|false'),
    ('newline', r'\n'),
    ('NULL', r'null'),
    ('colon', r':'),
    ('comma', r','),
    ('mismatch', r'.')
  ]   

  parse = Parser(rules)

  scanner = RuleScanner(data, parse)