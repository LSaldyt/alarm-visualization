#!/usr/bin/env python3
from  matplotlib.patches import Patch
import networkx as nx
import matplotlib.pyplot as plt

import pandas

try:
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    raise ImportError("This example needs Graphviz and either PyGraphviz or Pydot")

original = {17, 19, 25}

original_color = (131/255, 1.0, 66/255)

def create_graph():
    propagationData = pandas.read_csv('propagation.csv')

    G = nx.DiGraph()
    colors = []
    legend_handles = []
    edge_labels = dict()

    seen = set()
    received = set()

    def add(node, color, label=None):
        if node not in seen:
            G.add_node(node, label=str(node) if label is None else label)
            colors.append(color)
            seen.add(node)

    time_window = 2 # in seconds
    windows = 5
    time_colors = [(r/255, g/255, b/255)
                   for r, g, b in
                   [(178, 2, 0)] + [(255, int(x * (200 / windows)), 32) for x in range(windows)]]
    self_excite_color = (235/255, 135/255, 255/255)
    passive_color = (0.3, 0.5, 1.0)

    for i, color in enumerate(time_colors):
        label = str(int(i * time_window)) + ' seconds'
        if i == len(time_colors) - 1:
            label += ' or more'
        legend_handles.append(Patch(color=color, label=label))

    legend_handles.append(Patch(color=self_excite_color, label='Independent Excitement'))
    legend_handles.append(Patch(color=passive_color, label='Passive'))
    legend_handles.append(Patch(color=original_color, label='Original'))

    for index, row in propagationData.iterrows():
        source, dest = row['AlarmedFrom'], row['Alarmed']
        time = row['TimeForAlarm']
        time_color = time_colors[min((time // time_window), len(time_colors) - 1)]
        if not row['Self-Excitation']:
            if source in original:
                add(source, original_color)
            else:
                add(source, time_color)
            add(dest,   time_color)
            if dest not in received:
                G.add_edge(source, dest)
                edge_labels[(source, dest)] = str(time) + 's'
            received.add(dest)
        elif source not in received:
            if source in original:
                add(source, original_color, label=(str(source) + '!'))
            else:
                add(source, self_excite_color, label=(str(source) + '!'))
            received.add(source)
    for i in range(1, 62):
        if i not in seen:
            add(i, passive_color, label=(str(source) + '!'))
    print(colors)
    return G, colors, legend_handles, edge_labels

def visualize(G, colors, legend_handles, edge_labels):
    # dot, neato, fdp, sfdp, twopi, circo: see https://www.graphviz.org/
    pos=graphviz_layout(G, prog='twopi', args='')
    plt.figure(figsize=(12,8))
    plt.title('Alarm signal propagation from three source ants')
    nx.draw(G, pos, node_size=350, font_size=12, alpha=0.9, node_color=colors, with_labels=True, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.legend(handles=legend_handles)
    plt.axis('off')
    plt.savefig('circular_tree.png')
    plt.show()

def main():
    visualize(*create_graph())

if __name__ == '__main__':
    main()
