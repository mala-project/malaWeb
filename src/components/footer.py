from dash import html, dcc
import dash_bootstrap_components as dbc


# TABLES
    # Energy table
row1 = html.Tr([html.Td("Band energy", style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row2 = html.Tr([html.Td(0, id="bandEn", style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
row3 = html.Tr([html.Td('Total energy', style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row4 = html.Tr([html.Td(0, id="totalEn", style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
row5 = html.Tr([html.Td("Fermi energy", style={'text-align': 'center', 'padding': 3, 'font-size': '0.85em'})],
               style={"font-weight": "bold"})
row6 = html.Tr(
    [html.Td("placeholder", id='fermiEn', style={'text-align': 'right', 'padding': 5, 'font-size': '0.85em'})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

table = dbc.Table(table_body, bordered=True, striped=True, style={'padding': 0, 'margin': 0})


bar = dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody(table)), width='auto'),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6('Density of State', style={'font-size': '0.85em', 'font-weight': 'bold'}),
            dcc.Graph(id="dos-plot", style={'width': '20vh', 'height': '10vh', 'background': '#f8f9fa'}, config={'displaylogo': False})
        ])), width='auto', align='center'),
    ], style={'height': 'min-content', 'padding': 0}, justify='center')

])