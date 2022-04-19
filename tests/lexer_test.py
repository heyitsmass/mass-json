
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

  ('json', r'(:object|array:)+'), 
  ('object', r'\{!(:whitespace?pair!whitespace?:)*\}!'), 
  ('value', r'(:string|number|object|array|boolean|Null:)?'), 
  ('array', r'\[!(:whitespace?value!whitespace?comma$:)*\]!'),
  ('pair', r'(:string!whitespace?colon!whitespace?value!whitespace?comma$whitespace?:)?'),
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
  column:int

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
    self.lineno = self.col = 0
    self.delims = ['+', '!', '|', '*', '?', '$']

    self.ids = [key for key in self.rules] 

    match = self.__scan(self.rules[self.ids[0]], self.ids[0]) 

    if type(match) == tuple and len(match) > 1: 
      if match[0] == 'err': 
        raise InfoError(match[1]) 


    for token in self.tokens: 
      print(token) 

  def __scan(self, input, id, delim=None, parent_delim=None, prev_match=None, flag=None, match=None): 
    if type(input) == tuple: 
      tmp_input = input 
      if input[-1] in self.delims: 
        parent_delim = input[-1]
        tmp_input = input[:-1] 

      for i, arg in enumerate(tmp_input): 
        next = tmp_input[i+1] if i+1 < len(tmp_input) else None 
        rule = arg[:-1] 
        delim = arg[-1] 

        #print(id, i, rule, delim, prev_delim, parent_delim) 

        ret = self.__scan(rule, id, delim, parent_delim) 
        
        if type(ret) == tuple and len(ret) > 1:
          if ret[0] == 'err': 
            return ret 

          match = ret[0] 
          tok_regex = ret[1]
        else: 
          if type(ret) == re.Match and next: 
            continue 
          elif not ret: 
            continue
          elif ret == True: 
            return True
          else: 
            raise InfoError(locals()) 

        if match: 
          kind = match.lastgroup 
          value = match.group() 

          print(id, Token(kind, value, self.lineno, self.col)) #, Info(locals())) 
          
          self.data = re.sub(tok_regex, '', self.data, 1) 
          prev_match = match 

          if delim in ['!', '?'] and parent_delim == '+' and next: 
            continue 

          if delim in ['!', '?', '$'] and next and not flag: 
            continue 

          if delim == '|': 
            return match 

          if flag == '$':
            if value in ['}', ']'] or kind == 'whitespace': 
              flag = None 
              continue
            else: 
              raise InfoError(locals()) 
          
          if not next: 
            return self.__scan(input, id, parent_delim=parent_delim, flag=flag) 
          
          raise InfoError(self.__sort_locals(locals())) 
          
        else: 

          if delim == '?' and next: 
            continue 

          if delim == '|' and next: 
            continue 

          if delim == '$' and next: 
            flag = '$'
            continue 

          if flag == '$' and next: 
            return prev_match 

          if delim in ['!', '?', '|'] and parent_delim == '?': 
            return 

          if delim == '$' and not next: 
            return 

          if delim == '?' and not flag: 
            return 

          if delim == '!' and parent_delim == '+': 
            return 
          
          elif len(self.data) > 0: 
            print(len(self.data)) 
            #raise InfoError(locals())
            return ('err', locals()) 
          
          else: 
            return True 

          raise InfoError(self.__sort_locals(locals())) 

      if match: 
        raise Exception 
      else: 
        if prev_match and flag == '$': 
          return self.__scan(input, id, prev_match=prev_match, flag=flag) 
        raise InfoError(locals())

    elif type(input) == str: 
      if input in self.ids: 
        tok_regex = self.rules[input] 
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, input, delim, parent_delim, flag=flag) 
        elif type(input) != str: 
          raise Exception("Unknown type '%s'" % type(tok_regex)) 
      elif '?P' in input: 
        tok_regex = input 
      else: 
        raise Exception("Unknown input '%s'" % input) 
    else: 
      raise Exception("Invalid input '%s'" % input)
    return (re.match(tok_regex, self.data), tok_regex) 


  def __sort_locals(self, locals:dict) -> dict: 
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



    

