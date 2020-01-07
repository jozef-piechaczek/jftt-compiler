from parser import PypilerParser, PypilerLexer
import sys

lexer = PypilerLexer()
parser = PypilerParser()
while True:
    text = sys.stdin.read()
    parser.parse(lexer.tokenize(text))
    print('parsing finished')
