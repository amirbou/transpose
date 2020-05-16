import os
import subprocess
import networkx as nx
import pyclibrary
import re


class RecursiveUtil:
    """
    Class providing methods to generate a list of required headers
    """
    LOCAL_INCLUDE_MAGIC = '#include "..." search starts here:'
    GLOBAL_INCLUDE_MAGIC = '#include <...> search starts here:'
    END_MAGIC = 'End of search list.'
    REGEX_LOCAL = re.compile(r"^\s*\#\s*include\s*\"([^\"]+)\"")
    REGEX_GLOBAL = re.compile(r"^\s*\#\s*include\s*<([^<>]+)>")

    def __init__(self, base_header: str, parse_std: bool, include_dirs: list, compiler: str, max_headers=20):
        """
        Creates a RecursiveUtil object, using the include_dirs and compiler to generate a full list of paths to search in
        :param header: name of the base header
        :param parse_std: if True, also find standard headers
        :param include_dirs: list of include dirs
        :param compiler: path/name of the compiler
        :param max_headers: maximum number of headers to parse
        """
        self.base_header = base_header
        self.parse_std = parse_std
        self.compiler = compiler
        self.include_dirs = include_dirs
        self.max_headers = max_headers

    @staticmethod
    def include_dir_to_args(include_dirs: list) -> list:
        """
        Converts list of include direcories, to list of argumenets to the compiler including said directories
        """
        return [f'-I{include_dir}' for include_dir in include_dirs]

    @staticmethod
    def get_include_dirs(compiler: str, include_dirs: list):
        """
        Extract the include search order from the compiler
        :param compiler: path/name of the compiler
        :param include_dirs: list of -I dir to add to the search
        :return: ordered list of include search paths
        """
        include = RecursiveUtil.include_dir_to_args(include_dirs)

        args = [compiler, '-Wp,-v', '-xc', '-', '-fsyntax-only'] + include
        output = subprocess.run(args, capture_output=True, input=b'').stderr.decode('utf-8')
        lines = output.splitlines()
        local_index = lines.index(RecursiveUtil.LOCAL_INCLUDE_MAGIC)
        global_index = lines.index(RecursiveUtil.GLOBAL_INCLUDE_MAGIC)
        end_index = lines.index(RecursiveUtil.END_MAGIC)
        final_include = lines[local_index+1:global_index] + lines[global_index+1:end_index]
        return [os.path.realpath(include_dir.strip()) for include_dir in final_include]

    def create_header_traversal_list(self):
        """
        Create an ordered list of headers to traverse to meet all the dependencies of self.base_header
        :return: list of headers
        :rtype: list
        """
        traversal_list = []
        flag = '-M'
        if not self.parse_std:
            flag = '-MM'
        args = [compiler, flag, self.base_header] + self.include_dir_to_args(self.include_dirs)
        output = subprocess.run(args, capture_output=True).stdout.decode('utf-8')
        output = output.split(':')[1] # remove 'objfile.o:'
        output = output.replace('\\', ' ')
        traversal_list = [os.path.abspath(path) for path in output.split()]
        if len(traversal_list) > self.max_headers:
            print(f'Warning: required headers {len(traversal_list)} are more the max allowed ({self.max_headers}).', file=sys.stderr)
            print('Truncating required headers')
            traversal_list = traversal_list[:self.max_headers]
        return traversal_list
        