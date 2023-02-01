# IMPORTS
import itertools
import json
import random

import mala_inference
import ase.io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import dash_bootstrap_components as dbc
# from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# PX--Graph Object Theme
templ1 = dict(layout=go.Layout(
    scene={
        'xaxis': {'showbackground': False,
                  'ticks': '',
                  'visible': False,
                  },
        'yaxis': {'showbackground': False,
                  'ticks': '',
                  'visible': False},
        'zaxis': {'showbackground': False,
                  'ticks': '',
                  'visible': False},
        'aspectmode': 'data'
    },
    xaxis={
        'dtick': 2,
        'visible': True,
        'linewidth': 5,
    },
    paper_bgcolor='#f8f9fa',
))

default_scatter_marker = dict(marker=dict(
    size=12,
    opacity=1,
    line=dict(width=1, color='DarkSlateGrey')),
)
plot_layout = {
    'title': 'Plot',
    'height': '75vh',
    'width': '80vw',

    'background': '#000',  # not working
}
orientation_style = {
    'title': 'x-y-z',
    'height': '3em',
    'width': '3em',
    'background': '#f8f9fa',
    'position': 'fixed',
    'margin-top': '75vh',
    'margin-right': '0.5vw'
}

#Graph-Object Scene
orient_template = {
        'xaxis': {
                  'showgrid': False,
                  'showbackground': False,
                  'linecolor': 'red',
                  'linewidth': 0,
                  'ticks': 'inside',
                  'showticklabels': False,
                  'visible': False,
                    'title': 'x',

        },
        'yaxis': {
                  'showgrid': False,
                    'showbackground': False,
                  'linecolor': 'green',
                  'linewidth': 0,
                  'ticks': '',
                  'showticklabels': False,
                  'visible': False,
                    'title': 'y'
        },
        'zaxis': {
                  'showgrid': False,
                    'showbackground': False,
                  'linecolor': 'blue',
                  'linewidth': 0,
                  'ticks': '',
                  'showticklabels': False,
                  'visible': False,
                    'title': 'z'
        },
        'bgcolor': '#f8f9fa',
    }
'''
    'height': '8vh',
    'width': '8.33vw',
    
'''


dos_plot_layout = {
    'height': '400px',
    'width': '800px',
    'background': '#f8f9fa',
}

# TODO: (optional) ability to en-/disable individual Atoms (that are in the uploaded file) and let MALA recalculate
#  -> helps see each Atoms' impact in the grid




print("_________________________________________________________________________________________")
print("STARTING UP...")

app = dash.Dash(__name__, external_stylesheets=[dbc.icons.BOOTSTRAP, dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
app.title = 'MALAweb'

# just needed for styling of some headings
indent = '      '

# defining plot-choice-items
radioItems = dbc.RadioItems(
    options=[
        {"label": "Scatter", "value": "scatter"},
        {"label": "Isosurface", "value": "volume"},
    ], style={"font-size": "0.85em"},
    inline=True,
    id="plot-choice",
)

# -------------------------------
# Figs
def_fig = go.Figure(go.Scatter3d(x=[1], y=[1], z=[1], showlegend=False))
def_fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, xaxis_showgrid=False,
                      yaxis_showgrid=False, zaxis_showgrid=False)


orient_fig = go.Figure()

orient_fig.update_scenes(orient_template)
orient_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), title=dict(text="test"))
orient_fig.add_trace(go.Scatter3d(x=[0, 1], y=[0, 0], z=[0, 0], marker={'color': 'red', 'size': 0}, line={'width': 6}, showlegend=False))
orient_fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 1], z=[0, 0], marker={'color': 'green', 'size': 0}, line={'width': 6}, showlegend=False))
orient_fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], marker={'color': 'blue', 'size': 0}, line={'width': 6}, showlegend=False))

orient_plot = dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style, config={'displayModeBar': False})


#------------------------------------
# Table

row1 = html.Tr([html.Td(indent.join("Band - Energy"), style={'text-align': 'center', 'padding': 3})],
               style={"font-weight": "bold"})
row2 = html.Tr([html.Td(0, id="bandEn", style={'text-align': 'right', 'padding': 5})])
row3 = html.Tr([html.Td(indent.join("Total - Energy"), style={'text-align': 'center', 'padding': 3})],
               style={"font-weight": "bold"})
row4 = html.Tr([html.Td(0, id="totalEn", style={'text-align': 'right', 'padding': 5})])
row5 = html.Tr([html.Td(indent.join("Fermi - Energy"), style={'text-align': 'center', 'padding': 3})],
               style={"font-weight": "bold"})
row6 = html.Tr([html.Td("placeholder", id='fermiEn', style={'text-align': 'right', 'padding': 5})])
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]


table = dbc.Table(table_body, bordered=True, striped=True, style={'height': 'min-content', 'padding': 0, 'margin': 0})




