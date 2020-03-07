#! /usr/bin/env python
import argparse
from dataclasses import dataclass
from pyclibrary import CParser
from os.path import commonprefix


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
    macro = f"""#define {macro_name_prefix.upper()}_PARSER(n, buf) do {{
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
} while (0);"""
    final_macro = '\n'.join([line + '\\' for line in macro.splitlines()[:-1]])
    final_macro += '\n' + macro.splitlines()[-1]
    return define_max_length + '\n' + final_macro


def extract_enums(parser: CParser):
    """
    finds all enums declared in code text, and their name
    :param parser: CParser of the header
    :return: dictionary of [enum_name]=list of (names of ) values
    :rtype: dict
    """
    enums = parser.defs['enums']
    extracted = {}
    for enum in enums:
        extracted[enum] = list(enums[enum].keys())
    return extracted


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


def extract_defines(parser: CParser):
    """
    Extracts defines and groups them by prefix.
    :param parser: CParser of the header
    :return: dictionary where [prefix: str] = list of Define's with prefixed names after merging,
             and list of Define's without a sensible prefix
    :rtype: tuple(dict, list)
    """
    defines = [Define(name, value) for name, value in parser.defs['macros'].items()]
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
    header = f'#pragma once\n#include <string.h>\n#include "{orig_path}"\n\n\n'
    header += '\n\n\n'.join(enum_macros)
    header += '\n\n\n'
    header += '\n\n\n'.join(define_macros)
    return header


def main(path: str, out_path: str, basename=True):
    """
    Parses the header file in path and outputs header file of macros to out_path
    :param path: path of header to create macros for
    :param out_path: path in which the generated header will be created
    :param basename: if True, the generated header with use #include "`basename path`" instead of the original one
    """
    parser = CParser([path])
    enum_macros = []
    define_macros = []

    enums = extract_enums(parser)
    for enum_name in enums:
        enum_macros.append(create_macro(enum_name, enums[enum_name]))
    prefixes, no_prefix = extract_defines(parser)
    for prefix in prefixes:
        define_macros.append(create_macro(prefix, [define.name for define in prefixes[prefix]]))
    define_macros.append(create_macro("_DEFAULT", [define.name for define in no_prefix]))

    if basename:
        import os
        path = os.path.basename(path)
    output = create_output(path, enum_macros, define_macros)
    with open(out_path, 'w') as fd:
        fd.write(output)
