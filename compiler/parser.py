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
        ('left', PLUS, MINUS),
        ('left', TIMES, DIV, MOD),
    )

    # additional
    code_gen = CodeGenerator()

    def gen_code(self, code, param, lineno):
        if self.compile_mode:
            return self.code_gen.gen_code(code, param, lineno)

    # *********************** RULES ***********************

    # *********************** PROGRAM ***********************
    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):  # halt program
        if self.debug_mode:
            print('program1', end='\n')
        return self.gen_code(Cmd.PROG_HALT_D, (t.declarations, t.commands), t.lineno)

    @_('BEGIN commands END')
    def program(self, t):  # halt program
        if self.debug_mode:
            print('program2', end='\n')
        return self.gen_code(Cmd.PROG_HALT, t.commands, t.lineno)

    # *********************** DECLARATIONS ***********************
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        if self.debug_mode:
            print('declarations1', end='\n')
        return self.gen_code(Cmd.DECL_D_ID, (t.declarations, t.PIDENTIFIER), t.lineno)

    @_('declarations COMMA PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        if self.debug_mode:
            print('declarations2', end='\n')
        return self.gen_code(Cmd.DECL_D_ARRAY,
                             (t.declarations, t.PIDENTIFIER, int(t.NUMBER0), int(t.NUMBER1)), t.lineno)

    @_('PIDENTIFIER')
    def declarations(self, t):  # declare pidentifier
        if self.debug_mode:
            print()
            print('declarations3', end='\n')
        return self.gen_code(Cmd.DECL_ID, t.PIDENTIFIER, t.lineno)

    @_('PIDENTIFIER LBRACKET NUMBER COLON NUMBER RBRACKET')
    def declarations(self, t):  # declare array
        if self.debug_mode:
            print('declarations4', end='\n')
        return self.gen_code(Cmd.DECL_ARRAY, (t.PIDENTIFIER, int(t.NUMBER0), int(t.NUMBER1)), t.lineno)

    # *********************** COMMANDS ***********************
    @_('commands command')
    def commands(self, t):
        if self.debug_mode:
            print('commands1', end='\n')
        return self.gen_code(Cmd.CMDS_CMDS, (t.commands, t.command), None)

    @_('command')
    def commands(self, t):
        if self.debug_mode:
            print('commands2', end='\n')
        return self.gen_code(Cmd.CMDS_CMD, t.command, None)

    # *********************** COMMAND ***********************
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, t):  # assign
        if self.debug_mode:
            print('command1', end='\n')
        return self.gen_code(Cmd.CMD_ASSIGN, (t.identifier, t.expression), t.lineno)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        if self.debug_mode:
            print('command2', end='\n')
        return self.gen_code(Cmd.CMD_IF_ELSE, (t.condition, t.commands0, t.commands1), t.lineno)

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        if self.debug_mode:
            print('command3', end='\n')
        return self.gen_code(Cmd.CMD_IF, (t.condition, t.commands), t.lineno)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        if self.debug_mode:
            print('command4', end='\n')
        return self.gen_code(Cmd.CMD_WHILE, (t.condition, t.commands), t.lineno)

    @_('DO commands WHILE condition ENDDO')
    def command(self, t):
        if self.debug_mode:
            print('command5', end='\n')
        return self.gen_code(Cmd.CMD_DO_WHILE, (t.commands, t.condition), t.lineno)

    @_('FOR foridentifier FROM value TO value DO commands ENDFOR')
    def command(self, t):
        if self.debug_mode:
            print('command6', end='\n')
        return self.gen_code(Cmd.CMD_FOR_TO, (t.foridentifier, t.value0, t.value1, t.commands), t.lineno)

    @_('FOR foridentifier FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        if self.debug_mode:
            print('command7', end='\n')
        return self.gen_code(Cmd.CMD_FOR_DOWN_TO, (t.foridentifier, t.value0, t.value1, t.commands), t.lineno)

    @_('READ identifier SEMICOLON')
    def command(self, t):
        if self.debug_mode:
            print('command8', end='\n')
        return self.gen_code(Cmd.CMD_READ, t.identifier, t.lineno)

    @_('WRITE value SEMICOLON')
    def command(self, t):
        if self.debug_mode:
            print('command9', end='\n')
        return self.gen_code(Cmd.CMD_WRITE, t.value, t.lineno)

    # *********************** EXPRESSION ***********************
    @_('value')
    def expression(self, t):
        if self.debug_mode:
            print('expression1', end='\n')
        return self.gen_code(Cmd.EXPR_VAL, t.value, None)

    @_('value PLUS value')
    def expression(self, t):
        if self.debug_mode:
            print('expression2', end='\n')
        return self.gen_code(Cmd.EXPR_PLUS, (t.value0, t.value1), t.lineno)

    @_('value MINUS value')
    def expression(self, t):
        if self.debug_mode:
            print('expression3', end='\n')
        return self.gen_code(Cmd.EXPR_MINUS, (t.value0, t.value1), t.lineno)

    @_('value TIMES value')
    def expression(self, t):
        if self.debug_mode:
            print('expression4', end='\n')
        return self.gen_code(Cmd.EXPR_TIMES, (t.value0, t.value1), t.lineno)

    @_('value DIV value')
    def expression(self, t):
        if self.debug_mode:
            print('expression5', end='\n')
        return self.gen_code(Cmd.EXPR_DIV, (t.value0, t.value1), t.lineno)

    @_('value MOD value')
    def expression(self, t):
        if self.debug_mode:
            print('expression6', end='\n')
        return self.gen_code(Cmd.EXPR_MOD, (t.value0, t.value1), t.lineno)

    # *********************** CONDITION ***********************
    @_('value EQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition1', end='\n')
        return self.gen_code(Cmd.COND_EQ, (t.value0, t.value1), t.lineno)

    @_('value NEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition2', end='\n')
        return self.gen_code(Cmd.COND_NEQ, (t.value0, t.value1), t.lineno)

    @_('value LE value')
    def condition(self, t):
        if self.debug_mode:
            print('condition3', end='\n')
        return self.gen_code(Cmd.COND_LE, (t.value0, t.value1), t.lineno)

    @_('value GE value')
    def condition(self, t):
        if self.debug_mode:
            print('condition4', end='\n')
        return self.gen_code(Cmd.COND_GE, (t.value0, t.value1), t.lineno)

    @_('value LEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition5', end='\n')
        return self.gen_code(Cmd.COND_LEQ, (t.value0, t.value1), t.lineno)

    @_('value GEQ value')
    def condition(self, t):
        if self.debug_mode:
            print('condition6', end='\n')
        return self.gen_code(Cmd.COND_GEQ, (t.value0, t.value1), t.lineno)

    # *********************** VALUE ***********************
    @_('NUMBER')
    def value(self, t):
        if self.debug_mode:
            print('value1', end='\n')
        return self.gen_code(Cmd.VAL_NUM, int(t.NUMBER), t.lineno)

    @_('identifier')
    def value(self, t):
        if self.debug_mode:
            print('value2', end='\n')
        return self.gen_code(Cmd.VAL_ID, t.identifier, None)

    # *********************** IDENTIFIER ***********************
    @_('PIDENTIFIER')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier1', end='\n')
        return self.gen_code(Cmd.IDENTIFIER, t.PIDENTIFIER, t.lineno)

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier2', end='\n')
        return self.gen_code(Cmd.IDENTIFIER_NEST, (t.PIDENTIFIER0, t.PIDENTIFIER1), t.lineno)

    @_('PIDENTIFIER LBRACKET NUMBER RBRACKET')
    def identifier(self, t):
        if self.debug_mode:
            print('identifier3', end='\n')
        return self.gen_code(Cmd.IDENTIFIER_ARRAY, (t.PIDENTIFIER, int(t.NUMBER)), t.lineno)

    # *********************** FOR_IDENTIFIER ***********************
    @_('PIDENTIFIER')
    def foridentifier(self, t):
        if self.debug_mode:
            print('foridentifier1')
        return self.gen_code(Cmd.FORIDENTIFIER, t.PIDENTIFIER, t.lineno)

    def error(self, p):
        if p:
            print("Syntax error at token", p.type)
        else:
            print("Syntax error at EOF")
        exit(5)
