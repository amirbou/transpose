#! /usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
from .transpose import main
import os, sys



def _main():
    parser = argparse.ArgumentParser(prog='transpose', description='Create macros to reverse enums and defines from header file')
    parser.add_argument('in_file', help='input file')
    parser.add_argument('out_file', help='output file.')
    parser.add_argument('--no-basename', dest='basename', action='store_false',
                        help='include full path to input instead of basename')
    parser.add_argument('-D', action='append', default=[],
                        help='pass macros, as in gcc, for the preproceccor (i.e -D DEBUG)')
    parser.add_argument('-r', dest='recursive', action='store_true',
                        help='recursively transpose included headers, by default, only #include "header.h" are parsed (not <header.h>)')
    parser.add_argument('--parse-std', dest='parse_std', action='store_true',
                        help='when -r is given parse <> includes as well')
    parser.add_argument('--compiler', default='gcc',
                        help='when parse-std is given, use the same default include directories as the provided compiler')
    parser.add_argument('-I', action='append', default=[],
                        help='add include directories to search when recursively transposing headers')
    parser.add_argument('--max-headers', dest='max_headers', default=20, type=int,
                        help='maximum number of headers to parse in recursion mode')
    parser.add_argument('-f,--force', action='store_true', dest='force',
                        help='overwrite existing out_path')
    parser.set_defaults(basename=True, force=False)
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass
    args = parser.parse_args()
    if not args.recursive:
        if args.parse_std or args.I:
            print("Warning: no -r , ignoring --parse-std,-I and max-headers")
    if args.compiler != 'gcc' and not args.parse_std:
        print("Warning: no --parse-std, ignoring --compiler")
    if os.path.curdir not in [os.path.realpath(include_dir) for include_dir in args.I]:  # add cwd if not present
        args.I.insert(0, os.path.curdir)
    return main(args.in_file,
                args.out_file,
                args.D,
                args.basename,
                args.recursive,
                args.parse_std,
                args.compiler,
                args.I,
                args.max_headers,
                args.force
                )


if __name__ == '__main__':
    sys.exit(_main())

