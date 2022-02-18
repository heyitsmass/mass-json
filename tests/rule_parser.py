import re 

import argparse

argparser = argparse.ArgumentParser(description="Scan a json file for grammatical accuracy.")
argparser.add_argument('--depth', metavar='#', type=int)

args = vars(argparser.parse_args())

__depth__ = args['depth'] if args['depth'] else 0

rules = [ 
  ('_object', r'{+\(_whitespace+_string+_whitespace+:+_whitespace+_value+_comma+_newline\)+}+_newline'),
  ('_comma', r','),
  ('_newline', r'\n'),
  ('_array', r'\[+\(\(_whitespace|_value\)+_comma\)+\]+_newline'),
  ('_value', r'_whitespace+\(_string|_number|_object|_array|_boolean|_null\)+_whitespace+_newline'), 
  ('_string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('_boolean', r'true|false'),
  ('_null', r'null'), 
  ('_number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('_whitespace', r'[ \u0020\u000A\u000D\u0009\t]'),
  ('_mismatch', r'.'), 
]

class _Scanner(object): 
  def __init__(self, data, rules, line_num = 0): 
    self._position = 0
    self._lineno = line_num 
    self._data = data 
    self._size = len(data) 
    self._rules = _RuleParser(rules)
    self._ids = self._rules._ruleids

    if __depth__ > 3: 
      for rule in self._rules: 
        print(rule) 

      for id, rule in self._rules: 
        print(id, rule)  


    print(self._ids) 

    for id, rule in self._rules: 
      print(id, rule)

class _RuleParser(object): 
  def __init__(self, rules): 
    self._tmp = self.parse_rule(rules)
    self._position = 0
    self._data = list() 
    for x, y in enumerate(self._tmp[0], 0): 
      self._data.append(tuple((self._tmp[1][x], y)))
    self._ruleids = self._tmp[1]
    
  
  def __iter__(self): 
    return self 
  
  def __next__(self): 
    self._position +=1 
    if self._position >= len(self._data): 
      self._position = 0
      raise StopIteration 
    
    return self._data[self._position]


  def parse_rule(self, rules):
    # List of rule identifiers 
    rule_ids = [rules[i][0] for i in range(len(rules))]
    tmp = list() 

    for rule in rules: 
      captured = None
      rule_id = rule[0]   # current rule identifier
      rule_st = rule[1]   # current rule statement

      if __depth__ > 1:
        #Outputs current identifier 
        print(rule_id, ': ', rule_st)
      i = 0
      while i < len(rule_st):
        if i+1 < len(rule_st):
          if rule_st[i]+rule_st[i+1] == '\(':
            captured = self.capture(i+2, rule_st)
            i = captured[1]
            # Replace the returned string with a placeholder 
            rule_st = rule_st.replace(captured[0], '<capture>') 
            if __depth__ > 1: 
            #if __depth__:
              # Outputs the capture group returned by capture()
              print("\u001b[1mMain capture:\u001b[0m", captured[0])
              # Outputs the rule passed into capture() 
              print("\u001b[1mRule capture:\u001b[0m", rule_st)
              print()
            continue
        i+=1
      
      if captured: 
        tmp.append(self.tokenizer((rule_id, rule_st), rule_ids, captured[0])) # multi - rule capture 
      else: 
        tmp.append(self.tokenizer((rule_id, rule_st), rule_ids))              # single - rule capture 
    
    return (tmp, rule_ids)

  def capture(self, i, rule, _final=r''):
    _final += '\('  
    tmp = r'' 
    while i < len(rule): 
      if i+1 < len(rule): 
        # Parse the main rule conditions, avoiding sub conditions
        if rule[i]+rule[i+1] == '\)' and rule[i-1] != '\\':
          return [_final+(tmp+'\)'), i+2]
        # Recursively checks for any sub groups of conditions
        elif rule[i]+rule[i+1] == '\(': 
          _final += tmp 
          tmp = r''         
          captured = self.capture(i+2, rule)
          if __depth__ > 2: 
            #Debug, outputs any sub captured conditions
            print(" Sub capture:", captured[0])
          _final += captured[0]
          i = captured[1]
          continue 
      tmp+=rule[i] 
      i+=1
    raise Exception("Error") 

  def tokenizer(self, rule, ids, _capture=None): 

    rule_sts = [(rule[0], rule[1])] if not _capture else [(rule[0], st) for st in rule[1].split('+')]
    token_set = list()

    if __depth__ > 1:  
      print("\u001b[1mList of split tokens:\u001b[0m", rule_sts) 

      print("\u001b[1mList of all Identifiers:\u001b[0m", ids) 

    for pair in rule_sts: 
      if pair[1] in ['<capture>', _capture] or pair[1] in ids: 
        token_set.append(pair[1])
        continue  
      token_set.append('(?P<%s>%s)' % pair)

    if __depth__ > 0: 
      print("\x1b[1m[\x1b[32m✓\x1b[0m]\x1b[1m\x1b[1mToken set:\x1b[0m", token_set)
      if _capture: 
        print("\x1b[1m[\x1b[33m!\x1b[0m]\x1b[1m\t      \x1b[3mCapture Group:\x1b[0m", _capture)
    
    return token_set
        

data = open('sample_2.json', 'r').read() 

scanner = _Scanner(data, rules) 

#scanner.scan() 