# -----------------
# Left SIDEBAR content
menu = html.Div([
                # Logo Section
                html.Div([
                    html.Img(src='https://avatars.githubusercontent.com/u/81354661?s=200&v=4', className="logo"),
                    html.H2(children='MALA', style={'text-align': 'center'}),
                    html.Div(children='''
                    Framework for machine learning materials properties from first-principles data.
                ''', style={'text-align': 'center'}),
                ], className="logo"),

                html.Hr(style={'margin-bottom': '2rem', 'margin-top': '1rem', 'width': '5rem'}),

                dbc.Card(html.H6(children='File-Upload', style={'margin': '5px'}, id="open-upload", n_clicks=0),
                         style={"text-align": "center"}),

                dbc.Collapse(
                    dbc.Card(dbc.CardBody(  # Upload Section
                        html.Div([

                            html.Div(children='''
                            Upload atompositions via .cube! (later npy)
                            ''', style={'text-align': 'center'}),
                            # TODO: make this give dynamic promts (like "choose a plot!")
                            # right now we're reloading the whole "welcome mala"-cell for that

                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag & Drop', html.Br(), 'or ', html.Br(),
                                    html.A('Click to select')
                                ]),
                                style={
                                    'width': '90%',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin-left': "0.5em",
                                    'margin-top': '1em',
                                    'margin-bottom': '1em',
                                    "font-size": "0.85em",
                                },
                                # don't allow multiple files to be uploaded
                                multiple=False
                            ),
                            html.Div("Awaiting upload..", id='output-upload-state',
                                     style={'margin': '2px', "font-size": "0.85em",
                                    'textAlign': 'center',}),
                            dbc.Button("reset", id="reset-data", style={'margin-left': "1.75em"})

                        ], className="upload-section"
                        ),
                    )),
                    id="collapse-upload",
                    is_open=True,
                ),

                dbc.Card(
                    html.H6(children='Plot Style', style={'margin': '5px'}, id="open-plot-choice", n_clicks=0),
                    style={"text-align": "center", 'margin-top': '15px'}),

                dbc.Collapse(dbc.Card(dbc.CardBody(
                    html.Div(children=[radioItems]))),
                    id="collapse-plot-choice",
                    is_open=False,
                ),

            ], className="sidebar")

# Right SIDEBAR (default) content
r_content_sc = html.Div([
    html.H5("Settings"),
    dbc.Card(dbc.CardBody(
        [

            html.H6("Camera"),
            dbc.ButtonGroup(
                [
                    dbc.Button('Def.', id='default-cam', n_clicks=0),
                    dbc.Button('X-Y', id='x-y-cam', n_clicks=0),
                    dbc.Button('X-Z', id='x-z-cam', n_clicks=0),
                    dbc.Button('Y-Z', id='y-z-cam', n_clicks=0)
                ], vertical=True, size="sm",
            ),
            html.Hr(),

            dbc.Checkbox(label='Outline', value=True, id='sc-outline', style={'text-align': 'left'}),
            dbc.Checkbox(label='Atoms', value=True, id='sc-atoms', style={'text-align': 'left'}),

            html.Hr(),

            html.H6("", id="sz/isosurf-label"),
            html.Div(dcc.Slider(6, 18, 2, value=12, id='sc-size', vertical=True, verticalHeight=150), style={'margin-left': '1rem'}),

            html.Hr(),

            html.H6("Opacity", id="opac-label"),
            dbc.Input(type="number", min=0.1, max=1, step=0.1, id="sc-opac", placeholder="0.1 - 1", style={"width": "7em", 'margin-left': '1.5rem'}, size="sm"),


        ]
    ))], style={'text-align': 'center'})





# Bottom BAR content
bot_content = dbc.Container([

    dbc.Row(
        dbc.Col(
            dbc.Button(html.P("Close", style={"line-height": "0.65em", "font-size": "0.65em"}),
                       id="close-bot", style={"width": "5em", "height": "1.2em"}, n_clicks=0),
            style={'width': 'min-content', 'margin-bottom': '1em'}, width=2
        ), justify='center', className="g-0"
    ),

    dbc.Row([

        dbc.Col(dbc.Card(dbc.CardBody(table)), style={'height': 'min-content'}, width='auto', align="end"),
        dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="dos-plot", style={'width': '30vh', 'height': '15vh'}))), width='auto'),

    ], style={'height': 'min-content'}, justify='center')

])

# --------------------------

# Filling offcanvasses with respective content

# Left SIDEBAR
side_l = html.Div([
    dbc.Offcanvas(menu, id="offcanvas-l", is_open=True, scrollable=True, backdrop=False,
                  style={'width': '12rem', 'margin-top': '3rem', 'margin-left': '0.5vw', 'border-radius': '10px',
               'height': 'min-content',
                         'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px'},
),
])

# Right SIDEBAR
side_r = html.Div([
    dbc.Offcanvas(r_content_sc, id="offcanvas-r-sc", is_open=False,
                  style={'width': '9rem', 'height': 'min-content',
                         'margin-top': '3em',
                         'margin-right': '0.5vw', 'border-radius': '10px',
                         'box-shadow': 'rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px',
                         'position': 'absolute'},
                  scrollable=True, backdrop=False, placement='end'),
])

# Bottom BAR
bot = html.Div([dbc.Offcanvas(bot_content, id="offcanvas-bot", is_open=False,
                  style={'height': 'min-content', 'border-radius': '5px',
                         'margin-left': '15vw',
                         'margin-right': '15vw',
                         'background-color': 'rgba(0, 0, 0, .25)'},
                  scrollable=True, backdrop=False, close_button=False, placement='bottom')])


bot_button = html.Div(dbc.Offcanvas([

# this is not centered
    dbc.Row(
        dbc.Col(dbc.Button(html.P("Energy / Density of State",
                                  style={"line-height": "0.65em", "font-size": "0.65em"}),
                       id="open-bot", style={
                "width": "10em",
                "height": "1.2em",
                "position": "absolute",
                "left": "50%",
                "-webkit-transform": "translateX(-50%)",
                "transform": "translateX(-50%)",
                'bottom': '0.5em'
            }, n_clicks=0), width=1)
    ,)



    ], id="open-bot-canv", style={'height': 'min-content',
                         'background-color': 'rgba(0, 0, 0, 0)', 'border': '0'},
                  is_open=False, scrollable=True, backdrop=False, close_button=False, placement='bottom')
)


# TODO: Orientation fig & bottom offcanvas (table+dos)



