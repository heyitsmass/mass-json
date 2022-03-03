# *************** Imports ************** # 
from typing import Iterator, NamedTuple, Union
import argparse
import re 

# ********* Argparse Arguments ********* # 
args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args.add_argument('--debug', action='store_true', help="Enable debug")

args = vars(args.parse_args())
__FILENAME__ = args['filename'] 
__DEBUG__ = args['debug'] 


# ********** Custom Exceptions ********** # 
class TokenError(Exception):
  """
    A class that represents a Token Error:
      Unidentifiable tokens should raise a TokenError with the 
      associated information 
    
    Attributes
    ----------
      data : str
        Invalid data
    
    Methods
    -------
    __init__ : 
      Constructs the token error 
    __str__ : 
      Returns the exception string 

  """
  def __init__(self, data:str) -> None:
    self.data = str 

  def __str__(self) -> str: 
    return "Unable to process file: Invalid token '%s'." % self.data 


class CaptureError(Exception):
  """
    A class that represents a Capture Error 
      Errors capturing a rule within the capture function should raise a CaptureError. 
      Similarly, Rules with multiple sets of captures will raise an exception 

    Parameters
    ----------
      id : str 
      rule : str
      capture : str 

    Methods
    -------
      __init__ : 
        Constructs the capture error 
      __str__ : 
        Returns the exception string 

  """
  def __init__(self, id:str, rule:str, capture:str=None) -> None:
    self.id = id 
    self.rule = rule 
    self.capture = capture 
  
  def __str__(self) -> str: 
    return "Error capturing '%s':\n\t%s:\n\t%s" % (self.id, self.rule, self.capture) 
  

class FormatError(Exception):
  """
    A class to represent a general format issue. 
      If no other exception has occured, there is likely a format issue in the main data 
      which will throw an exception 
    
    Parameters
    ----------
      None
    
    Methods
    -------
    __str__ : 
      Returns the exception string
  """
  def __str__(self) -> str: 
    return "Error: Input file format is invalid."


class RuleError(Exception):
  """
  """
  def __init__(self, operand:str, rule:str) -> None:
    self.operand = operand
    self.rule = rule 

  def __str__(self) -> str: 
    return "Unsupported operand type '%s' in tuple:\n\t%s" % (self.operand, self.rule)  

class ScanError(Exception):
  """
    A class to represent a scan error 
      Any error within the scanner during the tokenizing process that isn't associated with a capture, grammar, or rule error 
      should raise a scan error exception 

    Parameters
    ----------
      None 
    
    Methods
    -------
      __str__ : 
        Returns the exception string 
  """
  def __str__(self) -> str: 
    return "Error: Unable to scan file properly (is the format valid?)"


# ************** Custom Types ************** # 
class Capture(object):
  """
    A class to represent a capture tuple
    
    Attributes
    ----------
      parent : str 
        parent rule data
      capture : str 
        holds the information of the capture 
  """
  def __init__(self, parent:str, capture:str=None) -> None: 
    self.parent = parent 
    self.capture = capture 

  def __setitem__(self, index:any, value:any) -> any: 
    if index == 0: 
      self.parent = value
    elif index == 1: 
      self.capture = value 
    else: 
      raise Exception
    return 
  
  def __getitem__(self, index:any) -> any: 
    if index == 0: 
      return self.parent 
    elif index ==  1: 
      return self.capture 
    raise Exception 

class Token(NamedTuple):
  """
    A class to represent a token tuple

    Attributes
    ----------
      type : str 
        The type of token that was received 
      value : str 
        The associated data within the token 
      line : int 
        The line number the data was found at 
  """
  type:str 
  value:str 
  line:int 

class Rules(object): 
  def __init__(self, rules:list) -> None: 
    self.__rules = self.__parse(rules) 

    if __DEBUG__: print("\u001b[1m\u001b[32mrules:", self.__rules, '\u001b[0m') 
    
  def __parse(self, rules:list) -> dict: 
    __ids = [id for id, rule in rules]
    __ret = dict()
    for arg in rules: 
      id = arg[0] 
      rule = arg[1] 

      if __DEBUG__: print("\u001b[1m\u001b[31minput:", id, ':', rule, '\u001b[0m')

      capture = self.__capture(id, rule) 
     
      if capture[1]: 
        capture[0] = capture[0].split('+') 
        capture[1] = re.split(r'([|+])', capture[1]) 
        c = 0 
        final = list() 
        while c+1 < len(capture[1]): 
          if c == 0: 
            final.append(capture[1][c]) 
            c+=1
            continue 
          tmp = capture[1][c] + capture[1][c+1]
          final.append(tmp) 
          c+=2
        # Convert to tuple to prevent further modification 
        capture[1] = tuple(final)

        a = 0
        while a < len(capture[0]): 
          if 'capture' in capture[0][a]: 
            capture[0][a] = capture[1] 
          elif capture[0][a] not in __ids: 
            capture[0][a] = '(?P<%s>%s)'% (id, capture[0][a])
          a+=1 
          continue 
        # Convert to tuple to prevent further modification 
        capture[0] = tuple(capture[0]) 

        #if __DEBUG__: print("\u001b[1m\u001b[33m1a.", capture[0], '\n\t', capture[1], '\u001b[0m')    # Debug
      else: 
        capture[0] = '(?P<%s>%s)'% (id, capture[0])
        #if __DEBUG__: print("\u001b[1m\u001b[36m1b.", capture[0], '\u001b[0m')    # Debug
      __ret[id] = capture[0] 

      if __DEBUG__: print("\u001b[1m\u001b[33mparse:\t->", id, capture[0], '\u001b[0m')    # Debug
    return __ret 
  
  def __iter__(self) -> Iterator: 
    return iter(self.__rules) 
  
  def __getitem__(self, key:any) -> any: 
    return self.__rules[key] 
  
  def __setitem__(self, key:any, value:any) -> any: 
    self.__rules[key] = value 
  
  def keys(self): 
    return self.__rules.keys()
  
  def values(self): 
    return self.__rules.values() 
  
  def items(self): 
    return self.__rules.items() 
  
  def __capture(self, id:str, rule:str) -> Capture: 
    __tmp = re.split(r'(\(\%|\%\))', rule)
    if len(__tmp) > 1: 
      i = 0
      while i < len(__tmp): 
        if __tmp[i] == '(%': 
          rule = rule.replace(__tmp[i+1], 'capture')
          return Capture(rule, __tmp[i+1]) 
        i+=1
    elif len(__tmp) == 1: 
      return Capture(rule)
    raise CaptureError(id, rule) 
    

