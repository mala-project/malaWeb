# IMPORTS
import ase.io
import dash
from dash.dependencies import Input, Output
from dash import dcc, html

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

                # PARAMS & (TEST)FILE IMPORT
# density- import / conversion to pandas dataframe / fig - density-visualisation params / plot-layout params
data = np.load("../examples/Be2/Be_dens.npy")
arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, data.shape), indexing="ij"))) + [data.ravel()])
df = pd.DataFrame(arr, columns=['x', 'y', 'z', 'val'])

# density of
dosData = np.load("../examples/Be2/Be_dos.npy")
dosArr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, dosData.shape), indexing="ij"))) + [dosData.ravel()])
dosDf = pd.DataFrame(dosArr, columns=['x', 'y'])


# _____________________________________________________________________________________________________________________


# atomposition
apData = '../examples/Be2/cubes/tmp.pp01Be_ldos.cube'
# apDf = pd.DataFrame()

# 0-1 = Comment, Energy, broadening
# 2 = number of atoms, coord origin
# 3-5 = number of voxels per Axis (x/y/z), lentgh of axis-vector -> info on cell-warping
# 6-x = atompositions
grind_warp = []
atoms = [[], [], [], [], []]
with open(apData, 'r') as f:
    lines = f.read().splitlines()
    no_of_atoms, _, _, _ = lines[2].split()
    #vectoren
            # all strings !!
    xVox, xV1, yV1, zV1 = lines[3].split()
    yVox, xV2, yV2, zV2 = lines[4].split()
    zVox, xV3, yV3, zV3 = lines[5].split()

    xVec = float(xV1) +float(xV2) +float(xV3)
    yVec = float(yV1) +float(yV2) +float(yV3)
    zVec = float(zV1) +float(zV2) +float(zV3)
    print("Calculator")
    print()
    print(float(zVox) / float(zVox) / float(zV3))


    for i in range(0,int(no_of_atoms)):
        ordinalNumber, charge, x, y, z = lines[6+i].split()         # atom-data starts @line-index 6
        print("Normal Coords: (", x, "/", y, "/", z)
        print("-----")
        atoms[0].append(int(ordinalNumber))
        atoms[1].append(float(charge))
        atoms[2].append(float(x) / (float(xV1)))       # stretch-faktor = axen-vektoren aus .cube // y-Axen verzerrung fehlt bei x-Achse
        atoms[3].append(float(y) / float(yV2))
        atoms[4].append(float(z) / float(zV3))

    print("vectors: (", xVec, "/", yVec, "/", zVec)
    print("-----")
    print("Coords multiplied with vectors: ")
    print("-----")

            # float(x)/0.237247 / float(y)/0.205462 /   float(z)/0.249855
        # print("altered Coords: (", atoms[2][0], "/", atoms[3][0], "/", atoms[4][0])

    #apDf = pd.DataFrame(atoms, columns=['oN', 'charge', 'x', 'y', 'z'])

# _____________________________________________________________________________________________________________________

                # THEME & FIGUREs
templ = "ggplot2"
load_figure_template(templ)

# relative color-scale, oder absolute Werte? Wenn letzteres: Welche Werte?
# df.max()-Wert in color-range etwas reduzieren (0.01), weil er dem Dichtewert für Atome entspricht.
# So ist Farbauflösung leicht reduziert und alles ist etwas heller

# density
# color_continuous_scale kann glaube nur vorgefertigte Farbverläufe nehmen (?)
fig = px.scatter_3d(df, x='x', y='y', z='z', color='val', opacity=0.3,
                    color_continuous_scale=px.colors.sequential.Inferno_r, range_color=[df.min()['val'], df.max()['val'] ], template=templ)

        # SLICING eines Bereichs
# Achsenaufteilung in Voxel
fig.update_layout(
    scene = dict(
        xaxis = dict(dtick=1),
        yaxis = dict(dtick=1),
        zaxis = dict(dtick=1)
    )
)
# fig.update_xaxes(ticklabelstep=2)

# ['#f15e64', '#faac5e', '#45c2c8']


# Atoms
fig.add_trace(go.Scatter3d(x=atoms[2], y=atoms[3], z=atoms[4], mode='markers', marker=dict(size=20, color=['white', 'black'])))

dos_fig = go.Figure()
dos_fig.add_trace(go.Scatter(x=dosDf['x'], y=dosDf['y'], name='Zustandsdichte', line=dict(color='#f15e64', width=3, dash='dot')))


# helper-cell
fig.add_trace(go.Scatter3d(x=[0, 0, 0, 0, data.shape[0], data.shape[0], data.shape[0], data.shape[0]],
                           y=[0, 0, data.shape[1],data.shape[1], 0, 0,  data.shape[1], data.shape[1]],
                           z=[0, data.shape[2], data.shape[2], 0, 0, data.shape[2],  0, data.shape[2]], mode='markers'))

# scale marker
print(float(xV1))
fig.add_trace(go.Scatter3d(x=[0, (0.6 * (1 / float(xV1)))], y=[0, 0], z=[0, 0]))

plot_layout = {
    'title': 'Test',
    'height': '800px',
    'width': '800px',
    'background': '#000',       # not working
}
dos_plot_layout = {
    'height': '400px',
    'width': '800px',
    'background': '#f8f9fa',
}
# _____________________________________________________________________________________________________________________

        # APP LAYOUT
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], prevent_initial_callbacks=True)
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
                         'margin': '10px',
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
        'margin-left': '1rem',
        'background-color': '#f8f9fa',
        'border-radius': '10px',
        'height': 'min-content',
        'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'

    }
)
        # __________________________________________________________________________________________________

                # MAIN CONTENT / PLOT
indent = '      '
load_figure_template("quartz")
content = html.Div(
    [
        # Plot Section
        html.Div(
            [
                # Density Section
                html.H3([indent.join('3D-Density-Plot')]),
                dbc.Card(dbc.CardBody(html.Div(
                            dcc.Graph(figure=fig, style=plot_layout),
                            className="density-plot"
                        )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content'}),


                # Density of S.. Section
                html.H4(indent.join('2D-Density-of-State-Plot'), style={'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(html.Div(
                            dcc.Graph(figure=dos_fig, style=dos_plot_layout),
                            className='dos-plot',
                        )), style={'position': 'float', 'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content', 'margin-bottom': '1rem', 'margin-top': '1rem', 'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'}),

                # histogram Section?
                html.H4(indent.join('Histogram?'), style={'margin-top': '1.5rem'}),
                dbc.Card(dbc.CardBody(html.Div(
                            # dcc.Graph(figure=fig, style=plot_layout),
                            className='hist-plot',
                        )), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content'})],
            className="plot-section"
        ),

    ],
    className="content",
    style={'margin-left': '1rem','margin-right': '2rem', 'padding': '2rem 1rem'}
)

app.layout = html.Div([
    dbc.Container(
        dbc.Row(
            [
                dbc.Col(sidebar, width="3"),
                dbc.Col(content, width="7"),
                dbc.Col(html.Div("Info-/Note-section / Legend"), width="2"),
            ]
        ), fluid=True,
    ),

], className="wrapper")          # , style={'background': 'white'} für light-mode
# _____________________________________________________________________________________________________________________

print("_________________________________________________________________________________________")
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
