from ruleParser import parser 


__FILENAME__ = 'sample.json' 

raw_rules= [ 
  ('object', '\{!whitespace?pair*whitespace?\}!'), 
  ('array', '\[!whitespace?value*whitespace?comma$whitespace?\]!'), 
  ('value', 'string|number|boolean|Null|array|object'), 
  ('pair', 'string!whitespace?colon!whitespace?value!whitespace?comma$'), 
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'), 
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'), 
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'), 
  ('Null', r'null'),
  ('colon', r':'), 
  ('comma', r',')
]


raw_rules = [ 
  ('object', f'{'something'}')
]


data = open(__FILENAME__, 'r').read()


rules = parser(raw_rules)
