#! /usr/bin/env python
from pyclibrary import CParser, utils
from .enums import create_enum_macros
from .macros import create_define_macros
from .recursive_utils import *
import sys

def create_output(orig_path: str, enum_macros: list, define_macros: list):
    """
    Creates the generated header file
    :param orig_path: path of the original file, to be included in the generated header
    :param enum_macros: list of macros associated with extracted enum's
    :param define_macros: list of macros associated with extracted define's
    :return: header file with includes to the original header and string.h and all the macros created.
    """
    header = f'#pragma once\n#include <string.h>\n#include <stdint.h>\n#include "{orig_path}"\n\n\n'
    header += '\n\n\n'.join(enum_macros)
    header += '\n\n\n'
    header += '\n\n\n'.join(define_macros)
    header += '\n'
    return header


def transpose_files(paths: list, macros: dict):
    """
    Parses the header files in paths and returns header file of macros
    :param paths: list of path of headers to create macros for. should be ordered in topological ordering regarding dependency
    :param macros: dictionary of macros to define before parsing the header
    :return: transposed header file content and dictionary of parsed macros
    :rtype: str
    """
    parser = CParser(paths, macros=macros)
    enum_macros = create_enum_macros(parser.defs['enums'])
    define_macros = create_define_macros(parser.defs['macros'])

    path = paths[-1]  # only the last header is needed to be included, as it will #include all the others
    return create_output(os.path.basename(path), enum_macros, define_macros)


def main(path: str,
         out_path: str,
         macros: list,
         recursive: bool,
         parse_std: bool,
         compiler: str,
         include_dirs: list,
         max_headers: int,
         force: bool,
         dry_run: bool
         ):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for.
    :param out_path: path in which the generated header will be created.
    :param macros: list of macros to pass to the header parser (i.e DEBUG=True).
    :param recursive: if True, recursively run through included (local) header files (#include "header.h").
    :param parse_std: if True, when recursing through included header files, also parse #include <header.h>.
    :param compiler: if parse_std, use the provided compiler to get the default include directories.
    :param include_dirs: list of include directories to search in when running recursively.
    :param max_headers: maximum number of headers to parse in recursion mode.
    :param force: overwrite existing out_path.
    :param dry_run: print a list of parsers to be created instead of creating the output file.
    """
    try:
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
            if not os.path.isdir(include_dir):
                raise ValueError(f'include dir {include_dir} does not exist')

        if recursive:
            traversal_list = RecursiveUtil(path, parse_std, include_dirs, compiler, max_headers).create_header_traversal_list()
            output = transpose_files(traversal_list, macros_dict)
        else:
            output = transpose_files([path, ], macros_dict)
        
        if dry_run:
            return 0
        
        if out_path == '-':
            sys.stdout.write(output)
            return 0
        if os.path.exists(out_path) and not force:
            raise ValueError(f'File {out_path} already exists, use -f to overwrite')
        with open(out_path, 'w') as fd:
            fd.write(output)
        return 0
    
    except ValueError as error:
        print(error, file=sys.stderr)
        return -1
