from parser import PypilerParser, PypilerLexer
import sys

lexer = PypilerLexer()
parser = PypilerParser()
with open('../vm/my_example/1.imp') as file:
    text = file.read()
    if parser.compile_mode:
        print('SUB 0')
        print('INC')
        print('STORE 1')
    parser.parse(lexer.tokenize(text))
    print('parsing finished')
