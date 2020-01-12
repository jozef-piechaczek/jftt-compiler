from parser import PypilerParser, PypilerLexer
import sys

lexer = PypilerLexer()
parser = PypilerParser()
path_in = '../vm/my_example/2.imp'
path_out = path_in[:len(path_in)-3] + 'mr'
with open(path_in) as file:
    text = file.read()
codes = parser.parse(lexer.tokenize(text))
with open(path_out, "w") as file:
    for code in codes:
        file.write(code + '\n')
print('parsing finished')
