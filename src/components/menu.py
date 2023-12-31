from dash import html, dcc
import dash_bootstrap_components as dbc

# I/O
import ase.io
import dash_uploader as du
import json

# CONSTANTS
# > "label" is the label visible in the apps dropdown ; "value"  is the value passed to the inference script. Ranges are to be surrounded by []
MODELS = json.load(open("../src/models/model_list.json"))
MODELS = [{'label': model['label'], 'value': model['value']} for model in MODELS]

# > Used for giving out high computation time warning
ATOM_LIMIT = 200

"""
Button for opening Upload Sidebar
"""


button = dbc.Button(
    ">",
    id="open-menu-button",
    n_clicks=0,
    style={"margin-top": "40vh", "position": "absolute", "left": "0"},
)


"""
Structure of Table showing uploaded atoms
"""
# List of ASE-atoms table
table_header = [
    html.Thead(
        html.Tr([html.Th("ID"), html.Th("X"), html.Th("Y"), html.Th("Z")]),
    )
]  # , html.Th("Use to run MALA")
table_body = [html.Tbody([], id="atoms_list")]
atoms_table = dbc.Table(table_header + table_body, bordered=True)

"""
Popup-Modal on accepted file-upload
(called in sidebar below)
"""
upload_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Your Upload")),
        dbc.ModalBody(
            [
                html.H6("The uploaded File contained the following atoms positions: "),
                html.Br(),
                dbc.Card(
                    html.H6(
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(width=1),
                                    dbc.Col("List of Atoms", width=10),
                                    dbc.Col("⌄", width=1, id="open-atom-list-arrow"),
                                ]
                            )
                        ],
                        style={"margin": "5px"},
                        id="open-atom-list",
                        n_clicks=0,
                    ),
                    style={"text-align": "center"},
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(  # Upload Section
                            [
                                atoms_table,
                                # html.P("Tick all the Atoms you want to use to send to MALA (Default: All checked).\nSee below for a pre-render of the chosen Atom-positions:"),
                            ]
                        )
                    ),
                    id="collapse-atom-list",
                    style={"max-height": "30rem"},
                    is_open=False,
                ),
                dcc.Graph(id="atoms-preview"),
                html.Hr(style={"margin-bottom": "1rem", "margin-top": "1rem"}),
                html.P("Choose the model that MALA should use for calculations"),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id="model-choice",
                                options=MODELS,
                                value=None,
                                placeholder="-",
                                optionHeight=45,
                                style={"font-size": "0.95em"},
                            ),
                            width=9,
                        ),
                        dbc.Col(
                            dbc.Input(
                                id="model-temp",
                                disabled=True,
                                type="number",
                                min=0,
                                max=10,
                                step=1,
                            ),
                            width=2,
                        ),
                        dbc.Col(html.P("K", style={"margin-top": "0.5rem"}), width=1),
                    ],
                    className="g-1",
                ),
                html.Br(),
                dbc.Alert(
                    id="atom-limit-warning",
                    children="The amount of Atoms you want to display exceeds our threshold ("
                    + str(ATOM_LIMIT)
                    + ") for short render times. Be aware that continuing with the uploaded data may negatively impact waiting times.",
                    color="warning",
                ),
                # only to be displayed if ATOM_LIMIT is exceeded (maybe as an alert window too)
            ]
        ),
        dbc.ModalFooter(
            dbc.Button(
                id="run-mala",
                style={"width": "min-content"},
                disabled=True,
                children=[
                    dbc.Stack(
                        [
                            html.Div(
                                dbc.Spinner([
                                    dcc.Store(id="df_store"),
                                    dcc.Store(id="client_df")],
                                    size="sm",
                                    color="success",  # Spinner awaits change here
                                ),
                                style={"width": "40px"},
                            ),
                            html.Div("Run MALA"),
                            html.Div(style={"width": "40px"}),
                        ],
                        direction="horizontal",
                    )
                ],
                color="success",
                outline=True,
            ),
            style={"justifyContent": "center"},
        ),
    ],
    id="upload-modal",
    size="lg",
    is_open=False,
)

"""
Structure/Layout of the Upload-sidebar
"""
sidebar = html.Div(
    [
        # Logo Section
        html.Div(
            [
                html.Img(src="./assets/logos/mala_vertical.png", className="logo"),
                html.Br(),
                html.Div(
                    children="""
                    Framework for machine learning materials properties from first-principles data.
                """,
                    style={"text-align": "center"},
                ),
            ],
            className="logo",
        ),
        html.Hr(style={"margin-bottom": "2rem", "margin-top": "1rem", "width": "5rem"}),
        dbc.Card(
            html.H6(
                children="File-Upload",
                style={"margin": "5px"},
                id="open-upload",
                n_clicks=0,
            ),
            style={"text-align": "center"},
        ),
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody(  # Upload Section
                    html.Div(
                        [
                            html.Div(
                                children="""
                            Upload atom-positions via file!
                            """,
                                style={"text-align": "center", "font-size": "0.85em"},
                            ),
                            html.Div(
                                children="""
                            Supported files
                            """,
                                id="supported-files",
                                style={
                                    "text-align": "center",
                                    "font-size": "0.6em",
                                    "text-decoration": "underline",
                                },
                            ),
                            html.Br(),
                            dbc.Popover(
                                dbc.PopoverBody(
                                    "ASE supports the following file-formats: "
                                    + str(ase.io.formats.ioformats.keys())[11:-2]
                                ),
                                style={"font-size": "0.6em"},
                                target="supported-files",
                                trigger="legacy",
                            ),
                            # dash-uploader component (not vanilla)
                            du.Upload(
                                id="upload-data", text="Drag & Drop or Click to select"
                            ),
                            # Can't manage to extract list of ASE-supported extensions from these IOFormats in:
                            # print(ase.io.formats.ioformats),
                            # -> TODO property "fileformat" could be used in du.Upload() to restrict uploadable extensions (safety-reasons for web-hosting)
                            html.Div(
                                "Awaiting upload..",
                                id="output-upload-state",
                                style={
                                    "margin": "2px",
                                    "font-size": "0.85em",
                                    "textAlign": "center",
                                },
                            ),
                            html.Hr(
                                style={
                                    "margin-bottom": "1rem",
                                    "margin-top": "1rem",
                                    "width": "5rem",
                                }
                            ),
                            dbc.Button(
                                "Edit",
                                id="edit-input",
                                color="success",
                                style={
                                    "lineHeight": "0.85em",
                                    "height": "min-content",
                                    "width": "100%",
                                    "font-size": "0.85em",
                                },
                            ),
                            dbc.Button(
                                "Reset",
                                id="reset-data",
                                color="danger",
                                style={
                                    "lineHeight": "0.85em",
                                    "height": "min-content",
                                    "width": "100%",
                                    "font-size": "0.85em",
                                },
                            ),
                        ],
                        className="upload-section",
                    ),
                )
            ),
            id="collapse-upload",
            is_open=True,
        ),
        upload_modal,
    ],
    className="sidebar",
)


"""
Inserting sidebar into off-canvas
"""
oc_sidebar = html.Div(
    [
        dbc.Offcanvas(
            sidebar,
            id="menu-offcanvas",
            is_open=True,
            scrollable=True,
            backdrop=False,
            style={
                "width": "12rem",
                "margin-top": "3rem",
                "left": "0",
                "borderTopRightRadius": "5px",
                "borderBottomRightRadius": "5px",
                "height": "min-content",
                "boxShadow": "rgba(50, 50, 93, 0.25) 0px 13px 27px -5px, rgba(0, 0, 0, 0.3) 0px 8px 16px -8px",
            },
        )
    ]
)
