from dataclasses import dataclass
from os.path import commonprefix
from typing import Any
import sys

@dataclass
class CDefinition:
    """
    Basic class holding C definition (macro or enum) name and value
    Comparisions are done by value
    """
    name: str
    value: Any

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value
    
    def __le__(self, other):
        return self == other or self < other
    
    def __ge__(self, other):
        return self == other or self > other
    
    def __ne__(self, other):
        return not self == other


class ParserCreator:
    """
    class holding an macro name, and a list of its CDefinitions
    """
    verbose = False
    masks = []
    def __init__(self, name: str, cdefs: list, inline_type = None,):
        self.name = name
        self.cdefs = cdefs
        self.inline_type = inline_type

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
        merged = self._merge_cdefs()
        if merged is None or len(merged) == 0:
            return ''
        if self.inline_type is not None:
            function = self._create_inline_function(merged)
            if self._create_inline_function_name() in self.masks:
                function += '\n' + self._create_mask_parser(merged)
            return function            
        return self._create_macro(merged)

    def _create_macro(self, merged):
        """
        creates 2 C macros:
            self.name_MAX_LEN - holding the max length of the names returned
            self.name_PARSER  - macro receiving a value and a buffer, that copies the name of the value to the buffer
        :return: string defining the macros
        :rtype: str
        """
        
        macro_name = f'{self.name.upper()}_PARSER'
        max_length = max([len(name) + 1 for name in merged.keys()])
        max_length = max(max_length, len('Unknown') + 1)
        max_length_macro = f'#define {self.name.upper()}_MAX_LEN ({max_length})'
        macro = f'''#define {self.name.upper()}_PARSER(n, buf) do {{
    switch(n) {{'''
        for name in merged:
            macro += f'''
    case {merged[name].name}:
            strcpy(buf, "{name}");
            break;'''
        macro += '''
    default:
            strcpy(buf, "Unknown");
            break;
    }
} while (0);'''
        final_macro = '\n'.join([line + '\\' for line in macro.splitlines()[:-1]])
        final_macro += '\n' + macro.splitlines()[-1]
        self._log(f'Created macro: {self.name.upper()}_MAX_LEN ({max_length})')
        self._log(f'Created macro: {macro_name}(n, buf)')
        if 'all' in self.masks or macro_name in self.masks:
            mask_parser = ''
        return max_length_macro + '\n' + final_macro

    def _create_inline_function_name(self):
        return self.name.lower() + '_parser'

    def _create_inline_function(self, merged):
        """
        Creates an inline function, taking argument of type self.inline_type and returning a pointer to 'const char *'
        the function will be named 'self.name_parser'
        :return: string defining the inline function
        :rtype: str
        """
        function = f'''static inline const char * {self._create_inline_function_name()}({self.inline_type} n) {{
    switch(n) {{'''
        for name in merged:
            function += f'''
    case {merged[name].name}:
        return "{name}";'''
        function += '''
    default:
        return "Unknown";
    }
}'''
        self._log(f'Created inline function: {self.name.lower()}_parser({self.inline_type} n)')
        return function
    
    def _create_mask_parser(self, merged):
        static_buffer_len = len(' | ') * (len(merged.keys()) - 1) + sum([len(name) for name in merged.keys()]) + 1
        value_count = len(merged.keys())
        mask = f'''static inline const char * {self.name.lower()}_mask_parser({self.inline_type} n) {{
    static char buffer[{static_buffer_len}] = {{ 0 }};
    memset(buffer, 0, sizeof(buffer));
    int i = 0;'''

        i = 1
        for name in merged:
            if i != value_count:
                string_to_add = f'"{name} | "'
            else:
                string_to_add = f'"{name}"'
            string_len = len(string_to_add) - 2 # subtract 2 from memcpy size to account for the ""
            mask += f'''
    if (n & {merged[name].name}) {{
        memcpy(buffer + i, {string_to_add}, {string_len});
        i += {string_len};
    }}'''
            i += 1
        mask += f'''
    else if (i > 0){{
        buffer[i - {len(' | ')}] = 0;
    }}
    return buffer;
}}'''
        return mask