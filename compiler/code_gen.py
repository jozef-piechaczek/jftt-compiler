import sys

from cmd import Cmd


class Errors:
    @staticmethod
    def declare_err_redefine(name, lineno):
        print(f'ERROR IN LINE {lineno}: variable {name} redefined', file=sys.stderr)
        exit(1)

    @staticmethod
    def identifier_not_declared(name, lineno):
        print(f'ERROR IN LINE {lineno}: identifier {name} not declared or used incorrectly', file=sys.stderr)
        exit(2)

    @staticmethod
    def identifier_not_assigned(name):
        print(f'ERROR: identifier {name} has no value assigned', file=sys.stderr)
        exit(3)

    @staticmethod
    def incorrect_array_bounds(name, begin, end, lineno):
        print(f'ERROR IN LINE {lineno}: incorrect array {name} bounds: {end} < {begin}', file=sys.stderr)
        exit(4)


class Utils:
    @staticmethod
    def __gen_abs_value(value):
        codes = [Code('LOAD', 1)]
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
    def gen_value(value):
        codes = []
        if value > 0:
            codes += Utils.__gen_abs_value(value)
        elif value == 0:
            codes.append(Code('SUB', 0))
        else:
            codes += Utils.__gen_abs_value(abs(value))
            codes.append(Code('STORE', 4))
            codes.append(Code('SUB', 0))
            codes.append(Code('SUB', 4))
        return codes

    @staticmethod
    def load_dyn_variable(offset1, offset2):  # elem1 - n, elem2 - j
        codes = [Code('LOAD', offset1), Code('ADD', offset2)]
        return codes

    @staticmethod
    def give_offset_label(codes, label):
        for code in codes:
            if code.name == 'JPOS' or code.name == 'JNEG' \
                    or code.name == 'JUMP' or code.name == 'JZERO':
                code.offset = label
        return codes


class DataElement:
    def __init__(self, name, offset, array=False, array_dyn=None, assigned=False):
        self.name = name
        self.offset = offset
        self.array = array
        self.array_dyn = array_dyn
        self.assigned = assigned

    def __str__(self):
        return f'name:{self.name} offset:{self.offset}'

    def check_assigned(self):
        if self.assigned is False:
            Errors.identifier_not_assigned(self.name)


class Code:
    def __init__(self, name, offset=None, label=None):
        if label is None:
            self.label = []
        else:
            self.label = [label]
        self.name = name
        self.offset = offset

    def __str__(self):
        return f'{self.name} {self.offset} {self.label}'

    def code_str(self):
        ret = self.name
        if self.offset is not None:
            ret += f' {self.offset}'
        return ret


class LabelMaker:
    __label_id = 0

    def get_label(self):
        self.__label_id += 1
        return f'l{self.__label_id}'


# noinspection PyMethodMayBeStatic
class PostProcessor:
    def process(self, codes):
        label_map = {}
        codes_to_remove = []
        for idx in range(len(codes)):
            code = codes[idx]
            if code.name == 'EMPTY':
                codes[idx + 1].label += code.label
                codes_to_remove.append(code)
        for code in codes_to_remove:
            codes.remove(code)
        for idx in range(len(codes)):
            code = codes[idx]
            if len(code.label) > 0:
                for lbl in code.label:
                    label_map[lbl] = idx
        for code in codes:
            for label, idx in label_map.items():
                if code.offset == label:
                    code.offset = idx
        return codes

    def print(self, codes):
        string_codes = []
        for idx in range(len(codes)):
            code = codes[idx]
            string_codes.append(code.code_str())
        return string_codes


