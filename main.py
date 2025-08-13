#!/usr/bin/python3
#
#  PROGRAM: main.py
#
#  PURPOSE: This is just a simple, Python-based test to play around with a path length algorithm or two
#           and with re-arranging the input data to see how it changes the number of loops/comparisons,
#           etc.
#
#  DATE:    August, 11, 2025
#
#  AUTHOR:  Christopher Petersen
#
#  NOTES:   It doesn't do a ton of error-checking on the inputs.  It doesn't check to make sure the
#           graph is either connected (a deal breaker if not) or acyclic (a big deal breaker).
#
from csv import DictReader
from sortedcontainers import SortedDict     #  The only dependency outside the standard libraries
from sys import argv as g_argv, exit
from time import perf_counter


#  Not much more than a dataclass, but not a lot of boilerplate either
#  Obviously:  FROM,TO,LENGTH - v1 in V, v2 in V, and l a positive real
class Edge:
    def __init__(self, p_from: str, p_to: str, p_length: float) -> None:
        if ((p_from != '') and (p_to != '') and (p_length > 0)):
            self.d_from: str = p_from
            self.d_to: str = p_to           #  Kind of redundant, since they'll be in a list w/in the destination vertex
            self.d_length: str = p_length
        else:
            raise ValueError(f'Edge: constructor requires non-empty from/to node names and positive length')
        return


#  Not a ton of functionality to this class
#  Keeping up the extra d_count_incoming saves us an extra len() one or two places
class Vertex:
    def __init__(self, p_name: str) -> None:
        self.d_name: str = p_name       #  Redundant but useful for debugging output
        self.d_count_incoming: int = 0
        self.d_incoming: list[Edge] = []
        self.d_length_incoming: float = -1.0
        self.d_shortest: str = ' '
        return

    def add_incoming_edge(self, p_incoming: dict[str,str]) -> int:
        """
        Create an Edge on the fly, append it, and increment the count of in-coming edges.
        Any funny business in the headers or format of the CSV will probably raise exceptions here.
        """
        self.d_incoming.append(Edge(p_incoming['From'],p_incoming['To'],float(p_incoming['Length'])))
        self.d_count_incoming += 1
        return self.d_count_incoming
    
    def set_source(self) -> None:
        """
        The d_length_incoming defaults to -1, so reset it to zero for a node with no in-coming edges.
        One small bit of data checking.
        """
        if self.d_count_incoming == 0:
            self.d_length_incoming = 0
        else:
            raise ValueError(f'Vertex: Only a vertex with no in-coming edges can be labeled as the single source')


def gather_path(p_sd_vertices:SortedDict[str,Vertex], p_end: str) -> list[str]:
    """
    This is where we could get ourselves into trouble if we're not using an acyclic graph!  So far, it looks
    like the single d_shortest value keeps us out of trouble.
    """
    l_return_value: list[str] = [p_end]

    l_curr: str = p_end
    while p_sd_vertices[l_curr].d_shortest != ' ':
        l_return_value.append(p_sd_vertices[l_curr].d_shortest)
        l_curr = p_sd_vertices[l_curr].d_shortest
    l_return_value.reverse()

    return l_return_value


def load_from_file(p_fileName: str, p_sd_vertices: SortedDict[str,Vertex]) -> bool:
    """
    Load the edges from a file in CSV format with headers: From,To,Length
    We don't have to explicitly load the vertices, since the edges name them in pairs anyway.
    Obviously, there are a ton of possible exceptions that could be thrown either here or in
    called functions/methods.
    """
    l_return_value: bool = False
    with open(p_fileName, 'r') as l_file:
        l_dict_reader: DictReader = DictReader(l_file)
        for l_dict in l_dict_reader:
            if l_dict['From'] not in p_sd_vertices:
                p_sd_vertices[l_dict['From']] = Vertex(l_dict['From'])
            if l_dict['To'] not in p_sd_vertices:
                p_sd_vertices[l_dict['To']] = Vertex(l_dict['To'])
            p_sd_vertices[l_dict['To']].add_incoming_edge(l_dict)
            l_return_value = True

            # print(f'Input data: {l_dict}')
    return l_return_value


