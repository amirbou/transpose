from pyclibrary import CParser
from .macro_creator import MacroCreator, Define


def strip_underscore(st: str):
    """
    Removes _* suffix from st
    :param st: string
    :return: string without the last _
    :rtype: str
    """
    return st[:st.rindex('_')]


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


def split_default_parser(defines: list):
    """
    Split the defines without a prefix to different parsers, to preserve one to one correspondents
    :param defines: list of Define's that hadn't fit in one of the specific parsers
    :return: list of lists of uniquely valued defines
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


def create_define_macros(parser: CParser):
    """
    Extracts defines, groups them by prefix, and creates matching macros.
    :param parser: CParser of the header
    :return: list of created macros
    :rtype: list
    """
    defines = list()

    for name, value in parser.defs['macros'].items():
        try:
            defines.append(Define(name, value))
        except (ValueError, TypeError):
            pass
    prefixes, no_prefix = find_prefixes(defines)
    prefixes = merge_prefixes(prefixes)
    macros = []
    for prefix in prefixes:
        macros.append(MacroCreator(prefix, prefixes[prefix]).create_macro())

    split_default_parsers = split_default_parser(no_prefix)
    if len(split_default_parsers) == 1:
        macros.append(MacroCreator(f'_DEFAULT', no_prefix).create_macro())
    else:
        for i in range(len(split_default_parsers)):
            macros.append(MacroCreator(f'_DEFAULT_{i}', split_default_parsers[i]).create_macro())
    return macros

