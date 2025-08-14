# cdag_play
Python code to play with some SSCDAG (single-source, connected, directed, acyclic, graph) algorithms in Python

The algorithm is pretty simple, but looking at how well/poorly Python handles this kind of thing without
going to great lengths with strange algorithms or data structures.

USAGE:  main.py csv-input-file

The input file is read with a CSV DictReader and needs headers: From,To,Length

The From and To are strings, so they can contain just about anything in or out of quotes.  The length values 
have to be positive, real numbers.

Changing the order of the input data without changing any of the contents can actually make the algorithm take
more loops to fully resolve the output.  For instance, data-e.csv versus data-i.csv.  The Vertex and Edge values
are the same, but changing the order of the input records changes it from 1 loop to 2.

NOTE:  At least for some cases, it doesn't matter if the graph is acyclic because of the way the vertices
and edges are evaluated.  Didn't think of that until after the first commits.

Also, wrote a little utility to put out my style of graph CSV file based on the directory tree of a Linux
system.

USAGE:  fs_to_graph.py > output-file

It needs to be run as root to capture everything.  It tries to avoid parts of the file system tree that
cause issues even when run as root.

NOTE:  data-k-eq.csv has the same graph but sets all edges to a cost/weight/length of 1 to see how things
work for a shortest-path case instead of a least-cost case.  It seems to work fine.

NOTE:  This algorithm depends on having one vertex in the graph with no in-coming edges as the "origin" or
starting vertex.  Doubling up every edge to turn a directed graph into an undirected graph won't work (yet).