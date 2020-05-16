from plusminus import ArithmeticParser
try:
    from plusminus import LiteralNode
except ImportError:
    from plusminus.plusminus import LiteralNode


# TODO: write tests for all this shit, maybe break up main a little
class MacrosArithmeticParser(ArithmeticParser):
    def add_variables(self, vars_dict: dict, reset=False):
        """
        Update the vars and constants dictionary used when parsing a string, if reset is True, then the current dictionary
        is replaced with vars_dict
        :param vars_dict: dictionary of constants and variables and their values
        :param reset: if True, the old dictionary will be ignored
        :return: None
        """
        formatted_dict = {}
        for var_name, value in vars_dict.items():
            formatted_dict[var_name] = LiteralNode([value])
        if reset:
            self._variable_map = formatted_dict
        else:
            self._variable_map.update(formatted_dict)

    def customize(self):
        self.add_operator('0x', 1, ArithmeticParser.RIGHT, lambda a: int(a, 16))
        self.add_operator('<<', 2, ArithmeticParser.LEFT, lambda a,b: a << b)
        self.add_operator('>>', 2, ArithmeticParser.LEFT, lambda a,b: a >> b)
        self.add_operator('|', 2, ArithmeticParser.LEFT, lambda a,b: a | b)
        self.add_operator('&', 2, ArithmeticParser.LEFT, lambda a,b: a & b)
        self.add_operator('~', 1, ArithmeticParser.RIGHT, lambda a: ~a )
        self.add_operator('L', 1, ArithmeticParser.LEFT, lambda a: a)
        self.add_operator('U', 1, ArithmeticParser.LEFT, lambda a: a)
        self.add_operator('##', 2, ArithmeticParser.LEFT, lambda a,b: int(f'{a}{b}'))
        self.add_operator('(void*)', 1, ArithmeticParser.RIGHT, lambda a: a)
        self.add_function('__attribute__', 1, lambda a: None)
        self.add_function('__pass_object_size_n', 1, lambda a: None)
