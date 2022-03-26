
import re 
import argparse
from typing import NamedTuple 


args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args = vars(args.parse_args())
__FILENAME__ = args['filename'] 

class Rules(object): 
  def __init__(self, rules): 
    # Initialize a dictionary to hold the parsed rules 
    self.rules = dict() 
    # Scan through the rule list 
    for id, rule in rules: 
      # Populate a list of ids in the rule list 
      ids = [id for id, rule in rules] 
      # Check if the rule has any repeatable statements 
      if ':=' in rule: 
        # Split the rule into its component parts 
        rule = re.split(r'(:=|=:[!])', rule) 
        #print(rule) 
        # Iterate through the component parts to reconstruct
        for i, arg in enumerate(rule): 
          # If the arg is the start of a repeatable statement 
          if arg == ':=':
            # Split the list of arguments and capture its delimiter 
            rule[i+1] = re.split(r'([+|?*])', rule[i+1]) 
            # Iterate through the captured arguments 
            for j in range(len(rule[i+1])): 
              # If the current place is within the captured argument list 
              if j + 1 < len(rule[i+1]): 
                # Concantenate the rule and it's delimiter
                rule[i+1][j] += rule[i+1][j+1]
                # Remove the delimiter from the captured arguments 
                rule[i+1].remove(rule[i+1][j+1]) 
              # Check if there's any arguments without a delimiter following  
              if j == len(rule[i+1])-1 and rule[i+1][j] != '' and rule[i+1][j-1][-1] in ['|', '+', '*']: 
                if rule[i+1][j-1][-1] == '*': 
                  raise Exception("Incorrectly formatted rule '%s'"% (id), rule) 
                # If there is then concantenate the delimiter from the previous argument
                rule[i+1][j] += rule[i+1][j-1][-1]
            # remove the repeatable statement beginning delimiter 
            rule.remove(rule[i]) 
            # Check if there's a free space in the list of captured arguments 
            if rule[i][-1] == '': 
              # If there is, place the repeatable statements delimiter at the end of the array 
              rule[i][-1] = rule[i+1][-1]
            else: 
              # Otherwise just append it to the end 
              rule[i].append(rule[i+1][-1])
            # Remove the repeatable statement ending delimiter 
            rule.remove(rule[i+1]) 
            # Convert the list of captured arguements into a tuple, limiting further modification
            rule[i] = tuple(rule[i]) 
          # Otherwise, check if the argument is a regex pattern or a placeholder 
          else:
            # Check if there's a delimiter before the value 
            if arg == '' and len(arg) <= 0: 
              continue 
            elif len(arg) <= 0: 
              raise Exception("Incorrectly formatted rule '%s'"% (id), rule)
            if arg[0] in ['?', '+', '|', '*']: 
              # If there is and the id is in the placeholder, 
              # then append it to the end and remove it front the beginning
              if arg[1:len(arg)] in ids: 
                rule[i] = (arg + arg[0]).replace('|', '', 1) 
              # Otherwise assume it's a regex pattern and convert 
              else: 
                rule[i] = '(?P<%s>%s)%s' % (id, arg[1:len(arg)], arg[0])
            # If there isnt a delimiter before the value and the rule isn't a placeholder, 
            # assume it's a regex pattern with delimiter and convert 
            elif arg[:-1] not in ids: 
              rule[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1])
        # Convert the rule into a tuple to prevent further modification and add it into the dictionary
        self.rules[id] = tuple(rule)  
      # Otherwise, assume the rule is a regex pattern 
      else: 
        # Convert the rule and add it into the dictionary 
        self.rules[id] = '(?P<%s>%s)' % (id, rule)

  def __iter__(self): 
    return iter(self.rules) 

  def __getitem__(self, key): 
    return self.rules[key] 

  def __setitem__(self, key, value): 
    self.rules[key] = value 
  
  def keys(self): 
    return self.rules.keys() 
  
  def values(self): 
    return self.rules.values() 
  
  def items(self): 
    return self.rules.items() 


class Token(NamedTuple): 
  type:str 
  value:str

class MissingInfo(Exception): 
  def __init__(self, rule, delim, match, next, prev_delim, prev_match): 
    self.rule = rule 
    self.delim = delim 
    self.match = match 
    self.next = next 
    self.prev_delim = prev_delim 
    self.prev_match = prev_match 

  def __str__(self): 
    return (("\n\trule= %s\n\t delim= %s\n\t match= %s\n\tnext= %s\n\tprev_delim= %s\n\tprev_match= %s\n\t") % 
           (self.rule, self.delim, self.match, self.next, self.prev_delim, self.prev_match))  


