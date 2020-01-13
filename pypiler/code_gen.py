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
    def __gen_abs_value(value):
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
                codes[idx + 1].label = code.label
                codes_to_remove.append(code)
        for code in codes_to_remove:
            codes.remove(code)
        for idx in range(len(codes)):
            code = codes[idx]
            if code.label is not None:
                label_map[code.label] = idx
        for code in codes:
            for label, idx in label_map.items():
                if code.offset == label:
                    code.offset = idx
        return codes

    def print(self, codes):
        string_codes = []
        for idx in range(len(codes)):
            code = codes[idx]
            print(code.code_str())
            string_codes.append(code.code_str())
        return string_codes


class SymbolTable:
    __data_offset = 100
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
    __post_processor = PostProcessor()

    def gen_code(self, code, param):
        # noinspection PyStatementEffect
        return {
            Cmd.PROG_HALT: lambda x: self.__prog_halt(x),
            Cmd.PROG_HALT_D: lambda x: self.__prog_halt_d(x),
            Cmd.DECL_ID: lambda x: self.__declare(x),
            Cmd.DECL_ARRAY: lambda x: self.__declare_array(x),
            Cmd.DECL_D_ID: lambda x: self.__declare_d(x),
            Cmd.DECL_D_ARRAY: lambda x: self.__declare_d_array(x),
            Cmd.IDENTIFIER: lambda x: self.__identifier(x),
            Cmd.IDENTIFIER_ARRAY: lambda x: self.__identifier_array(x),
            Cmd.IDENTIFIER_NEST: lambda x: self.__identifier_nest(x),
            Cmd.VAL_ID: lambda x: self.__value_identifier(x),
            Cmd.VAL_NUM: lambda x: self.__value_number(x),
            Cmd.EXPR_VAL: lambda x: self.__expr_val(x),
            Cmd.EXPR_PLUS: lambda x: self.__expr_plus(x),
            Cmd.EXPR_MINUS: lambda x: self.__expr_minus(x),
            Cmd.EXPR_TIMES: lambda x: self.__expr_times(x),
            Cmd.CMD_ASSIGN: lambda x: self.__cmd_assign(x),
            Cmd.CMD_WRITE: lambda x: self.__cmd_write(x),
            Cmd.CMD_READ: lambda x: self.__cmd_read(x),
            Cmd.CMD_IF: lambda x: self.__cmd_if(x),
            Cmd.CMD_IF_ELSE: lambda x: self.__cmd_if_else(x),
            Cmd.CMD_WHILE: lambda x: self.__cmd_while(x),
            Cmd.CMD_DO_WHILE: lambda x: self.__cmd_do_while(x),
            Cmd.CMD_FOR_TO: lambda x: self.__cmd_for_to(x),
            Cmd.CMD_FOR_DOWN_TO: lambda x: self.__cmd_for_down_to(x),
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
        (x_codes, x_info) = x
        codes = [Code('SUB', 0), Code('INC'), Code('STORE', 1), Code('DEC'), Code('DEC'), Code('STORE', 2)]
        codes += x_codes
        codes.append(Code('HALT'))
        codes = self.__post_processor.process(codes)
        string_codes = self.__post_processor.print(codes)
        return string_codes

    def __prog_halt_d(self, x):
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

    def __declare(self, x):
        self.__sym_tab.put_symbol(name=x)
        return [], (Cmd.DECL_ID, x)

    def __declare_array(self, x):
        (name, begin, end) = x
        code_list = self.__sym_tab.put_array(name=name, begin=begin, end=end)
        return code_list, (Cmd.DECL_ARRAY, name, begin, end)

    def __declare_d(self, x):
        (declarations, pidentifier) = x
        (declarations_code, declarations_info) = declarations
        self.__sym_tab.put_symbol(name=pidentifier)
        return declarations_code, (Cmd.DECL_D_ID, declarations_info, pidentifier)

    def __declare_d_array(self, x):
        codes = []
        (declarations, name, begin, end) = x
        (declarations_code, declarations_info) = declarations
        codes += declarations_code
        codes += self.__sym_tab.put_array(name=name, begin=begin, end=end)
        return codes, (Cmd.DECL_D_ARRAY, declarations, begin, end, name)

    def __identifier(self, x):
        elem = self.__sym_tab.get_symbol(x)
        return [], ("STATIC", elem)

    def __identifier_array(self, x):
        (name, idx) = x
        elem = self.__sym_tab.get_symbol(f'{name}{idx}')
        return [], ("STATIC", elem)

    def __identifier_nest(self, x):
        (name1, name2) = x
        elem1 = self.__sym_tab.get_symbol(name1)
        elem2 = self.__sym_tab.get_symbol(name2)
        return [], ("DYNAMIC", elem1, elem2)

    def __value_identifier(self, x):
        codes = []
        (x_codes, x_info) = x
        if x_info[0] == "STATIC":
            codes.append(Code('LOAD', x_info[1].offset))
        elif x_info[0] == "DYNAMIC":
            get_addr = Utils.load_dyn_variable(x_info[1], x_info[2])
            codes += get_addr
            codes.append(Code('STORE', 3))
            codes.append(Code('LOADI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes, (Cmd.VAL_ID, x_info)

    def __value_number(self, x):
        codes = Utils.gen_value(x)
        return codes, (Cmd.VAL_NUM, x)

    def __expr_val(self, x):
        (x_codes, x_info) = x
        return x_codes, (Cmd.EXPR_VAL, x_info)

    def __expr_plus(self, x):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1
        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('ADD', 5))
        return codes, (Cmd.EXPR_PLUS, value0_info, value1_info)

    def __expr_minus(self, x):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1
        codes += value1_code
        codes.append(Code('STORE', 5))
        codes += value0_code
        codes.append(Code('SUB', 5))
        return codes, (Cmd.EXPR_MINUS, value0_info, value1_info)

    def __expr_times(self, x):
        codes = []
        (value0, value1) = x
        (value0_code, value0_info) = value0
        (value1_code, value1_info) = value1
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        label3 = self.__label_maker.get_label()
        codes.append(Code('SUB', 0))
        codes.append(Code('STORE', 6))
        codes.append(Code('STORE', 7))
        codes += value0_code
        codes.append(Code('STORE', 10))
        codes += value1_code
        codes.append(Code('STORE', 9))
        codes.append(Code('JZERO', offset=label1, label=label2))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('STORE', 8))
        codes.append(Code('LOAD', 9))
        codes.append(Code('INC'))
        codes.append(Code('SHIFT', 2))
        codes.append(Code('SUB', 8))
        codes.append(Code('JZERO', offset=label3))
        codes.append(Code('LOAD', 10))
        codes.append(Code('SHIFT', 7))
        codes.append(Code('ADD', 6))
        codes.append(Code('STORE', 6))
        codes.append(Code('LOAD', offset=7, label=label3))
        codes.append(Code('INC'))
        codes.append(Code('STORE', 7))
        codes.append(Code('LOAD', 8))
        codes.append(Code('STORE', 9))
        codes.append(Code('JUMP', offset=label2))
        codes.append(Code('LOAD', 6, label=label1))
        return codes, (Cmd.EXPR_TIMES, value1_info, value1_info)

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

    def __cmd_assign(self, x):
        codes = []
        (identifier, expr) = x
        (identifier_code, identifier_info) = identifier
        (expr_code, expr_info) = expr
        if expr is None:
            raise Exception('expression not implemented')
        if identifier_info[0] == "STATIC":
            codes += expr_code
            codes.append(Code('STORE', identifier_info[1].offset))
        elif identifier_info[0] == "DYNAMIC":
            get_addr = Utils.load_dyn_variable(identifier_info[1], identifier_info[2])
            get_addr.append(Code('STORE', 3))
            codes += get_addr
            codes += expr_code
            codes.append(Code('STOREI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes, (Cmd.CMD_ASSIGN, 0, identifier_info, expr_info)

    def __cmd_read(self, x):
        codes = []
        (identifier_code, identifier_info) = x
        if identifier_info[0] == "STATIC":
            codes.append(Code('GET'))
            codes.append(Code('STORE', identifier_info[1].offset))
        elif identifier_info[0] == "DYNAMIC":
            get_addr = Utils.load_dyn_variable(identifier_info[1], identifier_info[2])
            get_addr.append(Code('STORE', 3))
            codes += get_addr
            codes.append(Code('GET'))
            codes.append(Code('STOREI', 3))
        else:
            raise Exception('incorrect identifier type')
        return codes, (Cmd.CMD_READ, 0, identifier_info)

    def __cmd_write(self, x):
        codes = []
        (value_codes, value_info) = x
        codes += value_codes
        codes.append(Code('PUT'))
        return codes, (Cmd.CMD_WRITE, 0, value_info)

    def __cmd_if(self, x):
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

    def __cmd_if_else(self, x):
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
        commands2_codes[0].label = label1
        codes += commands2_codes
        codes.append(Code('EMPTY', label=label2))
        return codes, (Cmd.CMD_IF_ELSE, 0, condition_info, commands1_info, commands2_info)

    def __cmd_while(self, x):
        codes = []
        (condition, commands) = x
        (condition_codes, condition_info) = condition
        (commands_codes, commands_info) = commands
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        condition_codes[0].label = label2
        Utils.give_offset_label(condition_codes, label1)
        codes += condition_codes
        codes += commands_codes
        codes.append(Code('JUMP', offset=label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_WHILE, 0, condition_info, commands_info)

    def __cmd_do_while(self, x):
        codes = []
        (commands, condition) = x
        (condition_codes, condition_info) = condition
        (commands_codes, commands_info) = commands
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        commands_codes[0].label = label1
        codes += commands_codes
        Utils.give_offset_label(condition_codes, label2)
        codes += condition_codes
        codes.append(Code('JUMP', offset=label1))
        codes.append(Code('EMPTY', label=label2))
        return codes, (Cmd.CMD_DO_WHILE, 0, condition_info, commands_info)

    def __cmd_for_to(self, x):
        codes = []
        (pid, from_value, to_value, commands) = x
        (from_value_code, from_value_info) = from_value
        (to_value_code, to_value_info) = to_value
        (commands_code, commands_info) = commands
        nest_level = 1
        for cmd in commands_info:
            if cmd[0] == Cmd.CMD_FOR_TO or cmd[0] == Cmd.CMD_FOR_DOWN_TO:
                if cmd[1] >= nest_level:
                    nest_level = cmd[1] + 1
        dyn_elem_id = 50 + nest_level
        elem = self.__sym_tab.get_symbol(pid)
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        codes += from_value_code
        codes.append(Code('DEC'))
        codes.append(Code('STORE', elem.offset))
        codes += to_value_code
        codes.append(Code('STORE', dyn_elem_id))
        codes.append(Code('LOAD', dyn_elem_id, label=label2))
        codes.append(Code('SUB', elem.offset))
        codes.append(Code('JNEG', label1))
        codes.append(Code('JZERO', label1))
        codes.append(Code('LOAD', elem.offset))
        codes.append(Code('INC'))
        codes.append(Code('STORE', elem.offset))
        codes += commands_code
        codes.append(Code('JUMP', label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_FOR_TO, 1, pid, from_value_info, to_value_info, commands_info)

    def __cmd_for_down_to(self, x):
        codes = []
        (pid, from_value, downto_value, commands) = x
        (from_value_code, from_value_info) = from_value
        (downto_value_code, downto_value_info) = downto_value
        (commands_code, commands_info) = commands
        nest_level = 1
        for cmd in commands_info:
            if cmd[0] == Cmd.CMD_FOR_TO or cmd[0] == Cmd.CMD_FOR_DOWN_TO:
                if cmd[1] >= nest_level:
                    nest_level = cmd[1] + 1
        dyn_elem_id = 50 + nest_level
        elem = self.__sym_tab.get_symbol(pid)
        label1 = self.__label_maker.get_label()
        label2 = self.__label_maker.get_label()
        codes += from_value_code
        codes.append(Code('INC'))
        codes.append(Code('STORE', elem.offset))
        codes += downto_value_code
        codes.append(Code('STORE', dyn_elem_id))
        codes.append(Code('LOAD', dyn_elem_id, label=label2))
        codes.append(Code('SUB', elem.offset))
        codes.append(Code('JPOS', label1))
        codes.append(Code('JZERO', label1))
        codes.append(Code('LOAD', elem.offset))
        codes.append(Code('DEC'))
        codes.append(Code('STORE', elem.offset))
        codes += commands_code
        codes.append(Code('JUMP', label2))
        codes.append(Code('EMPTY', label=label1))
        return codes, (Cmd.CMD_FOR_DOWN_TO, 1, pid, from_value_info, downto_value_info, commands_info)
    # **************** CONDITIONS ****************

    def __cond_neq(self, x):
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

    def __cond_eq(self, x):
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

    def __cond_ge(self, x):
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

    def __cond_geq(self, x):
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

    def __cond_le(self, x):
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

    def __cond_leq(self, x):
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