#---------------------------------
# Plots for the created Figures
main_plot = [


    dcc.Store(id="cam_store"),
    dbc.Row([
        # Plot section
        dbc.Col(
            [
                dbc.Card(dbc.CardBody(
                    [

                        dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style,
                                  config={'displayModeBar': False}),

                        html.Div(
                            dcc.Graph(id="scatter-plot", responsive=True, figure=def_fig, style=plot_layout),
                            className="density-scatter-plot"
                        ),




                        # Tools

                        dbc.Row([
                            html.Hr(),
                            dbc.Button(html.P("Tools", style={"line-height": "0.65em", "font-size": "0.65em"}),
                                       id="open-sc-tools", style={"width": "5em", "height": "1.2em"}, n_clicks=0)
                        ], justify="center", style={"text-align": "center"}),

                        dbc.Row(
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(
                                    [
                                        dbc.Row([
                                            # Buttons
                                            dbc.Col(
                                                dbc.ButtonGroup(
                                                    [
                                                        dbc.Button('X', id='sc-active-x', active=False, outline=True,
                                                                   color="danger", n_clicks=0),
                                                        dbc.Button('Y', id='sc-active-y', active=False, outline=True,
                                                                   color="success", n_clicks=0),
                                                        dbc.Button('Z', id='sc-active-z', active=False, outline=True,
                                                                   color="primary", n_clicks=0),
                                                        dbc.Button("Density", id='active-dense', active=False, outline=True,
                                                                   color="dark", n_clicks=0)
                                                    ],
                                                    vertical=True,
                                                ), width=1),

                                            # Sliders
                                            dbc.Col([
                                                dbc.Row([
                                                    dbc.Col(dcc.RangeSlider(id='range-slider-cs-x',
                                                                            disabled=True,
                                                                            min=0,
                                                                            max=1,
                                                                            marks=None,
                                                                            pushable=True,
                                                                            tooltip={"placement": "bottom",
                                                                                     "always_visible": False},
                                                                            updatemode='drag')),
                                                    dbc.Col(html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                                     style={'width': '1.25em'}), width=1)
                                                ], style={"margin-top": "7px"}),  # X-Axis

                                                dbc.Row([
                                                    dbc.Col(dcc.RangeSlider(
                                                        id='range-slider-cs-y',
                                                        disabled=True,
                                                        pushable=True,
                                                        min=0, max=1,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": False},
                                                        updatemode='drag')),
                                                    dbc.Col(html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                                     style={'width': '1.25em'}), width=1)
                                                ]),  # Y-Axis

                                                dbc.Row([
                                                    dbc.Col(dcc.RangeSlider(
                                                        id='range-slider-cs-z',
                                                        disabled=True,
                                                        pushable=True,
                                                        min=0, max=1,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": False},
                                                        updatemode='drag')),
                                                    dbc.Col(html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                                     style={'width': '1.25em'}), width=1)

                                                ]),  # Z-Axis

                                                dbc.Row([

                                                    dbc.Col(dcc.RangeSlider(
                                                        id='range-slider-dense',
                                                        disabled=True,
                                                        pushable=True,
                                                        min=0, max=1,
                                                        marks=None,
                                                        tooltip={"placement": "bottom", "always_visible": False},
                                                        updatemode='drag')),
                                                    dbc.Col(html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0,
                                                                     style={'width': '1.25em', 'position': 'float'}),
                                                            width=1),

                                                ]),  # Density
                                            ], width=11),
                                        ]),
                                    ]
                                )),
                                id="sc-tools-collapse",
                                is_open=False), style={'margin-top': '1em'}
                        )
                    ]
                ), style={'background-color': 'rgba(248, 249, 250, 1)', 'width': 'min-content',
                          'align-content': 'center', 'margin-top': '1.5rem'}),
            ],
            className="plot-section"),
    ]),
]


# ----------------
# landing-cell for mc0
mc0_landing = html.Div([
    html.Div([html.H1([indent.join('Welcome')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('To')], className='greetings',
                      style={'text-align': 'center'}),
              html.H1([indent.join('MALA')], className='greetings',
                      style={'text-align': 'center'}),
              html.Div('Upload a .cube-File for MALA to process'),
              html.Div('Then choose a style for plotting')],
             style={'text-align': 'center'}),

], style={'width': 'content-min', 'margin-top': '20vh'})

skel_layout = [dbc.Row([
        dbc.Col(

            [side_l,
             dbc.Button(">", id="open-offcanvas-l", n_clicks=0, style={'margin-top': '40vh'}),
            bot_button, bot     # it doesn't matter where offcanvasses are placed here - only their "placement"-prop matters
             ],
            id="l0", width='auto', style={'background-color': 'red'}),

        dbc.Col(mc0_landing, id="mc0", width='auto', style={'background-color': 'blue'}),

        dbc.Col(
            [
                side_r,
                dbc.Button("<", id="open-settings-sc", n_clicks=0, style={'margin-top': '40vh',}),
             ],

            id="r0", width='auto', style={'background-color': 'green'})

    ], justify='center')]


p_layout_landing = dbc.Container([

        dcc.Store(id="page_state", data="landing"),
        dcc.Store(id="df_store", storage_type="session"),
        dcc.Store(id="choice_store"),
        dcc.Store(id="sc_settings"),
        html.Div(skel_layout, id="content-layout")
    ], fluid=True, style={'height': '100vh', 'width': '100vw', 'background-color': '#023B59'})

app.layout = p_layout_landing


# p_layout_plotting will be redefined on page_state-change
# parts of plotting_layout will be redefined on data-upload

# FGEDF4 as contrast ??


# CALLBACKS & FUNCTIONS

