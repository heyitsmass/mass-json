import re
import argparse
from typing import Union
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

  def __init__(self, id: str, rule: str, capture: str = None):
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


class Capture(object):
  """
    A class to represent a capture Object 

    Attributes
    ----------
    value : str
        The captured rule
    index : int 
        The ending index of the captured rule 
        within the data passed
    Methods
    -------
    __init__:
        Constructs all the necessary attributes for the Capture object.
  """

  def __init__(self, value: str, index: int):
    """
      Constructs all the necessary attributes for the Capture object.

      Parameters
      ----------
          value : str
              The captured rule
          index : int 
              The ending index of the captured rule within the data passed
    """
    self.value = value
    self.index = index


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

  def __init__(self, rules: list):
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

  def __parse(self, rules: list) -> dict:
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

  def __capture(self, id: str, rule: str, index: int) -> Capture:
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

  def __tokenize(self, id: str, rule: Union[list, str], capture_val: str, rule_ids: list) -> Union[list, str]:
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

  def __init__(self, data: str, rules: Rules):
    """
    Constructs all the necessary attributes for the Scanner object.

    Parameters
    ----------
        data : str
            Input data to be scanned 
        rules : Rules
            Rules object of parsed rules 
    """
    self.data = data
    self.rules = Rules(rules)

    for id in self.rules:
      print(id, ':', self.rules[id])


if __name__ == "__main__":
  data = open(__filename__, 'r').read()
  rules = [
      ('object',
       r'{+\(whitespace+string+whitespace+colon+whitespace+value+comma+newline\)+}'),
      ('value',
          r'whitespace+\(string|number|object|array|boolean|null\)+whitespace'),
      ('string',
          r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('array',
          r'\[+\(whitespace|value+comma\)+\]+newline'),
      ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]'),
      ('boolean', r'true|false'),
      ('newline', r'\n'),
      ('NULL', r'null'),
      ('colon', r':'),
      ('comma', r','),
      ('mismatch', r'.')
  ]

  scanner = Scanner(data, rules)
