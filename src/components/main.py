from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from src.components.tools import plot_tools


# for Plot
# Templates
# Scene-Template for Graph-Object (orientation)
orient_template = {
    "xaxis": {
        "showgrid": False,
        "showbackground": False,
        "linecolor": "red",
        "linewidth": 0,
        "ticks": "inside",
        "showticklabels": False,
        "visible": False,
        "title": "x",
    },
    "yaxis": {
        "showgrid": False,
        "showbackground": False,
        "linecolor": "green",
        "linewidth": 0,
        "ticks": "",
        "showticklabels": False,
        "visible": False,
        "title": "y",
    },
    "zaxis": {
        "showgrid": False,
        "showbackground": False,
        "linecolor": "blue",
        "linewidth": 0,
        "ticks": "",
        "showticklabels": False,
        "visible": False,
        "title": "z",
    },
    "bgcolor": "#f8f9fa",
}

# Properties for Plot layout
plot_layout = {
    "title": "Plot",
    "height": "75vh",
    "width": "80vw",
}
orientation_style = {
    "title": "x-y-z",
    "height": "3em",
    "width": "3em",
    "background": "#f8f9fa",
    "position": "fixed",
    "marginTop": "75vh",
    "marginRight": "0.5vw",
}

# Figs as prep for Plot
# Default fig for the main plot - gets overwritten on initial plot update, after that it gets patched on update
def_fig = go.Figure(go.Scatter3d(x=[1], y=[1], z=[1], showlegend=False))
def_fig.update_scenes(
    xaxis_visible=False,
    yaxis_visible=False,
    zaxis_visible=False,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    zaxis_showgrid=False,
)

orient_fig = go.Figure()
orient_fig.update_scenes(orient_template)
orient_fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0),
    title=dict(text="test"),
    clickmode="none",
    dragmode=False,
)
orient_fig.add_trace(
    go.Scatter3d(
        x=[0, 1],
        y=[0, 0],
        z=[0, 0],
        marker={"color": "red", "size": 0},
        line={"width": 6},
        showlegend=False,
        hoverinfo="skip",
    )
)
orient_fig.add_trace(
    go.Scatter3d(
        x=[0, 0],
        y=[0, 1],
        z=[0, 0],
        marker={"color": "green", "size": 0},
        line={"width": 6},
        showlegend=False,
        hoverinfo="skip",
    )
)
orient_fig.add_trace(
    go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0, 1],
        marker={"color": "blue", "size": 0},
        line={"width": 6},
        showlegend=False,
        hoverinfo="skip",
    )
)

# The actual Plot
"""
STORE Variable & Card for the main plot 
"""
plot = [
    dcc.Store(id="cam_store"),
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dcc.Graph(
                            id="orientation",
                            responsive=True,
                            figure=orient_fig,
                            style=orientation_style,
                            config={
                                "displayModeBar": False,
                                "displaylogo": False,
                                "showAxisDragHandles": True,
                            },
                        ),
                        dcc.Graph(
                            id="scatter-plot",
                            responsive=True,
                            figure=def_fig,
                            style=plot_layout,
                            config={"displaylogo": False},
                        ),
                    ]
                ),
                # Button for plot-tools
                dbc.Row(
                    [
                        html.Hr(),
                        dbc.Button(
                            html.P(
                                "Tools",
                                style={"lineHeight": "0.65em", "fontSize": "0.65em"},
                            ),
                            id="open-sc-tools",
                            style={"width": "5em", "height": "1.2em"},
                            n_clicks=0,
                        ),
                    ],
                    justify="center",
                    style={"textAlign": "center"},
                ),
                # Collapsable containing 4 Rangesliders
                dbc.Row(plot_tools, style={"marginTop": "1em"}),
            ]
        ),
        style={
            "backgroundColor": "rgba(248, 249, 250, 1)",
            "width": "min-content",
            "alignContent": "center",
            "marginTop": "1.5rem",
        },
    ),
]

"""
Content for landing-page
"""
landing = html.Div(
    [
        html.Div(
            [
                html.H1(["      ".join("Welcome")], className="greetings"),
                html.H1(["      ".join("To")], className="greetings"),
                html.Img(
                    src="./assets/logos/crop_mala_horizontal_white.png",
                    style={
                        "width": "30%",
                        "display": "block",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                ),
            ]
        ),
    ],
    style={"width": "content-min", "marginTop": "20vh"},
)
