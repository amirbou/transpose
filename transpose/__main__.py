import argparse
from .transpose import main


def _main():
    parser = argparse.ArgumentParser(prog='transpose', description='Create macros to reverse enums and defines from header file')
    parser.add_argument('in_file', help='input file')
    parser.add_argument('out_file', help='output file')
    parser.add_argument('--no-basename', dest='basename', action='store_false',
                        help='include full path to input instead of basename')
    parser.add_argument('-D', action='append', help='pass macros, as in gcc, for the preproceccor (i.e -D DEBUG)')
    parser.set_defaults(basename=True)
    args = parser.parse_args()
    main(args.in_file, args.out_file, args.D, args.basename)


if __name__ == '__main__':
    _main()
