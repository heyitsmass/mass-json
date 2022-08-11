from doctest import run_docstring_examples
import re 
from dataclasses import dataclass
from typing import Any 


@dataclass 
class Value: 
  kind:str 
  value:Any
  flag:bool=False

@dataclass 
class Pair: 
  def __init__(self, key, value): 
    self.key = key 
    self.value = value.value 
    self.kind = value.kind 
    self.flag = value.flag 

  def __repr__(self):  
    return f"Pair(key={self.key}, value={self.value}, kind={self.kind}, flag={self.flag})" 


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

    # object scan 
    data, index = self.scan(value=self.pair)

    if not data: 
      data, index = self.scan(value=self.value)  
    
    if index != self.size: 
      raise RuntimeError("EOF expected") 


  def scan(self, value, index:int=0): 
    if value == self.pair:  #object scan 
      ret = dict() 
      start_regex = self.tokens['DICT_START'] 
      end_regex = self.tokens['DICT_END']  
    else: 
      ret = list() 
      start_regex = self.tokens['ARR_START']  
      end_regex = self.tokens['ARR_END']

    start = re.match(self.tokens['WS'] + start_regex + self.tokens['WS'], self.text[index:self.size])  

    if not start: 
      return None, index
    
    index += start.span()[1]  
    flag, count, attr = True, 0, None  

    while index < self.size: 
      attr, index = value(index)

      if not attr: 
        break  

      if attr.value and not flag: 
        raise RuntimeError(f"Expected ',' on line")  
      
      if type(attr) == Pair: 
        ret[attr.key] = attr.value
      else: 
        ret.append(attr.value)

      #print(attr)   
      
      flag = attr.flag  
      count += 1  

    if flag and not attr and count > 0: 
      raise RuntimeError(f"Unexpected ',' on line {...}")

    end = re.match(self.tokens['WS']+end_regex+self.tokens['WS'], self.text[index:self.size])  

    if not end: 
      raise RuntimeError(f"Expected {end_regex} on line {...}") 
    
    return ret, index + end.span()[1]

  def value(self, index=0, stmts=['STRING', 'NUMBER', 'BOOLEAN', 'NULL']):
    flag, kind, value = False, None, None
    
    tok_regex = '|'.join('(?P<%s>%s)' % (key, self.tokens[key]) for key in stmts)
    match = re.match(tok_regex, self.text[index:self.size]) 

    if match: 
      kind = match.lastgroup
      match kind: 
        case 'STRING': 
          value = match.groups()[1]
        case 'NUMBER':
          if '.' in match.group(): 
            value = float(match.group()) 
          else: 
            value = int(match.group()) 
        case 'BOOLEAN': 
          value = bool(match.group()) 
        case '_': 
          value = None 

      index += match.span()[1] 
    
    else: 
      for func in [self.pair, self.value]: 
        value, index = self.scan(func, index) 
        if value or value in [dict(), list()]: 
          kind = type(value) 
          break  

    if not kind: 
      return None, index 

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

    index += colon.span()[1]

    t, index = self.value(index)  

    if k and t: 

      return Pair(k, t), index

    return None, index 

def load(text:str) -> _json_: 
  return _json_(text) 
