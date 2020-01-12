from sly import Parser

from code_gen import CodeGenerator, Cmd
from lexer import PypilerLexer


# noinspection PyUnresolvedReferences,PyUnusedLocal
class PypilerParser(Parser):
    # for parser
    tokens = PypilerLexer.tokens
    start = 'program'

    debug_mode = False
    compile_mode = True

    precedence = (
        # ('left', IF, ELSE),
        # ('left', EQ, NE, LT, LE, GT, GE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIV, MOD),
    )

    # additional
    code_gen = CodeGenerator()

    def gen_code(self, code, param):
        if self.compile_mode:
            return self.code_gen.gen_code(code, param)

    # **************** RULES ****************
    # program
    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):  # halt program
        if self.debug_mode:
            print('program1', end='\n')
        self.gen_code(Cmd.PROG_HALT_D, (t.declarations, t.commands))

    @_('BEGIN commands END')
    def program(self, t):  # halt program
        if self.debug_mode:
            print('program2', end='\n')
        self.gen_code(Cmd.PROG_HALT, t.commands)

    # declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        if self.debug_mode:
            print('declarations3', end='\n')
        return self.gen_code(Cmd.DECLARE_D_ID, (t.declarations, t.PIDENTIFIER))

    @_('declarations COMMA PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        if self.debug_mode:
            print('declarations2', end='\n')
        return self.gen_code(Cmd.DECLARE_D_ARRAY, (t.declarations, t.PIDENTIFIER, int(t.NUMBER0), int(t.NUMBER1)))

    @_('PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        if self.debug_mode:
            print('declarations3', end='\n')
        return self.gen_code(Cmd.DECLARE_ID, t.PIDENTIFIER)

    @_('PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        if self.debug_mode:
            print('declarations4', end='\n')
        return self.gen_code(Cmd.DECLARE_ARRAY, (t.PIDENTIFIER, int(t.NUMBER0), int(t.NUMBER1)))

    # commands
    @_('commands command')
    def commands(self, t):
        if self.debug_mode:
            print('commands1', end='\n')
        return self.gen_code(Cmd.CMDS_CMDS, (t.commands, t.command))

    @_('command')
    def commands(self, t):
        if self.debug_mode:
            print('commands2', end='\n')
        return self.gen_code(Cmd.CMDS_CMD, t.command)

    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, t):  # assign
        if self.debug_mode:
            print('command1', end='\n')
        return self.gen_code(Cmd.CMD_ASSIGN, (t.identifier, t.expression))

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        if self.debug_mode:
            print('command2', end='\n')
        return self.gen_code(Cmd.CMD_IF_ELSE, (t.condition, t.commands0, t.commands1))

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        if self.debug_mode:
            print('command3', end='\n')
        return self.gen_code(Cmd.CMD_IF, (t.condition, t.commands))

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        if self.debug_mode:
            print('command4', end='\n')

    @_('DO commands WHILE condition ENDDO')
    def command(self, t):
        if self.debug_mode:
            print('command5', end='\n')

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, t):
        if self.debug_mode:
            print('command6', end='\n')

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        if self.debug_mode:
            print('command7', end='\n')

    @_('READ identifier SEMICOLON')
    def command(self, t):
        if self.debug_mode:
            print('command8', end='\n')
        return self.gen_code(Cmd.CMD_READ, t.identifier)

    @_('WRITE value SEMICOLON')
    def command(self, t):
        if self.debug_mode:
            print('command9', end='\n')
        return self.gen_code(Cmd.CMD_WRITE, t.value)

    # expression
    @_('value')
    def expression(self, t):
        if self.debug_mode:
            print('expression1', end='\n')
        return self.gen_code(Cmd.EXPR_VAL, t.value)

    @_('value PLUS value')
    def expression(self, t):
        if self.debug_mode:
            print('expression2', end='\n')
        return self.gen_code(Cmd.EXPR_PLUS, (t.value0, t.value1))

    @_('value MINUS value')
    def expression(self, t):
        if self.debug_mode:
            print('expression3', end='\n')
        return self.gen_code(Cmd.EXPR_MINUS, (t.value0, t.value1))

    @_('value TIMES value')
    def expression(self, t):
        if self.debug_mode:
            print('expression4', end='\n')

    @_('value DIV value')
    def expression(self, t):
        if self.debug_mode:
            print('expression5', end='\n')

    @_('value MOD value')
    def expression(self, t):
        if self.debug_mode:
            print('expression6', end='\n')

    # condition
    @_('value EQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition1', end='\n')
        return self.gen_code(Cmd.COND_EQ, (t.value0, t.value1))

    @_('value NEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition2', end='\n')
        return self.gen_code(Cmd.COND_NEQ, (t.value0, t.value1))

    @_('value LE value')
    def condition(self, t):
        if self.debug_mode:
            print('condition3', end='\n')
        return self.gen_code(Cmd.COND_LE, (t.value0, t.value1))

    @_('value GE value')
    def condition(self, t):
        if self.debug_mode:
            print('condition4', end='\n')
        return self.gen_code(Cmd.COND_GE, (t.value0, t.value1))

    @_('value LEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition5', end='\n')
        return self.gen_code(Cmd.COND_LEQ, (t.value0, t.value1))

    @_('value GEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition6', end='\n')
        return self.gen_code(Cmd.COND_GEQ, (t.value0, t.value1))

    # value
    @_('NUMBER')
    def value(self, t):
        if self.debug_mode:
            print('value1', end='\n')
        return self.gen_code(Cmd.VAL_NUM, int(t.NUMBER))

    @_('identifier')
    def value(self, t):
        if self.debug_mode:
            print('value2', end='\n')
        return self.gen_code(Cmd.VAL_ID, t.identifier)

    # identifier
    @_('PIDENTIFIER')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier1', end='\n')
        return self.gen_code(Cmd.IDENTIFIER, t.PIDENTIFIER)

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier2', end='\n')
        return self.gen_code(Cmd.IDENTIFIER_NEST, (t.PIDENTIFIER0, t.PIDENTIFIER1))

    @_('PIDENTIFIER LBRACKET NUMBER RBRACKET')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier3', end='\n')
        return self.gen_code(Cmd.IDENTIFIER_ARRAY, (t.PIDENTIFIER, int(t.NUMBER)))
