import sys
sys.path.append('..')

from src.ruleParser import Rule_parser


raw_rules= [ 
  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:pair!:)*\}!'), 
  ('value', r'(:string|number|object|array|boolean|Null?:)?'), 
  ('array', r'\[!(:whitespace?value!comma$whitespace?:)*\]!'),
  ('pair', r'(:string!whitespace?colon!whitespace?value!whitespace?comma$whitespace?:)?'),
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('Null', r'null'),
  ('colon', r':'),
  ('comma', r','),
  ('mismatch', r'.')  
]

parsed_rules = Rule_parser(raw_rules) 