# sidebar_l collapses
@app.callback(
    Output("collapse-upload", "is_open"),
    Input("open-upload", "n_clicks"),
    Input("collapse-upload", "is_open"),
    prevent_initial_call=True,
)
def toggle_upload(n_header, is_open):
    if n_header:
        return not is_open


# this callback is totally optional and only decides if the reset-button should also reset plot-choice
# turned off for development by PreventingUpdate for now
@app.callback(
    Output("plot-choice", "value"),
    Input("reset-data", "n_clicks"),
    prevent_initial_call=True,
)
def resetPlotChoice(trigger_reset):
    raise PreventUpdate
    return []


@app.callback(
    Output("collapse-plot-choice", "is_open"),
    [Input("open-plot-choice", "n_clicks"),
     Input("page_state", "data"),
     Input("df_store", "data"),
     Input("collapse-plot-choice", "is_open")],
    prevent_initial_call=True,
)
def toggle_plot_choice(n_header, page_state, data, is_open):
    # open plot-style-chooser when state is uploaded
    if dash.callback_context.triggered_id == "open-plot-choice":
        return not is_open
    elif dash.callback_context.triggered_id == "page_state" or "df_store":
        if data is not None:
            return True
        else:
            return False


# end of sidebar_l collapses


# BOTTOM bar callbacks

@app.callback(
    Output("open-bot-canv", "is_open"),
    Input("page_state", "data"),
    Input("offcanvas-bot", "is_open"),
    prevent_initial_call=True,
)
def toggle_bot_button(page_state, canv_open):
    if page_state == "plotting":
        if not canv_open:
            return True
        else:
            return False

    else:
        print("not plotting..")
        return False
# show button if we're plotting and if bot-canvas is closed

@app.callback(
    Output("offcanvas-bot", "is_open"),
    Input("open-bot", "n_clicks"),
    Input("close-bot", "n_clicks"),
    Input("page_state", "data"),
    prevent_initial_call=True,
)
def toggle_bot_canv(open_cl, close_cl, page_state):
    if page_state == "plotting":
        if dash.callback_context.triggered_id[0:4] == "open":
            return True
        else:
            return False
    else:
        return False



# END BOTTOM BAR CALLBACKS


# CALLBACKS FOR SCATTERPLOT

# collapsable cross-section and density tools
@app.callback(
    Output("sc-tools-collapse", "is_open"),
    Input("open-sc-tools", "n_clicks"),
    State("sc-tools-collapse", "is_open"),
    prevent_initial_call=True)
def toggle_sc_tools(n_sc_s, is_open):
    if n_sc_s:
        return not is_open


# toggle rangesliders
@app.callback(
    Output("range-slider-cs-x", "disabled"),
    Output("sc-active-x", "active"),
    Input("sc-active-x", "n_clicks"),
    Input("range-slider-cs-x", "disabled"),
    State("sc-active-x", "active"),
    prevent_initial_call=True)
def toggle_x_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


# END OLD SC CS X


# OLD SC CS Y
@app.callback(
    Output("range-slider-cs-y", "disabled"),
    Output("sc-active-y", "active"),
    Input("sc-active-y", "n_clicks"),
    Input("range-slider-cs-y", "disabled"),
    State("sc-active-y", "active"),
    prevent_initial_call=True)
def toggle_y_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


# END OLD SC CS Y

# OLD SC CS Z
@app.callback(
    Output("range-slider-cs-z", "disabled"),
    Output("sc-active-z", "active"),
    Input("sc-active-z", "n_clicks"),
    Input("range-slider-cs-z", "disabled"),
    State("sc-active-z", "active"),
    prevent_initial_call=True)
def toggle_z_cs(n_x, active, bc):
    if n_x:
        return not active, not bc


# END OLD SC CS Z


# OLD SC DENS
@app.callback(
    Output("range-slider-dense", "disabled"),
    Output("active-dense", "active"),
    Output("active-dense", "disabled"),
    Input("active-dense", "n_clicks"),
    State("range-slider-dense", "disabled"),
    State("active-dense", "active"),
    Input("choice_store", "data"),
    prevent_initial_call=True)
def toggle_density_sc(n_d, active, bc, plot_choice):
    # Disabling density-slider for volume-plots
    if dash.callback_context.triggered_id == "choice_store":
        if plot_choice == "scatter":
            return True, False, False
        else:
            return True, False, True
    elif dash.callback_context.triggered_id == "active-dense":
        return not active, not bc, False
    else:
        return True, False, True
    # active actually is the disabled parameter!


# END OLD SC DENS


