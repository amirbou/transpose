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
        self.include_dirs = self.get_include_dirs(compiler, include_dirs)
        self.max_headers = max_headers

    @staticmethod
    def get_include_dirs(compiler: str, include_dirs: list):
        """
        Extract the include search order from the compiler
        :param compiler: path/name of the compiler
        :param include_dirs: list of -I dir to add to the search
        :return: ordered list of include search paths
        """
        include = []
        for include_dir in include_dirs:
            include.append('-I')
            include.append(include_dir)
        args = [compiler, '-Wp,-v', '-xc', '-', '-fsyntax-only'] + include
        output = subprocess.run(args, capture_output=True, input=b'').stderr.decode('utf-8')
        lines = output.splitlines()
        local_index = lines.index(RecursiveUtil.LOCAL_INCLUDE_MAGIC)
        global_index = lines.index(RecursiveUtil.GLOBAL_INCLUDE_MAGIC)
        end_index = lines.index(RecursiveUtil.END_MAGIC)
        final_include = lines[local_index+1:global_index] + lines[global_index+1:end_index]
        return [os.path.realpath(include_dir.strip()) for include_dir in final_include]

    def find_header(self, header: str):
        """
        Search for a header in the include_dirs
        :param header: header name
        :return: the full path to the header, None if header was not found
        :rtype: str
        """
        try:
            return pyclibrary.utils.find_header(header, dirs=self.include_dirs)
        except OSError:
            return None

    def extract_dependencies(self, header: str):
        """
        Extract a list of headers our header depends on
        :param header: name of the header
        :return: list of headers
        :rtype: list
        """
        path = self.find_header(header)
        if not path:
            raise ValueError(f'Header {header} not found in include directories')
        with open(path, 'r') as reader:
            header_data = reader.read()
        lines = header_data.splitlines()
        included_headers = []
        for line in lines:
            match = self.REGEX_LOCAL.match(line)
            if not match and self.parse_std:
                match = self.REGEX_GLOBAL.match(line)
            if match:
                included_headers.append(match.group(1))
        return included_headers

    def build_dependencies_graph(self):
        """
        Generates the dependencies graph of the base header
        :return The dependencies graph
        :rtype: nx.DiGraph
        """
        new_nodes = True
        graph = nx.DiGraph()
        graph.add_node(self.base_header)
        parsed_headers = []
        while new_nodes:
            new_nodes = False
            if len(graph) > self.max_headers:
                raise ValueError(f'Needed headers surpasses the maximum allowed ({self.max_headers})')
            graph_nodes = graph.copy().nodes
            for current_header in graph_nodes:
                if current_header in parsed_headers:
                    continue
                headers = self.extract_dependencies(current_header)
                for header in headers:
                    if header not in graph:
                        new_nodes = True
                        header_full_path = self.find_header(header)
                        graph.add_node(header_full_path)
                        graph.add_edge(current_header, header_full_path)
                parsed_headers.append(current_header)
        return graph

    def create_header_traversal_list(self):
        """
        Create an ordered list of headers to traverse to meet all the dependencies of self.base_header
        :return: list of headers
        :rtype: list
        """
        graph = self.build_dependencies_graph()
        try:
            traversal_list = list(nx.algorithms.dag.topological_sort(graph))[::-1]
        except nx.NetworkXUnfeasible:
            raise ValueError("Dependencies graph contains cycles")
        return traversal_list
