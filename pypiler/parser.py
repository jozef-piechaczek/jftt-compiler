from sly import Parser
from lexer import PypilerLexer
from code_gen import CodeGenerator, Cmd, Errors, Utils


# noinspection PyUnresolvedReferences,PyUnusedLocal
class PypilerParser(Parser):
    # for parser
    tokens = PypilerLexer.tokens
    start = 'program'

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIV, MOD),
    )

    # additional
    code_gen = CodeGenerator()

    def gen_code(self, code, param):
        return self.code_gen.gen_code(code, param)

    # **************** RULES ****************
    # program
    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):  # halt program
        print('program1', end='\n')
        self.gen_code(Cmd.HALT, ())

    @_('BEGIN commands END')
    def program(self, t):  # halt program
        print('program2', end='\n')
        self.gen_code(Cmd.HALT, ())

    # declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        print('declarations3', end='\n')
        self.gen_code(Cmd.DECLARE, t.PIDENTIFIER)

    @_('declarations COMMA PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        print('declarations2', end='\n')
        self.gen_code(Cmd.DECLARE_ARRAY, (t.PIDENTIFIER, t.NUMBER0, t.NUMBER1))

    @_('PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        print('declarations3', end='\n')
        self.gen_code(Cmd.DECLARE, t.PIDENTIFIER)

    @_('PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        print('declarations4', end='\n')
        self.gen_code(Cmd.DECLARE_ARRAY, (t.PIDENTIFIER, int(t.NUMBER0), int(t.NUMBER1)))

    # commands
    @_('commands command')
    def commands(self, t):
        print('commands1', end='\n')

    @_('command')
    def commands(self, t):
        print('commands2', end='\n')

    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, t):  # assign
        print('command1', end='\n')

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        print('command2', end='\n')

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        print('command3', end='\n')

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        print('command4', end='\n')

    @_('DO commands WHILE condition ENDDO')
    def command(self, t):
        print('command5', end='\n')

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, t):
        print('command6', end='\n')

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        print('command7', end='\n')

    @_('READ identifier SEMICOLON')
    def command(self, t):
        print('command8', end='\n')

    @_('WRITE value SEMICOLON')
    def command(self, t):
        print('command9', end='\n')

    # expression
    @_('value')
    def expression(self, t):
        print('expression1', end='\n')
        self.gen_code(Cmd.EXPR_VAL, t.value)

    @_('value PLUS value')
    def expression(self, t):
        print('expression2', end='\n')

    @_('value MINUS value')
    def expression(self, t):
        print('expression3', end='\n')

    @_('value TIMES value')
    def expression(self, t):
        print('expression4', end='\n')

    @_('value DIV value')
    def expression(self, t):
        print('expression5', end='\n')

    @_('value MOD value')
    def expression(self, t):
        print('expression6', end='\n')

    # condition
    @_('value EQ value')
    def condition(self, t):
        print('condition1', end='\n')

    @_('value NEQ value')
    def condition(self, t):
        print('condition2', end='\n')

    @_('value LE value')
    def condition(self, t):
        print('condition3', end='\n')

    @_('value GE value')
    def condition(self, t):
        print('condition4', end='\n')

    @_('value LEQ value')
    def condition(self, t):
        print('condition5', end='\n')

    @_('value GEQ value')
    def condition(self, t):
        print('condition6', end='\n')

    # value
    @_('NUMBER')
    def value(self, t):
        print('value1', end='\n')
        return 'NUMBER', t.NUMBER

    @_('identifier')
    def value(self, t):
        print('value2', end='\n')
        return "IDENTIFIER", t.identifier

    # identifier
    @_('PIDENTIFIER')
    def identifier(self, t):
        print('identifier1', end='\n')
        elem = self.gen_code(Cmd.IDENTIFIER, t.PIDENTIFIER)
        return "ID_STATIC", elem

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, t):
        print('identifier2', end='\n')
        elem1, elem2 = self.gen_code(Cmd.IDENTIFIER_NEST, (t.PIDENTIFIER0, t.PIDENTIFIER1))
        return "ID_DYNAMIC", elem1, elem2

    @_('PIDENTIFIER LBRACKET NUMBER RBRACKET')
    def identifier(self, t):
        print('identifier3', end='\n')
        elem = self.gen_code(Cmd.IDENTIFIER_ARRAY, (t.PIDENTIFIER, t.NUMBER))
        return "ID_STATIC", elem
