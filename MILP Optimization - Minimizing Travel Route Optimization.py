#!/usr/bin/env python
# coding: utf-8

# ## Mixed-Integer Programming (MIP) Optimization
# ### __[Pyomo Documentation](https://pyomo.readthedocs.io/en/stable/index.html)__

# In[1]:
# Sample Diagram

import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add nodes
G.add_node('A')
G.add_node('B')
G.add_node('P1')
G.add_node('P2')
G.add_node('P3')

# Add edges with weights
G.add_edge('A', 'P1', weight=2)
G.add_edge('A', 'P2', weight=7)
G.add_edge('P1', 'P2', weight=10)
G.add_edge('P2', 'P1', weight=10)
G.add_edge('P1', 'B', weight=30)
G.add_edge('P2', 'P3', weight=8)
G.add_edge('P3', 'B', weight=5)

# Position nodes
pos = {'A': (0, 0), 'P1': (2, 0.02), 'P2': (2, -0.02), 'P3': (3.5, -0.01), 'B': (5, 0.01)}

# Draw all nodes with no color and a distinct node size and node border
nx.draw_networkx_nodes(G, pos, node_color='none', edgecolors='black', node_size=500)

# Highlight the 'A' and 'B' nodes to indicate start and end
nx.draw_networkx_nodes(G, pos, nodelist=['A', 'B'], node_color='none', edgecolors='black', node_size=700)

# Draw the edges
nx.draw_networkx_edges(G, pos)

# Draw the edge labels
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Draw the node labels
node_labels = {node:node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels)

# Remove axes
plt.axis('off')
plt.show()

# In[2]:


import pyomo.environ as pyo
from pyomo.opt import SolverFactory

m = pyo.ConcreteModel()

# Defines a list of all nodes in the network.
m.setAllNodes = ['A','P1','P2','P3','B']

# Defines a list of nodes excluding the start ('A') and end ('B') nodes.
m.setNodes = ['P1','P2','P3']

# Sets of routes from to
m.setRoutes = [['A','P1'],['A','P2'],['P1','P2'],['P2','P1'],['P1','B'],['P2','P3'],['P3','B']]
m.setRoutes_from = {key:[] for key in m.setAllNodes}
m.setRoutes_to = {key:[] for key in m.setAllNodes}
for arc in m.setRoutes:
    m.setRoutes_from[arc[0]].append(arc[1])
    m.setRoutes_to[arc[1]].append(arc[0])


# In[3]:


# Check the arcs
print(m.setRoutes_from)
print(m.setRoutes_to)


# In[4]:


# Parameters
m.D = {}
m.D['A','P1'] = 2
m.D['A','P2'] = 7
m.D['P1','P2'] = 10
m.D['P2','P1'] = 10
m.D['P1','B'] = 30
m.D['P2','P3'] = 8
m.D['P3','B'] = 5

# Binary Variable 'x'
m.x = pyo.Var(m.setRoutes, within=pyo.Binary)


# In[5]:


# Objective function (Minimize the distance)
m.obj = pyo.Objective(expr = sum([
    m.x[route[0], route[1]] * m.D[route[0], route[1]]
    for route in m.setRoutes
    ]), sense=pyo.minimize)


# In[6]:


#constraints
m.C1 = pyo.Constraint(expr = sum([m.x['A',j] for j in m.setRoutes_from['A']]) == 1)
m.C2 = pyo.Constraint(expr = sum([m.x[i,'B'] for i in m.setRoutes_to['B']]) == 1)
m.C3 = pyo.ConstraintList()
for i in m.setNodes:
    m.C3.add(sum([m.x[i,j] for j in m.setRoutes_from[i]]) == sum([m.x[j,i] for j in m.setRoutes_to[i]]))


# In[7]:


#solve
opt = SolverFactory('glpk', executable='/opt/homebrew/bin/glpsol')
m.results = opt.solve(m)


# In[8]:


#print the results
m.pprint()
print('\n\nOF:',pyo.value(m.obj))
for route in m.setRoutes:
    if pyo.value(m.x[route[0], route[1]]) >= 1:
        print('Route activated: %s-%s' % (route[0], route[1]))


# - Comment: With `Pyomo` framework, we got the optimal solution 20.

# In[9]:
# ## Generate a solution diagram

G = nx.DiGraph()

# Define activated routes
activated_routes = [('A', 'P2'), ('P2', 'P3'), ('P3', 'B')]

# Initially add all edges with default properties
edges_with_properties = [
    ('A', 'P1', {'weight': 2, 'color': 'black', 'width': 1}),
    ('A', 'P2', {'weight': 7, 'color': 'black', 'width': 1}),
    ('P1', 'P2', {'weight': 10, 'color': 'black', 'width': 1}),
    ('P2', 'P1', {'weight': 10, 'color': 'black', 'width': 1}),
    ('P1', 'B', {'weight': 30, 'color': 'black', 'width': 1}),
    ('P2', 'P3', {'weight': 8, 'color': 'black', 'width': 1}),
    ('P3', 'B', {'weight': 5, 'color': 'black', 'width': 1}),
]

