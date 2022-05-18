from rule_scanner import RuleScanner

from lexical_analysis import Lexer

__FILENAME__ = 'sample.json' 

data = open(__FILENAME__, 'r').read() 

scanner = Lexer(data, depth=2) 