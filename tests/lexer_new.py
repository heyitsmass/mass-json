"""
    Simple Grammar:
    A --> \"B
    B --> [a-z]A'
    A' --> \":
"""

import string 

class Scanner(object):
    def __init__(self, data): 
        self._position = -1
        self._data = data

    def __iter__(self): 
        return self 

    def __next__(self): 
        self._position += 1
        if self._position >= len(self._data): 
            self._position -= 1
            raise StopIteration
        return self._data[self._position]


filename = "sample.json"
scanner = Scanner(open(filename, 'r').read())

def A_prime(input):
    if input == ':': 
        return True 

def B(input): 
    if next(input) in string.ascii_letters: 
        print(input)
        B(next(input))
    elif next(input) == '\"':
        
        A_prime(next(input))

def A(input): 

    if next(input) == '\"': 
        print(True)
        

    """    
        if input == '\"':
            print(input)
            B(next(input))

    """


print(scanner.__next__()) 

scanner = iter(scanner.__next__())

print(next(scanner))

print(len(scanner)) 