class MissingTokenError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "\n\tError, missing token: '%s'" % self.rule 


class Scanner(object): 
  def __init__(self, data, rules): 
    self.rules = Rules(rules) 
    self.data = data 

    self.ids = [key for key in self.rules] 

    self.__scan(self.rules[self.ids[0]]) 

  def __scan(self, rule, delim=None, next=None, prev_delim=None, prev_match=None):
    if type(rule) != tuple: 
      if '?P' in rule: 
        tok_regex = rule
      elif rule in self.ids: 
        tok_regex = self.rules[rule] 
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, delim, next, prev_delim, prev_match)
    else:
      for i, arg in enumerate(rule):
        next = rule[i+1] if i+1 < len(rule) else None 
        tmp_rule = arg[:-1]
        tmp_delim = arg[-1] 

        match = self.__scan(tmp_rule, tmp_delim, next, delim, prev_match)

        if match: 
          prev_match = match 
          value = match.group() 
          kind = match.lastgroup 
          print(Token(kind, value), tmp_delim, delim, prev_delim) 
          self.data = re.sub(value, '', self.data, 1) 

          if delim == '|': 
            return match 
          
          raise Exception 

        else: 
          if tmp_delim == '?': 
            continue  

          
          
          raise MissingInfo(rule, delim, match, next, prev_delim, prev_match)

      #if match and delim == '!': 
        #return self.__scan(rule, delim, next, prev_delim, match)

    return re.match(tok_regex, self.data) 


rule_set = [ 
  ('json', r'whitespace?:=object|array=:!whitespace?'),
  ('object', r'\{+:=whitespace?string+whitespace?colon+whitespace?value+whitespace?comma*whitespace?=:!+\}'),
  ('value', r'whitespace?:=string|number|object|array|boolean|_null=:!whitespace?'), 
  ('array', r'\[+:=whitespace?value+comma*whitespace?=:!+\]'),
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('_null', r'null'),
  ('colon', r':'),
  ('comma', r','),
  ('mismatch', r'.')
]



scanner = Scanner(open(__FILENAME__).read(), rule_set)



"""
def __scan(self, rule, delim=None, next=None, prev_delim=None, prev_match=None):
    if type(rule) != tuple: 
      if '?P' in rule: 
        tok_regex = rule
      elif rule in self.ids: 
        tok_regex = self.rules[rule] 
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, delim, next, prev_delim, prev_match)
    else:
      for i, arg in enumerate(rule):
        if i+1 < len(rule): 
          next = rule[i+1]
        else: 
          next = None
        match = self.__scan(arg[:-1], arg[-1], next, delim, prev_match)
        '''
        if match:
          prev_match = match  
          if arg[-1] in ['+', '?', '*']: 
            continue 
          if arg[-1] == '|' and prev_delim == '+' and delim == '!': 
            return match 
          if delim == '+' and arg[-1] == '!': 
            return match 
          if arg[-1] == '!': 
            continue 
          if arg[-1] == '|': 
            return match 
          raise UnknownTokenError(arg[:-1], arg[-1], match, next, prev_delim, prev_match)
        else: 
          if arg[-1] == '?': 
            continue 
          if arg[-1] == '|' and next: 
            continue 
          if arg[-1] == '+' and delim == '|': 
            return match 
        print(rule, delim, prev_delim, prev_match)'''
        raise UnknownTokenError(arg[:-1], arg[-1], match, next, prev_delim, prev_match)
      
      if match and delim == '!': 
        return self.__scan(rule, delim, next, prev_delim, match) 


      return prev_match 

    match = re.match(tok_regex, self.data) 
    
    if match: 
      prev_match = match 
      print(Token(match.lastgroup, match.group()), delim, prev_delim)
      self.data = re.sub(tok_regex, '', self.data, 1) 

    else: 
      
      '''
      if delim == '?': 
        return match 
      
      if delim == '|' and next:
        return match 

      if delim == '*':
        return prev_match 

      if delim == '+' and prev_delim == '|': 
        #print(prev_match, match) 
        if prev_match: 
          print(rule, delim, next) 
        return match 

      if delim == '|' and prev_delim == '!': 
        return prev_match 
      '''

      raise UnknownTokenError(rule, delim, match, next, prev_delim, prev_match)

    return prev_match """