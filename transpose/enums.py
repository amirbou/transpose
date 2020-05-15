from .parser_creator import CDefinition, ParserCreator


class Enumee(CDefinition):
    """
    class holding name and values extracted from specific enum
    values are used to try resolve multiple enumees with the same value
    """
    pass


def create_enum_macros(enums: dict, verbose = False):
    """
    finds all enums declared in code text, merges enumees with same value and creates a macro for each
    :param enums: dictionary where enums[enum_name] is dictionary of enumees
    :param verbose: Use more verbose ParserCreator
    :return: list of resulting macros
    :rtype: list
    """
    macros = []
    for enum in enums:
        enumee_list = [Enumee(enumee.upper(), enums[enum][enumee]) for enumee in enums[enum]]
        current_enum = ParserCreator(enum.upper(), enumee_list, inline_type=f'enum {enum}', verbose=verbose)
        macros.append(current_enum.create_parser())

    return macros
