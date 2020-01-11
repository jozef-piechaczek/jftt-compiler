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
    def gen_value(value):
        print('LOAD 1')
        bin_str = bin(value)
        bin_str = bin_str[3:]
        for char in bin_str:
            if char == '0':
                print('SHIFT 1')
            elif char == '1':
                print('SHIFT 1')
                print('INC')
            else:
                break

    @staticmethod
    def load_dyn_variable(elem1, elem2):  # elem1 - n, elem2 - j
        print(f'LOAD {elem1.offset}')
        print(f'ADD {elem2.offset}')
        print(f'STORE 3')


class DataElement:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __str__(self):
        return f'name:{self.name} offset:{self.offset}'


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

    def put_array(self, name, begin, end):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            self.__data.append(DataElement(name=name, offset=self.__data_offset))
            Utils.gen_value(self.__data_offset - begin + 1)
            print(f'STORE {self.__data_offset}')
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
        }[code](param)

    def __halt(self, x):
        print("HALT")

    def __declare(self, x):
        self.__sym_tab.put_symbol(name=x)

    def __declare_array(self, x):
        self.__sym_tab.put_array(name=x[0], begin=int(x[1]), end=int(x[2]))

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
            Utils.gen_value(int(x[1]))
        else:
            if x[1][0] == 'ID_STATIC':
                print(f'LOAD {x[2].offset}')
            else:
                Utils.load_dyn_variable(x[1][1], x[1][2])
                print(f'LOADI 3')

    def __assign(self, x):
        if x[0] == "ID_STATIC":
            print(f'STORE {x[1].offset}')
        else:
            print(f'STORE 4')
            Utils.load_dyn_variable(x[1], x[2])
            print(f'LOAD 4')
            print(f'STOREI 3')

    def __expr_plus(self, x):
        self.__expr_val(x[1])
        print('STORE 2')
        self.__expr_val(x[0])
        print('ADD 2')

    def __expr_minus(self, x):
        self.__expr_val(x[1])
        print('STORE 2')
        self.__expr_val(x[0])
        print('SUB 2')

