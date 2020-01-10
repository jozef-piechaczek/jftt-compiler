from sly import Lexer


class PypilerLexer(Lexer):
    ignore = ' \t'
    ignore_comment = r'\[(.|\n)*\]'
    ignore_newline = r'\n+'
    # noinspection PyUnboundLocalVariable,PyUnresolvedReferences
    tokens = {
        PIDENTIFIER, NUMBER,
        PLUS, MINUS, TIMES, DIV, MOD,
        EQ, NEQ, GEQ, LE, GE, LEQ,
        ASSIGN, DECLARE, BEGIN, END,
        IF, THEN, ELSE, ENDIF,
        FOR, FROM, TO, DOWNTO, ENDFOR,
        WHILE, DO, ENDWHILE, ENDDO,
        READ, WRITE,
        SEMICOLON, COLON, COMMA, LBRACKET, RBRACKET,
    }

    PIDENTIFIER = r'[_a-z]+'
    NUMBER = r'-?\d+'

    ENDWHILE = r'ENDWHILE'
    DECLARE = r'DECLARE'
    ENDFOR = r'ENDFOR'
    ASSIGN = r'ASSIGN'
    DOWNTO = r'DOWNTO'
    ENDDO = r'ENDDO'
    BEGIN = r'BEGIN'
    MINUS = r'MINUS'
    TIMES = r'TIMES'
    WHILE = r'WHILE'
    WRITE = r'WRITE'
    ENDIF = r'ENDIF'
    READ = r'READ'
    PLUS = r'PLUS'
    ELSE = r'ELSE'
    FROM = r'FROM'
    THEN = r'THEN'
    DIV = r'DIV'
    MOD = r'MOD'
    NEQ = r'NEQ'
    LEQ = r'LEQ'
    GEQ = r'GEQ'
    END = r'END'
    FOR = r'FOR'
    EQ = r'EQ'
    GE = r'GE'
    LE = r'LE'
    IF = r'IF'
    TO = r'TO'
    DO = r'DO'
    SEMICOLON = r'[;]'
    COLON = r'[:]'
    LBRACKET = r'\('
    RBRACKET = r'\)'
    COMMA = r'\,'

    def error(self, t):
        print(f'Illegal character {t.value[0]}')
        self.index += 1


