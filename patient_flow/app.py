import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from data import load_with_bigquery_sankey
from sankey_diagram import create_sankey_diagram
from chord_diagram import create_chord_diagram
from controls import create_sidebar, create_bar_plots

from dash.dependencies import Input, Output

# Define your categories and their corresponding wards
# categories = {
#     'ICU': ['Medical Intensive Care Unit (MICU)', 'Surgical Intensive Care Unit (SICU)', 'Medical/Surgical Intensive Care Unit (MICU/SICU)', 'Cardiac Vascular Intensive Care Unit (CVICU)', 'Coronary Care Unit (CCU)', 'Neuro Surgical Intensive Care Unit (Neuro SICU)', 'Trauma SICU (TSICU)'],
#     'General Ward': ['Medicine', 'Med/Surg', 'Med/Surg/GYN', 'Med/Surg/Trauma', 'Surgery', 'Neurology', 'Psychiatry', 'Hematology/Oncology', 'Cardiology', 'Thoracic Surgery', 'Medicine/Cardiology', 'Medicine/Cardiology Intermediate', 'Surgery/Trauma', 'Surgery/Pancreatic/Biliary/Bariatric', 'Obstetrics (Postpartum & Antepartum)', 'Obstetrics Postpartum', 'Obstetrics Antepartum', 'Vascular', 'Cardiac Surgery'],
#     'Step-Down Unit': ['Cardiology Surgery Intermediate', 'Neuro Intermediate', 'Hematology/Oncology Intermediate', 'Neuro Stepdown', 'Medicine/Cardiology Intermediate'],
#     'Specialized Unit': ['Emergency Department Observation', 'Emergency Department', 'Observation', 'Discharge Lounge', 'PACU', 'Labor & Delivery', 'Medical/Surgical (Gynecology)', 'Psychiatry'],
#     'Other': ['Transplant', 'Hematology/Oncology', 'Unknown']
# }

