from .macro_creator import Enumee, MacroCreator


def create_enum_macros(enums: dict):
    """
    finds all enums declared in code text, merges enumees with same value and creates a macro for each
    :param enums: dictionary where enums[enum_name] is dictionary of enumees
    :return: list of resulting macros
    :rtype: list
    """
    macros = []
    for enum in enums:
        enumee_list = [Enumee(enumee.upper(), enums[enum][enumee]) for enumee in enums[enum]]
        current_enum = MacroCreator(enum.upper(), enumee_list)
        macros.append(current_enum.create_macro())

    return macros
