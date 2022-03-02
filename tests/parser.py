import re
import argparse
from secrets import token_urlsafe
from typing import NamedTuple, Union
args = argparse.ArgumentParser(
    description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename',
                  type=str, help="set the name for the input file")
args.add_argument('--debug', metavar='N',
                  type=int, help="set the debug depth level N (default: 0)",
                  default=0)

args = vars(args.parse_args())

__depth__ = args['debug'] if args['debug'] else 0
__filename__ = args['filename']

class Token(NamedTuple): 
  type:str 
  value:str
  line:int 


class RuleError(Exception): 
  def __init__(self, id:str, rule:str): 
    self.id = id 
    self.rule = rule 

  def __str__(self): 
    return "Error scanning rule: '%s', Invalid format?\n\t%s" % (self.id, self.rule) 

class CaptureError(Exception):
  """
    A class to represent an error in the capture function 
    i.e a CaptureError

    Attributes
    ----------
    id : str
        ID of errored rule
    rule : str
        Associated rule data

    Methods
    -------
    __str__:
        Returns the error message including id and rule
  """

  def __init__(self, id:str, rule:str, capture:str = None):
    """
      Constructs all the necessary attributes for the CaptureError object.

      Parameters
      ----------
          id : str
              ID of errored rule
          rule : str
              Associated rule data
          capture : str 
              Any associated capture data
    """
    self.id = id
    self.rule = rule
    self.capture = capture

  def __str__(self):
    """Returns the capture error message with id and rule including a sub capture if exists"""
    if self.capture:
      return "Error capturing %s:\n\t%s:\n\t%s" % (self.id, self.rule, self.capture)
    return "Error capturing %s:\n\t%s" % (self.id, self.rule)


class Capture(NamedTuple):

  value:str 
  index:int
  """
    A class to represent a capture Object 

    Attributes
    ----------
    value : str
        The captured rule
    index : int 
        The ending index of the captured rule 
        within the data passed
  """


