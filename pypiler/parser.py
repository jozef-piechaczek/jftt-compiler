from sly import Parser
from lexer import PypilerLexer


# noinspection PyUnresolvedReferences
class PypilerParser(Parser):
    tokens = PypilerLexer.tokens
    start = 'program'

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIV, MOD),
    )

    # program
    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):
        print('', end='')

    @_('BEGIN commands END')
    def program(self, t):
        print('', end='')

    # declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, t):
        print('', end='')

    @_('declarations COMMA PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):
        print('', end='')

    @_('PIDENTIFIER')
    def declarations(self, t):
        print('', end='')

    @_('PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):
        print('', end='')

    # commands
    @_('commands command')
    def commands(self, t):
        print('', end='')

    @_('command')
    def commands(self, t):
        print('', end='')

    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, t):
        print('', end='')

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        print('', end='')

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        print('', end='')

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        print('parsed while', end='')

    @_('DO commands WHILE condition ENDDO')
    def command(self, t):
        print('', end='')

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, t):
        print('', end='')

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        print('', end='')

    @_('READ identifier SEMICOLON')
    def command(self, t):
        print('', end='')

    @_('WRITE value SEMICOLON')
    def command(self, t):
        print('', end='')

    # expression
    @_('value')
    def expression(self, t):
        print('', end='')

    @_('value PLUS value')
    def expression(self, t):
        print('', end='')

    @_('value MINUS value')
    def expression(self, t):
        print('', end='')

    @_('value TIMES value')
    def expression(self, t):
        print('', end='')

    @_('value DIV value')
    def expression(self, t):
        print('', end='')

    @_('value MOD value')
    def expression(self, t):
        print('', end='')

    # condition
    @_('value EQ value')
    def condition(self, t):
        print('', end='')

    @_('value NEQ value')
    def condition(self, t):
        print('', end='')

    @_('value LE value')
    def condition(self, t):
        print('', end='')

    @_('value GE value')
    def condition(self, t):
        print('', end='')

    @_('value LEQ value')
    def condition(self, t):
        print('', end='')

    @_('value GEQ value')
    def condition(self, t):
        print('', end='')

    # value
    @_('NUMBER')
    def value(self, t):
        print('', end='')

    @_('identifier')
    def value(self, t):
        print('', end='')

    # identifier
    @_('PIDENTIFIER')
    def identifier(self, t):
        print('', end='')

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, t):
        print('', end='')

    @_('PIDENTIFIER LBRACKET NUMBER RBRACKET')
    def identifier(self, t):
        print('', end='')
