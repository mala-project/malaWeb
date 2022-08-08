import ase.io
import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import pandas as pd

# visualization
import numpy as np
import plotly.express as px

# TODO: clean up imports

# .numpy array
data = np.load("../examples/Be2/Be_dens.npy")

arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, data.shape), indexing="ij"))) + [data.ravel()])
df = pd.DataFrame(arr, columns=['x', 'y', 'z', 'val'])

# raelitve color-scale, oder absolute Werte? Wenn letzteres: Welche Werte
fig = px.scatter_3d(df, x='x', y='y', z='z', color='val', opacity=0.08, range_color=[df.min()['val'], df.max()['val']])

# LAYOUT
app = dash.Dash(__name__)
app.layout = html.Div([

    html.H1(children='Hello MALA'),

    html.Div(children='''
        Web-App for the Materials Learning Algorithm - A framework for machine learning materials properties from first-principles data.
    '''),

    html.Div([

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag & Drop or ',
                html.A('Click to select Files')
            ]),
            style={
                'width': '20%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),

        html.Div(id='output-upload-state',
                 style={
                     'margin': '10px'
                 }),
    ],
        className="upload-section"
    ),

    html.Div(
        dcc.Graph(figure=fig, style={
            'height': '800px',
            'width': '800px',
        }),
    )
])

@app.callback(Output('output-upload-state', 'children'),
              [Input('upload-data', 'filename'),
               Input('upload-data', 'contents')],
              )
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

            return 'Upload successfull. Filename: {filename}'.format(filename=filename)
        else:
            return 'Wrong file-type. .npy required'
    else:
        return 'Upload a file'




if __name__ == '__main__':
    app.run_server(debug=True)
