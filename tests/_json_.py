import re 
from dataclasses import dataclass
from typing import Any 


@dataclass 
class Token: 
  kind:str 
  value:Any
  flag:bool=False

@dataclass
class Pair: 
  key:str 
  token:Token

class _json_: 
  def __init__(self, text): 
    self.text, self.size = text, len(text) 
    self.tokens = { 
      'STRING' : r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"', 
      'NUMBER' : r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?', 
      'BOOLEAN' : r'true|false', 'NULL' : r'null', 
      'WS' : r'\s*', 'NEWLINE' : r'\n', 'COLON' : r':', 'COMMA' : r',', 
      'DICT_START' : r'\{', 'DICT_END' : r'\}', 'ARR_START' : r'\[','ARR_END' : r'\]',
      'MISMATCH' : r'.' 
    } 
    self.line_num = 0

    self.data = self.scan() 
    
  def scan(self): 
    data, index = self.__scanObj() 

    if not data: 
      data, index = self.__scanArr() 

    return data 

  
  def __scanObj(self, index=0): 
    ret = dict() 
    start = re.match(self.tokens['WS']+self.tokens['DICT_START']+self.tokens['WS'], self.text[index:self.size])
    pair = None 
    if start: 

      index += start.span()[1] 
      flag = True 
      count = line_num = 0
      while True: 
        pair, index = self.__getPair(index) 

        if not pair: 
          break    

        if pair.token and not flag: # or pair.token in [dict(), list(), '', 0] and not flag: 
          raise RuntimeError(f"Expected ',' on line {line_num}") 

        ret[pair.key] = pair.token.value

        space = re.match(self.tokens['WS'], self.text[index:self.size]) 
        if space: 
          index += space.span()[1]  
        flag = pair.token.flag
        count+=1 
      
      if flag and not pair and count > 0: 
        raise RuntimeError(f"Unexpected ',' on line {line_num}") 
      
      end = re.match(self.tokens['WS'] + self.tokens['DICT_END']+self.tokens['WS'], self.text[index:self.size])  

      if end: 
        index += end.span()[1]  
        return ret, index

    return None, index 

  def __scanArr(self, index=0): 
    ret = list() 
    start = re.match(self.tokens['WS']+self.tokens['ARR_START']+self.tokens['WS'], self.text[index:self.size])
  
    if start: 
      index += start.span()[1] 
      flag = True 
      count = line_num = 0

      while True: 
        token, index = self.__getValue(index)  

        if not token: 
          break  
          
        if token.kind and not flag: 
          raise RuntimeError(f"Expected ',' on line on {line_num}") 

        ret.append(token.value)  

        flag = token.flag 

        space = re.match(self.tokens['WS'], self.text[index:self.size])  

        index += space.span()[1] if space else 0  

        count += 1 

      if flag and not token and count > 0: 
        raise RuntimeError(f"Unexpected ',' on line {line_num}")

      end = re.match(self.tokens['WS']+self.tokens['ARR_END']+self.tokens['WS'], self.text[index:self.size]) 

      if end: 
        index += end.span()[1]
        return ret, index  

    return None, index 

  
  def __getValue(self, index=0): 
    tok_regex = self.tokens['WS']+self.tokens['COMMA'] 
    for kind in ['STRING', 'NUMBER', 'BOOLEAN', 'NULL', self.__scanObj, self.__scanArr]: 
      if not callable(kind):  
        value = re.match(self.tokens[kind], self.text[index:self.size]) 
        if value: 
          index += value.span()[1]  
          comma = re.match(tok_regex, self.text[index:self.size]) 
          if comma: 
            index += comma.span()[1]  
          return Token(kind, self.__convert(value.group(), kind), True if comma else False), index 
      else: 
        value, index = kind(index)  
        if value or value in [dict(), list()]: 
          comma = re.match(tok_regex, self.text[index:self.size]) 
          if comma: 
            index += comma.span()[1]  
          return Token(kind, value, True if comma else False), index 
    return None, index 

  def __getPair(self, index=0): 
    key, index = self.__getKey(index)
    line_num = 0 
    if key: 
      colon = re.match(self.tokens['COLON']+self.tokens['WS'], self.text[index:self.size])  

      if colon: 
        index += colon.span()[1]
      else: 
        raise RuntimeError(f"Missing ':' on line {line_num}") 

      token, index = self.__getValue(index)   

      if not token: 
        raise RuntimeError(f'Missing value on line {line_num}')  
      
      #print(Pair(key, token)) 

      return Pair(key, token), index  
    
    return None, index 

  def __getKey(self, index=0):
    key = re.match(self.tokens['STRING']+self.tokens['WS'], self.text[index:self.size]) 

    if key: 
      if '\n' in key.group(): 
        self.line_num += 1 

      index += key.span()[1] 
      return self.__convert(key.group(), 'STRING'), index  
    
    return None, index 

  
  def __convert(self, value:str, kind:str) -> Any: 
    line_num = 0 
    match kind: 
      case 'STRING': 
        l, r = value.find('\"'), value.rindex('\"')
        return value[:l] + '' + value[l+1:r] + '' + value[r+1:]
      case 'BOOLEAN': 
        return bool(value) 
      case 'NUMBER': 
        if '.' in value: 
          return float(value) 
        return int(value) 
      case 'NULL': 
        return None 
      case _: 
        raise RuntimeError(f'Unexpected type {kind} on line {line_num}') 


  


def load(text:str) -> _json_: 
  return _json_(text) 

 