from dataclasses import dataclass
from pyclibrary import CParser


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
    max_length_macro = f"#define {macro_name_prefix.upper()}_MAX_LEN {max_length}"
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
    return max_length_macro + '\n' + final_macro


def strip_underscore(st: str):
    """
    Removes _* suffix from st
    :param st: string
    :return: string without the last _
    :rtype: str
    """
    return st[:st.rindex('_')]


# TODO: Handle floats
@dataclass
class Define:
    """
    class holding name and values extracted from #define
    values are use to try and merge lists of Define's to minimize resulting code
    """
    name: str
    value: int

    def __init__(self, name, value):
        """
        casts value from string to integer, might throw ValueError
        """
        self.name = name
        if isinstance(value, int):
            self.value = value
        else:
            self.value = int(value, 0)

    def __eq__(self, other):
        """
        compares two Defines by value.
        :param other: other Define
        :return: True iff self and other have the same value
        :rtype: bool
        """
        if self.value == other.value:
            return True


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
        except ValueError:
            pass
    prefixes, no_prefix = find_prefixes(defines)
    prefixes = merge_prefixes(prefixes)
    macros = []
    for prefix in prefixes:
        macros.append(create_macro(prefix, [define.name for define in prefixes[prefix]]))
    macros.append(create_macro("_DEFAULT", [define.name for define in no_prefix]))

    return macros

