import ase.io
import dash
import matplotlib.pyplot as plt
from dash.dependencies import Input, Output, State
from dash import dcc, html
import pandas as pd
from plotly.subplots import make_subplots

# visualization
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# TODO: clean up imports

# .numpy array
data = np.load("../examples/Be2/Be_dens.npy")

arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, data.shape), indexing="ij"))) + [data.ravel()])
df = pd.DataFrame(arr, columns=['x', 'y', 'z', 'val'])

fig = px.scatter_3d(df, x='x', y='y', z='z', color='val', opacity=0.07, range_color=[0.03, 0.05])




# LAYOUT
app = dash.Dash(__name__)
print("------------------------------------------------")
print("------------------------------------------------")
app.layout = html.Div([
    html.Div(
        dcc.Graph(figure=fig),
    ),
    html.Div([

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag & Drop or ',
                html.A('Click to select Files')
            ]),
            style={
                'width': '30%',
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
        html.Div(id='output-upload-state'),
        dcc.Textarea(value="test", id="output_data_upload_block"),

    ],
        className="upload-section"
    ),

])


@app.callback(Output('output-upload-state', 'children'),
              [Input('upload-data', 'filename'),
               Input('upload-data', 'contents')]
              )
def update_output_div(filename, contents):
    # checks for cubes for now, as long as im working on vis
    # will check for .npy when mala is ready to give .cube output from
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    if filename is not None:
        if filename.endswith('.cube'):

            # USER INPUT ATOM POSITIONS - File Upload
            # TODO: parse file with ASE
            # ase.io.read(contents)
            # contents

            return 'Upload successfull. Filename: {filename}'.format(filename=filename)
        else:
            return 'Wrong file-type. .npy required'
    else:
        return 'Upload a file'


if __name__ == '__main__':
    app.run_server(debug=True)
