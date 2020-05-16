from .parser_creator import ParserCreator, CDefinition
from .arithmatic_parser import *
from pyparsing import ParseException
import sys
import re

HEX_REGEX = re.compile(r"0[xX]([0-9a-fA-F]+)")


class Define(CDefinition):
    """
    class holding name and values extracted from #define
    values are use to try and merge lists of Define's to minimize resulting code
    """
    def __init__(self, name, value):
        """
        casts value from string to integer, might raise ValueError
        """
        if not isinstance(value, (int, float)):
            value = int(value, 0)
        super().__init__(name, value)


def strip_underscore(st: str) -> str:
    """
    Removes _* suffix from st
    :param st: string
    :return: string without the last _
    :rtype: str
    """
    return st[:st.rindex('_')]


def parse_macros_values(macros: dict) -> dict:
    """
    Arithmetically parse the values of integral (and floating point) macros, in order to help creating a one to one
    mapping from values to names
    :param macros: dictionary of unparsed macros
    :return: the macros dictionary, after parsing the values (in place)
    :rtype: dict
    """
    hack_fix_hex_values(macros)
    values_changed = True
    arithmetic_parser = MacrosArithmeticParser()
    while values_changed:
        values_changed = False
        for name, value in macros.items():
            new_value = None
            if value and not isinstance(value, (int, float)):
                try:
                    result = arithmetic_parser.parse(value)
                    new_value = result.evaluate()
                except NameError:
                    continue
                except ParseException:
                    print(f'Warning: failed to parse {name} {value}', file=sys.stderr)
                    continue
                except RecursionError:
                    continue
            if new_value is not None and new_value != value:
                macros[name] = new_value
                values_changed = True
                arithmetic_parser.add_variables({name: new_value, })
    return macros


def guess_type(cdefs: list) -> str:
    """
    Try to guess C type that would fit the macros values
    :param cdefs: list of CDefinitions
    :return: C integer type
    :rtype str
    """
    try:
        min_value = min(cdefs).value
        max_value = max(cdefs).value
        max_bits = max(max_value.bit_length(), min_value.bit_length())
        
        # signed need one more bit
        if min_value < 0: 
            max_bits += 1
        
        possible_sizes = [8, 16, 32, 64, 128]
        chosen_size = 0
        for size in possible_sizes:
            if max_bits <= size:
                chosen_size = size
                break
        if chosen_size == 0:
            return None
        return f'{"u" if min_value > 0 else ""}int{chosen_size}_t'
    except:
        return None


def hack_fix_hex_values(macros: dict) -> dict:
    """
    iterate through macros and replace hex values from "0xabc" to "0x'abc'".
    this is a dirty hack so the arithmetic parser for the 0x operator created will receive the number unparsed,
    because the default numbers parser is evaluating 'a1' to 0
    :param macros: dictionary of macros
    :return: the macros dictionary, after replacing the values (in place)
    :rtype: dict
    """
    for name, value in macros.items():
        macros[name] = HEX_REGEX.sub(r"0x'\1'", value)
    return macros

def merge_prefixes(prefixes_dict: dict) -> dict:
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


def find_prefixes(defines: list) -> (dict, list):
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


def split_default_parser(defines: list) -> list:
    """
    Split the defines without a prefix to different parsers, to preserve one to one correspondents
    :param defines: list of Define's that hadn't fit in one of the specific parsers
    :return: list of lists of uniquely valued defines
    :rtype: list
    """
    split_parsers = list()
    for define in defines:
        if not split_parsers:  # initialize
            split_parsers.append([define, ])
            continue
        added = False
        for parser in split_parsers:
            can_add = True
            for inserted_define in parser:
                if define.value == inserted_define.value:
                    can_add = False
                    break
            if can_add:
                added = True
                parser.append(define)
        if not added:
            split_parsers.append([define, ])
    return split_parsers


def create_define_macros(original_macros: dict) -> list:
    """
    Parses defines, groups them by prefix, and creates matching macros.
    :param original_macros: dictionary of macros and their values
    :param verbose: use more verbose ParserCreator
    :return: list of created macros, and dict of parsed macros
    :rtype: list
    """
    parse_macros_values(original_macros)

    defines = list()

    for name, value in original_macros.items():
        try:
            defines.append(Define(name, value))
        except (ValueError, TypeError):
            pass
    prefixes, no_prefix = find_prefixes(defines)
    prefixes = merge_prefixes(prefixes)
    macros = []

    for prefix in prefixes:
        macros.append(ParserCreator(prefix, prefixes[prefix], guess_type(prefixes[prefix])).create_parser())

    split_default_parsers = split_default_parser(no_prefix)
    if len(split_default_parsers) == 1:
        macros.append(ParserCreator(f'_DEFAULT', no_prefix, guess_type(no_prefix)).create_parser())
    else:
        for i in range(len(split_default_parsers)):
            macros.append(ParserCreator(f'_DEFAULT_{i}', split_default_parsers[i], guess_type(split_default_parsers[i])).create_parser())
    return macros

