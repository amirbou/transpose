#! /usr/bin/env python
import argparse
from dataclasses import dataclass
import re


def comment_remover(text: str):
    """
    removes C/C++ comments and empty lines from text
    :param text: text associated to C/C++ code
    :return: code with comments removed
    :rtype: str
    """
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    text = re.sub(pattern, replacer, text)
    return '\n'.join([line for line in text.splitlines() if line.strip() != ''])


def create_macro(macro_name_prefix: str, macro_values: list):
    """
    creates 2 C macros:
        macro_name_prefix_MAX_LEN - holding the max length of the names returned
        macro_name_prefix_PARSER  - macro receiving a value and a buffer, that copies the name of the value to the buffer
    :param macro_name_prefix: prefix of the macros that will be created
    :param macro_values: list of the defines/enumees associated with the macro
    :return: string defining the macros
    :rtype: str
    """
    if macro_values is None or len(macro_values) == 0:
        return ""
    max_length = max([len(value)+1 for value in macro_values])
    max_length = max(max_length, len('Unknown') + 1)
    define_max_length = f"#define {macro_name_prefix.upper()}_MAX_LEN {max_length}"
    macro = f"""#define {macro_name_prefix.upper()}_PARSER (n, buf) do {{
    switch(n) {{"""
    for value in macro_values:
        macro += f"""
    case {value}:
            strcpy(buf, \"{value}\");
            break;"""
    macro += """
    default:
            strcpy(buf, \"Unknown\");
            break;
    }
} while (0)"""
    final_macro = '\n'.join([line + '\\' for line in macro.splitlines()[:-1]])
    final_macro += '\n' + macro.splitlines()[-1]
    return define_max_length + '\n' + final_macro


def extract_enums(text: str):
    """ NOT TESTED
    finds all enums declared in code text, and their name/typedef if available (otherwise the first value is taken for the name)
    :param text: C code
    :return: dictionary of [enum_name]=list of (names of ) values
    :rtype: dict
    """
    all_enums = dict()
    lines = text.splitlines()
    for i in range(len(lines)):
        if 'enum' in lines[i]:
            enum = list()
            start_line = None
            end_line = None
            for j in range(i, len(lines)):
                if '{' in lines[j]:
                    start_line = j
                if '}' in lines[j]:
                    end_line = j
            if start_line is None or end_line is None or start_line > end_line:
                raise Exception()
            if 'typedef' in lines[i]:
                current_line = lines[end_line]
                current_line.strip('};')
                current_line = current_line.strip()
                if current_line == "":
                    print(f"resulting enum name is empty, original line: {lines[end_line]}")
                    raise Exception()
                if current_line.count(' ') != 0:
                    print("enum name found includes spaces, replacing with _")
                    current_line.replace(' ', '_')
                enum_name = current_line
            else:
                current_line = lines[i]
                current_line = current_line.replace('{', '')
                current_line = current_line.replace('enum', '')
                current_line = current_line.replace('typedef', '')
                current_line = current_line.strip()
                if current_line == "":
                    print(f"resulting enum name is empty, original line: {lines[end_line]}")
                    raise Exception()
                if current_line.count(' ') != 0:
                    print("enum name found includes spaces, replacing with _")
                    current_line.replace(' ', '_')
                enum_name = current_line
            for j in range(start_line, end_line + 1):
                current_line = lines[j]
                current_line = current_line.strip()
                if '{' in current_line:
                    index = current_line.index('{')
                    current_line = current_line[index+1:]
                elif '}' in current_line:
                    index = current_line.index('}')
                    current_line = current_line[:index]

                current_line = current_line.strip('{,};')
                if '=' in current_line:
                    enum.append(current_line.split('=')[0])
                else:
                    enum.append(current_line)
            if enum_name == "":
                print("could not find enum name, using first entry instead")
                enum_name = enum[0]
            all_enums[enum_name] = enum
    return all_enums


def strip_underscore(st: str):
    """
    Removes _* suffix from st
    :param st: string
    :return: string without the last _
    :rtype: str
    """
    return st[:st.rindex('_')]

@dataclass
class Define:
    """
    class holding name and values extracted from #define
    values are use to try and merge lists of Define's to minimize resulting code
    """
    name: str
    value: str

    def __eq__(self, other):
        """
        compares two Defines by value, if both values are integers, their numerical value is compared
        :param other: other Define
        :return: True iff self and other have the same value
        :rtype: bool
        """
        if self.value == other.value:
            return True
        try:
            if int(self.value, 0) == int(other.value, 0):
                return True
        except ValueError:
            pass
        finally:
            return False


