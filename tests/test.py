
import re 
import argparse
from typing import NamedTuple, Union


args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="Set the name for the input file")
args = vars(args.parse_args())
__FILENAME__ = args['filename'] 

rule_set = [ 
<<<<<<< Updated upstream
  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:pair!:)*\}!'), 
  ('value', r'(:string|number|object|array|boolean|Null:)?'), 
  ('array', r'\[!(:whitespace?value!comma$whitespace?:)*\]!'),
  ('pair', r'(:whitespace?string!whitespace?colon!whitespace?value!whitespace?comma$whitespace?:)*'),
=======
  ('pair', r'(:whitespace?string!whitespace?colon!whitespace?string!whitespace?comma$whitespace?:)*'),
>>>>>>> Stashed changes
  ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
  ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
  ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
  ('boolean', r'true|false'),
  ('Null', r'null'),
  ('colon', r':'),
  ('comma', r','),
  ('mismatch', r'.')  
]

class RuleScanner(object): 
  def __init__(self, rules): 

    self.__ids = [rule[0] for rule in rules]
    self.__rules = dict() 

    delims = ['!', '|', '+', '?', '*', '$']

    for id, rule in rules: 
      if '(:' in rule: 
        rule = self.__remove(re.split(r'\(:|:\)([!?|+*$])', rule), ('', None))

        for i, arg in enumerate(rule): 
          rule[i] = self.__remove(re.split(r'([!?|+*$])', arg), '')

          if i+1 < len(rule): 
            if rule[i+1] in delims: 
              for j, r in enumerate(rule[i]): 
                if j+1 < len(rule[i]):
                  rule[i][j] = r + rule[i][j+1]
                  rule[i].remove(rule[i][j+1]) 
                else: 
                  if rule[i][j-1][-1] == '|': 
                    rule[i][j] = r + rule[i][j-1][-1]
                  else: 
                    raise Exception("Missing Delimiter") 
              rule[i].append(rule[i+1]) 
              rule.remove(rule[i+1])
              rule[i] = tuple(rule[i])
              continue 
          rule[i] ='(?P<%s>%s)%s' % (id, rule[i][0], rule[i][1])   
        if len(rule) <= 1: 
          self.__rules[id] = rule[0] 
        else: 
          self.__rules[id] = tuple(rule) 
      else: 
        self.__rules[id] = '(?P<%s>%s)' % (id, rule)

  def __remove(self, rule, delims:Union[str, tuple, list]): 
    if type(delims) == str: 
      while delims in rule: 
        rule.remove(delims) 
    elif type(delims) in [tuple, list]: 
      for arg in delims: 
        while arg in rule: 
          rule.remove(arg) 
    return rule 

  def __iter__(self): 
    return iter(self.__rules) 

  def __getitem__(self, key): 
    return self.__rules[key] 

  def __setitem__(self, key, value): 
    self.__rules[key] = value 
  
  def keys(self): 
    return self.__rules.keys() 
  
  def values(self): 
    return self.__rules.values() 
  
  def items(self): 
    return self.__rules.items() 
  

class Token(NamedTuple): 
  type:str 
  value:str
  line:int 

class MissingTokenError(Exception): 
  def __init__(self, rule): 
    self.rule = rule 

  def __str__(self): 
    return "\n\tError, missing token: '%s'" % self.rule 


class InfoError(Exception): 
  def __init__(self, locals:dict): 
    self.str = str() 

    for arg in locals: 
      if arg != 'self': 
        self.str += f"\n\t{arg}= {locals[arg]}"

  def __str__(self): 
    return self.str

class Info(object): 
  def __init__(self, locals): 

    self.str = '\n\t'

    for arg in locals: 
      if arg != 'self' and arg in ['parent_delim', 'delim', 'prev_delim']:  
        self.str += f"{arg}={locals[arg]} "

  def __str__(self): 
    return self.str




