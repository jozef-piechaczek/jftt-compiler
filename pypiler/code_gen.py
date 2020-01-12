from cmd import Cmd


class Errors:
    @staticmethod
    def declare_err_redefine(name):
        print(f'ERROR: variable {name} redefined')

    @staticmethod
    def identifier_not_declared(name):
        print(f'ERROR: identifier {name} not declared or is an array')

    @staticmethod
    def identifier_not_assigned(name):
        print(f'ERROR: identifier {name} has no value assigned')


# noinspection PyListCreation
class Utils:
    @staticmethod
    def gen_value(value):
        codes = []
        codes.append(Code('LOAD', 1))
        bin_str = bin(value)
        bin_str = bin_str[3:]
        for char in bin_str:
            if char == '0':
                codes.append(Code('SHIFT', 1))
            elif char == '1':
                codes.append(Code('SHIFT', 1))
                codes.append(Code('INC'))
            else:
                raise Exception('incorrect value in bit string')
        return codes

    @staticmethod
    def load_dyn_variable(elem1, elem2):  # elem1 - n, elem2 - j
        codes = []
        codes.append(Code('LOAD', elem1.offset))
        codes.append(Code('ADD', elem2.offset))
        return codes

    @staticmethod
    def give_offset_label(codes, label):
        for code in codes:
            if code.name == 'JPOS' or code.name == 'JNEG' \
                    or code.name == 'JUMP' or code.name == 'JZERO':
                code.offset = label
        return codes


class DataElement:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __str__(self):
        return f'name:{self.name} offset:{self.offset}'


class Code:
    def __init__(self, name, offset=None, label=None):
        self.name = name
        self.offset = offset
        self.label = label

    def __str__(self):
        return f'{self.name} {self.offset} {self.label}'

    def code_str(self):
        ret = self.name
        if self.offset is not None:
            ret += f' {self.offset}'
        if self.label is not None:
            ret += f' {self.label}'
        return ret


class LabelMaker:
    __label_id = 0

    def get_label(self):
        self.__label_id += 1
        return f'l{self.__label_id}'


class PostProcessor:
    def process(self, codes):
        pass

    def print(self, codes):
        pass


class SymbolTable:
    __data_offset = 10
    __data = []  # [(n0, 1), (n1, 2), (j, 3), (k, 4)]

    def put_symbol(self, name):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__data.append(DataElement(name, self.__data_offset))
            self.__data_offset += 1

    def put_array(self, name, begin, end):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
            return []
        else:
            self.__data.append(DataElement(name, self.__data_offset))
            codes = Utils.gen_value(self.__data_offset - begin + 1)
            codes.append(Code('STORE', self.__data_offset))
            self.__data_offset += 1
            for idx in range(begin, end + 1):
                self.__data.append(DataElement(name=f'{name}{idx}', offset=self.__data_offset))
                self.__data_offset += 1
            return codes

    def __check_if_exists(self, name):
        for elem in self.__data:
            if elem.name == name:
                return True
        return False

    def get_symbol(self, name):
        for elem in self.__data:
            if elem.name == name:
                return elem
        Errors.identifier_not_declared(name)
        return None


