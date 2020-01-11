import enum


class Cmd(enum.Enum):
    HALT = 1
    DECLARE = 2
    DECLARE_ARRAY = 3
    ASSIGN = 4
    IF_ELSE = 5
    IDENTIFIER = 6
    IDENTIFIER_ARRAY = 7
    IDENTIFIER_NEST = 8
    EXPR_VAL = 9
    EXPR_PLUS = 10
    EXPR_MINUS = 11
    READ = 12
    WRITE = 13
    EQ = 14
    NEQ = 15
    GE = 16
    LE = 17
    GEQ = 18
    LEQ = 19

