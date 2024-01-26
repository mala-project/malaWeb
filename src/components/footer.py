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
                            style={"lineHeight": "0.65em", "fontSize": "0.65em"},
                        ),
                        id="open-footer",
                        style={
                            "width": "10em",
                            "height": "1.2em",
                            "position": "absolute",
                            "left": "50%",
                            "WebkitTransform": "translateX(-50%)",
                            "transform": "translateX(-50%)",
                            "bottom": "0.5em",
                        },
                        n_clicks=0,
                    ),
                    width=1,
                )
            )
        ],
        id="open-footer-canvas",
        style={
            "height": "min-content",
            "backgroundColor": "rgba(0, 0, 0, 0)",
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
            style={"textAlign": "center", "padding": 3, "fontSize": "0.85em"},
        )
    ],
    style={"fontWeight": "bold"},
)
row2 = html.Tr(
    [
        html.Td(
            0,
            id="bandEn",
            style={"textAlign": "right", "padding": 5, "fontSize": "0.85em"},
        )
    ]
)
row3 = html.Tr(
    [
        html.Td(
            "Total energy",
            style={"textAlign": "center", "padding": 3, "fontSize": "0.85em"},
        )
    ],
    style={"fontWeight": "bold"},
)
row4 = html.Tr(
    [
        html.Td(
            0,
            id="totalEn",
            style={"textAlign": "right", "padding": 5, "fontSize": "0.85em"},
        )
    ]
)
row5 = html.Tr(
    [
        html.Td(
            "Fermi energy",
            style={"textAlign": "center", "padding": 3, "fontSize": "0.85em"},
        )
    ],
    style={"fontWeight": "bold"},
)
row6 = html.Tr(
    [
        html.Td(
            "placeholder",
            id="fermiEn",
            style={"textAlign": "right", "padding": 5, "fontSize": "0.85em"},
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
                                        "fontSize": "0.85em",
                                        "fontWeight": "bold",
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
            id="footer",
            is_open=False,
            style={
                "height": "min-content",
                "width": "max-content",
                "borderRadius": "5px",
                "backgroundColor": "rgba(248, 249, 250, 1)",
                "left": "0",
                "right": "0",
                "margin": "auto",
                "bottom": "0.5em",
                "boxShadow": "rgba(0, 0, 0, 0.3) 0px 0px 16px -8px",
                "padding": -30,
            },
            scrollable=True,
            backdrop=False,
            placement="bottom",
        )
    ]
)
