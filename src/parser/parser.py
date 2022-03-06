import sys
sys.path.append('../')

from lexer.lexer import Scanner
import argparse


if __name__ == "__main__":
  args = argparse.ArgumentParser(
      description="Scans a .json file for grammatical accuracy")
  args.add_argument('filename', metavar='filename',
                    type=str, help="Set the name for the input file")
  args = vars(args.parse_args())
  __FILENAME__ = args['filename']

  data = open(__FILENAME__, 'r').read()
  rules = [
      ('object',
       r'{+(%whitespace+string+whitespace+colon+whitespace+value+comma+whitespace%)+}'),
      ('value',
          r'whitespace+(%string|number|object|array|boolean|NULL%)+whitespace'),
      ('string',
          r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'),
      ('array',
          r'\[+(%whitespace+value+comma+whitespace%)+\]+whitespace'),
      ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+'),
      ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'),
      ('boolean', r'true|false'),
      ('NULL', r'null'),
      ('colon', r':'),
      ('comma', r','),
      ('mismatch', r'.')
  ]

  scanner = Scanner(data, rules)

  for token in scanner: 
      print(token) 


