from typing import NamedTuple 

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
  def __init__(self, data:str):
    """
    """
    self.data = str 

  def __str__(self): 
    return "Unable to process file: Invalid token '%s'" % self.data 


class CaptureError(Exception):
  """
  """
  def __init__(self):
    """
    """
    ...

class FormatError(Exception):
  """
  """
  def __init__(self):
    """
    """ 
    ...

class RuleError(Exception):
  """
  """
  def __init__(self):
    """
    """
    ...

class ScanError(Exception):
  """
  """
  def __init__(self):
    """
    """ 
    ... 

