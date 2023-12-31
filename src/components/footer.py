from dash import html, dcc
import dash_bootstrap_components as dbc

"""
Everything to do with the bottom-side off-canvas, displaying a table of Energies and DoS-Plot
"""
"""
Button for opening Footer / Bottom bar
"""
button = html.Div(
    dbc.Offcanvas(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        html.P(
                            "Energy / Density of State",
                            style={"line-height": "0.65em", "font-size": "0.65em"},
                        ),
                        id="open-bot",
                        style={
                            "width": "10em",
                            "height": "1.2em",
                            "position": "absolute",
                            "left": "50%",
                            "-webkit-transform": "translateX(-50%)",
                            "transform": "translateX(-50%)",
                            "bottom": "0.5em",
                        },
                        n_clicks=0,
                    ),
                    width=1,
                )
            )
        ],
        id="open-bot-canv",
        style={
            "height": "min-content",
            "background-color": "rgba(0, 0, 0, 0)",
            "border": "0",
        },
        is_open=False,
        scrollable=True,
        backdrop=False,
        close_button=False,
        placement="bottom",
    )
)

"""
Energy Table
"""
row1 = html.Tr(
    [
        html.Td(
            "Band energy",
            style={"text-align": "center", "padding": 3, "font-size": "0.85em"},
        )
    ],
    style={"fontWeight": "bold"},
)
row2 = html.Tr(
    [
        html.Td(
            0,
            id="bandEn",
            style={"text-align": "right", "padding": 5, "font-size": "0.85em"},
        )
    ]
)
row3 = html.Tr(
    [
        html.Td(
            "Total energy",
            style={"text-align": "center", "padding": 3, "font-size": "0.85em"},
        )
    ],
    style={"font-weight": "bold"},
)
row4 = html.Tr(
    [
        html.Td(
            0,
            id="totalEn",
            style={"text-align": "right", "padding": 5, "font-size": "0.85em"},
        )
    ]
)
row5 = html.Tr(
    [
        html.Td(
            "Fermi energy",
            style={"text-align": "center", "padding": 3, "font-size": "0.85em"},
        )
    ],
    style={"font-weight": "bold"},
)
row6 = html.Tr(
    [
        html.Td(
            "placeholder",
            id="fermiEn",
            style={"text-align": "right", "padding": 5, "font-size": "0.85em"},
        )
    ]
)
table_body = [html.Tbody([row1, row2, row3, row4, row5, row6])]

table = dbc.Table(
    table_body, bordered=True, striped=True, style={"padding": 0, "margin": 0}
)

"""
Structuring bottom bar content
"""
bar = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody(table)), width="auto"),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Density of State",
                                    style={
                                        "font-size": "0.85em",
                                        "font-weight": "bold",
                                    },
                                ),
                                dcc.Graph(
                                    id="dos-plot",
                                    style={
                                        "width": "20vh",
                                        "height": "10vh",
                                        "background": "#f8f9fa",
                                    },
                                    config={"displaylogo": False},
                                ),
                            ]
                        )
                    ),
                    width="auto",
                    align="center",
                ),
            ],
            style={"height": "min-content", "padding": 0},
            justify="center",
        )
    ]
)


"""
Inserting bottom bar content into Off-Canvas
"""
oc_bar = html.Div(
    [
        dbc.Offcanvas(
            bar,
            id="offcanvas-bot",
            is_open=False,
            style={
                "height": "min-content",
                "width": "max-content",
                "borderRadius": "5px",
                "background-color": "rgba(248, 249, 250, 1)",
                "left": "0",
                "right": "0",
                "margin": "auto",
                "bottom": "0.5em",
                "box-shadow": "rgba(0, 0, 0, 0.3) 0px 0px 16px -8px",
                "padding": -30,
            },
            scrollable=True,
            backdrop=False,
            placement="bottom",
        )
    ]
)