@app.callback(
    Output("range-slider-cs-x", "value"),
    Input("reset-cs-x", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_x(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['x']), max(scatter_df['x'])]


@app.callback(
    Output("range-slider-cs-y", "value"),
    Input("reset-cs-y", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_y(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['y']), max(scatter_df['y'])]


@app.callback(
    Output("range-slider-cs-z", "value"),
    Input("reset-cs-z", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_z(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['z']), max(scatter_df['z'])]


@app.callback(
    Output("range-slider-dense", "value"),
    Input("reset-dense", "n_clicks"),
    Input("df_store", "data"),
    prevent_initial_call=True)
def reset_cs_dense(n_clicks, data):
    if data is not None:
        scatter_df = pd.DataFrame(data['MALA_DF']['scatter'])
        return [min(scatter_df['val']), max(scatter_df['val'])]


# end of collapsable cross-section settings


# Storing camera position
@app.callback(
    Output("cam_store", "data"),
    [Input("default-cam", "n_clicks"),
     Input("x-y-cam", "n_clicks"),
     Input("x-z-cam", "n_clicks"),
     Input("y-z-cam", "n_clicks"),
     Input("scatter-plot", "relayoutData")],
    prevent_initial_call=True)
def store_cam(default_clicks, x_y_clicks, x_z_clicks, y_z_clicks, user_in):
    # user_in is the camera position set by mouse movement, it has to be updated on every mouse input on the fig

    # set stored_cam_setting according to which button was last pressed
    if dash.callback_context.triggered_id[0:-4] == "default":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-y":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00)
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0)
        )
    elif dash.callback_context.triggered_id[0:-4] == "y-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0))
    # set to plot cam when user input is camera-movement:
    elif dash.callback_context.triggered_id == "scatter-plot":

        # stops the update in case the callback is triggered by zooming/initializing/smth else
        if user_in is None or "scene.camera" not in user_in.keys():
            raise PreventUpdate
        else:
            if 'scene.camera' in user_in.keys():
                return user_in['scene.camera']
        # stops the update in case the callback is triggered by zooming/smth else
    else:
        print("unknown trigger caused cam_pos_update")
        raise PreventUpdate

    # Feels very unelegant -> this is always run twice when switching to scatter for example
    # END OF SCATTER CALLBACKS


# UPDATE STORED DATA

# page state
@app.callback(
    Output("page_state", "data"),
    [Input("df_store", "data"),
     Input("choice_store", "data"),
     Input("reset-data", "n_clicks"),
     State("page_state", "data")],
    prevent_initial_call=True)
def updatePageState(trig1, trig2, trig3, state):
    new_state = "landing"
    if dash.callback_context.triggered_id == "df_store" or "choice_store":
        if trig1 is not None and trig2 is not None:
            new_state = "plotting"
    elif dash.callback_context.triggered_id == "reset-data":
        new_state = "landing"

    # prevent unnecessary updates
    if state == new_state:
        raise PreventUpdate
    else:
        return new_state


# dataframes
# THIS IS RUNNING MALA INFERENCE
@app.callback(
    Output("df_store", "data"),
    Output('upload-data', 'contents'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename'),
     Input("reset-data", "n_clicks")],
    prevent_initial_call=True)
def updateDF(f_data, file, reset):
    # GOAL:
    # f_data = uploaded data -> to be .npy
    # TODO: smth like (mala_data = mala.webAPI(f_data)) (run a mala .getter(uploadedData))
    #  --> mala takes uploaded data and returns calculations
    #  --> waiting for Lenz

    # TODO: check if data is valid before updating
    #  maybe do this on upload, so this callback isn't even run
    #  --> raise preventUpdate if not

    # Always returning None for the Upload-Component as well, so that it's possible to reupload
    # (-> gotta clear up the space first)
    # reset on wrong filetype
    if file is not None and not file.endswith('.cube'):
        return None, f_data

    if dash.callback_context.triggered_id == "reset-data":
        return None, None
    # (a) GET DATA FROM MALA (/ inference script)
    print("Running MALA-Inference")
    mala_data = mala_inference.results
    bandEn = mala_data['band_energy']
    totalEn = mala_data['total_energy']
    density = mala_data['density']
    dOs = mala_data['density_of_states']
    enGrid = mala_data['energy_grid']

    coord_arr = np.column_stack(
        list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij"))) + [density.ravel()])
    data0 = pd.DataFrame(coord_arr, columns=['x', 'y', 'z', 'val'])  # untransformed Dataset

    atoms = [[], [], [], [], []]

    # Reding .cube-File
    # TODO: this has to be done with uploaded .npy

    # (b) GET ATOMPOSITION & AXIS SCALING FROM .cube CREATED BY MALA (located where 'mala-inference-script' is located
    atom_data = '/home/maxyyy/PycharmProjects/mala/app/Be2_density.cube'

    # 0-1 = Comment, Energy, broadening     //      2 = number of atoms, coord origin
    # 3-5 = number of voxels per Axis (x/y/z), lentgh of axis-vector -> info on cell-warping
    # 6-x = atompositions

    with open(atom_data, 'r') as f:
        lines = f.read().splitlines()
        no_of_atoms, _, _, _ = lines[2].split()

        # AXIS-SCALING-FACTOR
        # axis-List-Format: voxelcount[0]   X-Scale[1]     Y-Scale[2]     Z-Scale[3]
        x_axis = [float(i) for i in lines[3].split()]
        y_axis = [float(i) for i in lines[4].split()]
        z_axis = [float(i) for i in lines[5].split()]

    # READING ATOMPOSITIONS
    for i in range(0, int(no_of_atoms)):
        ordinal_number, charge, x, y, z = lines[6 + i].split()  # atom-data starts @line-index 6
        # atoms-List-Format: ordinalNumber[0]    charge[1]  x[2]   y[3]   z[4]
        atoms[0].append(int(ordinal_number))
        atoms[1].append(float(charge))
        atoms[2].append(float(x))
        atoms[3].append(float(y))
        atoms[4].append(float(z))
    atoms_data = pd.DataFrame(
        data={'x': atoms[2], 'y': atoms[3], 'z': atoms[4], 'ordinal': atoms[0], 'charge': atoms[1]})

    # SCALING AND SHEARING SCATTER DF
    # (b) SCALING to right voxel-size
    # need to bring atompositions and density-voxels to the same scaling
    data0['x'] *= x_axis[1]
    data0['y'] *= y_axis[2]
    data0['z'] *= z_axis[3]
    data_sc = data0.copy()
    data_vol = data0.copy()

    # SHEARING für scatter_3d - linearcombination
    data_sc.x += y_axis[1] * (data0.y / y_axis[2])
    data_sc.x += z_axis[1] * (data0.z / z_axis[3])

    data_sc.y += x_axis[2] * (data0.x / x_axis[1])
    data_sc.y += z_axis[2] * (data0.z / z_axis[3])

    data_sc.z += y_axis[3] * (data0.y / y_axis[2])
    data_sc.z += x_axis[3] * (data0.x / x_axis[1])

    '''
           Importing Data 
               Parameters imported from:
               (a) inference script:
                   - bandEn
                   - totalEn
                   - density
                   - density of states - dOs
                   - energy Grid - enGrid

               (b) .cube file created by running inference script
                   =   axis-data -> x_, y_ and z_axis
                   - voxel"resolution"
                       - f.e. x_axis[0]
                   - unit-vector
                       - f.e. ( x_axis[1] / x_axis[2] / x_axis[3] ) is x-axis unit-vector
               TODO: find a GOOD way to transform our data from kartesian grid to the according (in example data sheared) one
                   - so far only doing that with a linear combination for dataframe in scatter_3d format
                   - need to to this for volume too
                   --> good way would be a matrix multiplication of some sort
    '''

    # _______________________________________________________________________________________

    df_store = {'MALA_DF': {'default': data0.to_dict("records"), 'scatter': data_sc.to_dict("records"),
                            'volume': data_vol.to_dict("records")},
                'MALA_DATA': mala_data,
                'INPUT_DF': atoms_data.to_dict("records"),
                'SCALE': {'x_axis': x_axis, 'y_axis': y_axis, 'z_axis': z_axis}}

    print("DATA IMPORT COMPLETE")
    print("_________________________________________________________________________________________")
    return df_store, None


# PLOT-CHOICE STORING

@app.callback(
    Output("choice_store", "data"),
    [Input('plot-choice', 'value')],
    prevent_initial_call=True)
def update_choice_store(choice):
    return choice


# SC SETTINGS STORING
# TODO: fix Opacity/Outline (Double Binding?)
@app.callback(
    Output("sc_settings", "data"),
    [Input('sc-size', 'value'),
     Input("sc-outline", "value"),
     Input("sc-atoms", "value"),
     Input("sc-opac", "value")
     ],
    State("sc_settings", "data"),
)
def update_settings_store(size, outline, atoms, opac, saved):
    if saved is None:
        # default settings
        settings = {
            "size": 12,
            "opac": 1,
            "outline": True,
            "atoms": True,
        }
    else:
        settings = saved
    if dash.callback_context.triggered_id == "sc-size":
        settings["size"] = size
    elif dash.callback_context.triggered_id == "sc-opac":
        if opac is None:
            raise PreventUpdate
        settings["opac"] = opac
        if opac < 1:
            settings["outline"] = False
    elif dash.callback_context.triggered_id == "sc-outline":
        settings["outline"] = outline
    elif dash.callback_context.triggered_id == "sc-atoms":
        settings["atoms"] = atoms
    return settings


# END UPDATE FOR STORED DATA


# TODO: update Tool-Sliders - DENSITY BUG!!
@app.callback(
    [

        Output("range-slider-cs-x", "min"),
        Output("range-slider-cs-x", "max"),
        Output("range-slider-cs-x", "step"),

        Output("range-slider-cs-y", "min"),
        Output("range-slider-cs-y", "max"),
        Output("range-slider-cs-y", "step"),

        Output("range-slider-cs-z", "min"),
        Output("range-slider-cs-z", "max"),
        Output("range-slider-cs-z", "step"),

        Output("range-slider-dense", "min"),
        Output("range-slider-dense", "max"),
        Output("range-slider-dense", "step"),
    ],
    [
        Input("df_store", "data"),
    ],
    [
        # as long as volume and scatter don't share their dataset: state instead of input
        State("choice_store", "data")
    ],
)
def update_tools(data, plot_choice):
    if data is None:  # in case of reset:
        raise PreventUpdate
    else:
        if plot_choice == "scatter":
            df = pd.DataFrame(data['MALA_DF']['scatter'])
        elif plot_choice == "volume":
            df = pd.DataFrame(data['MALA_DF']['volume'])
        else:
            # return these default values if we don#t have a plot-choice for some reason
            return 0, 1, 1, \
                   0, 1, 1, \
                   0, 1, 1, \
                   0, 1, 1,

        scale = pd.DataFrame(data['SCALE'])
        x_step = scale["x_axis"][1]
        y_step = scale["y_axis"][2]
        z_step = scale["z_axis"][3]
        dense_step = round((max(df['val']) - min(df['val'])) / 30, ndigits=5)

        # BUG: have to add another half-step, else rangeslider won't ever be filled and will cut off very last x-column
        return min(df["x"]), max(df["x"])+0.5*x_step, x_step, \
               min(df["y"]), max(df["y"]), y_step, \
               min(df["z"]), max(df["z"]), z_step, \
               min(df["val"]), max(df["val"]), dense_step


# LAYOUT CALLBACKS
# UPDATING CONTENT-CELL 0

@app.callback(
    Output("mc0", "children"),
    Input("page_state", "data"),
    State("choice_store", "data"),
    State("df_store", "data"),
    prevent_initial_call=True)
def updateMC0(state, plots, data):
    if data is None or state == "landing":
        return mc0_landing

    elif state == "plotting":
        return main_plot


'''
# cam-position buttons have to stay as parameters, so they trigger an update. 
cam_store can't be an input or else it triggers an update everytime the cam is moved
'''


@app.callback(
    Output("scatter-plot", "figure"),
    #Output("vtk-plot", "children"),
    [
        # Tools
        Input("range-slider-dense", "value"),
        Input("active-dense", "active"),
        Input("range-slider-cs-x", "value"),
        Input("sc-active-x", "active"),
        Input("range-slider-cs-y", "value"),
        Input("sc-active-y", "active"),
        Input("range-slider-cs-z", "value"),
        Input("sc-active-z", "active"),
        # Settings
        Input("sc_settings", "data"),
        Input("default-cam", "n_clicks"),
        Input("x-y-cam", "n_clicks"),
        Input("x-z-cam", "n_clicks"),
        Input("y-z-cam", "n_clicks"),
        Input("choice_store", "data")
    ],
    [State("scatter-plot", "relayoutData"),
     State("cam_store", "data"),
     Input("df_store", "data"),
     State("scatter-plot", "figure")
     ],
    # prevent_initial_call=True
)
def updatePlot(slider_range, dense_inactive, slider_range_cs_x, cs_x_inactive, slider_range_cs_y, cs_y_inactive,
               slider_range_cs_z, cs_z_inactive,
               settings,
               cam_default, cam_xy, cam_xz, cam_yz, plots, relayout_data, stored_cam_settings, f_data, fig):
    # TODO: make this function more efficient
    #  - for example on settings-change, only update the settings and take the fig from relayout data instead of redefining it
    # --> most likely only possible with client-side-callbacks

    # DATA
    # the density-Dataframe that we're updating, taken from df_store (=f_data)

    if f_data is None or plots is None:
        raise PreventUpdate

    print("GET DATA from df_store")

    scale = pd.DataFrame(f_data['SCALE'])
    x_axis, y_axis, z_axis = scale.x_axis, scale.y_axis, scale.z_axis
    x_ratio, y_ratio, z_ratio = x_axis[1], y_axis[2], z_axis[3]

    if plots == "scatter":
        df = pd.DataFrame(f_data['MALA_DF']['scatter'])
    elif plots == "volume":
        df = pd.DataFrame(f_data['MALA_DF']['volume'])
    else:
        # No Data to plot -> don't update
        raise PreventUpdate
    dfu = df.copy()


    # atoms-Dataframe also taken from f_data
    atoms = pd.DataFrame(f_data['INPUT_DF'])
    no_of_atoms = len(atoms)


    df_bound = df.from_dict({
        'x': [min(dfu['x']), min(dfu['x']), min(dfu['x']), min(dfu['x']), max(dfu['x']), max(dfu['x']), max(dfu['x']), max(dfu['x'])],
        'y': [min(dfu['y']), min(dfu['y']), max(dfu['y']), max(dfu['y']), min(dfu['y']), min(dfu['y']), max(dfu['y']), max(dfu['y'])],
        'z': [min(dfu['z']), max(dfu['z']), min(dfu['z']), max(dfu['z']), min(dfu['z']), max(dfu['z']), min(dfu['z']), max(dfu['z'])]

    })
    fig_bound = go.Scatter3d(
        x=df_bound['x'], y=df_bound['y'], z=df_bound['z'], mode='markers',
        marker=dict(size=0, color='white'), visible=False, showlegend= False,
    )

    # Dataframes are ready



    # TOOLS
        # these edit the DF before the figure is built
    # filter-by-density
    if slider_range is not None and dense_inactive:  # Any slider Input there?
        low, high = slider_range
        mask = (dfu['val'] >= low) & (dfu['val'] <= high)
        dfu = dfu[mask]

    # x-Cross-section
    if slider_range_cs_x is not None and cs_x_inactive:  # Any slider Input there?
        low, high = slider_range_cs_x
        mask = (dfu['x'] >= low) & (dfu['x'] <= high)
        dfu = dfu[mask]

    # Y-Cross-section
    if slider_range_cs_y is not None and cs_y_inactive:  # Any slider Input there?
        low, high = slider_range_cs_y
        mask = (dfu['y'] >= low) & (dfu['y'] <= high)
        dfu = dfu[mask]

    # Z-Cross-section
    if slider_range_cs_z is not None and cs_z_inactive:  # Any slider Input there?
        low, high = slider_range_cs_z
        mask = (dfu['z'] >= low) & (dfu['z'] <= high)
        dfu = dfu[mask]



    # SETTINGS
    # plot-settings

    # ADD ATOMS
    # TODO: COLOR-CODING ATOMS BASED OFF THEIR CHARGE
    if settings["atoms"]:
        atom_colors = []
        for i in range(0, int(no_of_atoms)):
            if atoms['charge'][i] == 4.0:
                atom_colors.append("black")
            else:
                atom_colors.append("white")
        atoms_fig = go.Scatter3d(name="Atoms", x=atoms['x'], y=atoms['y'], z=atoms['z'], mode='markers',
                         marker=dict(size=30, color=atom_colors))
    else:
        atoms_fig = go.Figure()



         # creating the figure, updateing some things

    if plots == "scatter":
        # updating fig according to (cs'd) DF
        fig_upd = px.scatter_3d(
            dfu, x="x", y="y", z="z",
            color="val",
            hover_data=['val'],
            opacity=settings["opac"],
            color_continuous_scale=px.colors.sequential.Inferno_r,
            range_color=[min(df['val']), max(df['val'])],
            # takes color range from original dataset, so colors don't change
        )
        # Outline settings
        if settings["outline"]:
            outlined = dict(width=1, color='DarkSlateGrey')
        else:
            outlined = dict(width=0, color='DarkSlateGrey')

        # applying marker settings
        fig_upd.update_traces(marker=dict(size=settings["size"], line=outlined), selector=dict(mode='markers'))


    elif plots == "volume":
        fig_upd = go.Figure(
            data=go.Volume(

            x=dfu.x,        #df for non-sliced
            y=dfu.y,
            z=dfu.z,
            value=dfu.val,

            opacity=0.3,
            surface={'count': settings["size"], 'fill': 1}, # fill=0.5 etc adds a nice texture/mesh inside
            #spaceframe={'fill': 0.5}, # does what exactly?
            contour={'show': settings["outline"], 'width': 5},
            colorscale=px.colors.sequential.Inferno_r,
            cmin=min(df['val']),
            cmax=max(df['val'])
            #cauto=True,
        ))
    else:
        fig_upd=def_fig


    # atoms fig
    if settings["atoms"]:
        fig_upd.add_trace(atoms_fig)

    # UPDATING FIG-SCENE- and Layout- PROPERTIES
    fig_upd.update_layout(margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor="#f8f9fa", modebar=dict())
    fig_upd.update_layout(modebar_remove=["zoom", "resetcameradefault", "resetcameralastsave"])

    # CAMERA
    if dash.callback_context.triggered_id == "default-cam":
        new_cam=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    elif dash.callback_context.triggered_id == "x-y-cam":
        new_cam=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00)
        )
    elif dash.callback_context.triggered_id == "x-z-cam":
        new_cam=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0)
        )
    elif dash.callback_context.triggered_id == "y-z-cam":
        new_cam=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0))
    else: new_cam=stored_cam_settings


    fig_upd.update_layout(scene_camera=new_cam, template=templ1,)
    '''
    set camera-position according to the clicked button, 
                                OR 
                - if no button has been clicked - 
    to the most recently stored manually adjusted camera position
    '''

    # adding helperfigure to keep camera-zoom the same, regardless of data(-slicing)-changes
    fig_upd.add_trace(fig_bound)

    return fig_upd