# noinspection PyMethodMayBeStatic,DuplicatedCode
class CodeGenerator:
    __code_offset = 0
    __sym_tab = SymbolTable()
    __label_maker = LabelMaker()

    def gen_code(self, code, param):
        # noinspection PyStatementEffect
        return {
            Cmd.PROG_HALT: lambda x: self.__prog_halt(x),
            Cmd.PROG_HALT_D: lambda x: self.__prog_halt_d(x),
            Cmd.DECLARE_ID: lambda x: self.__declare(x),
            Cmd.DECLARE_ARRAY: lambda x: self.__declare_array(x),
            Cmd.DECLARE_D_ID: lambda x: self.__declare_d(x),
            Cmd.DECLARE_D_ARRAY: lambda x: self.__declare_d_array(x),
            Cmd.IDENTIFIER: lambda x: self.__identifier(x),
            Cmd.IDENTIFIER_ARRAY: lambda x: self.__identifier_array(x),
            Cmd.IDENTIFIER_NEST: lambda x: self.__identifier_nest(x),
            Cmd.VAL_ID: lambda x: self.__value_identifier(x),
            Cmd.VAL_NUM: lambda x: self.__value_number(x),
            Cmd.EXPR_VAL: lambda x: self.__expr_val(x),
            Cmd.EXPR_PLUS: lambda x: self.__expr_plus(x),
            Cmd.EXPR_MINUS: lambda x: self.__expr_minus(x),
            Cmd.CMD_ASSIGN: lambda x: self.__cmd_assign(x),
            Cmd.CMD_WRITE: lambda x: self.__cmd_write(x),
            Cmd.CMD_READ: lambda x: self.__cmd_read(x),
            Cmd.CMD_IF: lambda x: self.__cmd_if(x),
            Cmd.CMD_IF_ELSE: lambda x: self.__cmd_if_else(x),
            Cmd.COND_EQ: lambda x: self.__cond_eq(x),
            Cmd.COND_NEQ: lambda x: self.__cond_neq(x),
            Cmd.COND_GE: lambda x: self.__cond_ge(x),
            Cmd.COND_GEQ: lambda x: self.__cond_geq(x),
            Cmd.COND_LE: lambda x: self.__cond_le(x),
            Cmd.COND_LEQ: lambda x: self.__cond_leq(x),
            Cmd.CMDS_CMDS: lambda x: self.__cmds_cmds(x),
            Cmd.CMDS_CMD: lambda x: self.__cmds_cmd(x),
        }[code](param)

    # noinspection PyUnusedLocal
    def __prog_halt(self, x):
        codes = [Code('SUB', 0), Code('INC'), Code('STORE', 1)]
        codes += x
        codes.append(Code('HALT'))
        for code in codes:
            print(code.code_str())

    def __prog_halt_d(self, x):
        (declarations, commands) = x
        codes = [Code('SUB', 0), Code('INC'), Code('STORE', 1)]
        codes += declarations
        codes += commands
        codes.append(Code('HALT'))
        for code in codes:
            print(code.code_str())

    def __declare(self, x):
        self.__sym_tab.put_symbol(name=x)
        return []

    def __declare_array(self, x):
        (name, begin, end) = x
        code_list = self.__sym_tab.put_array(name=name, begin=begin, end=end)
        return code_list

    def __declare_d(self, x):
        (declarations, pidentifier) = x
        self.__sym_tab.put_symbol(name=pidentifier)
        return declarations

    def __declare_d_array(self, x):
        (declarations, name, begin, end) = x
        code_list = self.__sym_tab.put_array(name=name, begin=begin, end=end)
        return declarations + code_list

    def __identifier(self, x):
        elem = self.__sym_tab.get_symbol(x)
        return "STATIC", elem

    def __identifier_array(self, x):
        (name, idx) = x
        elem = self.__sym_tab.get_symbol(f'{name}{idx}')
        return "STATIC", elem

    def __identifier_nest(self, x):
        (name1, name2) = x
        elem1 = self.__sym_tab.get_symbol(name1)
        elem2 = self.__sym_tab.get_symbol(name2)
        return "DYNAMIC", elem1, elem2

    def __value_identifier(self, x):
        codes = []
        if x[0] == "STATIC":
            codes.append(Code('LOAD', x[1].offset))
        elif x[0] == "DYNAMIC":
            get_addr = Utils.load_dyn_variable(x[1], x[2])
            codes += get_addr
            codes.append(Code('STORE', 3))
            codes.append(Code('LOADI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes

    def __value_number(self, x):
        codes = Utils.gen_value(x)
        return codes

    def __expr_val(self, x):
        return x

    def __expr_plus(self, x):
        (value0, value1) = x
        codes = []
        codes += value1
        codes.append(Code('STORE', 2))
        codes += value0
        codes.append(Code('ADD', 2))
        return codes

    def __expr_minus(self, x):
        (value0, value1) = x
        codes = []
        codes += value1
        codes.append(Code('STORE', 2))
        codes += value0
        codes.append(Code('SUB', 2))
        return codes

    def __cmd_assign(self, x):
        codes = []
        (identifier, expr) = x
        if identifier[0] == "STATIC":
            codes += expr
            codes.append(Code('STORE', identifier[1].offset))
        elif identifier[0] == "DYNAMIC":
            get_addr = Utils.load_dyn_variable(identifier[1], identifier[2])
            get_addr.append(Code('STORE', 3))
            codes += get_addr
            codes += expr
            codes.append(Code('STOREI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes

    def __cmds_cmds(self, x):
        codes = []
        (commands, command) = x
        codes += commands
        codes += command
        return codes

    def __cmds_cmd(self, x):
        codes = []
        command = x
        codes += command
        return codes

    def __cmd_read(self, x):
        codes = []
        codes += self.__cmd_assign((x, [Code('GET')]))
        return codes

    def __cmd_write(self, x):
        codes = []
        value = x
        codes += value
        codes.append(Code('PUT'))
        return codes

    def __cmd_if(self, x):
        codes = []
        (condition, commands) = x
        label = self.__label_maker.get_label()
        codes += condition
        codes += commands
        codes.append(Code('EMPTY', label=label))
        Utils.give_offset_label(codes, label)
        return codes

    def __cmd_if_else(self, x):
        codes = []
        (condition, commands1, commands2) = x
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        codes += condition
        Utils.give_offset_label(codes, label1)
        codes += commands1
        codes.append(Code('JUMP', offset=label2))
        commands2[0].label = label1
        codes += commands2
        codes.append(Code('EMPTY', label=label2))
        return codes

    def __cond_neq(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JZERO'))
        return codes

    def __cond_eq(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JPOS'))
        codes.append(Code('JNEG'))
        return codes

    def __cond_ge(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JNEG'))
        codes.append(Code('JZERO'))
        return codes

    def __cond_geq(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JNEG'))
        return codes

    def __cond_le(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JPOS'))
        codes.append(Code('JZERO'))
        return codes

    def __cond_leq(self, x):
        codes = []
        codes += self.__expr_minus(x)
        codes.append(Code('JPOS'))
        return codes
