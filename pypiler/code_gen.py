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


class Utils:
    @staticmethod
    def gen_value(code_list, value):
        code_list.push(('LOAD', 1))
        bin_str = bin(value)
        bin_str = bin_str[3:]
        for char in bin_str:
            if char == '0':
                code_list.push(('SHIFT', 1))
            elif char == '1':
                code_list.push(('SHIFT', 1))
                code_list.push(('INC', None))
            else:
                break

    @staticmethod
    def load_dyn_variable(code_list, elem1, elem2):  # elem1 - n, elem2 - j
        code_list.push(('LOAD', elem1.offset))
        code_list.push(('ADD', elem2.offset))
        code_list.push(('STORE', 3))


class DataElement:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __str__(self):
        return f'name:{self.name} offset:{self.offset}'


class CodeList:
    __codes = []

    def push(self, code):
        self.__codes.append(code)

    def pop(self):
        self.__codes.pop()

    def print_all(self):
        for code in self.__codes:
            if code[1] is not None:
                print(f'{code[0]} {code[1]}')
            else:
                print(f'{code[0]}')
        self.__codes.clear()


class SymbolTable:
    __data_offset = 10
    __symbols = []  # [n, j, k]
    __data = []  # [(n0, 1), (n1, 2), (j, 3), (k, 4)]

    def put_symbol(self, name):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            self.__data.append(DataElement(name=name, offset=self.__data_offset))
            self.__data_offset += 1

    def put_array(self, code_list, name, begin, end):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            self.__data.append(DataElement(name=name, offset=self.__data_offset))
            Utils.gen_value(code_list, self.__data_offset - begin + 1)
            code_list.push(('STORE', self.__data_offset))
            self.__data_offset += 1
            for idx in range(begin, end + 1):
                self.__data.append(DataElement(name=f'{name}{idx}', offset=self.__data_offset))
                self.__data_offset += 1

    def __check_if_exists(self, name):
        for symbol in self.__symbols:
            if symbol == name:
                return True
        return False

    def get_symbol(self, name, idx=None):
        search_name = name + ("" if idx is None else str(idx))
        for d in self.__data:
            if d.name == search_name:
                return d
        return None


# noinspection PyMethodMayBeStatic,DuplicatedCode
class CodeGenerator:
    __code_offset = 0
    __sym_tab = SymbolTable()
    __code_list = CodeList()

    def gen_code(self, code, param):
        # noinspection PyStatementEffect
        return {
            Cmd.HALT: lambda x: self.__halt(x),
            Cmd.DECLARE: lambda x: self.__declare(x),
            Cmd.DECLARE_ARRAY: lambda x: self.__declare_array(x),
            Cmd.IDENTIFIER: lambda x: self.__get_identifier(x),
            Cmd.IDENTIFIER_ARRAY: lambda x: self.__get_identifier_array(x),
            Cmd.IDENTIFIER_NEST: lambda x: self.__get_identifier_nest(x),
            Cmd.ASSIGN: lambda x: self.__assign(x),
            Cmd.EXPR_VAL: lambda x: self.__expr_val(x),
            Cmd.EXPR_PLUS: lambda x: self.__expr_plus(x),
            Cmd.EXPR_MINUS: lambda x: self.__expr_minus(x),
            Cmd.WRITE: lambda x: self.__write(x),
            Cmd.READ: lambda x: self.__read(x),
        }[code](param)

    def __push_code(self, x):
        self.__code_offset += 1
        self.__code_list.push(x)

    def __halt(self, x):
        self.__push_code(("HALT", None))
        self.__code_list.print_all()

    def __declare(self, x):
        self.__sym_tab.put_symbol(name=x)

    def __declare_array(self, x):
        self.__sym_tab.put_array(code_list=self.__code_list, name=x[0], begin=int(x[1]), end=int(x[2]))

    def __get_identifier(self, x):
        elem = self.__sym_tab.get_symbol(name=x)
        if elem is None:
            Errors.identifier_not_declared(name=x)
        else:
            return elem

    def __get_identifier_array(self, x):
        name = f'{x[0]}{x[1]}'
        elem = self.__sym_tab.get_symbol(name=name)
        if elem is None:
            Errors.identifier_not_declared(name=x[0])
        else:
            return elem

    def __get_identifier_nest(self, x):
        name1 = x[0]
        name2 = x[1]
        elem1 = self.__sym_tab.get_symbol(name=name1)
        elem2 = self.__sym_tab.get_symbol(name=name2)
        if elem1 is None:
            Errors.identifier_not_declared(name=name1)
            return None
        if elem2 is None:
            Errors.identifier_not_declared(name=name2)
            return None
        return elem1, elem2

    def __expr_val(self, x):
        if x[0] == "NUMBER":
            Utils.gen_value(self.__code_list, int(x[1]))
        else:
            if x[1][0] == 'ID_STATIC':
                self.__code_list.push(('LOAD', x[1][1].offset))
            else:
                Utils.load_dyn_variable(code_list=self.__code_list, elem1=x[1][1], elem2=x[1][2])
                self.__code_list.push(('LOADI', 3))

    def __assign(self, x):
        if x[0] == "ID_STATIC":
            self.__code_list.push(('STORE', x[1].offset))
        else:
            self.__code_list.push(('STORE', 4))
            Utils.load_dyn_variable(code_list=self.__code_list, elem1=x[1], elem2=x[2])
            self.__code_list.push(('LOAD', 4))
            self.__code_list.push(('STOREI', 3))

    def __expr_plus(self, x):
        self.__expr_val(x[1])
        self.__code_list.push(('STORE', 2))
        self.__expr_val(x[0])
        self.__code_list.push(('ADD', 2))

    def __expr_minus(self, x):
        self.__expr_val(x[1])
        self.__code_list.push(('STORE', 2))
        self.__expr_val(x[0])
        self.__code_list.push(('SUB', 2))

    def __write(self, x):
        self.__expr_val(x)
        self.__code_list.push(('PUT', None))

    def __read(self, x):
        if x[0] == "ID_STATIC":
            self.__code_list.push(('GET', None))
            self.__code_list.push(('STORE', x[1].offset))
        else:
            Utils.load_dyn_variable(code_list=self.__code_list, elem1=x[1], elem2=x[2])
            self.__code_list.push(('GET', None))
            self.__code_list.push(('STOREI', 3))
