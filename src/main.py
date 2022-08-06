from inputScanner import Input_scanner

__FILENAME__ = 'sample.json' 

raw_rules= [ 
  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:pair!whitespace?:)*\}!'), 
  ('value', r'(:string|number|boolean|object|array|Null:)?'), 
  ('array', r'\[!(:whitespace?value!comma$whitespace?:)*\]!'),
  ('pair', r'(:whitespace?string!whitespace?colon!whitespace?value!whitespace?comma$:)?'),
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('Null', r'null'),
  ('colon', r':'),
  ('comma', r','),
]

scanner = Input_scanner(open(__FILENAME__, 'r').read(), raw_rules) 

