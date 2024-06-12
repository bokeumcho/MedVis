from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from data import load_with_bigquery
import pandas as pd

def create_sidebar(categories):
    category_options = [{'label': category, 'value': category} for category in categories.keys()]
    all_wards = [ward for wards in categories.values() for ward in wards]
    return dbc.Card(
        [
            dbc.CardHeader("Node Controls"),
            dbc.CardBody(
                [
                    html.P("Select source category:", className="card-text"),
                    dcc.Dropdown(
                        id='source-category-dropdown',
                        options=category_options,
                        value=list(categories.keys())[0],  # Default value
                        clearable=False,
                        style={'margin-bottom': '20px'}
                    ),
                    html.P("Select target category:", className="card-text"),
                    dcc.Dropdown(
                        id='target-category-dropdown',
                        options=category_options,
                        value=list(categories.keys())[0],  # Default value
                        clearable=False,
                        style={'margin-bottom': '20px'}
                    ),
                    html.P("Select nodes for source category to display:", className="card-text"),
                    dcc.Checklist(
                        id='source-node-checklist',
                        options=[{'label': ward, 'value': ward} for ward in all_wards],
                        value=all_wards,
                        labelStyle={'display': 'block'},
                        style={'margin-bottom': '20px'}
                    ),
                    html.P("Select nodes for target category to display:", className="card-text"),
                    dcc.Checklist(
                        id='target-node-checklist',
                        options=[{'label': ward, 'value': ward} for ward in all_wards],
                        value=all_wards,
                        labelStyle={'display': 'block'}
                    )
                    # ,html.Button('Show All Wards', id='show-all-wards-button', n_clicks=0, style={'margin-top': '20px'})
                ]
            )
        ],
        style={'height': '120vh', 'width': '100%'}
    )

def create_bar_plots(source_category, target_category):
    # Optimize queries by selecting necessary fields and using WHERE clauses effectively
    query1 = f"""
    SELECT admission_location, SUM(transfer_num) AS transfer_count
    FROM `filtered_data.admit_disch_loc`
    WHERE link_index IN (
        SELECT link_index FROM `filtered_data.link_index_cat` 
        WHERE source_category='{source_category}' AND target_category='{target_category}' 
        )
    GROUP BY admission_location
    ORDER BY transfer_count DESC
    LIMIT 5; 
    """

    data1 = load_with_bigquery(query1)

    query2 = f"""
    SELECT discharge_location, SUM(transfer_num) AS transfer_count
    FROM `filtered_data.admit_disch_loc`
    WHERE link_index IN (
        SELECT link_index FROM `filtered_data.link_index_cat` 
        WHERE source_category='{source_category}' AND target_category='{target_category}' 
        )
    GROUP BY discharge_location
    ORDER BY transfer_count DESC
    LIMIT 5;
    """

    data2 = load_with_bigquery(query2)
    
    query3 = f"""
    SELECT DISTINCT subject_id, gender, anchor_age, race
    FROM `filtered_data.subject_linkID`
    WHERE link_index IN (
        SELECT link_index FROM `filtered_data.link_index_cat` 
        WHERE source_category='{source_category}' AND target_category='{target_category}' 
        )
    """

    data3 = load_with_bigquery(query3)
    # print(data1.head(), data2.head())
    
    query4 = f"""
    SELECT diagnosis_icd_code, long_title, count(*) as diagnosis_count
    FROM `filtered_data.icd_code_linkID`
    WHERE link_index IN (
        SELECT link_index FROM `filtered_data.link_index_cat` 
        WHERE source_category='{source_category}' AND target_category='{target_category}' 
        ) --AND diagnosis_seq_num=1
    GROUP BY diagnosis_icd_code, long_title
    ORDER BY diagnosis_count DESC
    LIMIT 5
    """

    data4 = load_with_bigquery(query4)

    fig1 = px.bar(data1, x='admission_location', y='transfer_count', title='Top 5 admission locations')
    fig2 = px.bar(data2, x='discharge_location', y='transfer_count', title='Top 5 discharge locations')
    fig4 = px.bar(data4, x='diagnosis_icd_code', y='diagnosis_count', title='Top 5 diagnosed ICD codes', hover_data={'long_title': True})

    # Customize hover template to display the long title
    fig4.update_traces(
        hovertemplate="<br>".join([
            "ICD Code: %{x}",
            "Count: %{y}",
            "Description: %{customdata[0]}"
        ])
    )

    # Bar chart for age distribution
    fig_age = px.histogram(data3, x='anchor_age', nbins=10, title='Age Distribution')

    # Pie chart for gender distribution
    fig_gender = px.pie(data3, names='gender', title='Gender Distribution')

    # Stacked bar chart for combined age and gender distribution
    data3['Age Group'] = pd.cut(data3['anchor_age'], bins=[10,20, 30, 40, 50, 60, 70, 80,90], labels=['10-20','20-30', '30-40', '40-50', '50-60', '60-70', '70-80','80-90'])
    fig_combined = px.histogram(data3, x='Age Group', color='gender', barmode='stack', title='Age and Gender Distribution')

    # Adjust margins for each figure
    # fig1.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    # fig2.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    # fig_age.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    # fig_gender.update_layout(margin=dict(l=10, r=10, t=30, b=10))

    return fig1, fig2, fig_combined, fig4
