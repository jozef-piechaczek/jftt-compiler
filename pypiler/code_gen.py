from cmd import Cmd


class Errors:
    @staticmethod
    def declare_err_redefine(name):
        print(f'ERROR: variable {name} redefined')


class SymbolTable:
    __data_offset = 1
    __symbols = []  # [n, j, k]
    __data = []  # [(n0, 1), (n1, 2), (j, 3), (k, 4)]

    def put_symbol(self, name):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            self.__data.append((name, self.__data_offset))
            self.__data_offset += 1

    def put_array(self, name, begin, end):
        if self.__check_if_exists(name):
            Errors.declare_err_redefine(name)
        else:
            self.__symbols.append(name)
            for idx in range(begin, end+1):
                self.__data.append((f'{name}{idx}', self.__data_offset))
                self.__data_offset += 1

    def __check_if_exists(self, name):
        for symbol in self.__symbols:
            if symbol == name:
                return True
        return False

    def get_symbol(self, name, idx=None):
        search_name = name + ("" if idx is None else str(idx))
        for d in self.__data:
            if d[0] == search_name:
                return d
        return None


# noinspection PyMethodMayBeStatic
class CodeGenerator:
    __code_offset = 0

    symbol_table = SymbolTable()

    def gen_code(self, code, param):
        # noinspection PyStatementEffect
        return {
            Cmd.HALT: lambda x: self.__halt(x),
            Cmd.DECLARE: lambda x: self.__declare(x),
            Cmd.DECLARE_ARRAY: lambda x: self.__declare_array(x),
            Cmd.IDENTIFIER1: lambda x: self.__get_identifier(x),
            Cmd.ASSIGN: lambda x: self.__assign(x),
        }[code](param)

    def __halt(self, x):
        print("HALT")

    def __declare(self, x):
        self.symbol_table.put_symbol(x)

    def __declare_array(self, x):
        self.symbol_table.put_array(x[0], x[1], x[2])

    def __get_identifier(self, x):
        pass

    def __assign(self, x):
        pass