categories = {
    'Cardiac Care': [
        'Cardiac Surgery',
        'Cardiac Vascular Intensive Care Unit (CVICU)',
        'Cardiology Surgery Intermediate',
        'Coronary Care Unit (CCU)',
        'Medicine/Cardiology',
        'Medicine/Cardiology Intermediate'
    ],
    'General Medicine': [
        'Medicine',
        'Med/Surg',
        'Med/Surg/GYN',
        'Med/Surg/Trauma',
        'Medicine/Cardiology',
        'Medicine/Cardiology Intermediate'
    ],
    'Intensive Care': [
        'Medical Intensive Care Unit (MICU)',
        'Medical/Surgical Intensive Care Unit (MICU/SICU)',
        'Surgical Intensive Care Unit (SICU)',
        'Trauma SICU (TSICU)',
        'Neuro Surgical Intensive Care Unit (Neuro SICU)',
        'Cardiac Vascular Intensive Care Unit (CVICU)'
    ],
    'Emergency Services': [
        'Emergency Department',
        'Emergency Department Observation'
    ],
    'Obstetrics & Gynecology': [
        'Labor & Delivery',
        'Obstetrics (Postpartum & Antepartum)',
        'Obstetrics Antepartum',
        'Medical/Surgical (Gynecology)'
    ],
    'Neurology': [
        'Neurology',
        'Neuro Intermediate',
        'Neuro Stepdown',
        'Neuro Surgical Intensive Care Unit (Neuro SICU)'
    ],
    'Surgical Services': [
        'Surgery',
        'Surgery/Trauma',
        'Surgery/Pancreatic/Biliary/Bariatric'
    ],
    'Specialized Units': [
        'Hematology/Oncology',
        'Hematology/Oncology Intermediate',
        'Transplant',
        'Vascular'
    ],
    'Supportive Care and Recovery': [
        'Discharge Lounge',
        'Observation',
        'PACU'
    ],
    'Other': [
        'Psychiatry',
        'Cardiology',
        'Thoracic Surgery',
        'Unknown'
    ]
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def setup_layout():
    # data = load_and_prepare_data()
    data = load_with_bigquery_sankey()
    sankey_figure = create_sankey_diagram(data)
    chord_figure = create_chord_diagram(data)
    
    app.layout = dbc.Container(
        [
            dbc.Row(
                [ 
                    dbc.Col(dcc.Graph(id='bar-plot-1'), width={'size':3, "offset":1}, style={'padding': '0px', 'margin': '0px'}),
                    dbc.Col(dcc.Graph(id='bar-plot-2'), width={'size':3, "offset":1}, style={'padding': '0px', 'margin': '0px'}),
                    dbc.Col(dcc.Graph(id='bar-plot-3'), width={'size':3, "offset":1}, style={'padding': '0px', 'margin': '0px'}),
                    dbc.Col(dcc.Graph(id='bar-plot-4'), width={'size':3, "offset":1}, style={'padding': '0px', 'margin': '0px'}) 
                    ],
                    style={'margin-bottom': '10px'} 
                    # className="g-0"
            ),
            dbc.Row(
                [
                    dbc.Col(create_sidebar(categories), width=3, id='sidebar-col'),
                    dbc.Col([
                        dcc.Graph(id='sankey-diagram', figure=sankey_figure, style={'height': '700px','padding': '0px', 'margin': '0px'}),
                        html.Div(id='chord-diagram', style={'display': 'flex', 'justify-content': 'center', 'align-items': 'stretch', 'width': '100%','height': '100%'})
                    ], width=9)
                ]
            )
        ],
        fluid=True
    )
    
    

# Callback to update the source checklist based on the selected source category
@app.callback(
    Output('source-node-checklist', 'options'),
    Output('source-node-checklist', 'value'),
    Input('source-category-dropdown', 'value'),
    State('source-node-checklist', 'value')
)
def update_source_checklist(source_category, current_selection):
    source_wards = categories[source_category]
    options = [{'label': ward, 'value': ward} for ward in source_wards]
    values = [ward for ward in current_selection if ward in source_wards] + source_wards
    return options, list(set(values))

# Callback to update the target checklist based on the selected target category
@app.callback(
    Output('target-node-checklist', 'options'),
    Output('target-node-checklist', 'value'),
    Input('target-category-dropdown', 'value'),
    State('target-node-checklist', 'value')
)
def update_target_checklist(target_category, current_selection):
    target_wards = categories[target_category]
    options = [{'label': ward, 'value': ward} for ward in target_wards]
    values = [ward for ward in current_selection if ward in target_wards] + target_wards
    return options, list(set(values))

# Callback to update the Sankey diagram based on selected nodes from both checklists
@app.callback(
    Output('sankey-diagram', 'figure'),
    Input('source-node-checklist', 'value'),
    Input('target-node-checklist', 'value')
)
def update_sankey(source_nodes, target_nodes):
    # data = load_and_prepare_data()
    data = load_with_bigquery_sankey()
    # selected_nodes = list(set(source_nodes + target_nodes))
    # Filter data based on selected nodes
    filtered_data = data[data['source'].isin(source_nodes) & data['target'].isin(target_nodes)]
    return create_sankey_diagram(filtered_data)

@app.callback(
    Output('chord-diagram', 'children'),
    Input('chord-diagram', 'id'),
    Input('source-node-checklist', 'value'),
    Input('target-node-checklist', 'value')
)
def display_chord_diagram(_, source_nodes, target_nodes):
    data = load_with_bigquery_sankey()
    filtered_data = data[data['source'].isin(source_nodes) & data['target'].isin(target_nodes)]
    plot_html = create_chord_diagram(filtered_data)
    
    return html.Div([
        html.Iframe(srcDoc=plot_html, style={'width': '700px', 'height': '700px', 'border': 'none'})
     ])

# Callback to show all wards for all categories
# @app.callback(
#     Output('source-node-checklist', 'value'),
#     Output('target-node-checklist', 'value'),
#     Input('show-all-wards-button', 'n_clicks')
# )
# def show_all_wards(n_clicks):
#     if n_clicks>0:
#         all_wards = [ward for wards in categories.values() for ward in wards]
#     return all_wards, all_wards

@app.callback(
    Output('bar-plot-1', 'figure'),
    Output('bar-plot-2', 'figure'),
    Output('bar-plot-3', 'figure'),
    Output('bar-plot-4', 'figure'),
    Input('source-category-dropdown', 'value'),
    Input('target-category-dropdown', 'value')
)
def update_bar_plots(source_category, target_category):
    return create_bar_plots(source_category, target_category)

setup_layout()

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=True)
