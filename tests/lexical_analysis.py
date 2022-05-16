from rule_scanner import RuleScanner

__FILENAME__ = 'sample.json' 

data = open(__FILENAME__, 'r').read() 


raw_rules = [('json', r'(:object|array:)'), 
             ('object', r'(:\{!whitespace?pair*whitespace?,$whitespace?\}!:)'), 
             ('array', r'(:\[!whitespace?value*whitespace?,$whitespace?\]!:)'), 
             ('value', r'(:string|number|true|false|null|array|object:)'),  
             ('pair', r'(:string!whitespace?:!whitespace?value!:)'), 
             ('string', r'\"(?:(?:(?!\\)[^\"])*(?:\\[/bfnrt\"]|\\u[0-9a-fA-F]{4}|\\\\)?)+?\"'), 
             ('number', r'[-]?\d+(?:[.]?\d+)?(?:[Ee]?[-+]?\d+)?'), 
             ('whitespace', r'[ \u0020\u000A\u000D\u0009\t]+')]


if __name__ == "__main__": 
  rule = RuleScanner(raw_rules, 'simple') 

  for id in rule: 
    print(id, rule[id]) 
