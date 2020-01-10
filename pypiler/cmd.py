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
    IDENTIFIER_VALUE = 9
