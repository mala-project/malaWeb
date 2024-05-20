from dash.dependencies import Input, Output, State
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# from src.app import app


plot_tools = dbc.Collapse(
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        # Buttons
                        dbc.Col(
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "X",
                                        id="slice-x",
                                        active=False,
                                        outline=True,
                                        color="danger",
                                        n_clicks=0,
                                        style={"height": "2.7em"}
                                    ),
                                    dbc.Button(
                                        "Y",
                                        id="slice-y",
                                        active=False,
                                        outline=True,
                                        color="success",
                                        n_clicks=0,
                                        style={"height": "2.7em"}
                                    ),
                                    dbc.Button(
                                        "Z",
                                        id="slice-z",
                                        active=False,
                                        outline=True,
                                        color="primary",
                                        n_clicks=0,
                                        style={"height": "2.7em"}
                                    ),
                                    dbc.Button(
                                        "Density",
                                        id="filter-val",
                                        active=False,
                                        outline=True,
                                        color="dark",
                                        n_clicks=0,
                                        style={"height": "2.7em"}
                                    ),
                                ],
                                vertical=True,
                            ),
                            width=1,
                        ),
                        # Sliders
                        dbc.Col(
                            [
                                # TODO: Triggers need work
                                # TODO: rangesliders are only optimized with the example cell used in current models. Differently sheared planes will mess things up, as will cells with bigger datasets (minimum slice will grow/shrink)
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="slider-x",
                                                disabled=True,
                                                min=0,
                                                max=1,
                                                # step=None,
                                                marks=None,
                                                pushable=10,  # the sheared plane needs a range of values to be able to slice down to approx. 1 layer
                                                updatemode="drag",
                                            ), style={"marginTop": "0.25em"},
                                        ),
                                        dbc.Col(
                                            html.I(className="bi bi-x-lg", id="reset-slider-x"),
                                            width=1,
                                        ),
                                    ],
                                    style={"marginTop": "7px"},
                                ),  # X-Axis
                                dbc.Tooltip(
                                    id="x-min-indicator",
                                    target="slider-x",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="x-max-indicator",
                                    target="slider-x",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="slider-y",
                                                disabled=True,
                                                pushable=0,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            ), style={"marginTop": "0.25em"},
                                        ),
                                        dbc.Col(
                                            html.I(className="bi bi-x-lg", id="reset-slider-y"),
                                            width=1,
                                        ),
                                    ]
                                ),  # Y-Axis
                                dbc.Tooltip(
                                    id="y-lower-bound",
                                    target="slider-y",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="y-higher-bound",
                                    target="slider-y",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="slider-z",
                                                disabled=True,
                                                pushable=0,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            ), style={"marginTop": "0.25em"},
                                        ),
                                        dbc.Col(
                                            html.I(className="bi bi-x-lg", id="reset-slider-z"),
                                            width=1,
                                        ),
                                    ]
                                ),  # Z-Axis
                                dbc.Tooltip(
                                    id="z-lower-bound",
                                    target="slider-z",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="z-higher-bound",
                                    target="slider-z",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="slider-val",
                                                disabled=True,
                                                pushable=True,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            ), style={"marginTop": "0.25em"},
                                        ),
                                        dbc.Col(
                                            html.I(className="bi bi-x-lg", id="reset-slider-val"),
                                            width=1,
                                        ),
                                    ]
                                ),  # Density
                                dbc.Tooltip(
                                    id="dense-lower-bound",
                                    target="slider-val",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="dense-higher-bound",
                                    target="slider-val",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                            ],
                            width=11,
                        ),
                    ]
                ),
            ]
        )
    ),
    id="tools",
    is_open=False,
)
