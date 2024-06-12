import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews import opts, dim
from bokeh.embed import file_html
from bokeh.resources import CDN
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import random

# Sample data
data = pd.DataFrame({
    'source': ['A', 'B', 'C', 'A', 'B', 'C'],
    'target': ['B', 'C', 'A', 'C', 'A', 'B'],
    'value': [10, 15, 10, 5, 10, 15]
})

# Create Chord Diagram using holoviews
hv.extension('bokeh')

def create_chord_diagram(data):
    # Aggregate values for each node
    node_values = data.groupby('source')['value'].sum() + data.groupby('target')['value'].sum()
    node_values = node_values.sort_values(ascending=False)

    # Create a list of sorted nodes
    nodes = node_values.index.tolist()
    node_index = {node: i for i, node in enumerate(nodes)}

    random.seed(5)
    node_colors = {node: '#'+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for node in nodes}

    # Convert the DataFrame to a format suitable for hvplot Chord
    edges = [(node_index[from_], node_index[to_], count) for from_, to_, count in data[['source', 'target', 'value']].itertuples(index=False)]

    # Define nodes in the format required by holoviews
    nodes_hv = hv.Dataset({'index': list(range(len(nodes))), 'name': nodes, 'color': [node_colors[node] for node in nodes]}, 'index')

    # Create the Chord diagram
    chord = hv.Chord((edges, nodes_hv)).opts(
        opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color='source', 
                   labels='name', node_color='color', edge_line_width='value',
                   height=600, width=600, title="Chord Diagram")
    )

    # Render the Holoviews plot to a Bokeh plot
    bokeh_plot = hv.render(chord, backend='bokeh')
    plot_html = file_html(bokeh_plot, CDN, "Chord Diagram")

    return plot_html

# Create a Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='bar-plot-1'), width=3, style={'padding': '0px', 'margin': '0px'}),
                dbc.Col(dcc.Graph(id='bar-plot-2'), width=3, style={'padding': '0px', 'margin': '0px'}),
                dbc.Col(dcc.Graph(id='bar-plot-3'), width=3, style={'padding': '0px', 'margin': '0px'}),
                dbc.Col(dcc.Graph(id='bar-plot-4'), width=3, style={'padding': '0px', 'margin': '0px'})
            ],
            style={'margin-bottom': '10px'}
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(id='bokeh-plot'), width=12),
            ]
        )
    ],
    fluid=True
)

@app.callback(
    Output('bokeh-plot', 'children'),
    Input('bokeh-plot', 'id')
)
def display_bokeh_plot(_):
    plot_html = create_chord_diagram(data)
    return html.Div([
        html.Iframe(srcDoc=plot_html, style={'width': '100%', 'height': '700px', 'border': 'none'})
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
