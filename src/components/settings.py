from dash import html, dcc
import dash_bootstrap_components as dbc

"""
Button for opening settings sidebar
"""
button = dbc.Button(
    "<",
    id="open-settings-button",
    style={
        "visibility": "hidden",
        "marginTop": "40vh",
        "position": "absolute",
        "right": "0",
    },
)

"""
Structure/Layout of the Settings sidebar
"""
sidebar = html.Div(
    [
        html.H5("Settings"),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Camera", style={"fontSize": "0.95em"}),
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                "Def.",
                                id="default-cam",
                                n_clicks=0,
                                style={"fontSize": "0.85em"},
                            ),
                            dbc.Button(
                                "X-Y",
                                id="x-y-cam",
                                n_clicks=0,
                                style={"fontSize": "0.85em"},
                            ),
                            dbc.Button(
                                "X-Z",
                                id="x-z-cam",
                                n_clicks=0,
                                style={"fontSize": "0.85em"},
                            ),
                            dbc.Button(
                                "Y-Z",
                                id="y-z-cam",
                                n_clicks=0,
                                style={"fontSize": "0.85em"},
                            ),
                        ],
                        vertical=True,
                        size="sm",
                    ),
                    html.Hr(),
                    dbc.Checkbox(
                        label="Outline",
                        value=True,
                        id="sc-outline",
                        style={"textAlign": "left", "fontSize": "0.85em"},
                    ),
                    dbc.Checkbox(
                        label="Atoms",
                        value=True,
                        id="sc-atoms",
                        style={"textAlign": "left", "fontSize": "0.85em"},
                    ),
                    dbc.Checkbox(
                        label="Cell",
                        value=True,
                        id="cell-boundaries",
                        style={"textAlign": "left", "fontSize": "0.85em"},
                    ),
                    html.Hr(),
                    html.H6("", id="sz/isosurf-label", style={"fontSize": "0.95em"}),
                    html.Div(
                        dcc.Slider(
                            4,
                            16,
                            2,
                            value=10,
                            id="sc-size",
                            vertical=True,
                            verticalHeight=150,
                        ),
                        style={"marginLeft": "1.2em"},
                    ),
                    html.Hr(),
                    html.H6("Opacity", id="opac-label", style={"fontSize": "0.95em"}),
                    dbc.Input(
                        type="number",
                        min=0.1,
                        max=1,
                        step=0.1,
                        id="sc-opac",
                        placeholder="0.1 - 1",
                        style={"width": "7em", "marginLeft": "1.5rem"},
                        size="sm",
                    ),
                ]
            )
        ),
    ],
    style={"textAlign": "center"},
)


"""
Inserting sidebar into Off-Canvas
"""
oc_sidebar = html.Div(
    [
        dbc.Offcanvas(
            sidebar,
            id="settings-offcanvas",
            is_open=False,
            style={
                "width": "9rem",
                "height": "min-content",
                "marginTop": "3em",
                "marginRight": "0",
                "borderTopLeftRadius": "5px",
                "borderBottomLeftRadius": "5px",
                "boxShadow": "rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px",
            },
            scrollable=True,
            backdrop=False,
            placement="end",
        ),
    ]
)