class Rules(object):
  """
    A class to parse and hold rule data available the Rule Scanner.

    Attributes
    ----------
    rules : dict()
        ID of errored rule
    rule : str
        Associated rule data

    Methods
    -------
    __init__(rules) :
        Constructs all the necessary attributes for the Rules object.
    __iter__ : 
        Returns an iterator of the rules dict
    __getitem__(key) : 
        Returns the value associated with the key in rules
    __setitem__(key, value) : 
        Sets the value in rule at place key
    keys : 
        Returns the keys in rules
    values :
        Returns the values in rules
    items : 
        Returns the key, values in rules
    __parse : 
        Parses the rules defined by the user
    __capture :
        Captures any sets of information that should be repeatedly scanned by the RuleScanner
    __tokenize :
        Converts rules into tokens readable by re.match() 
    
  """

  def __init__(self, rules:list):
    """
      Constructs all the necessary attributes for the Rules object.

      Parameters
      ----------
          rules : list
              List of rules defined by the user
    """
    self.rules = self.__parse(rules)

  def __iter__(self):
    """Returns an iterator of the rules dict"""
    return iter(self.rules)
  
 #def __next__(self, key, index): 
    #return self.rules[key][index] 

  def __getitem__(self, key):
    """Returns the value associated with the key in rules""" 
    return self.rules[key]

  def __setitem__(self, key, value):
    """Sets the value in rule at place 'key'"""
    self.rules[key] = value

  def keys(self):
    """Returns the keys in rules"""
    return self.rules.keys()

  def values(self):
    """Returns the values in rules"""
    return self.rules.values()

  def items(self):
    """Returns the key, values in rules"""
    return self.rules.items()

  def __parse(self, rules:list) -> dict:
    """
        Parses the rules defined by the user

        Parameters
        ----------
        rules : list
            Unparsed list of rules defined by the user

        Returns
        -------
        ret : dict
            Parsed dict of rules readable by the RuleScanner 
    """
    ret = dict()
    rule_ids = [ids for ids, rules in rules]

    for id, rule in rules:
      capture_val = ''
      i = 0
      while i < len(rule):
        if i+1 < len(rule):
          if rule[i] + rule[i+1] == '\(':
            capture_ret = self.__capture(id, rule, i)
            capture_val = capture_ret.value
            i = capture_ret.index
            rule = rule.replace('\('+capture_val+'\)', '<capture>')  # value

        i += 1

      ret[id] = self.__tokenize(id, rule, capture_val, rule_ids)

      if __depth__ > 1:
        print(id, ':', ret[id], ': \''+rule+'\'', ':', capture_val)

    return ret

  def __capture(self, id:str, rule:str, index:int) -> Capture:
    """
        Captures any sets of information that should be repeatedly scanned by the RuleScanner

        If the rule has no close parenthesis then the function will raise a Capture Error, passing 
        the id and rule to the CaptureError exception 

        If a sub rule is captured within the main rule (not supported currently):
        The function will notify the user via console of the sub rule but will not be saved. Then, 
        raise a CaptureError with the sub capture

        Parameters
        ----------
        id : str
            current id of the rule being captured
        rule: str 
            full rule being captured from 
        index: int 
            current index of the rule being scanned, this is the start 
            index of the function 

        Returns
        -------
        capture : Capture obj 
            The captured rule 
        
    """
    tmp = ''
    i = index+2
    while i < len(rule):
      if i+1 < len(rule):
        if rule[i]+rule[i+1] == '\(':
          captured = self._capture(id, rule, i)
          if __depth__ > -1:
            print("[\x1b[33m\x1b[1m!!\x1b[0m]", captured)
          raise CaptureError(id, rule, captured)
        elif rule[i]+rule[i+1] == '\)':
          return Capture(tmp, i)
        tmp += rule[i]
      i += 1
    raise CaptureError(id, rule)

  def __tokenize(self, id:str, rule:Union[list, str], capture_val:str, rule_ids:list) -> Union[list, str]:
    """
        Converts rules into tokens readable by re.match() 

        If there is a capture_val passed then it will replace the value with a tuple 
        of the split capture_val, similarly any non-tokenizable input will be left alone 

        Parameters
        ----------
        id : str
            current rule id
        rule : list, str
            The rule or list of rules to be turned into tokens 
        capture_val : str
            any captured data within the rule
        rule_ids : list
            list of rule ids

        Returns
        -------
        statements : list, str 
            the list of tokens or singular token associated with the id passed in 

    """
    statements = rule
    capture = tuple()
    if capture_val:
      statements = statements.split('+')
      capture_split = re.split(r'([+|])', capture_val)
      i = 0
      while i < len(capture_split):
        if i+1 < len(capture_split):
          capture += (capture_split[i]+capture_split[i+1],)
        else:
          capture += (capture_split[i],)
        i += 2

      i = 0
      while i < len(statements):
        if statements[i] not in rule_ids:
          if statements[i] == '<capture>':
            statements[i] = capture
          else:
            statements[i] = '(?P<%s>%s)' % (id, statements[i])
        i += 1

    else:
      return '(?P<%s>%s)' % (id, statements)

    return statements


