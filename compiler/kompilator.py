#!/usr/bin/python3
import sys
from parser import PypilerParser, PypilerLexer

if len(sys.argv) != 3:
    print('Usage: python3 kompilator.py <path_in> <path_out>')
    exit(1)

path_in = sys.argv[1]
path_out = sys.argv[2]
lexer = PypilerLexer()
parser = PypilerParser()
with open(path_in) as file:
    text = file.read()
    codes = parser.parse(lexer.tokenize(text))
with open(path_out, "w") as file:
    if codes is not None:
        for code in codes:
            file.write(code + '\n')
print(f'Compiled: {path_in}, saved to: {path_out}')