G.add_edges_from(edges_with_properties)

# Update properties for the activated routes
for route in activated_routes:
    if G.has_edge(*route):
        G[route[0]][route[1]]['color'] = 'red'
        G[route[0]][route[1]]['width'] = 2.5  # Make solution path thicker

# Positions
pos = {'A': (0, 0), 'P1': (2, 0.02), 'P2': (2, -0.02), 'P3': (3.5, -0.01), 'B': (5, 0.01)}

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color='none', edgecolors='black', node_size=500)
nx.draw_networkx_nodes(G, pos, nodelist=['A', 'B'], node_color='none', edgecolors='black', node_size=700)

# Separate edgelist for colors and widths
edges = G.edges(data=True)
edge_colors = [data['color'] for _, _, data in edges]
edge_widths = [data['width'] for _, _, data in edges]

# Draw edges with specified colors and widths
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_colors, width=edge_widths)

# Draw edge labels
edge_labels = {(u, v): data['weight'] for u, v, data in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Draw node labels
node_labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels)

# Remove axes
plt.axis('off')
plt.show()

# In[10]:
## Compare with Greedy Heuristic Algorithm

def greedy_heuristic(routes, distances):
    current_point = 'A'
    end_point = 'B'
    path = []
    total_distance = 0

    while current_point != end_point:
        # Filter routes starting from the current point
        available_routes = [r for r in routes if r[0] == current_point]
        # Ensure there are available routes to prevent infinite loop
        if not available_routes:
            raise Exception("No available route to destination.")
            
        # Select the route with the minimum distance not already in the path
        next_route = min(available_routes, key=lambda x: distances[x])
        path.append(next_route)
        total_distance += distances[next_route]  # Accumulate the distance
        current_point = next_route[1]  # Move to the next point

    return path, total_distance


# In[11]:
## Greedy Heuristic Algorithm Results

# Define your routes and distances as before
routes = [('A', 'P1'), ('A', 'P2'), ('P1', 'P2'),('P2', 'P1'),('P2', 'P3'),('P1', 'B'),('P3', 'B')]
distances = {('A', 'P1'): 2, ('A', 'P2'): 7, ('P1', 'P2'):10,('P2', 'P1'):10,
             ('P2', 'P3'):8,('P1', 'B'):30,('P3', 'B'):5}

# Select routes using the heuristic
selected_routes, total_distance = greedy_heuristic(routes, distances)
print("Selected Routes:", selected_routes)
print("Total Distance:", total_distance)


# In[12]:


G = nx.DiGraph()

activated_routes = [('A', 'P1'), ('P1', 'P2'), ('P2', 'P3'), ('P3', 'B')]

# Initially add all edges with default properties
edges_with_properties = [
    ('A', 'P1', {'weight': 2, 'color': 'black', 'width': 1}),
    ('A', 'P2', {'weight': 7, 'color': 'black', 'width': 1}),
    ('P1', 'P2', {'weight': 10, 'color': 'black', 'width': 1}),
    ('P2', 'P1', {'weight': 10, 'color': 'black', 'width': 1}),
    ('P1', 'B', {'weight': 30, 'color': 'black', 'width': 1}),
    ('P2', 'P3', {'weight': 8, 'color': 'black', 'width': 1}),
    ('P3', 'B', {'weight': 5, 'color': 'black', 'width': 1}),
]

G.add_edges_from(edges_with_properties)

# Update properties for the activated routes
for route in activated_routes:
    if G.has_edge(*route):
        G[route[0]][route[1]]['color'] = 'red'
        G[route[0]][route[1]]['width'] = 2.5  # Make solution path thicker

# Positions
pos = {'A': (0, 0), 'P1': (2, 0.02), 'P2': (2, -0.02), 'P3': (3.5, -0.01), 'B': (5, 0.01)}

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color='none', edgecolors='black', node_size=500)
nx.draw_networkx_nodes(G, pos, nodelist=['A', 'B'], node_color='none', edgecolors='black', node_size=700)

# Separate edgelist for colors and widths
edges = G.edges(data=True)
edge_colors = [data['color'] for _, _, data in edges]
edge_widths = [data['width'] for _, _, data in edges]

# Draw edges with specified colors and widths
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_colors, width=edge_widths)

# Draw edge labels
edge_labels = {(u, v): data['weight'] for u, v, data in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Draw node labels
node_labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels)

# Remove axes
plt.axis('off')
plt.show()