class InputScanner(object): 
  def __init__(self, data, rules): 
    self.rules = RuleScanner(rules) 
    self.data = data 
    self.tokens = list()
    self.lineno = 1
    self.delims = ['+', '!', '|', '*', '?', '$']

    self.ids = [key for key in self.rules] 
    
    if not self.__scan(self.rules[self.ids[0]], self.ids[0]): 
      raise Exception 
    
  def __scan(self, input, id, delim = None, _delim = None):
    if type(input) == tuple: 
      _input = input 
      if input[-1] in self.delims: 
        _delim = input[-1] 
        _input = input[:-1]
      
      print(id, _input, _delim, delim) 

      for i, arg in enumerate(_input):
        next = _input[i+1] if i+1 < len(_input) else None 
        rule = arg[:-1] 
        delim = arg[-1] 

        print('\t', i, rule, delim, _delim)

        ret = self.__scan(rule, id, delim, _delim)  

        if type(ret) == tuple and len(ret) >= 1: 
          match = ret[0] 
          tok_regex = ret[1] 
        
        if match: 
          ... 
        elif not match: 
          
          raise InfoError(locals()) 

      raise InfoError(locals()) 
    elif type(input) == str: 
      print(id, input, delim, _delim) 
      if input in self.ids: 
        tok_regex = self.rules[input] 
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, input, _delim, delim) 
        elif type(tok_regex) != str: 
          raise Exception("Unknown type '%s'" % type(tok_regex)) 
      elif '?P' in input: 
        tok_regex = input 
      else: 
        raise Exception("Unknown expression '%s'" % input) 
    else: 
      raise Exception("Unknown type '%s'" % input) 

    return (re.match(tok_regex, self.data), tok_regex)


<<<<<<< Updated upstream
  def __scan_old(self, input, id, delim=None, parent_delim=None, prev_match=None, flag=None, final=''): 
    match = None 
=======
  def __scan(self, input, id, delim=None, parent_delim=None, flag=None, prev_match=None): 
>>>>>>> Stashed changes
    if type(input) == tuple: 
      tmp_input = input 
      #print(tmp_input, delim) 
      if input[-1] in self.delims: 
        parent_delim = input[-1]
        tmp_input = input[:-1] 
      elif input[-1] not in self.delims:
        parent_delim = delim 

      final = ''
      for i, arg in enumerate(tmp_input): 
        next = tmp_input[i+1] if i+1 < len(tmp_input) else None 
        rule = arg[:-1] 
        delim = arg[-1] 

<<<<<<< Updated upstream
        ret = self.__scan(rule, id, delim, parent_delim, prev_match, flag, final)
        print(ret)  
        #print(final) 
        # Return value handling 
=======
        #print(id, i, rule, delim, prev_delim, parent_delim) 

        ret = self.__scan(rule, id, delim, parent_delim, flag, prev_match) 
        
>>>>>>> Stashed changes
        if type(ret) == tuple and len(ret) > 1: 
          match = ret[0] 
          tok_regex = ret[1]
          if match and match.lastgroup in ['object', 'array']: 
            if id != 'value': 
              print(Token(match.lastgroup, match.group(), self.lineno))
            if not next: 
              return ret 
        else: 
          if type(ret) == re.Match and next:
            final += ret.group()
            continue 
          elif not ret: 
            continue 
          else: 
            return ret

        if match: 
          kind = match.lastgroup 
          value = match.group() 

          # Handles concatenation for the token 
          #*****************    2a    *****************#
          if kind not in ['object', 'array', 'whitespace', 'comma'] and id not in ['object', 'array']:
              final += value
          else:
            if '\n' in value: 
              self.lineno += 1

          #*****************    2a    *****************#
          
          self.data = re.sub(tok_regex, '', self.data, 1) 