def merge_prefixes(prefixes_dict: dict):
    """
    Tries to merge prefixes in which one is a prefix of the other, and their values are disjoint
    :param prefixes_dict: dictionary where [prefix: str] = list of Define's with prefixed names
    :return: dictionary where [prefix: str] = list of Define's with prefixed names (hopefully smaller)
    :rtype: dict
    """
    # sorts the keys, because if a string is prefixed by another, they must be 'close' under lexicographic order
    keys = sorted(list(prefixes_dict.keys()))
    merge_candidates = []
    for i in range(len(keys)-1):
        if keys[i+1].startswith(keys[i]):
            merge_candidates.append(i)

    # reverse the candidates, because if we have 'a', 'aa', 'aaa',
    # then it's easier to merge 'aaa' with 'aa' and then 'aa' with 'a' (we only need one loop)
    merge_candidates_rev = merge_candidates[::-1]
    for i in merge_candidates_rev:
        can_merge = True
        # we can't merge if the values of the Define's associated with each prefix are not disjoint
        for define_1 in prefixes_dict[keys[i]]:
            for define_2 in prefixes_dict[keys[i+1]]:
                if define_1 == define_2:
                    can_merge = False
        if can_merge:
            prefixes_dict[keys[i]] += prefixes_dict[keys[i+1]]
            del prefixes_dict[keys[i+1]]
    return prefixes_dict


def find_prefixes(defines: list):
    """
    Finds all prefixes that more then 2 defines share, and the associated strings. All strings that don't share a prefix
    with anything else, are returned as a list.
    the prefixes are searched by _'s (meaning ABC_SHIT, ABC_SHAT will be associated with ABC, not ABC_SH)
    :param defines: list of all Define's found in the code
    :return: dictionary where [prefix: str] = list of Define's with prefixed names,
             and list of Define's without a sensible prefix
    :rtype: tuple(dict, list)
    """
    prefixes_count = {}
    no_prefix = []
    for define in defines:
        prefixes_count[define.name] = [define, ]

    has_lonely = True
    while has_lonely:
        has_lonely = False
        prefixes = list(prefixes_count.keys())
        for prefix in prefixes:
            orig_keys = prefixes_count[prefix]
            count = len(orig_keys)
            if count == 1:
                has_lonely = True
                orig_key = orig_keys[0]
                del prefixes_count[prefix]
                try:
                    new_prefix = strip_underscore(prefix)
                    if new_prefix in prefixes_count.keys():
                        prefixes_count[new_prefix].append(orig_key)
                    else:
                        prefixes_count[new_prefix] = orig_keys
                except ValueError:  # we removed all _ from strings and
                    no_prefix.append(orig_key)
    return prefixes_count, no_prefix


def is_macro(line: str):
    """
    Try to check if line is constant of macro
    :param line:
    :return: True if line contains one of '\','(',')'
    :rtype: bool
    """
    return '\\' in line or '(' in line or ')' in line


def extract_defines(text: str):
    """
    Extracts and parses, single line defines. There is no good check whether the define is a macro or a constant
    :param text: code
    :return: dictionary where [prefix: str] = list of Define's with prefixed names after merging,
             and list of Define's without a sensible prefix
    :rtype: tuple(dict, list)
    """
    lines = [line for line in text.splitlines() if '#define' in line and not is_macro(line)]
    lines = [line.replace('#define', '') for line in lines]
    lines = [' '.join(line.split()) for line in lines]
    defines = []
    for line in lines:
        try:
            i = line.index(' ')
            defines.append(Define(line[:i], line[i+1:]))
        except ValueError:
            pass
    prefixes, no_prefix = find_prefixes(defines)
    prefixes = merge_prefixes(prefixes)
    return prefixes, no_prefix


def create_output(orig_path: str, enum_macros: list, define_macros: list):
    """
    Creates the generated header file
    :param orig_path: path of the original file, to be included in the generated header
    :param enum_macros: list of macros associated with extracted enum's
    :param define_macros: list of macros associated with extracted define's
    :return: header file with includes to the original header and string.h and all the macros created.
    """
    header = f'#include <string.h>\n#include "{orig_path}"\n'
    header += '\n\n\n'.join(enum_macros)
    header += '\n\n\n'.join(define_macros)
    return header


def main(path: str, out_path: str, basename=True):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for
    :param out_path: path in which the generated header will be created
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    """
    with open(path, 'r') as fd:
        text = fd.read()
    text = comment_remover(text)
    enum_macros = []
    define_macros = []
    enums = extract_enums(text)
    for enum_name in enums:
        enum_macros.append(create_macro(enum_name, enums[enum_name]))
    prefixes, no_prefix = extract_defines(text)
    for prefix in prefixes:
        define_macros.append(create_macro(prefix, [define.name for define in prefixes[prefix]]))
    define_macros.append(create_macro("_DEFAULT", [define.name for define in no_prefix]))

    if basename:
        import os
        path = os.path.basename(path)
    output = create_output(path, enum_macros, define_macros)
    with open(out_path, 'w') as fd:
        fd.write(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create macros to reverse enums and defines from header file')
    parser.add_argument('in_file', help='input file')
    parser.add_argument('out_file', help='output file')
    parser.add_argument('--no-basename', dest='basename', action='store_false',
                        help='include full path to input instead of basename')
    parser.set_defaults(basename=True)
    args = parser.parse_args()
    main(args.in_file, args.out_file, args.basename)