''' maybe interesting: animations on plot change:

https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html
"transition
Sets transition options used during Plotly.react updates."

'''



@app.callback(
    Output("orientation", "figure"),
    Input("cam_store", "data"),
    State("scatter-plot", "figure")
)
def updateOrientation(saved_cam, fig):
    #print(fig)
    fig_upd=orient_fig
    fig_upd.update_layout(scene_camera=saved_cam, clickmode="none")
    return fig_upd


# TODO: updateDoS
@app.callback(
    Output("dos-plot", "figure"),
    Output("bandEn", "children"),
    Output("totalEn", "children"),
    Output("fermiEn", "children"),
    [Input("df_store", "data"),
     Input("page_state", "data")]
)
def update_bot_canv(f_data, state):


# TODO: this is NOT working - FIX IT - (also style that thing..)

    if f_data is not None:
        #print(f_data['MALA_DATA'])
        # PLOT data
        dOs = f_data['MALA_DATA']['density_of_states']
        df = pd.DataFrame(dOs)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df.index, y=df[0], name='densityOfstate',
                       line=dict(color='#f15e64', width=3, dash='dot')))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))

        # TABLE data
        # take the first
        band_en = f_data['MALA_DATA']['band_energy']
        total_en = f_data['MALA_DATA']['total_energy']
        fermi_en = 0

    else:
        fig = px.scatter()

        band_en = '-'
        total_en = '-'
        fermi_en = '-'

    return fig, band_en, total_en, fermi_en

