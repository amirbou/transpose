from plusminus import ArithmeticParser, ArithmeticParseException
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