"""
  def __scan(self, input, delim=None, _delim=None, _match=None, p_delim=None, id=None):
    if type(input) == tuple: 
      p_delim = delim 
      tmp = '' 
      for index, arg in enumerate(input): 
        _delim = delim 
        next = input[index+1] if index+1 < len(input) else None 
        length = len(input) 
        rule = arg[:-1] 
        delim = arg[-1] 

        #print(id) 
        ret = self.__scan(rule, delim, id=id) 

        #print(ret) 

        if type(ret) == tuple and len(ret) > 1: 
          match = ret[0] 
          tok_regex = ret[1] 
        else: 
          match = ret 

        if match: 
          _match = match 
          kind = match.lastgroup 
          value = match.group()  
          
          if delim == '|' and input[len(input)-1] == '*' or delim == '!' and _delim == '*':
            return (match, tok_regex) 
          
          if delim == '*': 
            continue

          if '}' in tmp: 
            print(Token(kind, value, self.lineno, self.col, self.numchars), delim, _delim)
            continue 

          if kind == 'whitespace' and '\n' in value: 
            self.lineno += 1
            self.col = 0          

          tmp += value 
          #print(Token(kind, value, self.lineno, self.col, self.numchars), delim, _delim)
          #self.tokens.append(Token(kind, value, self.lineno, self.col))
          if value in ['{', '}', '[', ']']: 
            print(Token(kind, value, self.lineno, self.col, self.numchars))

          self.col += match.span()[1]
          self.numchars += match.span()[1]

          #print(tok_regex) 
          self.data = re.sub(tok_regex, '', self.data, 1) 


          if delim in ['!', '?'] and next: 
            continue

          if not next: 
              print(Token('pair', tmp, self.lineno, self.col, self.numchars)) #, delim, _delim, p_delim, next)
              return self.__scan(input, _delim, id=id) 

          if delim == '|':  
            return match 

          raise Info(locals())
        else: 

          if delim in ['?', '|'] and next or _match and delim == '*':
            continue 

          if delim == '?':
            return _match 

          if delim == '!' and _delim == '|' or delim == '*' and _delim == '|': 
            return 

          if delim == '!' and p_delim == '*': 
            if not _match: 
              return 
          
          
          raise Info(locals())
      
    
    else: 
      if '?P' in input: 
        tok_regex = input 
      elif input in self.ids: 
        tok_regex = self.rules[input] 
        if type(tok_regex) == tuple: 
          #print(Token(id, tmp, self.lineno, self.col, self.numchars)) #, delim, _delim, p_delim, next)
          return self.__scan(tok_regex, delim, id=input)
      else: 
        return 
    
    return (re.match(tok_regex, self.data), tok_regex) 
"""
"""
  def __scan_old(self, input, id, delim = None, _delim=None, _match=None, prev_delim=None): 
    if type(input) == tuple:
      if input[-1] in self.delims: 
        _delim = input[-1] 

      tmp = input[:-1] if input[-1] in self.delims else input
      final = ''
      for i, arg in enumerate(tmp): 
        next = tmp[i+1] if i+1 < len(tmp) else None 
        rule = arg[:-1] 
        delim = arg[-1] 

        ret = self.__scan(rule, id, delim, _delim, _match, prev_delim)
        if type(ret) == str: 
          continue 
        elif ret == True: 
          continue 
          raise Info(locals())

        match = ret[0]
        tok_regex = ret[1] 

        if match: 
          
          #kind = match.lastgroup 
          #value = match.group()
          final += match.group() 
          #print(Token(kind, value, self.lineno, self.column), prev_delim)
          self.data = re.sub(tok_regex, '', self.data, 1) 

          
          if delim == '$' and len(self.data) <= 0 and next: 
            return (None, final) 

          if prev_delim == '$':
            if match.lastgroup == 'whitespace': 
              continue 
            if not _match:
              return (None, final)
            else: 
              #print(_match) 
              continue
              raise Info(locals())
          if type(next) == tuple or next == None: 
            print(Token(match.lastgroup, match.group(), self.lineno, self.column)) 

          _match = match 
          prev_delim = delim

        else: 

          if delim == '?': 
            continue 
          
          if delim == '$':
            _match = match 
            prev_delim = delim 
            continue 

          if delim == '|' and next: 
            continue 
          
          return ret  
          #return None
          raise Info(locals())
      #match = True 
      #print(delim, prev_delim) 
      delim = _delim
      if _delim:
        if '\n' in final: 
          self.lineno += 1

        print(Token(id, final, self.lineno, self.column)) 

      if _delim == '*' and len(self.data) > 0 and match: 
        return self.__scan(input, id, None, None, _match, prev_delim) 
      #raise Info(locals()) 
      elif _delim == '*' and not match: 
        #_match = final 
        return final
        raise Info(locals())
        #return True 

      else: 
        return True 
        raise Info(locals())

    elif type(input) == str: 
      #print(input)
      if input in self.ids: 
        tok_regex = self.rules[input]
        if type(tok_regex) == tuple: 
          return self.__scan(tok_regex, input, delim, _delim, _match, prev_delim) 
      elif '?P' in input: 
        tok_regex = input 
    else: 
      raise Info(locals()) 

    return (re.match(tok_regex, self.data), tok_regex) 
"""


scanner = InputScanner(open(__FILENAME__).read(), rule_set)

print("done")