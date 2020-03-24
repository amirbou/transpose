from dataclasses import dataclass
from pyclibrary import CParser
from os.path import commonprefix
from typing import Any


@dataclass
class CDefinition:
    name: str
    value: Any

    def __eq__(self, other):
        """
        compares two CDefs by value.
        :param other: other CDef
        :return: True iff self and other have the same value
        :rtype: bool
        """
        if self.value == other.value:
            return True


class Define(CDefinition):
    """
    class holding name and values extracted from #define
    values are use to try and merge lists of Define's to minimize resulting code
    """
    def __init__(self, name, value):
        """
        casts value from string to integer, might throw ValueError
        """
        self.name = name
        if isinstance(value, (int, float)):
            self.value = value
        else:
            self.value = int(value, 0)


class Enumee(CDefinition):
    """
    class holding name and values extracted from specific enum
    values are used to try resolve multiple enumees with the same value
    """
    pass


class MacroCreator:
    """
    class holding an macro name, and a list of its CDefinitions
    """
    def __init__(self, name: str, cdefs: list):
        self.name = name
        self.cdefs = cdefs

    def _merge_cdefs(self):
        """
        Merges enumees with the same value so the reverse lookup will return PREFIX_VAL1_OR_VAL2 where prefix is
        a common prefix of val1 and val2 and VAL1, VAL2 are val1,val2 without the prefix.
        :return: dictionary such that [enumee_merged_name] = one enumee associated with it
        :rtype: dict
        """
        reverse_cdefs = {}
        result = {}
        for cdef in self.cdefs:
            if cdef.value in reverse_cdefs.keys():
                reverse_cdefs[cdef.value].append(cdef)
            else:
                reverse_cdefs[cdef.value] = [cdef, ]
        for value in reverse_cdefs:
            if len(reverse_cdefs[value]) > 1:
                names = [cdef.name.upper() for cdef in reverse_cdefs[value]]
                prefix = commonprefix(names)
                try:
                    prefix = prefix[:prefix.rindex('_')]
                except ValueError:
                    pass
                final_name = prefix + '_OR'.join([name[len(prefix):] for name in names])
                result[final_name] = reverse_cdefs[value][0]
            else:
                cdef = reverse_cdefs[value][0]
                result[cdef.name] = cdef
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
        merged = self._merge_cdefs()
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
