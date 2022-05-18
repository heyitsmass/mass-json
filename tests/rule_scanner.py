import re 
from typing import Union

class Rule(object):
  """Represents a Rule object which holds the necessary information fed into the input scanner module.

  Attributes
  ----------
      id : str
          The ID of the parent rule.
      delim : str
          The delimiter associated with the rule.
      tok_regex: str
          The regex token (pre-processing) for the re.match function.
      __str : str 
          The string for __repr__.

  Methods
  -------
      __repr__: 
          Outputs the information within the Rule depending on the depth value defined by the user (Default to 1). 

      __set_str(depth): 
          Set the string for __repr__ considering the depth value.

  """

  def __init__(self, depth:Union[str, int], id:str, delim:str=None, tok_regex:str=None):
    """Construct and hold the necessary information for a Rule object

    Parameters
    ----------
        depth : str, int
            Defines the depth of the information outputted when printing. 
            
            Defaults to 1 or 'moderate', Information stored is constant.

        id : str
            The ID the rule does or helps represent.

        delim : str, optional
            The associated delimiter with the rule. Defaults to None if not defined.

        tok_regex : str, optional 
            The associated regex token (pre-processing).
    """

    self.id = id
    self.delim = delim 
    self.tok_regex = tok_regex 
    self.__str = self.__set_str(depth) 

  def __repr__(self):
    return self.__str 

  def __set_str(self, depth:Union[str,int]): 
    """Set the string for __repr__ considering the depth value. 

    Raises an InputError if the depth value is unknown.

    Parameters
    ----------
        depth : str, int
            Defines the depth of the information outputted when printing. 
            
            Defaults to 1 or 'moderate', Information stored is constant.

    Returns
    -------
        An f string that represents the elements in the object. 
    """ 

    if depth in ['simple', 'simplified', 0]:
      return f"{self.tok_regex + (self.delim if self.delim else '')}"
    elif depth in ['intermediate', 'moderate', 1]: 
      return f"Rule(tok_regex={self.tok_regex}, delim={self.delim})"
    elif depth in ['advanced', 'complex', 2]:
      return f"Rule(id={self.id}, tok_regex={self.tok_regex}, delim={self.delim})"
    else: 
      raise InputError(depth) 


class DelimiterError(Exception): 
  def __init__(self, delim): 
    self._OR = '|'
    self.delim = delim
  
  def __str__(self): 
    return f"Invalid previous delimiter '{self.delim}' (must be {self._OR})"


class ParseError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 
  
  def __str__(self): 
    return f"Unable to parse '{self.rule}' (No previous rule found)"


class FormatError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 
  
  def __str__(self): 
    return f"Invalid format for rule '{self.rule}'"


class InputError(Exception): 
  def __init__(self, depth): 
    self.depth = depth 
  
  def __str__(self): 
    return f"Invalid user input '{self.depth}' for depth"


