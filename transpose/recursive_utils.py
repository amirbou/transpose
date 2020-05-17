import os
import subprocess
import networkx as nx
import pyclibrary
import re


class RecursiveUtil:
    """
    Class providing methods to generate a list of required headers
    """

    def __init__(self, base_header: str, parse_std: bool, include_dirs: list, compiler: str, macros: list, max_headers=20):
        """
        Creates a RecursiveUtil object, using the include_dirs and compiler to generate a full list of paths to search in
        :param header: name of the base header
        :param parse_std: if True, also find standard headers
        :param include_dirs: list of include dirs
        :param compiler: path/name of the compiler
        :param macros: list of macros of the form 'key=value' or 'key'
        :param max_headers: maximum number of headers to parse
        """
        self.base_header = base_header
        self.parse_std = parse_std
        self.compiler = compiler
        self.include_dirs = include_dirs
        self.macros = macros
        self.max_headers = max_headers

    def include_dir_to_args(self) -> list:
        """
        Converts list of include direcories, to list of argumenets to the compiler including said directories
        """
        return [f'-I{include_dir}' for include_dir in self.include_dirs]
    
    def macros_to_args(self) -> list:
        """
        Converts dict of macros, to list of argumenets to the compiler including said directories
        """
        return [f'-D{macro}' for macro in self.macros]

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
        args = [compiler, flag, self.base_header] + self.include_dir_to_args() + self.macros_to_args()
        output = subprocess.run(args, capture_output=True).stdout.decode('utf-8')
        output = output.split(':')[1] # remove 'objfile.o:'
        output = output.replace('\\', ' ')
        traversal_list = [os.path.abspath(path) for path in output.split()]
        if len(traversal_list) > self.max_headers:
            print(f'Warning: required headers {len(traversal_list)} are more the max allowed ({self.max_headers}).', file=sys.stderr)
            print('Truncating required headers')
            traversal_list = traversal_list[:self.max_headers]
        return traversal_list
        