import re 
from dataclasses import dataclass
from typing import Any 


@dataclass 
class Value: 
  kind:str 
  raw_value:Any
  flag:bool=False

@dataclass
class Pair: 
  key:str 
  value:Value

class _json_: 
  def __init__(self, text): 
    self.text, self.size = text, len(text) 
    self.tokens = { 
      'STRING' : r'\"((?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?)\"', 
      'NUMBER' : r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?', 
      'BOOLEAN' : r'true|false', 'NULL' : r'null', 
      'WS' : r'\s*', 'NEWLINE' : r'\n', 'COLON' : r':', 'COMMA' : r',', 
      'DICT_START' : r'\{', 'DICT_END' : r'\}', 'ARR_START' : r'\[','ARR_END' : r'\]',
      'MISMATCH' : r'.' 
    } 
    self.line_num = 0

    data, index = self.object() 

    if not data: 
      data, index = self.array()  

    if index != self.size: 
      raise RuntimeError("EOF expected") 

  def object(self, index=0): 
    ret = dict()   
    start = re.match(self.tokens['WS']+self.tokens['DICT_START']+self.tokens['WS'], self.text[index:self.size])

    if not start: 
      return None, index 

    index += start.span()[1] 
    flag = True 
    count = 0
    pair = None 
    while index < self.size: 
      pair, index = self.pair(index)  

      if not pair: 
        break 

      if pair.value and not flag: 
        raise RuntimeError("Expected ',' on line") 

      print(pair.key, pair.value.raw_value)

      ret[pair.key] = pair.value.raw_value 

      flag = pair.value.flag 

      count += 1 

    if flag and not pair and count > 0: 
      raise RuntimeError("Unexpected ',' on line")  

    end = re.match(self.tokens['WS']+self.tokens['DICT_END']+self.tokens['WS'], self.text[index:self.size])

    if not end: 
      raise RuntimeError("Expected '}' on line") 

    return ret, index+end.span()[1] 

  def array(self, index=0): 
    ret = list() 
    start = re.match(self.tokens['WS']+self.tokens['ARR_START']+self.tokens['WS'], self.text[index:self.size])

    if not start: 
      return None, index 

    index += start.span()[1] 
    val = None 
    count = 0 
    flag = True 
    while index < self.size: 
      val, index = self.value(index)  
        
      if not val: 
        break  

      if val.raw_value and not flag: 
        raise RuntimeError(f"Expected ',' on line")  
      
      ret.append(val.raw_value)  

      print(val) 
    
      flag = val.flag 
      count += 1 

    if flag and not val and count > 0: 
      raise RuntimeError("Unexpected ',' on line")

    end = re.match(self.tokens['WS']+self.tokens['ARR_END']+self.tokens['WS'], self.text[index:self.size])

    if not end: 
      raise RuntimeError("Expected ']' on line")   
    
    return ret, index + end.span()[1] 

  def value(self, index=0, stmts=['STRING', 'NUMBER', 'BOOLEAN', 'NULL']):
    flag, kind = False, None 
    
    tok_regex = '|'.join('(?P<%s>%s)' % (key, self.tokens[key]) for key in stmts)
    match = re.match(tok_regex, self.text[index:self.size]) 

    if match: 
      kind = match.lastgroup
      value = self.convert(match.group(), kind) if kind != 'STRING' else match.groups()[1]
      
      index += match.span()[1] 

    else: 
      for func in [self.object, self.array]: 
        value, index = func(index)  
        if value or value in [dict(), list()]: 
          kind = type(value) 
          break 
          
    if not kind: 
      return None, index 
      raise RuntimeError("Missing value on line")  

    cma_regex = self.tokens['WS']+self.tokens['COMMA']+self.tokens['WS']
    comma = re.match(cma_regex, self.text[index:self.size])  
    if comma: 
      index += comma.span()[1] 
      flag = True 

    return Value(kind, value, flag), index 
    
  def key(self, index=0): 
    
    tok_regex = r'\"((?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?)\"(\s*)'

    key = re.match(tok_regex, self.text[index:self.size]) 
    
    if not key: 
      return None, index 

    return key.groups()[0]+key.groups()[1], index + key.span()[1] 
  
  def pair(self, index=0): 
    k, index = self.key(index) 

    col_regex = self.tokens['COLON'] + self.tokens['WS']

    colon = re.match(col_regex, self.text[index:self.size])  
    
    if not colon: 
      return None, index 
      raise RuntimeError("Expected ':' on line") 

    index += colon.span()[1]

    t, index = self.value(index)  

    if k and t: 

      return Pair(k, t), index

    return None, index 

  def convert(self, value, kind): 
    match kind: 
      case 'NUMBER': 
        if '.' in value: 
          return float(value) 
        return int(value) 
      case 'BOOLEAN': 
        return bool(value) 
      case 'NULL': 
        return None  
      case '_': 
        raise RuntimeError(f'Unexpected type {kind}') 


def load(text:str) -> _json_: 
  return _json_(text) 


__filename__ = 'large-file.json' 

data = load(open(__filename__, 'r').read()) 


 