class Scanner(object):
  """
    A class to represent an iterable Scanner object where each token can be listed via iteration

    ...

    Attributes
    ----------
    TBD

    Methods
    -------
    TBD 
  """

  def __init__(self, data:str, rules:Rules):
    """
    Constructs all the necessary attributes for a Scanner object.

    Parameters
    ----------
        data : str
            Input data to be scanned 
        rules : Rules
            Rules object of parsed rules 
    """
    self.data = data
    self.rules = Rules(rules)
    self.ruleids = list(self.rules.keys()) 
    self.lineno = 0

    #print(self.rules['object'][0]) 

    self.default = self.rules[list(self.rules.keys())[0]]

    if type(self.default) is not list:
      raise RuleError(list(self.rules.keys())[0], self.default)
    

    i = 0

    while i < len(self.default): 
      if type(self.default[i]) == str: 
        tok_regex = self.default[i] 
        last = self.matchToken(tok_regex) 
      elif type(self.default[i]) == tuple: 
        self.__scanTuple(self.default[i])
      i+=1 

        

    return 
    self.__scan_list(self.rules[id]) 
    '''
    #print(self.rules[id]) 
    for token in self.rules[id]: 
      match = ''
      #print(token) 
      if type(token) == str: 
        tok_regex = token 
        match = re.match(tok_regex, self.data)
        if match: 
          value = match.group() 
          kind = match.lastgroup 
          self.data = re.sub(tok_regex, '', self.data, 1) 
          print(Token(kind, value, self.lineno))
          continue  
      elif type(token) == tuple: 
        self.__scan_tuple(token) 
    '''

  def __scanTuple(self, token): 

    isMatch = True
    i = 0

    while isMatch and i < len(token):
      #if i == len(token): 
        #print(i) 
      #if i == len(token): 
        #print(i)
        #i = 0 
        #print("Returned 1")  
        #continue 
      tmp = re.split(r'([|+])', token[i])
      id = tmp[0]
      if len(tmp) > 1:
        tmp = tmp[:-1] 
        delim = tmp[1]

      tok_regex = self.rules[id]
      #print(tmp) 
      if type(tok_regex) == list: 
        self.__scanList(tok_regex)
        #print(id, i, token) 
        i+=1
        continue 

      match = re.match(tok_regex, self.data) 
      if match: 
        self.__printToken(match, tok_regex)
        if i == len(token)-1:  
          i = 0
          continue 

        if delim == '|':
          if id in 'whitespace': 
            i+=1
            continue 
          return
      elif (not match and id in ['whitespace', 'comma', 'newline'] or
            not match and delim == '|'):
        i+=1 
        continue 
      elif not match:
        raise(Exception('%s, %d'%(tmp,i))) 

      #print(tok_regex, i) 
      isMatch = self.__checkMatch(match)
      i+=1 

    return

  def __checkMatch(self, match=None):
    #print(match) 
    return True if match else False 


  # We want to try and (1) scan the list in the order the items are received, if it fails to satisfy any condition then; 
  # There exists an issue in the file. 
  # If we capture a sub-condition (which should be a tuple) then it must be repeated until failure; 
  # if the sub-capture fails or fails to satisy (1) then there exists an issue in the file. 
  # If we are not within a sub-capture and complete all sequences of the first input list, then we have a correct file
  # The rule assumptions are such: 
  #   i) any rule that is repeatedly captured (like a sub-list) must be placed within \(\) delimiters
  #         - Ex: 
  #   ii) rules that are repeatedly captured cannot have raw strings within them
  #         - if they do, create another placeholder rule or a large placeholder with multiple raw strings 
  #            then replace the rawstring with the placeholder 
  #         - Ex: 
  #   iii) only the first rule is going to be checked for completion; it's assumed that the file being checked 
  #         can follow an order such that every rule can be replaced with a placeholder, with the placeholders
  #         making up the first rule
  #         - Ex: 
  #   iv) The first rule must be an array
  #   v) sub rules can only be seperated by '+' (and), and '|' (or) 
  def __scanList(self, token):
    #print(token)  
    for rule in token: 
      #print(rule)
      if type(rule) == str: 
        #print(rule) 
        if rule in self.ruleids: 
          tok_regex = self.rules[rule] 
        else: 
          tok_regex = rule

        if type(tok_regex) == list: 
          self.__scanList(tok_regex) 
          continue
        
      elif type(rule) == tuple: 
        self.__scanTuple(rule) 
        continue 
      #print(tok_regex) 
      match = re.match(tok_regex, self.data) 

      if match: 
        self.__printToken(match, tok_regex) 
        if rule == 'whitespace': 
          #print("True")
          ...
        continue
      elif not match and rule != 'whitespace':
        return 

    return 



  def __printToken(self, match, tok_regex): 
    val = match.group() 
    kind = match.lastgroup 
    print('\033[1m', Token(kind, val, self.lineno), '\033[0m') 
    self.data = re.sub(tok_regex, '', self.data, 1)

  def matchToken(self, tok_regex, prev=''): 
    match = re.match(tok_regex, self.data)
    if match: 
      value = match.group() 
      kind = match.lastgroup 
      print('\033[1m', Token(kind, value, self.lineno), '\033[0m') 
      self.data = re.sub(tok_regex, '', self.data, 1)
      return kind
    return prev 


if __name__ == "__main__":
  data = open(__filename__, 'r').read()
  rules = [
      ('object',
       r'{+\(whitespace+string+whitespace+colon+whitespace+value+comma+newline\)+}'),
      ('value',
          r'whitespace+\(string|number|object|array|boolean|NULL\)+whitespace'),
      ('string',
          r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('array',
          r'\[+\(whitespace|value|comma\)+\]+newline'),
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
