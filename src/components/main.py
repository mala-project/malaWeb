from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# for Plot
        # Templates
    # Scene-Template for Graph-Object (orientation)
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

    # Properties for Plot layout
plot_layout = {
    'title': 'Plot',
    'height': '75vh',
    'width': '80vw',
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

    # Figs as prep for Plot
# Default fig for the main plot - gets overwritten on initial plot update, after that it gets patched on update
def_fig = go.Figure(go.Scatter3d(x=[1], y=[1], z=[1], showlegend=False))
def_fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, xaxis_showgrid=False,
                      yaxis_showgrid=False, zaxis_showgrid=False)

orient_fig = go.Figure()
orient_fig.update_scenes(orient_template)
orient_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), title=dict(text="test"), clickmode="none", dragmode=False)
orient_fig.add_trace(
    go.Scatter3d(x=[0, 1], y=[0, 0], z=[0, 0], marker={'color': 'red', 'size': 0}, line={'width': 6}, showlegend=False,
                 hoverinfo='skip'))
orient_fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 1], z=[0, 0], marker={'color': 'green', 'size': 0}, line={'width': 6},
                                  showlegend=False, hoverinfo='skip'))
orient_fig.add_trace(
    go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], marker={'color': 'blue', 'size': 0}, line={'width': 6}, showlegend=False,
                 hoverinfo='skip'))


    # Orientational Plots
'''
Default Plot for orientation
(could be integrated into the "main-card" at some point)
'''
orient_plot = dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style,
                        config={'displayModeBar': False, 'displaylogo': False})

    # The actual Plot
'''
STORE Variable & Card for the main plot 
'''
plot = [

    dcc.Store(id="cam_store"),

    dbc.Card(dbc.CardBody(
        [
            dbc.Row([
                dcc.Graph(id="orientation", responsive=True, figure=orient_fig, style=orientation_style,
                          config={'displayModeBar': False, 'displaylogo': False, 'showAxisDragHandles': True}),

                dcc.Graph(id="scatter-plot", responsive=True, figure=def_fig, style=plot_layout,
                          config={'displaylogo': False}),
            ]),

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
                                    # TODO: Triggers need work
                                    # TODO: rangesliders are only optimized with the example cell used in current models. Differently sheared planes will mess things up, as will cells with bigger datasets (minimum slice will grow/shrink)
                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(id='range-slider-cs-x',
                                                                disabled=True,
                                                                min=0,
                                                                max=1,
                                                                #step=None,
                                                                marks=None,
                                                                pushable=10,            # the sheared plane needs a range of values to be able to slice down to approx. 1 layer
                                                                updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-x", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)
                                    ], style={"margin-top": "7px"}),  # X-Axis
                                    dbc.Tooltip(id="x-lower-bound", target="range-slider-cs-x", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="x-higher-bound", target="range-slider-cs-x", trigger="hover focus", placement="right"),


                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-cs-y',
                                            disabled=True,
                                            pushable=0,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-y", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)
                                    ]),  # Y-Axis
                                    dbc.Tooltip(id="y-lower-bound", target="range-slider-cs-y", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="y-higher-bound", target="range-slider-cs-y", trigger="hover focus", placement="right"),

                                    dbc.Row([
                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-cs-z',
                                            disabled=True,
                                            pushable=0,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-cs-z", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em'}), width=1)

                                    ]),  # Z-Axis
                                    dbc.Tooltip(id="z-lower-bound", target="range-slider-cs-z", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="z-higher-bound", target="range-slider-cs-z", trigger="hover focus", placement="right"),

                                    dbc.Row([

                                        dbc.Col(dcc.RangeSlider(
                                            id='range-slider-dense',
                                            disabled=True,
                                            pushable=True,
                                            min=0, max=1,
                                            marks=None,
                                            updatemode='drag')),
                                        dbc.Col(html.Img(id="reset-dense", src="/assets/x.svg", n_clicks=0,
                                                         style={'width': '1.25em', 'position': 'float'}),
                                                width=1),

                                    ]),  # Density
                                    dbc.Tooltip(id="dense-lower-bound", target="range-slider-dense", trigger="hover focus", placement="left"),
                                    dbc.Tooltip(id="dense-higher-bound", target="range-slider-dense", trigger="hover focus", placement="right"),
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

]


    # Landing-cell
landing = html.Div([
    html.Div([html.H1(['      '.join('Welcome')], className='greetings'),
              html.H1(['      '.join('To')], className='greetings'),
              html.Img(src="./assets/logos/crop_mala_horizontal_white.png", style={'width': '30%', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
              ]),

], style={'width': 'content-min', 'margin-top': '20vh'})

