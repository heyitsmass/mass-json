import re 
from typing import NamedTuple, Union 

from ruleParser import Rule_parser

class Info(Exception): 
  def __init__(self, locals): 

    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str


class Token(NamedTuple): 
  type:str 
  value:str 
  line:int


class MissingTokenError(Exception): 
  def __init__(self): 
    ... 

  def __str__(self): 
    return "Missing token" 


class Input_scanner(object): 
  def __init__(self, data, rules): 
    self.rules = Rule_parser(rules) 
    self.data = data 
    self.ids = [id for id in self.rules] 
    self.delims = ['|', '!', '$', '*', '+', '?'] 

    self.lineno = 1

    self.parentID = self.ids[0] 

    match = self._scan(self.rules[self.parentID], self.parentID) 

  def _verify_rule(self, input, prev): 
    delim = input[-1] 
    rule = input 
    if delim not in self.delims: 
      if prev[-1] == '|': 
        delim = prev[-1] 
      else: 
        raise Exception("Missing Delimiter") 
    else: 
      rule = input[:-1] 
    
    return rule, delim 


  def _check_ret(self, ret): 
    if type(ret) == tuple and len(ret) > 1: 
      return ret 
    elif type(ret) == re.Match:
      return True 
    


  def _scan(self, inputRule, inputID, prev_delim=None, parent_delim=None): 
    match = None
    if type(inputRule) == tuple:
      
      tmp_rule = inputRule 
      if inputRule[-1] in self.delims: 
        prev_delim = inputRule[-1] 
        tmp_rule = inputRule[:-1]  

      
      #print(tmp_rule, prev_delim, parent_delim)
      prev_match = None 
      for i, arg in enumerate(tmp_rule): 
        next = inputRule[:-1][i+1] if i+1 < len(inputRule[:-1]) else None 
        prev = inputRule[:-1][i-1] if i-1 >= 0 else None 


        rule, delim = self._verify_rule(arg, prev)


        ret = self._check_ret(self._scan(rule, inputID, delim, prev_delim))

        if type(ret) != tuple: 
          continue 
          raise Info(locals())

        match = ret[0] 
        tok_regex = ret[1] 

        if match: 
          prev_match = match 
          kind = match.lastgroup 
          value = match.group() 

          print(Token(kind, value, self.lineno), delim, prev_delim, parent_delim) 

          if kind == 'whitespace' and '\n' in value: 
            self.lineno += 1

          self.data = re.sub(tok_regex, '', self.data, 1)
          
          if delim == '!' or delim == '?': 
            continue

          if delim == '|':  

            # check next rule, if it doesnt contain the current delimiter then we can skip that value and continue with the next 
            # otherwise we need to iterate through until we find a required value and continue from there
            tmp_delim = next[-1] 

             
            if tmp_delim == '|': 
              for j, tmp in enumerate(tmp_rule[i+1:]): 
                r, d = self._verify_rule(tmp, tmp_rule[j])
                if d != '|': 
                  return self._scan(r, d, delim, parent_delim) 
              return match 
            else: 
              if i+2 <= len(tmp_rule): 
                r, d = self._verify_rule(tmp_rule[i+2], next) 
                return self._scan(r, d, delim, parent_delim) 
              else: 
                raise MissingTokenError() 

          # needs updated delimiter information 
          if delim == '$': 
            continue 


          raise Info(locals()) 
        else: 

          if delim == '?': 
            continue 
          
          # needs updated delimiter information
          if delim == '$': 
            continue 
          # **********************************************************
          if delim == '|': 
            if next: 
              #print(next)
              for j, tmp in enumerate(tmp_rule[i+1:]):
                r, d = self._verify_rule(tmp, tmp_rule[j]) 

                ret = self._check_ret(self._scan(r, d, delim, parent_delim)) 

                if type(ret) == tuple: 
                  if ret[0]: 
                    return ret 
                elif ret: 
                  return ret 

              if not parent_delim: 
                return 

              raise Info(locals())
            else: 
              # Needs updated information 
              ... 

          if delim == '!' and prev_delim == '|': 
            return #prev_match 

          # **********************************************************
          raise Info(locals()) 

      if not match: 
        # needs updated delimiter information for $
        return prev_match 

      if match: 
        if i+1 >= len(tmp_rule) and match.lastgroup in ['object', 'array']: 
          return match 
        return self._scan(inputRule, inputID, None, parent_delim) 

      raise Info(locals()) 

    if type(inputRule) == str: 
      if inputRule in self.ids: 
        tok_regex = self.rules[inputRule] 
        if type(tok_regex) == tuple: 
          return self._scan(tok_regex, inputRule, prev_delim, parent_delim) 
      elif '?P' in inputRule: 
        tok_regex = inputRule 
      else: 
        raise Exception("Unknown type '%s' for rule '%s'" % (inputRule, inputID))
    else: 
      raise Exception("Unable to interpret rule '%s'" % inputRule) 
    
    return (re.match(tok_regex, self.data), tok_regex) 


  def _next_(self, input, i): 
    return input[i+1] if i+1 < len(input) else None 
  
  

        



  
