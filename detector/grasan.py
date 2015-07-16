'''
Created on 2015/07/14

@author: samejima
'''

import maxflow
import numpy as np

# Weight for gap between neighborhoods


# Create a graph with integer capacities.
g = maxflow.Graph[float](4, 2)
# Add two (non-terminal) nodes. Get the index to the first one.
nodes = g.add_nodes(4)
# Create two edges (forwards and backwards) with the given capacities.
# The indices of the nodes are always consecutive.
g.add_edge(nodes[0], nodes[1], 0.05, 0.05)
g.add_edge(nodes[1], nodes[3], 0.03, 0.03)
g.add_edge(nodes[0], nodes[2], 0.01, 0.01)
g.add_edge(nodes[2], nodes[3], 0.07, 0.07)

# Set the capacities of the terminal edges...
# ...for the first node.
g.add_tedge(nodes[0], 0.1, 0.9)
# ...for the second node.
g.add_tedge(nodes[1], 0.6, 0.4)

g.add_tedge(nodes[2], 0.2, 0.8)

g.add_tedge(nodes[3], 0.9, 0.1)

flow = g.maxflow()
print "Maximum flow:", flow
print "Segment of the node 0:", g.get_segment(nodes[0])
print "Segment of the node 1:", g.get_segment(nodes[1])
print "Segment of the node 2:", g.get_segment(nodes[2])
print "Segment of the node 3:", g.get_segment(nodes[3])