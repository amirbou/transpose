import argparse
from .transpose import main

__version__ = '0.0.1'
__author__ = 'amirbou'


def _main():
    parser = argparse.ArgumentParser(prog='transpose', description='Create macros to reverse enums and defines from header file')
    parser.add_argument('in_file', help='input file')
    parser.add_argument('out_file', help='output file')
    parser.add_argument('--no-basename', dest='basename', action='store_false',
                        help='include full path to input instead of basename')
    parser.set_defaults(basename=True)
    args = parser.parse_args()
    main(args.in_file, args.out_file, args.basename)


if __name__ == '__main__':
    _main()