class SymbolTable:
    __data_offset = 100
    __data = []

    def put_symbol(self, name, lineno):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name, lineno)
            return [], ()
        else:
            elem = DataElement(name, self.__data_offset, array=False)
            self.__data.append(elem)
            self.__data_offset += 1
            return [], elem

    def put_array(self, name, begin, end, lineno):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name, lineno)
            return [], ()
        else:
            array_dyn = self.__data_offset - begin + 1
            elem = DataElement(name, self.__data_offset, array=True, array_dyn=array_dyn)
            self.__data.append(elem)
            codes = Utils.gen_value(array_dyn)
            codes.append(Code('STORE', self.__data_offset))
            self.__data_offset += 1
            self.__data_offset += (end - begin + 1)
            return codes, elem

    def __check_if_exists(self, name):
        for elem in self.__data:
            if elem.name == name:
                return True
        return False

    def get_symbol(self, name, lineno, is_array=False, errors=True):
        ret = None
        for elem in self.__data:
            if elem.name == name and elem.array == is_array:
                ret = elem
        if ret is None and errors is True:
            Errors.identifier_not_declared(name, lineno)
        return ret


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class CodeGenerator:
    __code_offset = 0
    __sym_tab = SymbolTable()
    __label_maker = LabelMaker()
    __post_processor = PostProcessor()

    def gen_code(self, code, param, lineno):
        return {
            Cmd.PROG_HALT: lambda x, l: self.__prog_halt(x, l),
            Cmd.PROG_HALT_D: lambda x, l: self.__prog_halt_d(x, l),
            Cmd.DECL_ID: lambda x, l: self.__declare(x, l),
            Cmd.DECL_ARRAY: lambda x, l: self.__declare_array(x, l),
            Cmd.DECL_D_ID: lambda x, l: self.__declare_d(x, l),
            Cmd.DECL_D_ARRAY: lambda x, l: self.__declare_d_array(x, l),
            Cmd.IDENTIFIER: lambda x, l: self.__identifier(x, l),
            Cmd.IDENTIFIER_ARRAY: lambda x, l: self.__identifier_array(x, l),
            Cmd.IDENTIFIER_NEST: lambda x, l: self.__identifier_nest(x, l),
            Cmd.VAL_ID: lambda x, l: self.__value_identifier(x),
            Cmd.VAL_NUM: lambda x, l: self.__value_number(x, l),
            Cmd.EXPR_VAL: lambda x, l: self.__expr_val(x),
            Cmd.EXPR_PLUS: lambda x, l: self.__expr_plus(x, l),
            Cmd.EXPR_MINUS: lambda x, l: self.__expr_minus(x, l),
            Cmd.EXPR_TIMES: lambda x, l: self.__expr_times(x, l),
            Cmd.EXPR_DIV: lambda x, l: self.__expr_div(x, l),
            Cmd.EXPR_MOD: lambda x, l: self.__expr_mod(x, l),
            Cmd.CMD_ASSIGN: lambda x, l: self.__cmd_assign(x, l),
            Cmd.CMD_WRITE: lambda x, l: self.__cmd_write(x, l),
            Cmd.CMD_READ: lambda x, l: self.__cmd_read(x, l),
            Cmd.CMD_IF: lambda x, l: self.__cmd_if(x, l),
            Cmd.CMD_IF_ELSE: lambda x, l: self.__cmd_if_else(x, l),
            Cmd.CMD_WHILE: lambda x, l: self.__cmd_while(x, l),
            Cmd.CMD_DO_WHILE: lambda x, l: self.__cmd_do_while(x, l),
            Cmd.CMD_FOR_TO: lambda x, l: self.__cmd_for_to(x, l),
            Cmd.CMD_FOR_DOWN_TO: lambda x, l: self.__cmd_for_down_to(x, l),
            Cmd.COND_EQ: lambda x, l: self.__cond_eq(x, l),
            Cmd.COND_NEQ: lambda x, l: self.__cond_neq(x, l),
            Cmd.COND_GE: lambda x, l: self.__cond_ge(x, l),
            Cmd.COND_GEQ: lambda x, l: self.__cond_geq(x, l),
            Cmd.COND_LE: lambda x, l: self.__cond_le(x, l),
            Cmd.COND_LEQ: lambda x, l: self.__cond_leq(x, l),
            Cmd.CMDS_CMDS: lambda x, l: self.__cmds_cmds(x),
            Cmd.CMDS_CMD: lambda x, l: self.__cmds_cmd(x),
            Cmd.FORIDENTIFIER: lambda x, l: self.__foridentifier(x, l),
        }[code](param, lineno)

    def __prog_halt(self, x, lineno):
        (x_codes, x_info) = x
        codes = [Code('SUB', 0), Code('INC'), Code('STORE', 1), Code('DEC'), Code('DEC'), Code('STORE', 2)]
        codes += x_codes
        codes.append(Code('HALT'))
        codes = self.__post_processor.process(codes)
        string_codes = self.__post_processor.print(codes)
        return string_codes

    def __prog_halt_d(self, x, lineno):
        (declarations, commands) = x
        (declarations_code, declarations_info) = declarations
        (commands_code, commands_info) = commands
        codes = [Code('SUB', 0), Code('INC'), Code('STORE', 1), Code('DEC'), Code('DEC'), Code('STORE', 2)]
        codes += declarations_code
        codes += commands_code
        codes.append(Code('HALT'))
        codes = self.__post_processor.process(codes)
        string_codes = self.__post_processor.print(codes)
        return string_codes

    def __declare(self, x, lineno):
        (codes, elem) = self.__sym_tab.put_symbol(name=x, lineno=lineno)
        return codes, (Cmd.DECL_ID, elem)

    def __declare_array(self, x, lineno):
        codes = []
        (name, begin, end) = x

        array_info = None
        if end < begin:
            Errors.incorrect_array_bounds(name=name, begin=begin, end=end, lineno=lineno)
        else:
            (array_codes, array_info) = self.__sym_tab.put_array(name=name, begin=begin, end=end, lineno=lineno)
            codes += array_codes
        return codes, (Cmd.DECL_ARRAY, array_info)

    def __declare_d(self, x, lineno):
        codes = []
        (declarations, pidentifier) = x
        (declarations_code, declarations_info) = declarations
        (symbol_codes, symbol_info) = self.__sym_tab.put_symbol(name=pidentifier, lineno=lineno)
        codes += declarations_code
        codes += symbol_codes
        return codes, (Cmd.DECL_D_ID, symbol_info, declarations_info)

    def __declare_d_array(self, x, lineno):
        codes = []
        (declarations, name, begin, end) = x
        (declarations_code, declarations_info) = declarations

        array_info = None
        codes += declarations_code
        if end < begin:
            Errors.incorrect_array_bounds(name=name, begin=begin, end=end, lineno=lineno)
        else:
            (array_codes, array_info) = self.__sym_tab.put_array(name=name, begin=begin, end=end, lineno=lineno)
            codes += array_codes
        return codes, (Cmd.DECL_D_ARRAY, array_info, declarations_info)

    def __identifier(self, x, lineno):
        name = x
        elem = self.__sym_tab.get_symbol(name, lineno=lineno, is_array=False)
        return [], ('SYMBOL', elem)

    def __identifier_array(self, x, lineno):
        (name, idx) = x
        elem = self.__sym_tab.get_symbol(name, lineno=lineno, is_array=True)
        return [], ('ARRAY', elem.array_dyn + idx)

    def __identifier_nest(self, x, lineno):
        (name0, name1) = x
        elem1 = self.__sym_tab.get_symbol(name1, lineno=lineno, is_array=False)
        elem0 = self.__sym_tab.get_symbol(name0, lineno=lineno, is_array=True)
        return [], ('ARRAY_NEST', elem0.offset, elem1.offset)

    def __value_identifier(self, x):
        codes = []
        (id_codes, id_info) = x
        if id_info[0] == 'SYMBOL':
            elem = id_info[1]
            # elem.check_assigned()
            codes.append(Code('LOAD', elem.offset))
        elif id_info[0] == 'ARRAY':
            codes.append(Code('LOAD', id_info[1]))
        elif id_info[0] == 'ARRAY_NEST':
            codes.append(Code('LOAD', id_info[1]))
            codes.append(Code('ADD', id_info[2]))
            codes.append(Code('STORE', 3))
            codes.append(Code('LOADI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes, (Cmd.VAL_ID, id_info)

    def __value_number(self, x, lineno):
        codes = Utils.gen_value(x)
        return codes, (Cmd.VAL_NUM, x)

    def __expr_val(self, x):
        (x_codes, x_info) = x
        return x_codes, (Cmd.EXPR_VAL, x_info)

    def __expr_plus(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        #  OPTIMIZE FOR X PLUS 1
        (value0_type, value0_val) = value0_info
        (value1_type, value1_val) = value1_info
        if value1_val == 1:
            codes += value0_code
            codes.append(Code('INC'))
            return codes, (Cmd.EXPR_MINUS, value0_info, value1_info)

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('ADD', 5))
        return codes, (Cmd.EXPR_PLUS, value0_info, value1_info)

    def __expr_minus(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        #  OPTIMIZE FOR X MINUS 1
        (value0_type, value0_val) = value0_info
        (value1_type, value1_val) = value1_info
        if value1_val == 1:
            codes += value0_code
            codes.append(Code('DEC'))
            return codes, (Cmd.EXPR_MINUS, value0_info, value1_info)

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        return codes, (Cmd.EXPR_MINUS, value0_info, value1_info)

    def __expr_times(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        label3 = self.__label_maker.get_label()
        label4 = self.__label_maker.get_label()
        label5 = self.__label_maker.get_label()
        label6 = self.__label_maker.get_label()
        label7 = self.__label_maker.get_label()
        label8 = self.__label_maker.get_label()

        codes.append(Code('SUB', 0))
        codes.append(Code('STORE', 25))
        codes.append(Code('STORE', 26))
        codes += value0_code
        codes.append(Code('STORE', 21))
        codes.append(Code('JPOS', offset=label1))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 21))
        codes.append(Code('STORE', 23, label=label1))
        codes += value1_code
        codes.append(Code('STORE', 22))
        codes.append(Code('JPOS', offset=label2))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 22))
        codes.append(Code('STORE', 24, label=label2))
        codes.append(Code('LOAD', 24, label=label3))
        codes.append(Code('JZERO', offset=label4))
        codes.append(Code('JNEG', offset=label4))  # ??
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 27))
        codes.append(Code('LOAD', 24))
        codes.append(Code('INC'))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('SUB', 27))
        codes.append(Code('JZERO', offset=label5))
        codes.append(Code('LOAD', 23))
        codes.append(Code('SHIFT', 25))
        codes.append(Code('ADD', 26))
        codes.append(Code('STORE', 26))
        codes.append(Code('LOAD', 25, label=label5))
        codes.append(Code('INC'))
        codes.append(Code('STORE', 25))
        codes.append(Code('LOAD', 24))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 24))
        codes.append(Code('JUMP', offset=label3))

        codes.append(Code('EMPTY', label=label4))
        codes.append(Code('LOAD', 21))
        codes.append(Code('JPOS', offset=label6))
        codes.append(Code('LOAD', 22))
        codes.append(Code('JNEG', offset=label6))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 26))
        codes.append(Code('JUMP', offset=label8))
        codes.append(Code('LOAD', 21, label=label6))
        codes.append(Code('JNEG', offset=label7))
        codes.append(Code('LOAD', 22))
        codes.append(Code('JPOS', offset=label7))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 26))
        codes.append(Code('JUMP', offset=label8))
        codes.append(Code('LOAD', 26, label=label7))
        codes.append(Code('EMPTY', label=label8))
        return codes, (Cmd.EXPR_TIMES, value0_info, value1_info)

    def __expr_div(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        #  OPTIMIZE FOR X DIV 2
        (value0_type, value0_val) = value0_info
        (value1_type, value1_val) = value1_info
        if value1_val == 2:
            codes += value0_code
            codes.append(Code('SHIFT', 2))
            return codes, (Cmd.EXPR_DIV, value0_info, value1_info)

        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        label3 = self.__label_maker.get_label()
        label4 = self.__label_maker.get_label()
        label5 = self.__label_maker.get_label()
        label6 = self.__label_maker.get_label()
        label7 = self.__label_maker.get_label()
        label8 = self.__label_maker.get_label()

        codes += value0_code
        codes.append(Code('JZERO', offset=label7))
        codes.append(Code('STORE', 11))
        codes.append(Code('JPOS', offset=label1))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 11))
        codes.append(Code('STORE', 13, label=label1))
        codes.append(Code('STORE', 15))
        codes += value1_code
        codes.append(Code('JZERO', offset=label7))
        codes.append(Code('STORE', 12))
        codes.append(Code('JPOS', offset=label2))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 12))
        codes.append(Code('STORE', 14, label=label2))
        codes.append(Code('STORE', 16))
        codes.append(Code('SUB', 0))
        codes.append(Code('STORE', 17))
        codes.append(Code('INC'))
        codes.append(Code('STORE', 18))
        codes.append(Code('LOAD', 16, label=label3))
        codes.append(Code('SUB', 13))
        codes.append(Code('JPOS', offset=label4))
        codes.append(Code('JZERO', offset=label4))
        codes.append(Code('LOAD', 16))
        codes.append(Code('SHIFT', 1))
        codes.append(Code('STORE', 16))
        codes.append(Code('LOAD', 18))
        codes.append(Code('SHIFT', 1))
        codes.append(Code('STORE', 18))
        codes.append(Code('JUMP', offset=label3))
        codes.append(Code('EMPTY', label=label4))
        codes.append(Code('LOAD', 15))
        codes.append(Code('SUB', 16))
        codes.append(Code('JNEG', offset=label5))
        codes.append(Code('LOAD', 15))
        codes.append(Code('SUB', 16))
        codes.append(Code('STORE', 15))
        codes.append(Code('LOAD', 17))
        codes.append(Code('ADD', 18))
        codes.append(Code('STORE', 17))
        codes.append(Code('LOAD', 16, label=label5))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 16))
        codes.append(Code('LOAD', 18))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 18))
        codes.append(Code('JZERO', offset=label6))
        codes.append(Code('JUMP', offset=label4))
        codes.append(Code('LOAD', 17, label=label6))
        codes.append(Code('JUMP', offset=label8))
        codes.append(Code('SUB', 0, label=label7))
        codes.append(Code('EMPTY', label=label8))
        return codes, (Cmd.EXPR_DIV, value0_info, value1_info)

    def __expr_mod(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        #  OPTIMIZE FOR X MOD 2
        (value0_type, value0_val) = value0_info
        (value1_type, value1_val) = value1_info
        if value1_val == 2:
            codes += value0_code
            codes.append(Code('STORE', 11))
            codes.append(Code('SHIFT', 2))
            codes.append(Code('STORE', 12))
            codes.append(Code('LOAD', 11))
            codes.append(Code('INC'))
            codes.append(Code('SHIFT', 2))
            codes.append(Code('SUB', 12))
            return codes, (Cmd.EXPR_MOD, value0_info, value1_info)

        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        label3 = self.__label_maker.get_label()
        label4 = self.__label_maker.get_label()
        label5 = self.__label_maker.get_label()
        label6 = self.__label_maker.get_label()
        label7 = self.__label_maker.get_label()
        label8 = self.__label_maker.get_label()

        codes += value0_code
        codes.append(Code('JZERO', offset=label7))
        codes.append(Code('STORE', 11))
        codes.append(Code('JPOS', offset=label1))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 11))
        codes.append(Code('STORE', 13, label=label1))
        codes.append(Code('STORE', 15))
        codes += value1_code
        codes.append(Code('JZERO', offset=label7))
        codes.append(Code('STORE', 12))
        codes.append(Code('JPOS', offset=label2))
        codes.append(Code('SUB', 0))
        codes.append(Code('SUB', 12))
        codes.append(Code('STORE', 14, label=label2))
        codes.append(Code('STORE', 16))
        codes.append(Code('SUB', 0))
        codes.append(Code('STORE', 17))
        codes.append(Code('INC'))
        codes.append(Code('STORE', 18))
        codes.append(Code('LOAD', 16, label=label3))
        codes.append(Code('SUB', 13))
        codes.append(Code('JPOS', offset=label4))
        codes.append(Code('JZERO', offset=label4))
        codes.append(Code('LOAD', 16))
        codes.append(Code('SHIFT', 1))
        codes.append(Code('STORE', 16))
        codes.append(Code('LOAD', 18))
        codes.append(Code('SHIFT', 1))
        codes.append(Code('STORE', 18))
        codes.append(Code('JUMP', offset=label3))
        codes.append(Code('EMPTY', label=label4))
        codes.append(Code('LOAD', 15))
        codes.append(Code('SUB', 16))
        codes.append(Code('JNEG', offset=label5))
        codes.append(Code('LOAD', 15))
        codes.append(Code('SUB', 16))
        codes.append(Code('STORE', 15))
        codes.append(Code('LOAD', 17))
        codes.append(Code('ADD', 18))
        codes.append(Code('STORE', 17))
        codes.append(Code('LOAD', 16, label=label5))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 16))
        codes.append(Code('LOAD', 18))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 18))
        codes.append(Code('JZERO', offset=label6))
        codes.append(Code('JUMP', offset=label4))
        codes.append(Code('LOAD', 15, label=label6))
        codes.append(Code('JUMP', offset=label8))
        codes.append(Code('SUB', 0, label=label7))
        codes.append(Code('EMPTY', label=label8))


        return codes, (Cmd.EXPR_MOD, value0_info, value1_info)

    def __cmds_cmds(self, x):
        codes = []
        (commands, command) = x
        (commands_code, commands_info) = commands
        (command_code, command_info) = command
        codes += commands_code
        codes += command_code
        commands_info.append(command_info)
        return codes, commands_info

    def __cmds_cmd(self, x):
        codes = []
        (command_code, command_info) = x
        codes += command_code
        return codes, [command_info]

    def __cmd_assign(self, x, lineno):
        codes = []
        (idtf, expr) = x
        (idtf_code, idtf_info) = idtf
        (expr_code, expr_info) = expr
        if expr is None:
            raise Exception('expression not implemented')
        if idtf_info[0] == 'SYMBOL':
            elem = idtf_info[1]
            elem.assigned = True
            codes += expr_code
            codes.append(Code('STORE', elem.offset))
        elif idtf_info[0] == 'ARRAY':
            codes += expr_code
            codes.append(Code('STORE', idtf_info[1]))
        elif idtf_info[0] == 'ARRAY_NEST':
            codes += expr_code
            codes.append(Code('STORE', 40))
            codes.append(Code('LOAD', idtf_info[1]))
            codes.append(Code('ADD', idtf_info[2]))
            codes.append(Code('STORE', 3))
            codes.append(Code('LOAD', 40))
            codes.append(Code('STOREI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes, (Cmd.CMD_ASSIGN, 0, idtf_info, expr_info)

    def __cmd_read(self, x, lineno):
        codes = []
        (idtf_code, idtf_info) = x
        if idtf_info[0] == 'SYMBOL':
            elem = idtf_info[1]
            elem.assigned = True
            codes.append(Code('GET'))
            codes.append(Code('STORE', elem.offset))
        elif idtf_info[0] == 'ARRAY':
            codes.append(Code('GET'))
            codes.append(Code('STORE', idtf_info[1]))
        elif idtf_info[0] == 'ARRAY_NEST':
            codes.append(Code('LOAD', idtf_info[1]))
            codes.append(Code('ADD', idtf_info[2]))
            codes.append(Code('STORE', 3))
            codes.append(Code('GET'))
            codes.append(Code('STOREI', 3))
        else:
            raise Exception('COMPILER_ERROR: incorrect identifier type')
        return codes, (Cmd.CMD_READ, 0, idtf_info)

    def __cmd_write(self, x, lineno):
        codes = []
        (value_codes, value_info) = x
        codes += value_codes
        codes.append(Code('PUT'))
        return codes, (Cmd.CMD_WRITE, 0, value_info)

    def __cmd_if(self, x, lineno):
        codes = []
        (condition, commands) = x
        (condition_codes, condition_info) = condition
        (commands_codes, commands_info) = commands
        label = self.__label_maker.get_label()
        Utils.give_offset_label(condition_codes, label)
        codes += condition_codes
        codes += commands_codes
        codes.append(Code('EMPTY', label=label))
        return codes, (Cmd.CMD_IF, 0, condition_info, commands_info)

    def __cmd_if_else(self, x, lineno):
        codes = []
        (condition, commands1, commands2) = x
        (condition_codes, condition_info) = condition
        (commands1_codes, commands1_info) = commands1
        (commands2_codes, commands2_info) = commands2
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        Utils.give_offset_label(condition_codes, label1)
        codes += condition_codes
        codes += commands1_codes
        codes.append(Code('JUMP', offset=label2))
        commands2_codes[0].label = [label1]
        codes += commands2_codes
        codes.append(Code('EMPTY', label=label2))
        return codes, (Cmd.CMD_IF_ELSE, 0, condition_info, commands1_info, commands2_info)

    def __cmd_while(self, x, lineno):
        codes = []
        (condition, commands) = x
        (condition_codes, condition_info) = condition
        (commands_codes, commands_info) = commands
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        condition_codes[0].label = [label2]
        Utils.give_offset_label(condition_codes, label1)
        codes += condition_codes
        codes += commands_codes
        codes.append(Code('JUMP', offset=label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_WHILE, 0, condition_info, commands_info)

    def __cmd_do_while(self, x, lineno):
        codes = []
        (commands, condition) = x
        (condition_codes, condition_info) = condition
        (commands_codes, commands_info) = commands
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        commands_codes[0].label = [label1]
        codes += commands_codes
        Utils.give_offset_label(condition_codes, label2)
        codes += condition_codes
        codes.append(Code('JUMP', offset=label1))
        codes.append(Code('EMPTY', label=label2))
        return codes, (Cmd.CMD_DO_WHILE, 0, condition_info, commands_info)

    # **************** CONDITIONS ****************
    def __cmd_for_to(self, x, lineno):
        codes = []
        (identifier, from_value, to_value, commands) = x

        (identifier_code, identifier_info) = identifier
        (from_value_code, from_value_info) = from_value
        (to_value_code, to_value_info) = to_value
        (commands_code, commands_info) = commands

        (_, elem_type, elem) = identifier_info
        offset = elem.offset

        nest_level = 1
        for cmd in commands_info:
            if cmd[0] == Cmd.CMD_FOR_TO or cmd[0] == Cmd.CMD_FOR_DOWN_TO:
                if cmd[1] >= nest_level:
                    nest_level = cmd[1] + 1
        dyn_elem_id = 50 + nest_level

        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()

        codes += from_value_code
        codes.append(Code('DEC'))
        codes.append(Code('STORE', offset))
        codes += to_value_code
        codes.append(Code('STORE', dyn_elem_id))
        codes.append(Code('LOAD', dyn_elem_id, label=label2))
        codes.append(Code('SUB', offset))
        codes.append(Code('JNEG', label1))
        codes.append(Code('JZERO', label1))
        codes.append(Code('LOAD', offset))
        codes.append(Code('INC'))
        codes.append(Code('STORE', offset))
        codes += commands_code
        codes.append(Code('JUMP', label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_FOR_TO, nest_level, identifier, from_value_info, to_value_info, commands_info)

    def __cmd_for_down_to(self, x, lineno):
        codes = []
        (identifier, from_value, downto_value, commands) = x

        (identifier_code, identifier_info) = identifier
        (from_value_code, from_value_info) = from_value
        (downto_value_code, downto_value_info) = downto_value
        (commands_code, commands_info) = commands

        (_, elem_type, elem) = identifier_info
        offset = elem.offset

        nest_level = 1
        for cmd in commands_info:
            if cmd[0] == Cmd.CMD_FOR_TO or cmd[0] == Cmd.CMD_FOR_DOWN_TO:
                if cmd[1] >= nest_level:
                    nest_level = cmd[1] + 1
        dyn_elem_id = 50 + nest_level

        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()

        codes += from_value_code
        codes.append(Code('INC'))
        codes.append(Code('STORE', offset))
        codes += downto_value_code
        codes.append(Code('STORE', dyn_elem_id))
        codes.append(Code('LOAD', dyn_elem_id, label=label2))
        codes.append(Code('SUB', offset))
        codes.append(Code('JPOS', label1))
        codes.append(Code('JZERO', label1))
        codes.append(Code('LOAD', offset))
        codes.append(Code('DEC'))
        codes.append(Code('STORE', offset))
        codes += commands_code
        codes.append(Code('JUMP', label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_FOR_DOWN_TO, nest_level, identifier, from_value_info, downto_value_info, commands_info)

    def __cond_neq(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JZERO'))
        return codes, (Cmd.COND_NEQ, value0_info, value1_info)

    def __cond_eq(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JPOS'))
        codes.append(Code('JNEG'))
        return codes, (Cmd.COND_EQ, value0_info, value1_info)

    def __cond_ge(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JNEG'))
        codes.append(Code('JZERO'))
        return codes, (Cmd.COND_GE, value0_info, value1_info)

    def __cond_geq(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1

        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JNEG'))
        return codes, (Cmd.COND_GEQ, value0_info, value1_info)

    def __cond_le(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1
        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JPOS'))
        codes.append(Code('JZERO'))
        return codes, (Cmd.COND_LE, value0_info, value1_info)

    def __cond_leq(self, x, lineno):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1
        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        codes.append(Code('JPOS'))
        return codes, (Cmd.COND_LEQ, value0_info, value1_info)

    def __foridentifier(self, x, lineno):
        elem_type = "EXISTING"
        pidentifier = x
        elem = self.__sym_tab.get_symbol(pidentifier, lineno=lineno, is_array=False, errors=False)
        if elem is None:
            (elem_code, elem_info) = self.__sym_tab.put_symbol(pidentifier, lineno=lineno)
            elem = elem_info
            elem_type = "NEW"
        return [], ('FORIDENTIFIER', elem_type, elem)
