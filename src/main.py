import re 

from dataclasses import dataclass

@dataclass 
class Pair: 
  kind:str
  key:str 
  value:str 
  column:int=-1 
  flag:bool=False

@dataclass 
class Token: 
  kind:str
  value:str 
  column:int=-1
  flag:bool=False 
  
class JSON: 
  def __init__(self, text:str): 
    self.text = text 
    self.size = len(text) 

    self.tokens = { 
      'STRING' : r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"', 
      'NUMBER' : r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?', 
      'BOOLEAN' : r'true|false', 'NULL' : r'null', 
      'WS' : r'\s*', 'NEWLINE' : r'\n', 'COLON' : r':', 'COMMA' : r',', 
      'DICT_START' : r'\{', 'DICT_END' : r'\}', 'ARR_START' : r'\[','ARR_END' : r'\]',
      'MISMATCH' : r'.' 
    } 

    self.data, index = self.getObject() 

    if not self.data: 
      self.data, index = self.getArray() 


  def getObject(self, curr=0) -> dict: 
    obj = dict() 

    start = re.match(self.tokens['WS']+self.tokens['DICT_START']+self.tokens['WS'], self.text[curr:self.size]) 

    if start: 
      curr += start.span()[1] 

      flag = True 
      count = 0

      while True: 
        pair, curr = self.getPair(curr) 

        if not pair: 
          break 

        if pair.value and not flag: 
          raise RuntimeError(f"Expected ',' on line") 

        flag = pair.flag 

        obj[pair.key] = pair.value 

        space = re.match(self.tokens['WS'], self.text[curr:self.size]) 

        if space: 
          curr += space.span()[1]

        count += 1
        
      if flag and not pair and count > 0: 
        raise RuntimeError(f"Unexpected ',' on line")  
    
      end = re.match(self.tokens['WS']+self.tokens['DICT_END']+self.tokens['WS'], self.text[curr:self.size]) 

      if end: 
        curr += end.span()[1]
        return obj, curr 

    return None, curr 


  def getArray(self, curr=0) -> list: 
    arr = list() 
    start = re.match(self.tokens['WS']+self.tokens['ARR_START']+self.tokens['WS'], self.text[curr:self.size]) 

    if start: 
      curr += start.span()[1] 
      count = 0
      flag = True 

      while True: 
        value, kind, comma, curr = self.getValue(curr) 
        
        if kind and not flag: 
          raise RuntimeError(f"Expected ',' on line") 

        if not kind: 
          break  

        #print(value, kind, comma, curr) 

        arr.append(value)  

        flag = comma 

        space = re.match(self.tokens['WS'], self.text[curr:self.size]) 

        if space: 
          curr += space.span()[1]

        count += 1

      if flag and not kind and count > 0: 
        raise RuntimeError(f"Unexpcted ',' on line") 

      end = re.match(self.tokens['WS']+self.tokens['ARR_END']+self.tokens['WS'], self.text[curr:self.size]) 

      if end: 
        curr += end.span()[1]
        return arr, curr       

    return None, curr 

  def getValue(self, curr=0):
    # Returns: raw value, associated type, if there exists a comma after the raw value, and the index in the scan 

    for kind in ['STRING', 'NUMBER', 'BOOLEAN', 'NULL', self.getObject, self.getArray]: 
      if type(kind) == str: 
        value = re.match(self.tokens[kind], self.text[curr:self.size]) 
        if value: 
          curr += value.span()[1]

          comma = re.match(self.tokens['WS']+self.tokens['COMMA'], self.text[curr:self.size])

          if comma: 
            curr += comma.span()[1] 

          #print(f'value={value.group()}, {kind=}, {comma=}, {curr=}')

          return self.convertValue(value.group(), kind), kind, True if comma else False, curr  
      else: 
        value, curr = kind(curr)  

        if value or value in [dict(), list()]: 
          comma = re.match(self.tokens['WS']+self.tokens['COMMA'], self.text[curr:self.size])

          if comma: 
            curr += comma.span()[1] 
              
          return value, type(value), True if comma else False, curr 
        

    return None, None, None, curr  

  def getPair(self, curr=0): 

    key, curr = self.getKey(curr)

    if key: 
      #raise RuntimeError(f'Missing key on line')  

      colon = re.match(self.tokens['COLON'] + self.tokens['WS'], self.text[curr:self.size]) 

      if colon: 
        curr += colon.span()[1]
      else: 
        raise RuntimeError(f"Missing ':' on line")  
      
      value, kind, comma, curr = self.getValue(curr)

      #print(key, value, kind) 

      if kind: 
        return Pair(kind, key, value, flag=comma), curr 

      if key: 
        raise RuntimeError(f'Missing value on line')  
    
    return None, curr 


  def getKey(self, curr=0, kind:str='STRING'): 
    # Returns: raw key, associated type, the current index of the scan 

    tok_regex = self.tokens[kind] + self.tokens['WS']  

    key = re.match(tok_regex, self.text[curr:self.size])

    if key: 
      curr += key.span()[1]  
      return self.convertValue(key.group(), kind), curr 

    return None, curr

    

  def convertValue(self, value:str, kind:str) -> str|int|float|bool|None: 
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
        raise RuntimeError(f'Unexpected type {kind} on line') 

def load(text): 
  return JSON(text) 
  