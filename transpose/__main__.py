#! /usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
from .transpose import main
import os, sys

DEFAULT_MAX_HEADERS = 20


def _main():
    parser = argparse.ArgumentParser(prog='transpose', description='Create macros to reverse enums and defines from header file')
    parser.add_argument('in_file', help='input file')
    parser.add_argument('-D', action='append', default=[], metavar='macro[=defn]',
                        help='pass macros, as in gcc, for the preproceccor (i.e -D DEBUG)')
    parser.add_argument('-r', dest='recursive', action='store_true',
                        help='recursively transpose included headers, by default, only #include "header.h" are parsed (not <header.h>)')
    parser.add_argument('--parse-std', dest='parse_std', action='store_true',
                        help='when -r is given parse <> includes as well')
    parser.add_argument('--compiler', default='gcc',
                        help='when parse-std is given, use the same default include directories as the provided compiler')
    parser.add_argument('-I', action='append', default=[], metavar='dir',
                        help='add include directories to search when recursively transposing headers')
    parser.add_argument('--max-headers', dest='max_headers', default=DEFAULT_MAX_HEADERS, type=int,
                        help=f'maximum number of headers to parse in recursion mode ({DEFAULT_MAX_HEADERS} by default)', metavar='n')
    parser.add_argument('-f,--force', action='store_true', dest='force', help='overwrite existing out_path')
    # parser.add_argument('--mask', action='append', default=[], metavar='parser', help='create a mask parser for the given parser')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', help='output file', dest='out_file', nargs='?', default='-', metavar='output file')
    output_group.add_argument('--dry-run', action='store_true', dest='dry_run', help='only list the parsers to be created')
    output_group.add_argument('--brave', action='store_true', dest='is_brave', help=argparse.SUPPRESS)
    parser.set_defaults(force=False)
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass
    args = parser.parse_args()
    if not args.recursive:
        if args.parse_std or args.I:
            print('Warning: no -r , ignoring --parse-std,-I and max-headers', file=sys.stderr)
    if args.compiler != 'gcc' and not args.parse_std:
        print('Warning: no --parse-std, ignoring --compiler', file=sys.stderr)
    if os.path.curdir not in [os.path.realpath(include_dir) for include_dir in args.I]:  # add cwd if not present
        args.I.insert(0, os.path.curdir)
    if not args.dry_run and args.out_file == '-' and sys.stdout.isatty() and not args.is_brave:
        print('Error: cowardly refusing to print to shell (use --brave if necessary)', file=sys.stderr)
        return -1
    return main(args.in_file,
                args.out_file,
                args.D,
                args.recursive,
                args.parse_std,
                args.compiler,
                args.I,
                args.max_headers,
                args.force,
                args.dry_run
                )


if __name__ == '__main__':
    sys.exit(_main())

