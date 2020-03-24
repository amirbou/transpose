#! /usr/bin/env python
from pyclibrary import CParser
from .enums import create_enum_macros
from .marcos import create_define_macros
from .recursive_utils import *


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


def transpose_single_file(path: str, macros: dict, basename: bool):
    """
    Parses the header file in path and returns header file of macros
    :param path: path: path of header to create macros for
    :param macros: dictionary of macros to define before parsing the header
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    :return: transposed header file content and dictionary of parsed macros
    :rtype: (str, dict)
    """
    for key, value in macros.items():
        macros[key] = str(value)
    parser = CParser([path], macros=macros)

    enum_macros = create_enum_macros(parser.defs['enums'])
    define_macros, parsed_macros = create_define_macros(parser.defs['macros'])

    if basename:
        import os
        path = os.path.basename(path)
    return create_output(path, enum_macros, define_macros), parsed_macros


def main(path: str,
         out_path: str,
         macros: list,
         basename: bool,
         recursive: bool,
         parse_std: bool,
         compiler: str,
         include_dirs: list,
         max_headers: int,
         force: bool
         ):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for
    :param out_path: path in which the generated header will be created, if in recursive mode,
                     path to directory in which the generated headers will reside
    :param macros: list of macros to pass to the header parser (i.e DEBUG=True)
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    :param recursive: if True, recursively run through included (local) header files (#include "header.h")
    :param parse_std: if True, when recursing through included header files, also parse #include <header.h>
    :param compiler: if parse_std, use the provided compiler to get the default include directories
    :param include_dirs: list of include directories to search in when running recursively.
    :param max_headers: maximum number of headers to parse in recursion mode
    :param force: overwrite existing out_path
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
    for include_dir in include_dirs:
        if not os.path.exists(include_dir):
            raise ValueError(f'include dir {include_dir} does not exist')
    if recursive:
        traversal_list = RecursiveUtil(path, parse_std, include_dirs, compiler, max_headers).create_header_traversal_list()
        output = []
        for header in traversal_list:
            transposed, macros_dict = transpose_single_file(header, macros_dict, basename)
            output.append((header, transposed))
        try:
            os.mkdir(out_path)
        except FileExistsError:
            if not force:
                raise ValueError(f'Directory {out_path} already exists, use -f to overwrite')
        for header, transposed in output:
            with open(os.path.join(out_path, 'transposed_' + header), 'w') as writer:
                writer.write(transposed)
        return 0
    else:
        output, _ = transpose_single_file(path, macros_dict, basename)
        if os.path.exists(out_path) and not force:
            raise ValueError(f'File {out_path} already exists, use -f to overwrite')
        with open(out_path, 'w') as fd:
            fd.write(output)
