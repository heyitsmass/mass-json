import re 
from typing import Union 


class DelimiterError(Exception): 
  def __init__(self, delim): 
    self.__delim = delim
  
  def __str__(self): 
    return f"Invalid previous delimiter '{self.__delim}' (must be |)"


class ParseError(Exception): 
  def __init__(self, rule): 
    self.__rule = rule 
  
  def __str__(self): 
    return f"Unable to parse '{self.__rule}' (No previous rule found)"


class FormatError(Exception): 
  def __init__(self, rule): 
    self.__rule = rule 
  
  def __str__(self): 
    return f"Invalid format for rule '{self.__rule}'"


class InputError(Exception): 
  def __init__(self, depth): 
    self.__depth = depth 
  
  def __str__(self): 
    return f"Invalid user input '{self.__depth}' for depth"


class TerminationError(Exception): 
  def __str__(self): 
    return f"Unterminated sub_rule set (Missing (: or :) symbols)"


class Rule(object): 
  def __init__(self, id, tok_regex, delim, next_regex, next_delim, depth:int=2):
    self.rule = id 
    self.tok_regex = tok_regex 
    self.delim = delim 
    self.next = next_regex 
    self.next_delim = next_delim 
    self.depth = depth 
  
  def get_msg(self, depth): 
    match depth: 
      case 0: 
        return f"{self.tok_regex + self.delim}"
      case 1: 
        return f"{self.rule}: {self.tok_regex + self.delim}"
      case 2: 
        return f"Rule(tok_regex={self.tok_regex}, delim={self.delim})"
      case 3: 
        return f"Rule(rule={self.rule}, tok_regex={self.tok_regex}, delim={self.delim})"
      case 4: 
        return f"Rule(tok_regex={self.tok_regex}, delim={self.delim}, next={self.next}, next_delim={self.next_delim})"
      case 5: 
        return f"Rule(rule={self.rule}, tok_regex={self.tok_regex}, delim={self.delim}, next={self.next}, next_delim={self.next_delim})"
      case _: 
        return self.get_msg(2) 
      
  def __repr__(self): 
    return self.get_msg(self.depth) 

class RuleScanner(object): 
  def __init__(self, raw_rules, depth:int=2):
    self.__depth = self.__verify_depth(depth) 

    self.ids = self.get_ids(raw_rules) 
    
    expressions = self.get_expressions(raw_rules) 
    self.__verify_expressions(expressions)

    self.__rules = self.compile(raw_rules) 

    for key in self.__rules: 
      print(key, self.__rules[key]) 

  # Public Methods 

  def compile(self, raw_rules:list): 
    final = dict() 
    for id, expression in raw_rules: 
      final[id] = self.parse(id, expression) 
    
    return final 

  
  def parse(self, id, expression:str): 
    if '(:' in expression and ':)' in expression: 
      sub_expressions = self.sanitize(expression) 
      for i, expression in enumerate(sub_expressions): 
        sub_expressions[i] = self.set_rule(id, sub_expressions, i, expression)
      return tuple(sub_expressions) if len(sub_expressions) > 1 else sub_expressions[0]

    return self.construct_rule(id, expression) 


  def construct_rule(self, id, expression, delim=None, next_expression=None, next_delim=None): 
    if expression not in self.ids: 
      tok_regex = '(?P<%s>%s)' % (id, expression)
    else: 
      tok_regex = expression 

    if next_expression and next_expression not in self.ids: 
      next_regex = '(?P<%s>%s)' % (id, next_expression) 
    else: 
      next_regex = next_expression

    return Rule(id, tok_regex, delim, next_regex, next_delim, self.__depth) 

      
  def sanitize(self, expression:str, delim:str='', count:int=0): 
    sub_expressions = re.split(r'([?|!*$])', expression.strip('(:)'))
    if count <= 0: 
      while delim in sub_expressions: 
        sub_expressions.remove(delim) 
    else: 
      for i in range(count): 
        sub_expressions.remove(delim) 

    return sub_expressions 


  def set_rule(self, id, sub_expressions:list, i, expression): 
    delim = next_exp=next_delim=None 
    if i+1 < len(sub_expressions): 
      delim = sub_expressions[i+1]
      sub_expressions.remove(delim) 
      next_exp, next_delim = self.get_next_rule(sub_expressions, i, delim)
    else: 
      delim = self.get_prev_delim(sub_expressions, i)

    return self.construct_rule(id, expression, delim, next_exp, next_delim)


  def get_next_rule(self, sub_expressions, i, delim): 
    next_exp=next_delim=None 
    if i+1 < len(sub_expressions): 
      next_exp = sub_expressions[i+1]
      next_delim = self.get_next_delim(i, sub_expressions, delim) 

    return next_exp, next_delim 
  

  def get_next_delim(self, i, sub_expressions, delim): 
    return sub_expressions[i+2] if i+2 < len(sub_expressions) else self.get_prev_delim(delim) 


  def get_prev_delim(self, input:Union[list,str], i:int=None): 
    if type(input) == list:
      if i-1 >= 0:
        if type(input[i-1]) == Rule:
          return input[i-1].delim
        else: 
          raise TypeError
      else: 
        raise ParseError(input[i]) 
    elif type(input) == str: 
      if input == '|': 
        return input
      else: 
        raise DelimiterError(input) 
    else: 
      raise TypeError
  

  def get_ids(self, raw_rules:list): 
    return [id for id, rule in raw_rules] 
  

  def get_expressions(self, raw_rules:list): 
    return [rule for id, rule in raw_rules] 


  #Private Methods 

  def __verify_depth(self, depth:Union[str, int]): 
    if type(depth) != int: 
      raise TypeError 
    return depth 

  def __verify_expressions(self, expressions): 
    for expression in expressions: 
      if not self.__verify_expression(expression):
        raise FormatError(expression) 

  def __verify_expression(self, expression:str): 
    # Check if the rule matches our regex rule pattern 
    if '(:' in expression and ':)' in expression: 
      return re.Match == type(re.match(r'\(:(?:[^)]+?[!*$?|]?)*:\)', expression))
    
    # Verify the rule isn't an 're' verifiable rule, then assume it's a rule for our parser if not
    elif '(:' in expression and ':)' not in expression or '(:' not in expression and ':)' in expression:
      try: 
        re.compile(expression)
      except:
        raise TerminationError() 
    else: 
      # Verify the rule isn't an 're' verifiable rule (throws an re.error if not) 
      re.compile(expression) 
    
    return expression
  
  # Class-specific methods
  def __iter__(self): 
    return iter(self.__rules) 
  
  def __getitem__(self, key): 
    return self.__rules[key] 

  def __repr__(self): 
    return self.__rules.__repr__()
  
  def keys(self): 
    """Return a list of keys in __rules"""
    return self.__rules.keys()
  
  def values(self): 
    """Return a list of keys in __rules"""
    return self.__rules.values() 
  
  def items(self): 
    """Return a set-like object of items in __rules"""
    return self.__rules.items() 

