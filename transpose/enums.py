from pyclibrary import CParser
from dataclasses import dataclass
from os.path import commonprefix


@dataclass
class Enumee:
    """
    class holding name and values extracted from specific enum
    values are used to try resolve multiple enumees with the same value
    """
    name: str
    value: int


class Enum:
    """
    class holding an enum name, and a list of its enumees
    """
    def __init__(self, name: str, enumees: list):
        self.name = name
        self.enumees = enumees

    def _merge_enumees(self):
        """
        Merges enumees with the same value so the reverse lookup will return PREFIX_VAL1_OR_VAL2 where prefix is
        a common prefix of val1 and val2 and VAL1, VAL2 are val1,val2 without the prefix.
        :return: dictionary such that [enumee_merged_name] = one enumee associated with it
        :rtype: dict
        """
        reverse_enumees = {}
        result = {}
        for enumee in self.enumees:
            if enumee.value in reverse_enumees.keys():
                reverse_enumees[enumee.value].append(enumee)
            else:
                reverse_enumees[enumee.value] = [enumee, ]
        for value in reverse_enumees:
            if len(reverse_enumees[value]) > 1:
                names = [enumee.name.upper() for enumee in reverse_enumees[value]]
                prefix = commonprefix(names)
                try:
                    prefix = prefix[:prefix.rindex('_')]
                except ValueError:
                    pass
                final_name = prefix + '_OR'.join([name[len(prefix):] for name in names])
                result[final_name] = reverse_enumees[value][0]
            else:
                enumee = reverse_enumees[value][0]
                result[enumee.name] = enumee
        return result

    def create_macro(self):
        """
        creates 2 C macros:
            self.name_MAX_LEN - holding the max length of the names returned
            self.name_PARSER  - macro receiving a value and a buffer, that copies the name of the value to the buffer
        :param self:
        :return: string defining the macros
        :rtype: str
        """
        merged = self._merge_enumees()
        if merged is None or len(merged) == 0:
            return ""
        max_length = max([len(name) + 1 for name in merged.keys()])
        max_length = max(max_length, len('Unknown') + 1)
        max_length_macro = f"#define {self.name.upper()}_MAX_LEN {max_length}"
        macro = f"""#define {self.name.upper()}_PARSER(n, buf) do {{
        switch(n) {{"""
        for name in merged:
            macro += f"""
        case {merged[name].name}:
                strcpy(buf, \"{name}\");
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


def create_enum_macros(parser: CParser):
    """
    finds all enums declared in code text, merges enumees with same value and creates a macro for each
    :param parser: CParser of the header
    :return: list of resulting macros
    :rtype: list
    """
    enums = parser.defs['enums']
    macros = []
    for enum in enums:
        enumee_list = [Enumee(enumee.upper(), enums[enum][enumee]) for enumee in enums[enum]]
        current_enum = Enum(enum.upper(), enumee_list)
        macros.append(current_enum.create_macro())

    return macros