# END OF CALLBACKS FOR DOS PLOT



# CALLBACKS FOR SIDEBAR

# Update settings sidebar
@app.callback(
    Output("sz/isosurf-label", "children"),
    Output("opac-label", "style"),
    Output("sc-opac", "style"),
    Input("choice_store", "data"),
    prevent_initial_call=True
)
def updateSettingsBar(plot_choice):
    if plot_choice == "scatter":
        return "Size", {'visibility': 'visible'}, {'visibility': 'visible', 'width': '5em'}
    elif plot_choice == "volume":
        return "Resolution", {'visibility': 'hidden'}, {'visibility': 'hidden'}
    else:
        raise PreventUpdate



@app.callback(  # sidebar_r canvas (1/?)
    Output("offcanvas-r-sc", "is_open"),
    Input("open-settings-sc", "n_clicks"),
    [State("offcanvas-r-sc", "is_open")],
)
def toggle_settings_bar(n1, is_open):
    if n1:
        return not is_open
    return is_open



# toggle canvas
@app.callback(  # sidebar_l canvas
    Output("offcanvas-l", "is_open"),
    Input("open-offcanvas-l", "n_clicks"),
    [State("offcanvas-l", "is_open")],
)
def toggle_offcanvas_l(n1, is_open):
    if n1:
        return not is_open
    return is_open



# FILE-UPLOAD-STATUS
@app.callback(
    Output('output-upload-state', 'children'),
    [Input('upload-data', 'filename'),
     Input('upload-data', 'contents'),
     Input('df_store', 'data'),
     Input('reset-data', 'n_clicks')],
    prevent_initial_call=True,
)
def uploadStatus(filename, contents, data, reset):
    # checks for .cubes for now, as long as im working on visuals
    # will check for .npy when mala is ready to give .cube output from
    # is this enough input-sanitization or proper type-check needed?
    # upload component also has accept property to allow only certain types - might be better
    if dash.callback_context.triggered_id == "reset-data":
        status = "Awaiting upload.."
    elif filename is not None:
        if filename.endswith('.cube'):

            # USER INPUT ATOM POSITIONS - .cube File Upload
            # 1. File Upload of .cube File
            # 2. TODO: parse file with ASE
            # ase.io.read(contents)
            # 3. process with MALA
            # DONE:
            # receiving MALA Input (from script for now)
            # 4. contents

            status = 'Upload successful'
        else:
            status = 'Wrong file-type. .cube required'

    else:
        status = 'Awaiting upload..'

    return status


# END OF CALLBACKS FOR SIDEBAR

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
