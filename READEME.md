## Mass JSON
### A mediocre but still acceptable JSON parser

Usages: 
```python
  import massJson 

  data = massJson.scan(open('/examples/sample.json').read()) 

  print(data) 

  """ 
  Output: 
  -----------------------------------------------------------------------------------------------------------
  {'glossary': {'title': 'example glossary', 'GlossDiv': {'title': 'S', 'GlossList': {'GlossEntry': {'ID': 'SGML', 'SortAs': 'SGML', 'GlossTerm': 'Standard Generalized Markup Language', 'Acronym': 'SGML', 'Abbrev': 'ISO 8879:1986', 'GlossDef': {'para': 'A meta-markup language, used to create markup languages such as DocBook.', 'GlossSeeAlso': ['GML', 'XML']}, 'GlossSee': 'markup'}}}}}
  -----------------------------------------------------------------------------------------------------------
  Timing Results: 
  ----------------
  real    0m0.030s
  user    0m0.014s
  sys     0m0.007s
  ----------------
  """
  
  data = massJson.scan(open('/examples/large-file.json').read()) 

  print(data) 

  """ 
  Output: 
  -----------------------------------------------------------------------------------------------------------
  *** Omitted for length ***
  -----------------------------------------------------------------------------------------------------------
  Timing Results: 
  ----------------
  real    0m3.748s
  user    0m3.582s
  sys     0m0.130s
  ----------------
  """
```