def load_sd_by_incoming_count(p_sd_incoming_edges: SortedDict[int,list[str]], p_sd_vertices: SortedDict[str,Vertex]) -> None:
    """
    Trivial loop over the loaded data to make lists of Vertex names in buckets by count of in-coming edges
    """
    for l_vertex in p_sd_vertices:
        if p_sd_vertices[l_vertex].d_count_incoming not in p_sd_incoming_edges:
            p_sd_incoming_edges[p_sd_vertices[l_vertex].d_count_incoming] = []
        p_sd_incoming_edges[p_sd_vertices[l_vertex].d_count_incoming].append(l_vertex)
    return


def print_results(p_sd_vertices: SortedDict[str,Vertex]) -> None:
    """
    A little extra for debugging purposes
    """
    for l_vertex in sorted(p_sd_vertices):
        print(f'{l_vertex=} {p_sd_vertices[l_vertex].d_length_incoming} {gather_path(p_sd_vertices, l_vertex)}')
    return


def resolve_loop(p_sd_incoming_edges: SortedDict[int,list[str]], p_sd_vertices: SortedDict[str,Vertex]) -> (int, int):
    """
    This is where things happen.  For every main loop, we loop in increasing order by count of in-coming edges, then vertices in
    the equivalence list, then their in-coming edges.
    """
    l_count_changes: int = 0
    l_count_unsatisfied: int = 0

    for l_count_incoming in p_sd_incoming_edges:
        for l_vertex in p_sd_incoming_edges[l_count_incoming]:
            for l_incoming_edge in p_sd_vertices[l_vertex].d_incoming:
                if p_sd_vertices[l_incoming_edge.d_from].d_length_incoming == -1:
                    l_count_unsatisfied += 1
                else:
                    if ((p_sd_vertices[l_vertex].d_length_incoming == -1) or ((p_sd_vertices[l_incoming_edge.d_from].d_length_incoming + l_incoming_edge.d_length) < p_sd_vertices[l_vertex].d_length_incoming)):
                        p_sd_vertices[l_vertex].d_length_incoming = p_sd_vertices[l_incoming_edge.d_from].d_length_incoming + l_incoming_edge.d_length
                        p_sd_vertices[l_vertex].d_shortest = l_incoming_edge.d_from
                        l_count_changes += 1

    return l_count_unsatisfied, l_count_changes


def set_single_source(p_sd_vertices: SortedDict[str,Vertex]) -> bool:
    """
    Find a Vertex with no in-coming edges and reset its d_length_incoming to zero.  One of the few error
    checks is this raises an exception if there are multiple Vertex with no in-coming edges.
    """
    l_return_value: bool = False
    for l_vertex in p_sd_vertices:
        if p_sd_vertices[l_vertex].d_count_incoming == 0:
            if l_return_value is False:
                p_sd_vertices[l_vertex].set_source()
                l_return_value = True
            else:
                raise ValueError(f'set_single_source: Only one vertex can have zero in-coming edges')
    return l_return_value


def main(p_argv: list[str]) -> None:
    """
    Basically, some setup and a main loop to "resolve" the lengths of the paths through the single-source,
    connected, directed, acyclic graph with some data outputs for debugging purposes.
    """
    l_count_changes: int = -1
    l_count_loops: int = 0
    l_count_unsatisfied: int = -1
    l_sd_incoming_edges: SortedDict[int,list[str]] = {}
    l_sd_vertices: SortedDict[str,Vertex] = {}

    if len(p_argv) == 2:
        if load_from_file(p_argv[1], l_sd_vertices):
            # print(f'Data loaded!')
            # print(f'{l_sd_vertices}')
            # print(f'Zero in-coming Edge Vertices: {[x for x in l_sd_vertices if l_sd_vertices[x].d_count_incoming == 0]}')

            if set_single_source(l_sd_vertices):
                load_sd_by_incoming_count(l_sd_incoming_edges, l_sd_vertices)
                # print(f'{l_sd_incoming_edges}')
                l_time1 = perf_counter()
                while ((l_count_unsatisfied != 0) and (l_count_changes != 0)):
                    # print(f'{l_count_loops}:')
                    # print_lengths(l_sd_vertices)
                    l_count_unsatisfied, l_count_changes = resolve_loop(l_sd_incoming_edges, l_sd_vertices)
                    l_count_loops += 1
                l_time2 = perf_counter()
                print(f'Elapsed time: {l_time2 - l_time1}')
                print(f'{l_count_loops}:')
                print_results(l_sd_vertices)
            else:
                print(f'No from Vertex with zero in-coming Edge found!')
        else:
            print(f'No data loaded!')
    else:
        print(f'USAGE:  main.py input-file')

    return


#  The usual safety check
if __name__ == '__main__':
    main(g_argv)
    exit(0)