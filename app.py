# IMPORTS
import ase.io
import dash
from dash.dependencies import Input, Output
from dash import dcc, html

import dash_daq as daq
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
# _____________________________________________________________________________________________________________________

                # PARAMS & (TEST)FILE IMPORT
# density numpy-array import / conversion to pandas dataframe / fig - density-visualisation params / plot-layout params
data = np.load("../examples/Be2/Be_dens.npy")
arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, data.shape), indexing="ij"))) + [data.ravel()])
df = pd.DataFrame(arr, columns=['x', 'y', 'z', 'val'])
# _____________________________________________________________________________________________________________________

                # THEME & FIGUREs
templ = "morph"
load_figure_template(templ)

# relative color-scale, oder absolute Werte? Wenn letzteres: Welche Werte?
# df.max()-Wert in color-range etwas reduzieren (0.01), weil er dem Dichtewert für Atome entspricht.
# So ist Farbauflösung leicht reduziert und alles ist etwas heller
fig = px.scatter_3d(df, x='x', y='y', z='z', color='val', opacity=0.1,
                    range_color=[df.min()['val'], df.max()['val'] - 0.01], template=templ)

plot_layout = {
    'title': 'Test',
    'height': '800px',
    'width': '800px',
    'background': '#000',
}
# _____________________________________________________________________________________________________________________

        # APP LAYOUT
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = 'MALA'


                # SIDEBAR
sidebar = html.Div(
    [

        # Logo Section
        html.Div([
            html.Img(src='https://avatars.githubusercontent.com/u/81354661?s=200&v=4', className="logo"),
            html.H2(children='MALA', style={'text-align': 'center'}),
            html.Div(children='''
        Framework for machine learning materials properties from first-principles data.
    ''', style={'text-align': 'center'})
        ],
            className="logo"
        ),
        html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),

        # Upload Section
        html.Div([
            html.H5(children='File-Upload'),
                # maybe do as info-on-hover
            html.Div(children='''
                MALA needs Atompositions
                ''', style={'text-align': 'center'}),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag & Drop', html.Br(), 'or ', html.Br(),
                    html.A('Click to select Files')
                ]),
                style={
                    'width': '90%',
                    'height': 'auto',
                    'lineHeight': '20px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '0.5rem',
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
        ],
            className="upload-section"
        ),
        html.Hr(style={'margin-bottom': '2rem', 'margin-top': '2rem'}),
        html.Div([
            html.H5(children='Status'),
            html.Div(children='''
                Awaiting Data Input
                ''', style={'text-align': 'left'}),
            html.Div(id='output-upload-state',
                     style={
                         'margin': '10px'
                     }),
        ], className="status-section")
    ],
    className="sidebar",
    style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '17rem',
        'padding': '2rem 1rem',
        'margin-top': '5vh',
        'margin-left': '2rem',
        'background-color': '#f8f9fa',
        'border-radius': '10px',
        'height': 'min-content',

    }
)
        # __________________________________________________________________________________________________
                # PLOT
indent = '      '
load_figure_template("quartz")
content = html.Div(
    [
        # Plot Section
        html.Div(
            [
                # Density Section

                dbc.Card(
                    [
                        dbc.CardHeader([indent.join('3D-Density-Plot')]),
                        dbc.CardBody(html.Div(
                            dcc.Graph(figure=fig, style=plot_layout),
                            className="density-plot"
                        ))],
                            style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content'}),


                # Density of S.. Section
                dbc.Card(
                    [
                        dbc.CardHeader([indent.join('2D-DOS-Plot')]),
                        dbc.CardBody(html.Div(
                            dcc.Graph(figure=fig, style=plot_layout),
                            className='dos-plot',
                        ))],
                            style={'position': 'float', 'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'margin-bottom': '1rem', 'margin-top': '1rem'}),

                # histogram Section?
                dbc.Card(
                    [
                        dbc.CardHeader([indent.join('Histogram?')]),
                        dbc.CardBody(html.Div(
                            dcc.Graph(figure=fig, style=plot_layout),
                            className='hist-plot',
                        ))],
                            style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content'})],
            className="plot-section"
        ),

    ],
    className="content",
    style={'margin-left': '20rem', 'margin-right': '2rem', 'padding': '2rem 1rem'}
)

app.layout = html.Div([sidebar, content], className="wrapper")
# _____________________________________________________________________________________________________________________


                # CALLBACKS & FUNCTIONS
@app.callback(
    Output('output-upload-state', 'children'),
    [
        Input('upload-data', 'filename'),
        Input('upload-data', 'contents'),
    ])
def uploadInput(filename, contents):
    # checks for .cubes for now, as long as im working on vis
    # will check for .npy when mala is ready to give .cube output from
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    if filename is not None:
        if filename.endswith('.cube'):

            # USER INPUT ATOM POSITIONS - .cube File Upload
            # 1. File Upload of .cube File
            # 2. TODO: parse file with ASE
            # ase.io.read(contents)
            # 3. process with MALA
            # save MALA output .npy as 'data'-variable
            # 4. contents

            return 'Upload successful. Filename: {filename}'.format(filename=filename)
        else:
            return 'Wrong file-type. .cube required'
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True)