<<<<<<< Updated upstream

          #*****************    1a    *****************#
          # User customizable options for '$' delimiter 
          # <expression>$ cannot be followed by []
          if flag:
            if delim == '$': 
              flag = None 
            elif value not in ['}', ']', '{', '['] and kind != 'whitespace':
              raise InfoError(locals())
          
          # Reset the flag for the next check 
          if delim == '$': 
            flag = None 

          prev_match = match 
          #*****************    1a    *****************#

          if delim == '|': 
            #print(prev_match) 
            return match 

        else: 

          if delim == '?' and parent_delim in ['*', '?']: 
            continue 

          #*****************    1b    *****************#
          # Sets an inverse flag for next check 
          elif delim == '$': 
            flag = delim 
            if next: 
              continue 
            break 
          #*****************    1b    *****************#

          elif delim == '|' and next: 
            continue 

          elif parent_delim in ['|', '*', '?']: 
            return prev_match

          raise InfoError(self.__sort_dict(locals())) 

      if final != '' and id not in ['object', 'array']: 
        #prev_match = final 
        print(Token(id, final, self.lineno)) #, Info(self.__sort_dict(locals())))
      #*****************    1c    *****************#
      # Handles repeatability
      #   i)    checks if a full match is made 
      #   ii)   checks if a majority match has been made ignoring whitespace (assists single line object parsing)
      #   iii)  assists majority match (ii) handling

      if match and parent_delim == '*' or not match and prev_match.lastgroup == 'whitespace' or not flag and prev_match and parent_delim == '*':
        return self.__scan(input, id, delim, parent_delim, prev_match, flag, final)
      # Handles '$' delimiter (user adjustable) 
      elif flag:
        return prev_match 
      # Handles the ending of a file 
      elif match and not parent_delim: 
        return match
      elif match and parent_delim == '|': 
        return match 
      # Handles all other errors 
      else: 
        raise InfoError(locals())
      #*****************    1c    *****************#
=======

          prev_match = match 

          if parent_delim == '*': 
            if flag: 
              if value in ['}', ']'] or kind == 'whitespace': 
                flag = None 
                continue
              else: 
                raise Exception 

            if delim in ['!', '?']: 
              continue 
            
            if delim == '$': 
              flag = delim 
              continue       


          raise InfoError(self.__sort_locals(locals())) 
          
        else: 

          if parent_delim == '*': 
            if delim in ['?', '!']: 
              continue 

            if delim == '$': 
              flag = delim 
              continue 

          raise InfoError(self.__sort_locals(locals())) 

      if match and not flag: 
        return self.__scan(input, id, delim, parent_delim, flag, prev_match) 
      else: 
        raise InfoError(locals()) 
>>>>>>> Stashed changes

    elif type(input) == str: 
      if input in self.ids: 
        tok_regex = self.rules[input] 

        if type(tok_regex) == tuple: 
<<<<<<< Updated upstream
          return self.__scan(tok_regex, input, delim, parent_delim, prev_match, flag, final) 
=======
          return self.__scan(tok_regex, input, delim, parent_delim, flag, prev_match) 
>>>>>>> Stashed changes
        elif type(input) != str: 
          raise Exception("Unknown type '%s'" % type(tok_regex)) 
      
      elif '?P' in input: 
        tok_regex = input 
      else: 
        raise Exception("Unknown input '%s'" % input) 

    else: 
      raise Exception("Invalid input '%s'" % input)
    
    return (re.match(tok_regex, self.data), tok_regex) 



  def __sort_dict(self, locals:dict) -> dict: 
    my_list = list(locals.items())[1:len(locals)-1]

    for i in range(len(my_list)): 
      for j in range(len(my_list)): 
        #print(my_list[i][0], my_list[j][0]) 
        if my_list[i][0] < my_list[j][0]:
          tmp = my_list[i]
          my_list[i] = my_list[j] 
          my_list[j] = tmp 

    ret = dict() 

    for i in range(len(my_list)): 
      ret[my_list[i][0]] = my_list[i][1] 

    return ret 

scanner = InputScanner(open(__FILENAME__).read(), rule_set)

print("done")