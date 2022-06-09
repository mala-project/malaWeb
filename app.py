import base64
import datetime
import io

import ase.io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import pandas as pd
# TODO: clean up imports

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
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
    dcc.Textarea(value = "test", id="output_data_upload_block")
])


@app.callback(Output('output-upload-state', 'children'),
              [Input('upload-data', 'filename'),
               Input('upload-data', 'contents')]
              )
def update_output_div(filename, contents):
    print(filename)
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    if filename is not None:
        if filename.endswith('.npy'):
            # TODO: parse file with ASE
            # ase.io.read(contents)
            # contents
            print("ASE READ")

            return 'Upload successfull. Filename: {filename}'.format(filename=filename)
        else:
            return 'Wrong file-type. .npy required'
    else:
        return 'Upload a file'


if __name__ == '__main__':
    app.run_server(debug=True)
