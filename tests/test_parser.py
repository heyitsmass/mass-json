from typing import NamedTuple
import re

class Token(NamedTuple):
    type: str
    value: str
    line: int

class InputError(Exception): 
  def __init__(self, default):
    self._name = default 

  def __str__(self): 
    return "Unable to locate %s tokenizer rules" % self._name 

class TokenError(Exception): 
  def __init__(self, value, column): 
    self._value = value
    self._column = column 
  
  def __str__(self): 
    return "%s unexpected found on line %s" % (self._value, self._column)

rules = [ 
  ('_object', r'{+'+(r'_whitespace+_string+_whitespace+:+_whitespace+_value+_comma+_whitespace+_newline')+r'+}+_newline'),
  ('_comma', r','),
  ('_newline', r'\n'),
  ('_array', r'\[+'+((r'_whitespace|_value')+r'_comma')+r'+\]+_newline'),
  ('_value', r'_whitespace+'+(r'_string|_number|_object|_array|_boolean|_null')+r'+_whitespace+_newline'), 
  ('_string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('_boolean', r'true|false'),
  ('_null', r'null'), 
  ('_number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('_whitespace', r'[ \u0020\u000A\u000D\u0009\t]'),
  ('_mismatch', r'.'), 
]

class _scanner(object): 
  def __init__(self, data, rules, line_num=0): 
    self._data = data
    self._default = 'default'
    self._size = len(self._data) 

    self._position = 0
    self._line_num = line_num
    
    self._rules = self._tokenizer(rules)

    if self._default in self._rules: 
      self._tok_regex = self._rules[self._default]
    else: 
      raise InputError(self._default)

  def _tokenizer(self, rules, _ret=dict()): 
    for name, sub_rule in rules: 
      _ret[name] = '|'.join('(?P<%s>%s)' % pair for pair in sub_rule)
    return _ret

  def _shrink(self, length): 
    tmp = '' 
    for i in range(length, len(self._data)): 
      tmp += self._data[i] 
    return tmp 

  def scan(self): 
    #print(self._tok_regex) 

    last_match = ''

    while len(self._data) > 0: 
      match = re.match(self._tok_regex, self._data)
      if match: 
        value = match.group() 
        kind = match.lastgroup 

        if kind == 'obj_begin': 
          self._tok_regex = self._rules['token_object'] 

        elif kind == 'new_line': 
          self._line_num += 1

        elif kind == 'obj_end': 
          if last_match == ',': 
            raise TokenError(value, self._line_num)

        elif kind == 'mismatch': 
          raise TokenError(value, self._line_num)

        self._data = re.sub(self._tok_regex, '', self._data, 1)
        last_match = match 

        if kind not in ['whitespace', 'new_line']: 
          print(Token(kind, value, self._line_num))

      else: 
        raise Exception("Parse Error: (did you include a mismatch case? r'.')")


data = open('sample_1.json', 'r').read() 
#scanner = _scanner(data, rules) 

#scanner.scan() 

for i in range(len(rules)): 
  print(rules[i][0], ':', end='')
  tmp = rules[i][1]
  if tmp == '.': 
    print(' else') 
  else: 
    print(' '+rules[i][1])


"""
def tokenize(code):
    keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
    token_object = [ 

    ] 

    token_array = [ 

    ]

    token_general = [ 

    ]

    token_specification = [ 
      ('OBJ_BEGIN', r'{'),
      # ('NEWLINE', r'\n'),
      # ('STRING', r'\"(?:(?:(?!\\)[^\"])+(?:\\n|\\t|\\u[0-9a-fA-F]{4})?)+?\"'),
      # ('KEY_STRING',r'\"(?:(?:(?!\\)[^\"])+(?:\\n|\\t|\\u[0-9a-fA-F]{4})?)+?\",{1}'),
      ('SKIP', r'[ \u0020\u000A\u000D\u0009\t]'),
      # ('COLON', r':'),
      ('MISMATCH', r'.')
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID' and value in keywords:
            kind = value
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        yield Token(kind, value, line_num, column)

statements = open('sample.json', 'r').read() 

for token in tokenize(statements):
    print(token)
"""