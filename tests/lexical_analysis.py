from rule_scanner import RuleScanner
from typing import Union 

RAW_RULES = { 
  'json' : [('json', r'(:object|array:)'), 
              ('object', r'(:\{!whitespace?pair*whitespace?,$whitespace?\}!:)'), 
              ('array', r'(:\[!whitespace?value*whitespace?,$whitespace?\]!:)'), 
              ('value', r'(:string|number|true|false|null|array|object:)'),  
              ('pair', r'(:string!whitespace?:!whitespace?value!:)'), 
              ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'), 
              ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'), 
              ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+')]
}

class UnknownFormatError(Exception): 
  def __init__(self, format): 
    self.str = f"Unknown format '{format}'." 
  
  def __str__(self): 
    return self.str 

class UnknownTypeError(Exception): 
  def __init__(self, type): 
    self.str = f"Unknown type for input rules '{type}'."
  
  def __str__(self): 
    return self.str 

class MissingFormatError(Exception): 
  def __str__(self): 
    return "Missing format; Verify the format is correct then retry." 


class Lexer(object): 

  def __init__(self, data:str, format:str='json', depth:Union[str, int]=1, raw_rules:Union[dict,list]=RAW_RULES): 

    self.tokens = InputScanner(self.scan_rules(format, raw_rules, depth), 
                               data, 
                               format if type(format) == str else None) 




  def scan_rules(self, format:str, raw_rules:Union[dict,list], depth:Union[str, int]) -> RuleScanner: 
    if type(raw_rules) == dict: 
      if format in raw_rules.keys(): 
        return RuleScanner(raw_rules[format], depth)
      else: 
        raise UnknownFormatError(format) 
    elif type(raw_rules) == list: 
      return RuleScanner(raw_rules, depth) 
    else: 
      raise UnknownTypeError(type(raw_rules)) 


class InputScanner(object): 
  def __init__(self, rules:dict, data:str, format:str): 
    if not format: 
      raise MissingFormatError() 

    self.rules = rules 
    self.data = data 

    ret = self.scan(self.rules[format])

  def scan(self, head): 
    if type(head) == tuple: 
      print(type(head), head)
      for i, arg in enumerate(head): 
        print(i, arg) 
        
    elif type(head) == str: 
      print(type(head), head)
    else: 
      raise TypeError 











