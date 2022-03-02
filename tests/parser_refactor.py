# *************** Imports ************** # 
from typing import NamedTuple, Union
import argparse
import re 

# ********* Argparse Arguments ********* # 
args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="set the name for the input file")
args = vars(args.parse_args())
__filename__ = args['filename'] 


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
    A class that represents a rule error 
      Rules that are improperly created will be rejected and a RuleError is thrown 
    
    Parameters
    ----------
      id : str 
        The ID of the errored rule 
      data : str 
        The associated rule data 
    
    Methods 
    -------
      __init__ : 
        Constructs the rule error 
      __str__ : 
        Returns the exception string 
  """
  def __init__(self, id:str, data:str) -> None:
    self.id = id 
    self.data = data 

  def __str__(self) -> str: 
    return "Error reading rule '%s':\n\t%s" % (self.id, self.data) 

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
class Capture(NamedTuple):
  """
    A class to represent a capture tuple
    
    Attributes
    ----------
      value : str 
        holds the information of the capture 
      index : int 
        the end index from the main data the rule was captured from
      parent : str 
        id of the parent rule    
  """
  value:str 
  index:int 
  parent:str 

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
  def __init__(self, rules): 
    self.rules = self.__parse_rules(rules) 
    
  def __parse_rules(self, rules): 
    for arg in rules: 
      id = arg[0] 
      rule = arg[1] 

      print(id, ':', rule) 
      rule = self.__capture(id, rule) 

    #print(rules) 
  
  def __capture(self, id, rule): 
    tmp = re.split(r'\%\)|\%\(', rule)
    #tmp = rule.split('%)').split('%(')
    print(tmp)
    ...

class Scanner(object):
  def __init__(self, data, rules): 
    self.data = data 
    self.rules = Rules(rules) 


# ************* Main 'Function' ************* # 
if __name__ == "__main__":
  data = open(__filename__, 'r').read()
  rules = [
      ('object',
       r'{+%(whitespace+string+whitespace+colon+whitespace+value+comma+newline%)+}'),
      ('value',
          r'whitespace+%(string|number|object|array|boolean|NULL%)+whitespace'),
      ('string',
          r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('array',
          r'\[+%(whitespace+value+comma+whitespace+newline%)+\]+newline'),
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