class Scanner(object):
  def __init__(self, data:str, rules:list): 
    self.__data = data 
    self.__rules = Rules(rules) 
    self.__lineno = 0 

    if __DEBUG__: 
      for key in self.__rules: 
        print(key, ':', self.__rules[key])
    
  def scan(self): 
    ids = list(self.__rules.keys()) 
    default = self.__rules[ids[0]]

    #print(default) 

    for arg in default: 
      if type(arg) == str: 
        tok_regex = arg 
        match = re.match(tok_regex, self.__data) 

        if match: 
          kind = match.group() 
          value = match.lastgroup

          print(Token(value, kind, self.__lineno)) 

          self.__data = re.sub(tok_regex, '', self.__data, 1) 
        #raise TokenError(tok_regex) 
      elif type(arg) == tuple: 
        #print(arg) 
        self.__scan_tuple(arg, ids) 


    


        #print(arg) 
      #print(arg) 

  def __scan_tuple(self, rule:tuple, ids:list): 
    #print(rule) 
    prev = '' 
    i = 0 
    #print(len(rule)) 
    while i < len(rule):
      if type(rule[i]) == tuple: 
        self.__scan_tuple(rule[i], ids)
        #if match: 
        #  print("match %s" % match)
        #  print(rule[i]) 
        #  i-=1
        #  continue 
        i+=1 
        continue  
      elif '?P' in rule[i]: 
        #print(rule[i]) 
        tok_regex = rule[i] 
        match = re.match(tok_regex, self.__data)
        if match: 
          value = match.group() 
          kind = match.lastgroup
          print(Token(kind, value, self.__lineno)) 
          self.__data = re.sub(tok_regex, '', self.__data, 1) 
          i+=1
          continue   
        else: 
          #raise Exception("%s was required" % tok_regex) 
          return match 

      delim = '' 
      tmp = '' 
      if rule[i] not in ids: 
        delim = rule[i][0] 
        tmp = rule[i][1:len(rule[i])] 
      else: 
        tmp = rule[i] 

      #print(tmp, delim, end=' ') 
      if delim == '+': 
        #print("Required")
        tok_regex = self.__rules[tmp]
        if type(tok_regex) == tuple: 
          self.__scan_tuple(tok_regex, ids) 
          i+=1 
          continue 
        match = re.match(tok_regex, self.__data)
        if match:
          prev = match 
          value = match.group() 
          kind = match.lastgroup
          print(Token(kind, value, self.__lineno)) 
          self.__data = re.sub(tok_regex, '', self.__data, 1)
        elif not match and tmp in ['whitespace', 'comma', 'newline']:
          
          if type(rule) == tuple and i+1 >= len(rule) and prev:  
            print("rule") 
          i+=1 
          continue 
        elif not match: 

          raise Exception("%s was required" % tok_regex) 
        
      elif delim == '|': 
        #print("Optional")
        tok_regex = self.__rules[tmp]
        #print(tok_regex) 
        if type(tok_regex) == tuple: 
          self.__scan_tuple(tok_regex, ids) 
          i+=1
          continue 
          return 
        match = re.match(tok_regex, self.__data) 

        if match: 
          value = match.group() 
          kind = match.lastgroup 
          print(Token(kind, value, self.__lineno)) 
          self.__data = re.sub(tok_regex, '', self.__data, 1) 
        else: 
          i+=1 
          continue 
          raise Exception 
      else: 
        tok_regex = self.__rules[tmp] 

        match = re.match(tok_regex, self.__data) 
        if match: 
          value = match.group() 
          kind = match.lastgroup
          print(Token(kind, value, self.__lineno)) 

          self.__data = re.sub(tok_regex, '', self.__data, 1) 
        elif not match and tmp == 'whitespace': 
          i+=1 
          continue
        else:
          if not match and rule[i+1][0] == '|': 
            i+=1
            continue 
          print(tmp, tok_regex) 
          raise Exception 
      
      if i+1 >= len(rule) and match:
        i = 0
        continue 
          #print("Repeat") 
      i+=1 
    return match 


# ************* Main 'Function' ************* # 
if __name__ == "__main__":
  data = open(__FILENAME__, 'r').read()
  rules = [
      ('object',
       r'{+(%whitespace+string+whitespace+colon+whitespace+value+comma+newline%)+}'),
      ('value',
          r'whitespace+(%string|number|object|array|boolean|NULL%)+whitespace'),
      ('string',
          r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('array',
          r'\[+(%whitespace+value+comma+whitespace+newline%)+\]+newline'),
      ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
      ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
      ('boolean', r'true|false'),
      ('newline', r'\n'),
      ('NULL', r'null'),
      ('colon', r':'),
      ('comma', r','),
      ('mismatch', r'.')
  ]

  scanner = Scanner(data, rules)

  scanner.scan() 