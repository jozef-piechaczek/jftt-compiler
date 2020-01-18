import enum


class Cmd(enum.Enum):
    PROG_HALT = 1
    PROG_HALT_D = 2
    DECL_ID = 3
    DECL_ARRAY = 4
    DECL_D_ID = 5
    DECL_D_ARRAY = 6
    IDENTIFIER = 7
    IDENTIFIER_ARRAY = 8
    IDENTIFIER_NEST = 9
    VAL_ID = 10
    VAL_NUM = 11
    EXPR_VAL = 12
    EXPR_PLUS = 13
    EXPR_MINUS = 14
    EXPR_DIV = 15
    EXPR_TIMES = 16
    EXPR_MOD = 17
    CMD_ASSIGN = 18
    CMD_IF_ELSE = 19
    CMD_IF = 20
    CMD_READ = 21
    CMD_WRITE = 22
    CMD_WHILE = 23
    CMD_DO_WHILE = 24
    CMD_FOR_TO = 25
    CMD_FOR_DOWN_TO = 26
    COND_EQ = 27
    COND_NEQ = 28
    COND_GE = 29
    COND_LE = 30
    COND_GEQ = 31
    COND_LEQ = 32
    CMDS_CMDS = 33
    CMDS_CMD = 34
    FORIDENTIFIER = 35

