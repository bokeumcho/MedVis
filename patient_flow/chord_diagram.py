import pandas as pd
import holoviews as hv
from holoviews import opts,dim

from bokeh.embed import file_html
from bokeh.resources import CDN

def create_chord_diagram(data):
    # Create Chord Diagram using holoviews
    hv.extension('bokeh')

    # Create a list of nodes (unique careunits)
    # nodes = list(set(transition_df['from']).union(set(transition_df['to'])))
    nodes = list(set(data['source']).union(set(data['target'])))
    
    node_values = data.groupby('source')['value'].sum() + data.groupby('target')['value'].sum()
    node_values = node_values.sort_values(ascending=False)

    # Create a list of sorted nodes
    nodes = node_values.index.tolist()

    # Create a dictionary for nodes index
    node_index = {node: i for i, node in enumerate(nodes)}

    # Convert the DataFrame to a format suitable for hvplot Chord
    # edges = [(node_index[from_], node_index[to_], count) for from_, to_, count in data[['source','target','value']].itertuples(index=False)]
    edges = pd.DataFrame({'source': [node_index[from_] for from_ in data['source']],
                        'target': [node_index[to_] for to_ in data['target']],
                        'value': data['value']})

    data2 = data.copy()
    data2['num']=1
    incoming = data2.groupby('target')['num'].sum()
    outgoing = data2.groupby('source')['num'].sum()
    incoming_val = data2.groupby('target')['value'].sum()
    outgoing_val = data2.groupby('source')['value'].sum()

    # Define nodes in the format required by holoviews
    nodes_hv = hv.Dataset(pd.DataFrame({'index': list(range(len(nodes))), 'name': nodes, 
                                        'outgoing flow count': [outgoing.get(node, 0) for node in nodes],
                                        'incoming flow count': [incoming.get(node, 0) for node in nodes],
                                        'outgoing flow value': [outgoing_val.get(node, 0) for node in nodes],                                        
                                        'incoming flow value': [incoming_val.get(node, 0) for node in nodes],                                        
                                }), 'index')

    # Create the Chord diagram
    chord = hv.Chord((edges, nodes_hv)).opts(
        opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(),
                labels='name', node_color=dim('index').str(), height=700, width=700, title="Chord Diagram")
    ).opts(fontsize={'title': 14})

    # Render the Holoviews plot to a Bokeh plot
    bokeh_plot = hv.render(chord, backend='bokeh')
    plot_html = file_html(bokeh_plot, CDN, "Chord Diagram")

    return plot_html