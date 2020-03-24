from pyclibrary import CParser
from .macro_creator import Enumee, MacroCreator


def create_enum_macros(parser: CParser):
    """
    finds all enums declared in code text, merges enumees with same value and creates a macro for each
    :param parser: CParser of the header
    :return: list of resulting macros
    :rtype: list
    """
    enums = parser.defs['enums']
    macros = []
    for enum in enums:
        enumee_list = [Enumee(enumee.upper(), enums[enum][enumee]) for enumee in enums[enum]]
        current_enum = MacroCreator(enum.upper(), enumee_list)
        macros.append(current_enum.create_macro())

    return macros
