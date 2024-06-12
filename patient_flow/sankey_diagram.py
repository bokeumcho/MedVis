import pandas as pd
import plotly.graph_objects as go
import random

node_colors = {}

def generate_node_colors(nodes):
    random.seed(5)
    for node in nodes:
        if node not in node_colors:
            node_colors[node] = '#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

def create_sankey_diagram(data):
    unique_nodes = pd.concat([data['source'], data['target']]).unique()
    generate_node_colors(unique_nodes)

    node_dict = {node: i for i, node in enumerate(unique_nodes)}
    colors = [node_colors[node] for node in unique_nodes]

    data['source_idx'] = data['source'].map(node_dict)
    data['target_idx'] = data['target'].map(node_dict)
    opacity = 0.4

    link_colors = [
        'rgba({0}, {1}, {2}, {3})'.format(*[int(colors[idx][i:i+2], 16) for i in (1, 3, 5)], opacity)
        for idx in data['source_idx']
    ]

    sankey_figure = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=list(unique_nodes),
            color=colors
        ),
        link=dict(
            source=data['source_idx'],
            target=data['target_idx'],
            value=data['value'],
            color=link_colors  # Use the corrected link colors with opacity
        )
    )])
    sankey_figure.update_layout(title_text="Sankey Diagram", height=700)
    return sankey_figure