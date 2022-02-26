import argparse
import re

from typing import NamedTuple


__depth__ = int
__filename__ = str


class Token(NamedTuple):
    type: str
    value: str
    line: int


class CaptureError(Exception):
    def __init__(self, rule):
        self._rule = rule

    def __str__(self):
        return "Error parsing capture within rule: %s" % self._rule


class _Scanner(object):
    def __init__(self, rules):
        self.rules = _RuleParse(rules)
        self.ids = self.rules.ruleids

        for id in self.rules:
            print(id, ':', self.rules[id])



class _RuleParse(object):
    def __init__(self, rules):
        self._tmp = self._parse(rules)
        self._data = self._tmp[0] 
        self.ruleids = self._tmp[1]



    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, name):
        return self._data[name]

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def _parse(self, rules):
        rule_ids = [rules[i][0] for i in range(len(rules))]
        captures = dict()
        tmp = dict()

        for rule in rules:
            capture = None          # captured statements
            id = rule[0]            # current rule id
            condition = rule[1]     # current rule condition

            if __depth__ == 1:
                print(id, ':', condition)

            i = 0
            while i < len(condition):
                if i+1 < len(condition):
                    if condition[i] + condition[i+1] == '\(':
                        capture = self._capture(i+2, condition, id)
                        i = capture[1]
                        condition = condition.replace(capture[0], '<capture>')
                        captures[id] = capture[0]
                i += 1

            if capture:
                tmp[id] = self._tokenizer(
                    (id, condition), rule_ids, capture[0])
                continue
            tmp[id] = self._tokenizer((id, condition), rule_ids)

        return (tmp, rule_ids)

    def _capture(self, i, rule, id, _final=r''):
        _final += '\('
        tmp = r''
        while i < len(rule):
            if i + 1 < len(rule):
                if rule[i] + rule[i+1] == '\)' and rule[i-1] != '\\':
                    return [_final+(tmp+'\)'), i+2]
                elif rule[i] + rule[i+1] == '\(':
                    _final += tmp

                    capture = self._capture(i+2, rule, id)
                    if __depth__ == 2:
                        print("\tSub capture:", capture[0])
                    _final += capture[0]
                    i = capture[1]
                    continue
            tmp += rule[i]
            i += 1
        raise CaptureError(rule)

    def _tokenizer(self, rule, ids, capture=None):                      # Need to fix for tuples 
        # id = rule[0] 
        # condition = rule[1] 

        statements = [(rule[0], rule[1])] if not capture else [
            (rule[0], st) for st in rule[1].split('+')]

        token_set = tuple()

        if __depth__ == 1:
            print("\u001b[1mList of split tokens:\u001b[0m", statements)
            print("\u001b[1mList of all Identifiers:\u001b[0m", ids)

        for pair in statements:
            if pair[1] in ['<capture>', capture] or pair[1] in ids:
                if pair[1] in ['<capture>']: 
                    #print(capture) 
                    tmp = capture.replace('\(', '').replace('\)', '') 
                    tmp = re.split(r'([|+])', tmp) 
                    #print(tmp) 
                    _set = list()
                    i = 0
                    while i < len(tmp): 
                        if i+1 < len(tmp): 
                            sub_capture = (tmp[i], tmp[i+1])
                        else: 
                            sub_capture = tmp[i] 
                        _set.append(sub_capture)  
                        i+=2 
                    token_set + tuple((_set))
                    continue 
                token_set + tuple(pair[1])
                continue
            token_set + tuple('(?P<%s>%s)' % pair)

        if __depth__ > 0:
            print(
                "\x1b[1m[\x1b[32m✓\x1b[0m]\x1b[1m\x1b[1mToken set:\x1b[0m", token_set)
            if capture:
                print(
                    "\x1b[1m[\x1b[33m!\x1b[0m]\x1b[1m\t\x1b[3mCapture Group:\x1b[0m", capture)

        return token_set


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

if __name__ == '__main__':
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

    data = open(__filename__, 'r').read()

    scanner = _Scanner(rules)
