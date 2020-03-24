#! /usr/bin/env python
from pyclibrary import CParser
from .enums import create_enum_macros
from .marcos import create_define_macros
from .arithmatic_parser import *
import re


def create_output(orig_path: str, enum_macros: list, define_macros: list):
    """
    Creates the generated header file
    :param orig_path: path of the original file, to be included in the generated header
    :param enum_macros: list of macros associated with extracted enum's
    :param define_macros: list of macros associated with extracted define's
    :return: header file with includes to the original header and string.h and all the macros created.
    """
    header = f'#pragma once\n#include <string.h>\n#include "{orig_path}"\n\n\n'
    header += '\n\n\n'.join(enum_macros)
    header += '\n\n\n'
    header += '\n\n\n'.join(define_macros)
    return header


def parse_macros_values(macros: dict):
    """
    Arithmetically parse the values of integral (and floating point) macros, in order to help creating a one to one
    mapping from values to names
    :param macros: dictionary of unparsed macros
    :return: the macros dictionary, after parsing the values (in place)
    :rtype: dict
    """
    values_changed = True
    arithmetic_parser = MacrosArithmeticParser()
    while values_changed:
        values_changed = False
        for name, value in macros.items():
            new_value = None
            if not isinstance(value, (int, float)):
                try:
                    result = arithmetic_parser.parse(value)
                    new_value = result.evaluate()
                except NameError:
                    continue
            if new_value is not None and new_value != value:
                macros[name] = new_value
                values_changed = True
                arithmetic_parser.add_variables({name: new_value, })
    return macros


def hack_fix_hex_values(macros: dict):
    """
    iterate through macros and replace hex values from "0xabc" to "0x'abc'".
    this is a dirty hack so the arithmetic parser for the 0x operator created will receive the number unparsed,
    because the default numbers parser is evaluating 'a1' to 0
    :param macros: dictionary of macros
    :return: the macros dictionary, after replacing the values (in place)
    :rtype: dict
    """
    for name, value in macros.items():
        macros[name] = re.sub(r"0[xX]([0-9a-fA-F]+)", r"0x'\1'", value)


def main(path: str, out_path: str, macros: list, basename=True):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for
    :param out_path: path in which the generated header will be created
    :param macros: list of macros to pass to the header parser (i.e DEBUG=True)
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    """
    # TODO: recursively parse headers
    macros_dict = dict()
    if macros:
        for macro in macros:
            if macro.count('=') == 1:
                key, value = macro.split('=')
                macros_dict[key] = value
            elif macro.count('=') == 0:
                macros_dict[macro] = ''
            else:
                raise ValueError('macros must comply to the gcc -D argument format')
    parser = CParser([path], macros=macros_dict)
    hack_fix_hex_values(parser.defs['macros'])
    parse_macros_values(parser.defs['macros'])

    enum_macros = create_enum_macros(parser)
    define_macros = create_define_macros(parser)

    if basename:
        import os
        path = os.path.basename(path)
    output = create_output(path, enum_macros, define_macros)
    with open(out_path, 'w') as fd:
        fd.write(output)
