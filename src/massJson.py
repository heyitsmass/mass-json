from tokenType import Token
import re

def scan(text:str):
  """ 
    
  """
  return __json()._scan(text)

  
class __json: 
  def __init__(self): 
    self.primitives = [ 
      'string', 'number', 'boolean', 'null'
    ]

    self.expressions = [ 
      'obj_start', 'arr_start'
    ]
  
  def _scan(self, text): 
    self.iter = self.tokenize(text)

    for curr in self.iter: 
      match curr.type: 
        case 'obj_start': 
          return self.get_object(next(self.iter))
        case 'arr_start': 
          return self.get_array(next(self.iter)) 
        case _: 
          raise RuntimeError(f"Type '{curr.type}' requires implementation")

  def get_array(self, curr:Token) -> list: 
    arr = list() 
    while curr: 
      if curr.type in self.primitives: 
        arr.append(curr.value) 
        curr = next(self.iter) 
      
      elif curr.type in self.expressions: 
        match curr.type:
          case 'obj_start': 
            ret = self.get_object(next(self.iter)) 
          case 'arr_start': 
            ret = self.get_array(next(self.iter)) 
          
        
        arr.append(ret) 
        curr = next(self.iter) 
      

      if curr.type != 'comma': 
        break 
      curr = next(self.iter) 
    
    if curr.type != 'arr_end': 
      raise Exception

    return arr 

  def get_object(self, curr:Token) -> dict: 

    tmp = dict() 

    while curr: 
      if curr.type != 'string': #valid key? 
        break 

      key = curr 
      curr = next(self.iter) 

      if curr.type != 'colon': 
        raise Exception(curr) 
      
      curr = next(self.iter) 

      ret = None 
      if curr.type in self.primitives: #scan primitive value 
        ''' type conversions '''
        tmp[key.value] = curr.value 
        curr = next(self.iter)  
      
      elif curr.type in self.expressions: #scan expression value 

        match curr.type: 
          
          case 'obj_start': 
            ret = self.get_object(next(self.iter))
          case 'arr_start': 
            ret = self.get_array(next(self.iter)) 
        
        tmp[key.value] = ret 
        curr = next(self.iter)  
      
      else: 
        raise RuntimeError(f"Unexpected type '{curr.type}'") 

      if curr.type != 'comma': #multiple pairs? 
        break 

      curr = next(self.iter) 
    
    if curr.type != 'obj_end': #valid object?  
      raise Exception(curr)
    
    return tmp 

  def tokenize(self, input:str): 
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
      for mo in re.finditer(tok_regex, input):
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