import _json_

__filename__ = 'large-file.json' 

print(_json_.load(open(__filename__, 'r').read()))