class RuleScanner(object):
  """Represents an iterable RuleScanner object, holding the parsed rules for the input scanner module. 

  Attributes
  ----------
      __rules : dict, private
            A private dictionary of stored rules after parsing accessed as 'id : rule'.

      __ids : list, private
            A private list of ids from the user defined raw_rules.

      __depth : str, int, private 
            A private, user defined output information depth level. Defaults to 1.

  Methods
  -------
      compile(raw_rules) -> dict: 
            Compiles the parsed rules into a formatted dictionary. 
  
      verify(rule) -> bool: 
            Verify the rule is formatted correctly prior to parsing.

      sanitize(raw_rule, delim='', count=0) -> list: 
            Split and sanitize the rule from the user delimiter. 

      parse(id, rule) -> tuple: 
            Parses and formats each rule from the sanitized list of rules.  

      set_rule(id, rule, i=None, tmp=None) -> Rule: 
            Generates and returns a Rule object from the input value.

      get_prev_delim(rule, i) -> str: 
            Returns the delimiter from the previous.

      get_ids(rules) -> list: 
            Returns a list of ids from the user defined raw_rules list. 

      keys(): 
            Returns a list of keys in __rules. 

      values(): 
            Returns a list of values in __rules. 

      items():
            Returns a set-like object of items in __rules.
  """

  def __init__(self, raw_rules:list, depth:Union[str,int]=1):  
    """Construct the necessary attributes for the RuleScanner class.

    Verifies and stores the depth is of correct type. 
    
    Collects a group of ids for the set_rule helper function. 
    
    Calls compile to parse and store the formatted rules. 

    Parameters
    ----------
        raw_rules: list
                User defined list of rules prior to parsing.    

        depth : str, int, optional 
                User defined depth value defining the amount of information outputting when printing each rule.  
    """

    self.__depth = self.__check_depth(depth) 
    self.__ids = self.get_ids(raw_rules) 

    self.__rules = self.compile(raw_rules)

  def compile(self, raw_rules:list) -> dict:
    """Compile the parsed rules into a formatted dictionary.

    Each rule will be a dictionary key with it's value being either a: 
      i)  Tuple of regex tokens 

      ii) Single regex token 
    
    Prepare a tuple of rules for the input scanner module.

    Parameters
    ----------
        raw_rules : list 
            The raw list of user defined rules to be verified and parsed.

    Returns
    -------
        final : dict 
            The dictionary of parsed rules.
    """

    final = dict() 
    for id, rule in raw_rules: 
      if '(:' in rule and ':)' in rule: 
        if not self.verify(rule):
          raise FormatError(rule)
        rule = self.sanitize(rule)  
        final[id] = self.parse(id, rule) 
      else: 
        final[id] = self.set_rule(id, rule) 
    return final 
  

  def verify(self, rule:str) -> bool:
    """Verify the rule is formatted correctly prior to parsing."""

    return re.Match == type(re.match(r'\(:(?:[^)]+?[!*$?|]?)*:\)', rule))


  def sanitize(self, raw_rule:str, delim:str='', count:int=0) -> list:
    """Split and sanitize the raw_rule from the user delimiter. 

    If count is specified, attempt to santize from 0 to <count> instances of the delimiter. 

    Delim defaults to an empty string.

    Split the rule based on pre-defined delimiters. This further prepares the rule for the parsing function.
    
    Parameters
    ----------
        raw_rule : str
              Raw input rule in string format.  

        delim : str, optional
              Delimiter to be removed from the array after splitting; 
              Sanitizes unecessary values from the re.split output. 

              Defaults to an empty string. 

        count : int, optional
              Number of times to remove the delimiter from the array; 
              Defaults to 0 (infinite) unless otherwise specified. 

    Returns
    -------
        rules : list
              Formatted array of split rules 
    """ 
    rules = re.split(r'([?|!*$])', raw_rule.strip('(:)'))

    if count <= 0: 
      while delim in rules: 
        rules.remove(delim)
    else: 
      for i in range(count): 
        rules.remove(delim)  
    return rules

    
  def parse(self, id:str, rule:list) -> tuple:
    """Parse and format each rule from the input. 

    Create a new tuple of parsed rules from the sanitized list of rules passed in from the compile function. 

    Formatting of data is handled by helper functions.

    Parameters
    ----------
        id : str
            Identifier of the parent rule being parsed.

        rule : list
            List of rules being parsed from the parent <id>.

    Returns
    -------
        A tuple of the parsed rule list
    """ 
    for i, tmp in enumerate(rule): 
      rule[i] = self.set_rule(id, rule, i, tmp) 
    return tuple(rule) 


  def set_rule(self, id:str, rule:Union[str,list], i:int=None, tmp:str=None) -> Rule:
    """Generate and return a Rule object from the input 

    Removes the delimiter from the main rule list and appends to the Rule object 
    
    Parameters
    ----------
        id : str
            The parent or rule identifier. 

            Parent identifier is expcted if rule is a list. 

            Rule identifier is expected if the rule is string. 

        rule : str, list
            A list of rules or a singular rule to be formed into a Rule object.

        i : int, optional 
            Current index from the rule being parsed. Default = None. 

            Expected if the input rule is a list or tmp is passed in.

        tmp : str, optional
            Temporary list or singular rule post parsing. Default=None. 

            Expected if the input rule is a list and i is passed in.  

    Returns
    -------
        A Rule object with associated information 
    """ 

    if not i and not tmp: 
      return Rule(self.__depth, id, None, ('(?P<%s>%s)' % (id, rule)))
    else: 
      if i+1 < len(rule): 
        ret = self.__set_rule(id, rule, i, tmp) 
        rule.remove(rule[i+1]) 
        return ret 
      else: 
        return Rule(self.__depth, id, self.get_prev_delim(rule, i), rule[i])


  def __set_rule(self, id:str, rule:str, i:int, tmp:str) -> Rule:
    """Helps generate Rule objects for rules not contained in the identifier list"""

    if tmp not in self.__ids: 
      return Rule(self.__depth, id, rule[i+1], '(?P<%s>%s)' % (id, tmp))
    return Rule(self.__depth, id, rule[i+1], rule[i])

  def get_prev_delim(self, rule:list, i:int) -> str:
    """Get the delimiter from the previous rule.

    Raises a ParseError if no previous delimiter exists.

    Raises a DelimiterError if the previous delimiter is not equal to <|>.

    Parameters
    ----------
        rule : list
          The current rule being parsed.

        i : int
          The current index of the passed rule. 

    Returns
    -------
        The previous delimiter if available.
    """ 

    if i-1 >= 0: 
      if rule[i-1].delim == '|': 
        return rule[i-1].delim 
      raise DelimiterError(rule[i-1][-1])
    raise ParseError(rule)
    
  def __check_depth(self, depth:Union[str, int]): 
    """Verify the type of depth, lowercase adjust for user input and return the value.

    Raises a TypeError if depth is not a string or integer. 

    Parameters
    ----------
        depth : str, int
            The associated user defined depth level. 

    Returns
    -------
        depth:
            A lowercase adjusted string or integer depending on input type.
    """
    if type(depth) == int: 
      return depth 
    elif type(depth) == str: 
      return depth.lower()
    else: 
      raise TypeError

  
  def get_ids(self, rules:list): 
    """Return a list of ids in the rules list.

    Parameters
    ----------
        rules : list
            A list of tuples seperated by (id, rule). 

    Returns
    -------
            A list of ids from the input. 
    """
    return [id for id, rule in rules] 
  

  def __iter__(self): 
    return iter(self.__rules) 
  
  def __getitem__(self, key:any) -> any: 
    return self.__rules[key] 
  
  def keys(self): 
    """Return a list of keys in __rules"""
    return self.__rules.keys()
  
  def values(self): 
    """Return a list of keys in __rules"""
    return self.__rules.values() 
  
  def items(self): 
    """Return a set-like object of items in __rules"""
    return self.__rules.items() 

