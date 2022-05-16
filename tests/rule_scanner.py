import re 


class Rule(object): 
  def __init__(self, depth:str, id:str, delim:str=None, tok_regex:str=None):  
    self.id = id
    self.delim = delim 
    self.tok_regex = tok_regex 
    self.__depth = depth

  def __repr__(self):
    if self.__depth in ['simple', 'simplified']: 
      return f"{self.tok_regex + (self.delim if self.delim else '')}"
    elif self.__depth in ['intermediate', 'moderate']: 
      return f"Rule(tok_regex={self.tok_regex}, delim={self.delim})"
    elif self.__depth in ['advanced', 'complex']:
      return f"Rule(id={self.id}, tok_regex={self.tok_regex}, delim={self.delim})"
    else: 
      raise InputError(self.__depth)


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
  def __init__(self, raw_rules:list, depth:str='intermediate'):  
    self.__depth = depth.lower()
    self.__ids = [id for id, rule in raw_rules]

    self.__rules = self._compile(raw_rules)
  
  def _verify(self, rule:str) -> bool: 
    return re.Match == type(re.match(r'\(:(?:[^)]+?[!*$?|]?)*:\)', rule))


  def _get_prev_delim(self, rule:list, i:int) -> str: 
    if i-1 >= 0: 
      if rule[i-1].delim == '|': 
        return rule[i-1].delim 
      raise DelimiterError(rule[i-1][-1])
    raise ParseError(rule)


  def __set_rule_helper(self, id:str, rule:str, i:int, tmp:str) -> Rule:
    if tmp not in self.__ids: 
      return Rule(self.__depth, id, rule[i+1], '(?P<%s>%s)' % (id, tmp))
    return Rule(self.__depth, id, rule[i+1], rule[i])


  def _set_rule(self, id:str, rule:str, i:int=None, tmp:str=None) -> Rule: 
    if not i and not tmp: 
      return Rule(self.__depth, id, None, ('(?P<%s>%s)' % (id, rule)))
    else: 
      if i+1 < len(rule): 
        ret = self.__set_rule_helper(id, rule, i, tmp) 
        rule.remove(rule[i+1]) 
        return ret 
      else: 
        return Rule(self.__depth, id, self._get_prev_delim(rule, i), rule[i])


  def _parse(self, id:str, rule:str) -> tuple: 
    for i, tmp in enumerate(rule): 
      rule[i] = self._set_rule(id, rule, i, tmp) 
    return tuple(rule) 


  def _compile(self, raw_rules:list) -> dict:
    final = dict() 
    for id, rule in raw_rules: 
      if '(:' in rule and ':)' in rule: 
        if not self._verify(rule):
          raise FormatError(rule)
        rule = self._sanitize(rule)  
        final[id] = self._parse(id, rule) 
      else: 
        final[id] = self._set_rule(id, rule) 
    return final 
    

  def _sanitize(self, raw_rule:str, delim:str='') -> list: 
    rules = re.split(r'([?|!*$])', raw_rule.strip('(:)'))
    while delim in rules: 
      rules.remove(delim)
    return rules

  def __iter__(self): 
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

