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
                                        id="sc-active-x",
                                        active=False,
                                        outline=True,
                                        color="danger",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Y",
                                        id="sc-active-y",
                                        active=False,
                                        outline=True,
                                        color="success",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Z",
                                        id="sc-active-z",
                                        active=False,
                                        outline=True,
                                        color="primary",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Density",
                                        id="active-dense",
                                        active=False,
                                        outline=True,
                                        color="dark",
                                        n_clicks=0,
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
                                                id="range-slider-cs-x",
                                                disabled=True,
                                                min=0,
                                                max=1,
                                                # step=None,
                                                marks=None,
                                                pushable=10,  # the sheared plane needs a range of values to be able to slice down to approx. 1 layer
                                                updatemode="drag",
                                            )
                                        ),
                                        dbc.Col(
                                            html.Img(
                                                id="reset-cs-x",
                                                src="/assets/x.svg",
                                                n_clicks=0,
                                                style={"width": "1.25em"},
                                            ),
                                            width=1,
                                        ),
                                    ],
                                    style={"margin-top": "7px"},
                                ),  # X-Axis
                                dbc.Tooltip(
                                    id="x-lower-bound",
                                    target="range-slider-cs-x",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="x-higher-bound",
                                    target="range-slider-cs-x",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="range-slider-cs-y",
                                                disabled=True,
                                                pushable=0,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            )
                                        ),
                                        dbc.Col(
                                            html.Img(
                                                id="reset-cs-y",
                                                src="/assets/x.svg",
                                                n_clicks=0,
                                                style={"width": "1.25em"},
                                            ),
                                            width=1,
                                        ),
                                    ]
                                ),  # Y-Axis
                                dbc.Tooltip(
                                    id="y-lower-bound",
                                    target="range-slider-cs-y",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="y-higher-bound",
                                    target="range-slider-cs-y",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="range-slider-cs-z",
                                                disabled=True,
                                                pushable=0,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            )
                                        ),
                                        dbc.Col(
                                            html.Img(
                                                id="reset-cs-z",
                                                src="/assets/x.svg",
                                                n_clicks=0,
                                                style={"width": "1.25em"},
                                            ),
                                            width=1,
                                        ),
                                    ]
                                ),  # Z-Axis
                                dbc.Tooltip(
                                    id="z-lower-bound",
                                    target="range-slider-cs-z",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="z-higher-bound",
                                    target="range-slider-cs-z",
                                    trigger="hover focus",
                                    placement="right",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.RangeSlider(
                                                id="range-slider-dense",
                                                disabled=True,
                                                pushable=True,
                                                min=0,
                                                max=1,
                                                marks=None,
                                                updatemode="drag",
                                            )
                                        ),
                                        dbc.Col(
                                            html.Img(
                                                id="reset-dense",
                                                src="/assets/x.svg",
                                                n_clicks=0,
                                                style={
                                                    "width": "1.25em",
                                                    "position": "float",
                                                },
                                            ),
                                            width=1,
                                        ),
                                    ]
                                ),  # Density
                                dbc.Tooltip(
                                    id="dense-lower-bound",
                                    target="range-slider-dense",
                                    trigger="hover focus",
                                    placement="left",
                                ),
                                dbc.Tooltip(
                                    id="dense-higher-bound",
                                    target="range-slider-dense",
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
    id="sc-tools-collapse",
    is_open=False,
)
