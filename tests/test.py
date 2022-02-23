import re 

from typing import NamedTuple 

class Token(NamedTuple): 
    type: str 
    value: str 
    line: int 

import argparse 

args = argparse.ArgumentParser(description="Scans a .json file for grammatical accuracy")
args.add_argument('filename', metavar='filename', 
                  type=str, help="set the name for the input file") 
args.add_argument('--debug', metavar='N', 
                  type=int, help="set the debug depth level N (default: 0)") 

args = vars(args.parse_args()) 

__depth__ = args['debug'] if args['debug'] else 0 
__filename__ = args['filename'] 



