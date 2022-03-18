"""

    Ideal expression: 

    ('object', r'\{+:=whitespace?string+whitespace?colon+whitespace?value+whitespace?comma+whitespace?=:!+\}')

    parsers into:
    
    'object' = ( 
     '(?P<object>\{)+',
        (
          whitespace?
          string+
          whitespace?
          colon+
          whitespace?
          value+
          whitespace?
          comma+
          whitespace?
          !
        ),
      '(?P<object>\})+'
    )

    meanings: 

      'string' = <rule name> 
      'regex pattern' = <expression> 
      'regex placeholder' = <expression_n>, n = 1, 2, 3, ...
      'delimiter' = <delimiter> 
        + => required 
        ? => not required 
        | => optional but atleast one required
      
    forms:  

      'string' = (
        <expression><delimiter>, 
        {
          <expression_1><delimiter>,
          <expression_2><delimiter>,
            .
            .
            .
          <expression_9><delimiter>,
          <delimiter>
        },
        <expression><delimiter>
      )


    or expressions: 

    ('value', r'whitespace?:=string|number|object|array|boolean|_null=:!whitespace?')

    forms:  

      'string' = (
        <expression><delimiter>, 
        {
          <expression_1>|,
          <expression_2>|,
            .
            .
            .
          <expression_9>|,
          <delimiter>
        },
        <expression><delimiter>
      )

    Note: Required and Optional delimiters must have a placeholder or expresion following otherwise the value is out of place 

"""

import re 

class Rules(object): 
  def __init__(self, rules): 

    self.rules = dict() 

    for id, rule in rules: 

      ids = [id for id, rule in rules] 
      
      
      if ':=' in rule: 
        rule = re.split(r'(:=|=:[!])', rule) 

        for i, arg in enumerate(rule): 
          
          if arg == ':=':

            rule[i+1] = re.split(r'([+|?])', rule[i+1]) 


            
            #print(rule[i+1]) 
            for j in range(len(rule[i+1])): 
              if j + 1 < len(rule[i+1]): 
                rule[i+1][j] += rule[i+1][j+1]
                rule[i+1].remove(rule[i+1][j+1]) 
              
              if j == len(rule[i+1])-1: 
                if rule[i+1][j] != '' and rule[i+1][j-1][-1] in ['|', '+']: 
                  rule[i+1][j] += rule[i+1][j-1][-1]

            rule.remove(rule[i]) 

            if rule[i][-1] == '': 
              rule[i][-1] = rule[i+1][-1]
            else: 
              rule[i].append(rule[i+1][-1])
          else:
            # Might cause problems with rule definitions 
            if i+1 < len(rule):
              rule[i] = '(?P<%s>%s)%s' % (id, arg[:-1], arg[-1]) 
            else: 
              rule[i] = '(?P<%s>%s)%s' % (id, arg[1:len(arg)], arg[0])

        self.rules[id] = tuple(rule)   
      else: 
        self.rules[id] = '(?P<%s>%s)' % (id, rule)

    print(self.rules) 





rules = [ 
  ('object', r'\{+:=whitespace?string+whitespace?colon+whitespace?value+whitespace?comma+whitespace?=:!+\}'),
  ('value', r'whitespace?:=string|number|object|array|boolean|_null=:!whitespace?')
]


newRules = Rules(rules) 

