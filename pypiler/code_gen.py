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


class DataElement:
    def __init__(self, name, offset, value=None):
        self.name = name
        self.offset = offset
        self.value = value

    def __str__(self):
        return f'name:{self.name} offset:{self.offset} value={self.value}'


class SymbolTable:
    __data_offset = 1
    __symbols = []  # [n, j, k]
    __data = []  # [(n0, 1), (n1, 2), (j, 3), (k, 4)]

    def put_symbol(self, name):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            elem = DataElement(name=name, offset=self.__data_offset)
            self.__data.append(elem)
            self.__data_offset += 1

    def put_array(self, name, begin, end):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            for idx in range(begin, end + 1):
                elem = DataElement(name=f'{name}{idx}', offset=self.__data_offset)
                self.__data.append(elem)
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


# noinspection PyMethodMayBeStatic
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
            Cmd.IDENTIFIER_VALUE: lambda x: self.__get_identifier_value(x),
            Cmd.ASSIGN: lambda x: self.__assign(x),
        }[code](param)

    def __halt(self, x):
        print("HALT")

    def __declare(self, x):
        self.__sym_tab.put_symbol(name=x)

    def __declare_array(self, x):
        self.__sym_tab.put_array(name=x[0], begin=x[1], end=x[2])

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
        name1 = x[1]
        elem1 = self.__sym_tab.get_symbol(name=name1)
        if elem1 is None:
            Errors.identifier_not_declared(name=name1)
        else:
            if elem1.value is None:
                Errors.identifier_not_assigned(name=name1)
            else:
                name2 = f'{x[0]}{elem1.value}'
                elem2 = self.__sym_tab.get_symbol(name=name2)
                if elem2 is None:
                    Errors.identifier_not_declared(name=x[0])
                else:
                    return elem2

    def __get_identifier_value(self, x):
        pass

    def __assign(self, x):
        pass
