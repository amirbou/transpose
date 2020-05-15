from dataclasses import dataclass
from os.path import commonprefix
from typing import Any
import sys

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


class ParserCreator:
    """
    class holding an macro name, and a list of its CDefinitions
    """
    def __init__(self, name: str, cdefs: list, inline_type = None, verbose = False):
        self.name = name
        self.cdefs = cdefs
        self.inline_type = inline_type
        self.verbose = verbose

    def _log(self, message):
        if self.verbose:
            print(message, file=sys.stderr)
    
    def _merge_cdefs(self):
        """
        Merges cdefs with the same value so the reverse lookup will return PREFIX_VAL1_OR_VAL2 where prefix is
        a common prefix of val1 and val2 and VAL1, VAL2 are val1,val2 without the prefix.
        :return: dictionary such that dict[cdefs_merged_name] = one cdef associated with it
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

    def create_parser(self):
        """
        Chooses whether to create an inline function or macro, based on the presence of inline_type
        :return: string defining parser macros / function
        :rtype: str
        """
        if self.inline_type:
            return self._create_inline_function()
        return self._create_macro()


    def _create_macro(self):
        """
        creates 2 C macros:
            self.name_MAX_LEN - holding the max length of the names returned
            self.name_PARSER  - macro receiving a value and a buffer, that copies the name of the value to the buffer
        :return: string defining the macros
        :rtype: str
        """
        merged = self._merge_cdefs()
        if merged is None or len(merged) == 0:
            return ""
        max_length = max([len(name) + 1 for name in merged.keys()])
        max_length = max(max_length, len('Unknown') + 1)
        max_length_macro = f"#define {self.name.upper()}_MAX_LEN ({max_length})"
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
        self._log(f'Created macro: {self.name.upper()}_MAX_LEN ({max_length})')
        self._log(f'Created macro: {self.name.upper()}_PARSER(n, buf)')
        return max_length_macro + '\n' + final_macro

    def _create_inline_function(self):
        """
        Creates an inline function, taking argument of type self.inline_type and returning a pointer to 'const char *'
        the function will be named 'self.name_parser'
        :return: string defining the inline function
        :rtype: str
        """
        merged = self._merge_cdefs()
        if merged is None or len(merged) == 0:
            return ""
        function = f"""static inline const char * {self.name.lower()}_parser({self.inline_type} n) {{
    switch(n) {{"""
        for name in merged:
            function += f"""
    case {merged[name].name}:
        return \"{name}\";"""
        function += """
    default:
        return \"Unknown\";
    }
}"""
        self._log(f'Created inline function: {self.name.lower()}_parser({self.inline_type} n)')
        return function