from typing import Any, NamedTuple
import re

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

def tokenize(code):
    token_specification = [
        ('string', r'\"((?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?)\"'), 
        ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'), 
        ('arr_start', r'\['),
        ('obj_start', r'\{'),
        ('obj_end', r'\}'),
        ('arr_end', r'\]'),
        ('colon', r':'), 
        ('comma', r','), 
        ('boolean', r'true|false'),
        ('null', r'null'), 
        ('newline',  r'\n'),           # Line endings
        ('whitespace', r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.')             # Any other character
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
      kind = mo.lastgroup
      value = mo.group()
      if(mo.groups()[1]):
        value = mo.groups()[1]
    
      column = mo.start() - line_start

      if kind == 'newline': 
        line_start = mo.end()
        line_num+=1
        continue  

      if kind == 'whitespace': 
        continue 

      elif(kind == 'MISMATCH'): 
        raise RuntimeError(f'{value} unexpected on line {line_num}')

      yield(Token(kind, value, line_num, column))



statements = open('large-file.json', 'r').read(); 
tokens = [] 
for token in tokenize(statements):
  tokens.append(token); 

primitives = [ 
  'string', 'number', 'boolean', 'null'
]

expressions = [ 
  'obj_start', 'arr_start'
]


class gatheredValues(NamedTuple): 
  index:int 
  value:dict|list 


def get_array(toks:list[Token], _i:int=0, _parent:Token=None): 
  if toks[_i].type != 'arr_start': 
    raise Exception() 

  _i += 1
  arr = list()
  while _i <= len(toks): 
    if toks[_i].type in primitives:
      arr.append(toks[_i].value)  
      _i+=1

    elif toks[_i].type in expressions: 
      if toks[_i].type == 'obj_start': 
        ret = get_object(toks, _i, _parent) 
      else: 
        ret = get_array(toks, _i, _parent) 
      
      if not ret: 
        raise Exception(toks[_i]) 
      
      arr.append(ret.value)  
      _i = ret.index
    
    if toks[_i].type != 'comma': 
      break 
    _i+=1 

  if toks[_i].type != 'arr_end': 
    raise Exception 

  return gatheredValues(_i+1, arr) 



def get_object(toks:list[Token], _i:int=0, _parent:Token=None): 
  if toks[_i].type != 'obj_start': 
    raise Exception() 

  _i += 1 

  tmp = dict()
  while _i <= len(toks):  # get pairs 

    if toks[_i].type != 'string': # valid key? 
      break 
    
    key = toks[_i]
    _i +=1 

    if toks[_i].type != 'colon': 
      raise Exception(toks[_i]) 

    _i+=1   
    ret = None 
    if toks[_i].type in primitives: #scan primitive value 
      tmp[key.value] = toks[_i].value
      _i+=1 
    elif toks[_i].type in expressions: #scan expression value 
      
      if toks[_i].type == 'obj_start': 
        ret = get_object(toks, _i, key) 
      else: 
        ret = get_array(toks, _i, key) 
      
      if not ret: 
        raise Exception(toks[_i]) 
      
      tmp[key.value] = ret.value 
      _i = ret.index

    else:
      raise RuntimeError(f"Unknown type '{toks[_i].type}'")

    if toks[_i].type != 'comma':  # multiple pairs? 
      break 

    _i+=1

  if toks[_i].type != 'obj_end':  # valid object? 
    raise Exception()  

  return gatheredValues(_i+1, tmp)   

ret = get_array(tokens)

print(ret.value)

