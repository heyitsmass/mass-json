import re 

__depth__ = False

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

def capture(i, rule, _final=r''):
  _final += '('  
  tmp = r'' 
  while i < len(rule): 
    if i+1 < len(rule): 
      # Parse the main rule conditions, avoiding sub conditions
      if rule[i]+rule[i+1] == '\)' and rule[i-1] != '\\':
        if _final != r'(': 
          _final += ')'
        return [_final+(tmp+')'), i+2]
      # Recursively checks for any sub groups of conditions
      elif rule[i]+rule[i+1] == '\(': 
        _final += tmp 
        tmp = r''         
        captured = capture(i+2, rule)
        if __depth__: 
          #Debug, outputs any sub captured conditions
          print(" Sub capture:", captured[0])
        _final += captured[0]
        i = captured[1]
        continue 
    tmp+=rule[i] 
    i+=1
  raise Exception("Unclosed Parenthesis") 


def recurse_rules(rule, rule_ids):

  
  return  

def parse_rule(rules):
  # List of rule identifiers 
  rule_ids = [rules[i][0] for i in range(len(rules))]

  for rule in rules: 
    rule_id = rule[0]   # current rule identifier
    rule_st = rule[1]   # current rule condition

    if __depth__:
      #Outputs current identifier 
      print(rule_id, ': ', rule_st)
    i = 0
    while i < len(rule_st):
      if i+1 < len(rule_st):
        if rule_st[i]+rule_st[i+1] == '\(':
          captured = capture(i+2, rule_st)
          i = captured[1]
          if not __debug__:
            # Outputs the capture group returned by capture()
            print("\u001b[1mMain capture:\u001b[0m", captured[0])
            # Outputs the rule passed into capture() 
            print("\u001b[1mRule capture:\u001b[0m", rule_st)
            print()
          continue
      i+=1

  return 

parse_rule(rules)

