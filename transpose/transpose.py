#! /usr/bin/env python
from pyclibrary import CParser
from .enums import create_enum_macros
from .marcos import create_define_macros


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


def main(path: str, out_path: str, macros: list, basename=True):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for
    :param out_path: path in which the generated header will be created
    :param macros: list of macros to pass to the header parser (i.e DEBUG=True)
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    """
    macros_dict = dict()
    for macro in macros:
        if macro.count('=') == 1:
            key, value = macro.split('=')
            macros_dict[key] = value
        elif macro.count('=') == 0:
            macros_dict[macro] = ''
        else:
            raise ValueError('macros must comply to the gcc -D argument format')
    parser = CParser([path], macros=macros_dict)
    enum_macros = create_enum_macros(parser)
    define_macros = create_define_macros(parser)

    if basename:
        import os
        path = os.path.basename(path)
    output = create_output(path, enum_macros, define_macros)
    with open(out_path, 'w') as fd:
        fd.write(output)
