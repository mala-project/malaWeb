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
        # TODO BUG dcc.Upload causes horizontal scrollbar in settings-sidebar
        dbc.Button(dcc.Upload(
            html.I(className="bi bi-upload", children="  Import"),
            id="import-settings",
            multiple=False,
            accept=".json",
            style={
                "lineHeight": "0.85em",
                "fontSize": "0.85em",
                "width": "fit-content"
            }),
            color="info"),

        html.Hr(),
        html.H6("Camera", style={"fontSize": "0.95em"}),
        dbc.ButtonGroup([
            dbc.ButtonGroup([
                dbc.Button(
                    "DEF.",
                    id="default-cam",
                    n_clicks=0,
                    style={"fontSize": "0.85em"},
                    color="info"
                ),
                dbc.Button(
                    "X-Y",
                    id="x-y-cam",
                    n_clicks=0,
                    style={"fontSize": "0.85em"},
                    color="info"
                ),
            ]),
            dbc.ButtonGroup([
                dbc.Button(
                    "X-Z",
                    id="x-z-cam",
                    n_clicks=0,
                    style={"fontSize": "0.85em"},
                    color="info"
                ),
                dbc.Button(
                    "Y-Z",
                    id="y-z-cam",
                    n_clicks=0,
                    style={"fontSize": "0.85em"},
                    color="info"
                ),
            ]),
        ], vertical=True, size="sm"),

        html.Hr(),
        html.H6("Visibility", style={"fontSize": "0.95em"}),
        dbc.Switch(
            label="Outline",
            value=True,
            id="show-outline",
            style={"textAlign": "left", "fontSize": "0.85em"},
        ),
        dbc.Switch(
            label="Atoms",
            value=True,
            id="show-atoms",
            style={"textAlign": "left", "fontSize": "0.85em"},
        ),
        dbc.Switch(
            label="Cell",
            value=True,
            id="show-cell",
            style={"textAlign": "left", "fontSize": "0.85em"},
        ),
        html.Hr(),
        html.H6("Size", id="sz/isosurf-label", style={"fontSize": "0.95em"}),
        html.Div(
            dcc.Slider(
                6,
                20,
                2,
                value=10,
                id="particle-size",
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
            value=1,
            id="opacity",
            placeholder="0.1 - 1",
            size="sm",
        ),

        html.Hr(),
        # TODO: put inside collapsable card

        dbc.Button(
            html.I(
                "  Export",
                className="bi bi-download"),
            id="export-settings",
            color="info",
            style={
                "lineHeight": "0.85em",
                "fontSize": "0.85em",
            },
            disabled=False,
        ),
        dcc.Download(id="settings-downloader"),

    ], style={"textAlign": "center", "alignContent": "center"},
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
            scrollable=True,
            backdrop=False,
            placement="end",
            style={
                "width": "min-content",
                "height": "min-content",
                "marginTop": "3em",
                "borderTopLeftRadius": "5px",
                "borderBottomLeftRadius": "5px",
                "boxShadow": "rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px",
            },
        ),
    ]
)
