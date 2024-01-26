# IMPORTS
import base64
import json
import os
from pathlib import Path
from timeit import default_timer as timer

import dash
import dash.exceptions
import dash_bootstrap_components as dbc
import flask

from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import Dash, dcc, html, Patch, clientside_callback
from dash.exceptions import PreventUpdate

# utils
from src.components import menu, settings, footer, main
from src.utils.exceptions import upload_exception
from src.utils.mala_inference import run_mala_prediction

# visualization
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

# I/O
import ase.io
import dash_uploader as du

# could be used to refactor callbacks into a seperate file callbacks.py
# from callbacks import get_callbacks


# CONSTANTS
ATOM_LIMIT = 200
# TODO implement caching of the dataset to improve performance
# as in: https://dash.plotly.com/performance

# TODO: implement patching so that figures are updated, not recreated
# as in: https://dash.plotly.com/partial-properties


# Scene-templates for PX-Objects (our 2 plots (1=main, 2=cell-preview))
templ1 = dict(
    layout=go.Layout(
        scene={
            "xaxis": {
                "showbackground": False,
                "visible": False,
            },
            "yaxis": {"showbackground": False, "visible": False},
            "zaxis": {"showbackground": False, "visible": False},
            "aspectmode": "data",
        },
        paper_bgcolor="#f8f9fa",
    )
)
templ2 = dict(
    layout=go.Layout(
        scene={
            "xaxis": {
                "showbackground": False,
                "visible": True,
            },
            "yaxis": {"showbackground": False, "visible": True},
            "zaxis": {"showbackground": False, "visible": True},
            "aspectmode": "data",
        },
        paper_bgcolor="#fff",
    )
)

# helper for removing unnecessary visuals on cell preview
removeHoverLines = go.layout.Scene(
    xaxis=go.layout.scene.XAxis(spikethickness=0),
    yaxis=go.layout.scene.YAxis(spikethickness=0),
    zaxis=go.layout.scene.ZAxis(spikethickness=0),
)

# shortcut for default marker-settings
default_scatter_marker = dict(
    marker=dict(size=12, opacity=1, line=dict(width=1, color="DarkSlateGrey")),
)

print(
    "_________________________________________________________________________________________"
)
print("STARTING UP...")

"""

"""
app = Dash(
    __name__,
    external_stylesheets=[dbc.icons.BOOTSTRAP, dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server
app.title = "MALAweb"

# Config of session folder
du.configure_upload(app, r"./session", http_request_handler=None)
# for publicly hosting this app, add http_request_handler=True and implement as in:
# https://github.com/np-8/dash-uploader/blob/dev/docs/dash-uploader.md


# ---------------------------------
# Plots for the created Figures

skel_layout = [
    dbc.Row(
        [
            dbc.Col(
                [
                    # Upload Sidebar Off-Canvas
                    menu.oc_sidebar,
                    menu.button,
                    # Bottom-Bar Off-Canvas
                    footer.oc_bar,
                    footer.button
                    # it doesn't matter where offcanvasses (oc) are placed here - only their "placement"-prop matters
                ],
                id="l0",
                width="auto",
            ),
            dbc.Col(main.landing, id="mc0", width="auto"),
            dbc.Col([settings.oc_sidebar, settings.button], id="r0", width="auto"),
        ],
        justify="center",
    )
]

# All the previously defined Components are not yet rendered in our app. They have to be inside app.layout
# app.layouts content gets updated, which makes our app reactive

p_layout_landing = dbc.Container(
    [
        dcc.Store(
            id="page_state", data="landing"
        ),  # determines what is rendered as main content (among other things?)
        dcc.Store(id="UP_STORE"),  # Info on uploaded file (path, ...)
        dcc.Store(id="BOUNDARIES_STORE"),  # Saving data for cell-boundaries
        dcc.Store(
            id="plot_settings"
        ),  # parameters of the righthand sidebar, used to update plot
        html.Div(skel_layout, id="content-layout"),
    ],
    fluid=True,
    style={"height": "100vh", "width": "100vw", "backgroundColor": "#023B59"},
)

app.layout = p_layout_landing

# CALLBACKS & FUNCTIONS


# RESET BUTTON
@app.callback(
    Output("page_state", "data", allow_duplicate=True),
    Output("df_store", "data", allow_duplicate=True),
    Output("settings-offcanvas", "is_open", allow_duplicate=True),
    Output("footer", "is_open", allow_duplicate=True),
    Output("UP_STORE", "data", allow_duplicate=True),
    Output("download-data", "disabled", allow_duplicate=True),
    Input("reset-data", "n_clicks"),
    prevent_initial_call=True,
)
def click_reset(click):
    """
    Resets the app to its initial state on reset button click (menu)
    """
    return "landing", None, False, False, None, True


# MENU COLLAPSABLE
@app.callback(
    Output("data-upload", "is_open"),
    Input("open-data-upload", "n_clicks"),
    Input("data-upload", "is_open"),
    prevent_initial_call=True,
)
def toggle_upload_section(n_header, is_open):
    """
    opens/collapses the upload section on menu
    """
    if n_header:
        return not is_open


# Collapsable in INFERENCE_MODAL
@app.callback(
    Output("collapse-atom-list", "is_open"),
    Output("open-atom-list-arrow", "children"),
    Input("open-atom-list", "n_clicks"),
    Input("collapse-atom-list", "is_open"),
    prevent_initial_call=True,
)
def toggle_uploaded_atoms(n_header, is_open):
    """
    opens/collapses the uploaded atoms list in inference-modal;
    turns arrow up/down accordingly
    """
    txt = "⌃"
    if n_header:
        if is_open:
            txt = "⌄"
        return not is_open, txt


# FOOTER
@app.callback(
    Output("open-footer-canvas", "is_open"),
    Input("page_state", "data"),
    State("footer", "is_open"),
    prevent_initial_call=True,
)
def toggle_footer_button(page_state, canv_open):
    """
    shows/hides the open-footer button (placed on offcanvas)
    BUG: button is hidden by ESC-key and unreachable
    """
    if page_state == "plotting":
        if not canv_open:
            return True

    else:
        return False


@app.callback(
    Output("footer", "is_open"),
    Input("open-footer", "n_clicks"),
    Input("page_state", "data"),
    prevent_initial_call=True,
)
def toggle_footer(open_cl, page_state):
    """
    shows/hides the footer (placed on offcanvas)
    """
    if page_state == "plotting":
        if dash.callback_context.triggered_id[0:4] == "open":
            return True
        else:
            return False
    else:
        return False


# PLOT
@dash.callback(
    Output("tools", "is_open"),
    Input("open-tools", "n_clicks"),
    State("tools", "is_open"),
    prevent_initial_call=True,
)
def toggle_tools(n_sc_s, is_open):
    """
    opens/collapses the tools section below plot
    """
    if n_sc_s:
        return not is_open


@app.callback(
    Output("slice-x", "active", allow_duplicate=True),
    Input("slice-x", "n_clicks"),
    State("slice-x", "active"),
    prevent_initial_call=True,
)
def toggle_slice_x(n_x, active):
    """
    visually enables/disables the x-slider-button on click
    """
    if n_x:
        return not active


# toggle slider x
@app.callback(
    Output("slider-x", "disabled", allow_duplicate=True),
    Input("slice-x", "active"),
    prevent_initial_call=True,
)
def toggle_x_slider(active):
    """
    enables/disables the x-slider on slice-x click
    """
    return not active


@app.callback(
    Output("slice-y", "active", allow_duplicate=True),
    Input("slice-y", "n_clicks"),
    State("slice-y", "active"),
    prevent_initial_call=True,
)
def toggle_slice_y(n_x, active):
    """
    visually enables/disables the y-slider-button
    """
    if n_x:
        return not active


@app.callback(
    Output("slider-y", "disabled", allow_duplicate=True),
    Input("slice-y", "active"),
    prevent_initial_call=True,
)
def toggle_y_slider(active):
    """
    enables/disables the y-slider on slice-y click
    """
    return not active


@app.callback(
    Output("slice-z", "active", allow_duplicate=True),
    Input("slice-z", "n_clicks"),
    State("slice-z", "active"),
    prevent_initial_call=True,
)
def toggle_slice_z(n_x, active):
    """
    visually enables/disables the z-slider-button
    """
    if n_x:
        return not active


@app.callback(
    Output("slider-z", "disabled", allow_duplicate=True),
    Input("slice-z", "active"),
    prevent_initial_call=True,
)
def toggle_z_slider(active):
    """
    enables/disables the z-slider on slice-z click
    """
    return not active


@app.callback(
    Output("filter-val", "active", allow_duplicate=True),
    Input("filter-val", "n_clicks"),
    State("filter-val", "active"),
    prevent_initial_call=True,
)
def toggle_slice_val(n_x, active):
    """
    visually enables/disables the val-slider-button
    """
    if n_x:
        return not active


@app.callback(
    Output("slider-val", "disabled", allow_duplicate=True),
    Input("filter-val", "active"),
    prevent_initial_call=True,
)
def toggle_val_slider(active):
    """
    enables/disables the val-slider on slice-val click
    """
    return not active


# TODO this can be included in tools_update
@app.callback(
    Output("slider-x", "value", allow_duplicate=True),
    Output("slider-y", "value", allow_duplicate=True,),
    Output("slider-z", "value", allow_duplicate=True,),
    Output("slider-val", "value", allow_duplicate=True,),
    Input("reset-slider-x", "n_clicks"),
    Input("reset-slider-y", "n_clicks"),
    Input("reset-slider-z", "n_clicks"),
    Input("reset-slider-val", "n_clicks"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def reset_sliders(n_clicks_x, n_clicks_y, n_clicks_z, n_clicks_dense, data):
    """
    resets the sliders to their initial state on reset-button click
    """
    df = pd.DataFrame(data["MALA_DF"]["scatter"])
    if dash.callback_context.triggered_id == "reset-slider-x":
        return (
            [0, len(np.unique(df["x"])) - 1],
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    elif dash.callback_context.triggered_id == "reset-slider-y":
        return (
            dash.no_update,
            [0, len(np.unique(df["y"])) - 1],
            dash.no_update,
            dash.no_update,
        )
    elif dash.callback_context.triggered_id == "reset-slider-z":
        return (
            dash.no_update,
            dash.no_update,
            [0, len(np.unique(df["z"])) - 1],
            dash.no_update,
        )
    elif dash.callback_context.triggered_id == "reset-slider-val":
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            [0, len(np.unique(df["val"])) - 1],
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("cam_store", "data", allow_duplicate=True),
    [
        Input("default-cam", "n_clicks"),
        Input("x-y-cam", "n_clicks"),
        Input("x-z-cam", "n_clicks"),
        Input("y-z-cam", "n_clicks"),
        Input("scatter-plot", "relayoutData"),
    ],
    prevent_initial_call=True,
)
def store_cam(default_clicks, x_y_clicks, x_z_clicks, y_z_clicks, user_in):
    # user_in is the camera position set by mouse movement, it has to be updated on every mouse input on the fig
    # set stored_cam_setting according to which button was last pressed
    """
    Changes camera position on button click (default, x-y, x-z, y-z);
    Stores camera position after mouse movement/input on plot
    """
    if dash.callback_context.triggered_id[0:-4] == "default":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1.5),
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-y":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=3.00),
        )
    elif dash.callback_context.triggered_id[0:-4] == "x-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=3.00, z=0),
        )
    elif dash.callback_context.triggered_id[0:-4] == "y-z":
        return dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=3.00, y=0, z=0),
        )
    # set to plot cam when user input is camera-movement:
    elif dash.callback_context.triggered_id == "scatter-plot":
        # stops the update in case the callback is triggered by zooming/initializing/smth else
        if user_in is None or "scene.camera" not in user_in.keys():
            raise PreventUpdate
        else:
            if "scene.camera" in user_in.keys():
                return user_in["scene.camera"]
        # stops the update in case the callback is triggered by zooming/smth else
    else:
        raise PreventUpdate

    # Feels very inelegant, but it works


# page state
# TODO this should be optimized to not transfer the all the data everytime
@app.callback(
    Output("page_state", "data"),
    Input("df_store", "data"),
    State("page_state", "data"),
    prevent_initial_call=True,
)
def update_page_state(trig1, state):
    """
    Updates the page-state (landing, plotting, inference) on df_store update
    """
    new_state = "landing"
    if dash.callback_context.triggered_id == "df_store":
        if trig1 is not None:
            new_state = "plotting"

    # prevent unnecessary updates
    if state == new_state:
        raise PreventUpdate
    else:
        return new_state


# DASH-UPLOADER
@du.callback(
    output=[
        Output("output-session-state", "children"),
        Output("UP_STORE", "data"),
        Output("atom-limit-warning", "is_open"),
        Output("atoms_list", "children"),
        Output("atoms-preview", "figure"),
        Output("session-data", "className"),
        Output("BOUNDARIES_STORE", "data"),
    ],
    id="session-data",
)
def upload_callback(status):  # <------- NEW: du.UploadStatus
    """
    Input
    :param status: All the info necessary to access (latest) uploaded files

    Output
    session-state: Upload-state below session-area;
    UP_STORE: dcc.Store-component, storing uploader-ID and path of uploaded file;
    atom-limit-warning: Boolean for displaying long-computation-time-warning;
    atoms_list: Table containing all atoms read by ASE;
    atoms-preview: Figure previewing ASE-read Atoms;
    session-data: Changing border-color of this component according to session-status;
    """
    UP_STORE = {
        "ID": status.upload_id,
        "PATH": str(status.latest_file.resolve()),
        "ATOMS": None,
    }
    LIMIT_EXCEEDED = False
    fig = px.scatter_3d()
    fig.update_layout(templ2["layout"])
    boundaries = []
    # ASE.reading to check for file-format support, to fill atoms_table, and to fill atoms-preview
    try:
        r_atoms = ase.io.read(status.latest_file)
        UPDATE_TEXT = "Upload successful"
        UP_STORE["ATOMS"] = r_atoms.todict()
        # delete uploaded file right after it's read by ASE - could be problematic, will see
        # TODO: delete session path either right here, or when session ends (how?)
        Path(str(status.latest_file.resolve())).unlink()

        if r_atoms.get_global_number_of_atoms() > ATOM_LIMIT:
            LIMIT_EXCEEDED = True
        table_rows = [
            html.Tr(
                [html.Td(atom.index), html.Td(atom.x), html.Td(atom.y), html.Td(atom.z)]
            )  # , html.Td("checkbox")
            for atom in r_atoms
        ]

        atoms_fig = go.Scatter3d(
            name="Atoms",
            x=[atom.x for atom in r_atoms],
            y=[atom.y for atom in r_atoms],
            z=[atom.z for atom in r_atoms],
            mode="markers",
            hovertemplate="X: %{x}</br></br>Y: %{y}</br>Z: %{z}<extra></extra>",
        )

        # Draw the outline of 4 planes and add them as individual traces
        # (2 / 6 Planes will be obvious by the 4 surrounding them)
        X_axis = r_atoms.cell[0]
        Y_axis = r_atoms.cell[1]
        Z_axis = r_atoms.cell[2]

        # Plane 1: X-Z-1
        x_points = [0, X_axis[0], X_axis[0] + Z_axis[0], Z_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1] + Z_axis[1], Z_axis[1], 0]
        z_points = [0, X_axis[2], X_axis[2] + Z_axis[2], Z_axis[2], 0]
        fig.add_trace(
            go.Scatter3d(
                x=x_points,
                y=y_points,
                z=z_points,
                hoverinfo="skip",
                mode="lines",
                marker={"color": "black"},
                name="Cell",
            )
        )
        boundary1 = go.Scatter3d(
            name="cell",
            x=x_points,
            y=y_points,
            z=z_points,
            hoverinfo="skip",
            mode="lines",
            marker={"color": "black"},
        )
        # Plane 2: X-Z-2
        x_points = [
            0 + Y_axis[0],
            X_axis[0] + Y_axis[0],
            X_axis[0] + Z_axis[0] + Y_axis[0],
            Z_axis[0] + Y_axis[0],
            0 + Y_axis[0],
        ]
        y_points = [
            0 + Y_axis[1],
            X_axis[1] + Y_axis[1],
            X_axis[1] + Z_axis[1] + Y_axis[1],
            Z_axis[1] + Y_axis[1],
            0 + Y_axis[1],
        ]
        z_points = [0, X_axis[2], X_axis[2] + Z_axis[2], Z_axis[2], 0]
        fig.add_trace(
            go.Scatter3d(
                x=x_points,
                y=y_points,
                z=z_points,
                hoverinfo="skip",
                mode="lines",
                marker={"color": "black"},
                showlegend=False,
            )
        )
        boundary2 = go.Scatter3d(
            name="cell",
            x=x_points,
            y=y_points,
            z=z_points,
            hoverinfo="skip",
            mode="lines",
            marker={"color": "black"},
            showlegend=False,
        )

        # Plane 3: X-Y-1
        x_points = [0, X_axis[0], X_axis[0] + Y_axis[0], Y_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1] + Y_axis[1], Y_axis[1], 0]
        z_points = [0, X_axis[2], X_axis[2] + Y_axis[2], Y_axis[2], 0]
        fig.add_trace(
            go.Scatter3d(
                x=x_points,
                y=y_points,
                z=z_points,
                hoverinfo="skip",
                mode="lines",
                marker={"color": "black"},
                showlegend=False,
            )
        )
        boundary3 = go.Scatter3d(
            name="cell",
            x=x_points,
            y=y_points,
            z=z_points,
            hoverinfo="skip",
            mode="lines",
            marker={"color": "black"},
            showlegend=False,
        )
        # Plane 4: X-Y-2
        x_points = [0, X_axis[0], X_axis[0] + Y_axis[0], Y_axis[0], 0]
        y_points = [0, X_axis[1], X_axis[1] + Y_axis[1], Y_axis[1], 0]
        z_points = [
            0 + Z_axis[2],
            X_axis[2] + Z_axis[2],
            X_axis[2] + Y_axis[2] + Z_axis[2],
            Y_axis[2] + Z_axis[2],
            0 + Z_axis[2],
        ]
        fig.add_trace(
            go.Scatter3d(
                x=x_points,
                y=y_points,
                z=z_points,
                hoverinfo="skip",
                mode="lines",
                marker={"color": "black"},
                showlegend=False,
            )
        )
        boundary4 = go.Scatter3d(
            name="cell",
            x=x_points,
            y=y_points,
            z=z_points,
            hoverinfo="skip",
            mode="lines",
            marker={"color": "black"},
            showlegend=False,
        )

        boundaries = [boundary1, boundary2, boundary3, boundary4]
        fig.update_scenes(removeHoverLines)
        fig.add_trace(atoms_fig)

        border_style = "session-success"

    # ValueError or File not sup. - exception for not supported formats (not yet filtered by session-component)
    except ValueError:
        r_atoms, UPDATE_TEXT, UP_STORE, table_rows, border_style = upload_exception()
    except ase.io.formats.UnknownFileTypeError:
        r_atoms, UPDATE_TEXT, UP_STORE, table_rows, border_style = upload_exception()
        # = FILE NOT SUPPORTED AS ASE INPUT
        # (some formats listed in supported-files for ase are output only. This will only be filtered here)

    return (
        UPDATE_TEXT,
        UP_STORE,
        LIMIT_EXCEEDED,
        table_rows,
        go.Figure(fig),
        border_style,
        boundaries,
    )


# END DASH UPLOADER

# IMPORT SETTINGS - DCC Uploader
@app.callback(
    Output("import-settings", "contents"),
    Output("show-outline", "value", allow_duplicate=True),
    Output("show-atoms", "value"),
    Output("show-cell", "value"),
    Output("particle-size", "value"),
    Output("opacity", "value"),

    Output("slider-val", "value"),
    Output("filter-val", "active"),
    Output("slider-x", "value"),
    Output("slice-x", "active"),
    Output("slider-y", "value"),
    Output("slice-y", "active"),
    Output("slider-z", "value"),
    Output("slice-z", "active"),

    Output("cam_store", "data"),
    Input("import-settings", "contents"),
    prevent_initial_call=True
)
def import_config(contents):
    """
    contents: base64 encoded string (JSON) that will be decoded, parsed and split up into returns for tools (multiple)
              and settings (one return to plot_settings)
    Changes to these Outputs will apply the imported settings to the plot automatically
    
    Returns:
    values to each component, either dash_no_update, or actual value parsed from input-data-JSON
    """
    if contents is None:
        raise PreventUpdate
    else:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        json_decoded = json.loads(decoded)

        if "tools" in json_decoded.keys():
            imported_tools = json_decoded["tools"]
            # split this up into multiple returns (2 for each slider =8 total)
        settings_to_parse = "settings" in json_decoded.keys()
        tools_to_parse = "tools" in json_decoded.keys()
        cam_to_parse = "cam" in json_decoded.keys()

        get_setting = lambda setting: json_decoded["settings"][setting] if settings_to_parse else dash.no_update
        get_tool = lambda tool: json_decoded["tools"][tool] if tools_to_parse else dash.no_update
        get_cam = lambda: json_decoded["cam"] if cam_to_parse else dash.no_update

        return (
            None,
            get_setting("outline"),
            get_setting("atoms"),
            get_setting("cell"),
            get_setting("size"),
            get_setting("opacity"),

            get_tool("val_val"),
            get_tool("val_act"),
            get_tool("x_val"),
            get_tool("x_act"),
            get_tool("y_val"),
            get_tool("y_act"),
            get_tool("z_val"),
            get_tool("z_act"),

            get_cam()
        )


# DATA DOWNLOAD CALLBACK
@app.callback(
    Output("data-downloader", "data"),
    Input("download-data", "n_clicks"),
    State("UP_STORE", "data"),
    prevent_initial_call=True
)
def download_data(click, up_data):
    """
    Send Download-prompt of MALA-data. The file was created on Inference, and is stored in the session-folder
    """
    try:
        return dcc.send_file(f"./session/{up_data['ID']}/inference_data.cube")
    except FileNotFoundError:
        print("File not found")
        raise PreventUpdate
    except TypeError:
        print("No file uploaded")
        raise PreventUpdate


@app.callback(
    Output("run-mala", "disabled", allow_duplicate=True),
    Input("run-mala", "n_clicks"),
    State("run-mala", "disabled"),
    Input("model-choice", "value"),
    Input("model-temp", "value"),
    prevent_initial_call=True,
)
def activate_run_mala_button(click, disabled, model, temp):
    """
    Enables the run-mala button, if a model and a temperature is selected
    TODO: Fix bug where button is disabled for the previously used model after (reset + ) upload of new data
    """
    if dash.callback_context.triggered_id == "run-mala" and disabled:
        raise PreventUpdate
    elif dash.callback_context.triggered_id == "run-mala":
        return True
    if model is not None and temp is not None:
        return False
    else:
        return True


@app.callback(
    Output("inference_modal", "is_open"),
    [
        Input("UP_STORE", "data"),
        Input("edit-input", "n_clicks"),
        Input("page_state", "data"),
        Input("df_store", "data"),
    ],
    prevent_initial_call=True,
)
def open_inference_modal(upload, edit_input, page_state, data):
    """
    Opens inference-modal on upload of Atoms, and/or on click of edit-input button.
    Closes inference-modal on click of "Start MALA" button (after inference and background updates)
    TODO: fix Bug where modal immediately closes after file-upload after reset(!)
    --> not happening if not resetting, but uploading new file
    """
    if (
            dash.callback_context.triggered_id == "page_state" and page_state == "plotting"
    ) or dash.callback_context.triggered_id == "df_store":
        return False
    elif (
            dash.callback_context.triggered_id == "UP_STORE"
            or dash.callback_context.triggered_id == "edit-input"
    ) and upload is not None:
        return True
    else:
        return False


@app.callback(
    Output("model-temp", "value"),
    Output("model-temp", "disabled"),
    Output("model-temp", "min"),
    Output("model-temp", "max"),
    Input("model-choice", "value"),
    prevent_initial_call=True,
)
def init_temp_choice(model_choice):
    """
    Initializes the temperature input depending on model-choice.
    If a temp-range is given by model-choice, the input is enabled and the range is set as min/max
    """
    if model_choice is None:
        raise PreventUpdate
    # splitting string input in substance and (possible) temperature(s)
    model, temp = model_choice.split("|")

    if "[" in temp:
        min_temp, max_temp = temp.split(",")
        min_temp = min_temp[1:]
        max_temp = max_temp[:-1]
        return min_temp, False, min_temp, max_temp

    else:
        return int(temp), True, None, None


# Trigger: button "run-mala", button "reset"
# (indirectly) Opens a popup, showing
#   - the uploaded Atoms with a checkmark;
#   - possibly giving a prerender of only the atoms;
#   - giving a warning if more than (ATOM_LIMIT) Atoms are selected
#   - has a "Start MALA" Button
# !!  THIS IS RUNNING MALA INFERENCE  !!
# AND "PARSING" DATA FOR CONTINUED USE


@app.callback(
    Output("df_store", "data"),
    Output("unique_df", "data"),
    Output("download-data", "disabled"),
    Input("run-mala", "n_clicks"),
    State("model-choice", "value"),
    State("model-temp", "value"),
    State("UP_STORE", "data"),
    prevent_initial_call=True,
)
def update_dataframes(trig, model_choice, temp_choice, upload):
    """
    Input
    :param trig: =INPUT - Pressing button "run-mala" triggers callback
    :param model_choice: =STATE - info on the cell-system (substance+temp(-range)), separated by |
    :param temp_choice: =STATE - chosen temperature - either defined by model-choice, or direct input inbetween range
    :param upload: =STATE - dict(session ID, filepath, ASE-Atoms-Obj as dict)

    :return: returns a dictionary with the data necessary to render to store-component

    Output
    df_store[data]... variable where we store the info necessary to render, so that we can use it in other callbacks

    NOW:
    read file from dict stored in UP_STORE['ATOMS']
    on MALA-call, give ATOMS-objs & model_choice
    -> returns density data and energy values +  a .cube-file
    """
    if upload is None:
        raise PreventUpdate
    model_temp_path = {"name": model_choice, "temperature": float(temp_choice)}

    # ASE.reading to receive ATOMS-objs, to pass to MALA-inference
    # no ValueError Exception needed, bc this is done directly on session
    read_atoms = ase.Atoms.fromdict(upload["ATOMS"])

    # (a) GET DATA FROM MALA (/ inference script)

    mala_data = run_mala_prediction(
        atoms_to_predict=read_atoms,
        model_and_temp=model_temp_path,
        session_id=upload["ID"],
    )
    # contains 'band_energy', 'total_energy', 'density', 'density_of_states', 'energy_grid'
    # mala_data is stored in df_store dict under key 'MALA_DATA'. (See declaration of df_store below for more info)
    density = mala_data["density"]

    coord_arr = np.column_stack(
        list(map(np.ravel, np.meshgrid(*map(np.arange, density.shape), indexing="ij")))
        + [density.ravel()]
    )
    data0 = pd.DataFrame(
        coord_arr, columns=["x", "y", "z", "val"]
    )  # untransformed Dataset

    atoms = [[], [], [], [], []]

    x_axis = [
        mala_data["grid_dimensions"][0],
        mala_data["voxel"][0][0],
        mala_data["voxel"][0][1],
        mala_data["voxel"][0][2],
    ]
    y_axis = [
        mala_data["grid_dimensions"][1],
        mala_data["voxel"][1][0],
        mala_data["voxel"][1][1],
        mala_data["voxel"][1][2],
    ]
    z_axis = [
        mala_data["grid_dimensions"][2],
        mala_data["voxel"][2][0],
        mala_data["voxel"][2][1],
        mala_data["voxel"][2][2],
    ]

    # READING ATOMPOSITIONS
    for i in range(0, len(read_atoms)):
        atoms[0].append(read_atoms[i].symbol)
        atoms[1].append(read_atoms[i].charge)
        atoms[2].append(read_atoms.get_positions()[i, 0])
        atoms[3].append(read_atoms.get_positions()[i, 1])
        atoms[4].append(read_atoms.get_positions()[i, 2])
    atoms_data = pd.DataFrame(
        data={
            "x": atoms[2],
            "y": atoms[3],
            "z": atoms[4],
            "ordinal": atoms[0],
            "charge": atoms[1],
        }
    )

    # SCALING AND SHEARING SCATTER DF
    # (b) SCALING to right voxel-size
    # need to bring atompositions and density-voxels to the same scaling
    data0["x"] *= x_axis[1]
    data0["y"] *= y_axis[2]
    data0["z"] *= z_axis[3]
    data_sc = data0.copy()

    # SHEARING für scatter_3d - linearcombination
    data_sc.x += y_axis[1] * (data0.y / y_axis[2])
    data_sc.x += z_axis[1] * (data0.z / z_axis[3])

    data_sc.y += x_axis[2] * (data0.x / x_axis[1])
    data_sc.y += z_axis[2] * (data0.z / z_axis[3])

    data_sc.z += y_axis[3] * (data0.y / y_axis[2])
    data_sc.z += x_axis[3] * (data0.x / x_axis[1])

    unique_df = {
        "x": data_sc.x.unique(),
        "y": data_sc.y.unique(),
        "z": data_sc.z.unique(),
        "val": np.unique(density),
    }

    """
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
    """

    # _______________________________________________________________________________________

    df_store = {
        "MALA_DF": {
            "default": data0.to_dict("records"),
            "scatter": data_sc.to_dict("records"),
        },
        "MALA_DATA": mala_data,
        "INPUT_DF": atoms_data.to_dict("records"),
        "SCALE": {"x_axis": x_axis, "y_axis": y_axis, "z_axis": z_axis},
    }
    return df_store, unique_df, False


# SETTINGS STORING
@app.callback(
    Output("plot_settings", "data"),
    Output("show-outline", "value"),
    Input("particle-size", "value"),
    Input("show-outline", "value"),
    Input("show-atoms", "value"),
    Input("opacity", "value"),
    Input("show-cell", "value"),
)
def update_settings_store(size, outline, atoms, opacity, cell):
    """
    Parameters
    ----------
    size
    outline
    atoms
    opacity
    cell

    Returns
    -------
    dict of settings-values
    bool for enabling/disabling Outline checkbox

    -------
    One change in the settings updates all settings in config

    """
    # On initial CB (default settings)
    if dash.callback_context.triggered_id is None:
        # default settings
        plot_settings = {
            "size": 10,  # particle size
            "opacity": 1,  # particle opacity
            "outline": dict(width=1, color="DarkSlateGrey"),  # particle outline
            "atoms": True,
            "cell": 5,  # cell boundaries (width)
        }
        return plot_settings, True

    else:
        settings_patch = Patch()
        if outline:
            settings_patch["outline"] = dict(width=1, color="DarkSlateGrey")
        else:
            settings_patch["outline"] = dict(width=0, color="DarkSlateGrey")
        settings_patch["atoms"] = atoms
        if cell:
            settings_patch["cell"] = 5
        else:
            settings_patch["cell"] = 0.01
            # for disabling cell-boundaries, we just draw them thinly
        settings_patch["size"] = size
        settings_patch["opacity"] = opacity
        if opacity is not None:
            if opacity < 1:
                outline = False
                settings_patch["outline"] = dict(width=0, color="DarkSlateGrey")
        return settings_patch, outline


# EXPORT SETTINGS
# TODO: include CAM-data
@app.callback(
    Output("settings-downloader", "data"),
    Input("export-settings", "n_clicks"),

    State("show-outline", "value"),
    State("show-atoms", "value"),
    State("show-cell", "value"),
    State("particle-size", "value"),
    State("opacity", "value"),

    State("slider-val", "value"),
    State("filter-val", "active"),
    State("slider-x", "value"),
    State("slice-x", "active"),
    State("slider-y", "value"),
    State("slice-y", "active"),
    State("slider-z", "value"),
    State("slice-z", "active"),
    State("UP_STORE", "data"),

    State("cam_store", "data"),
    prevent_initial_call=True
)
def export_settings(click, show_outline, show_atoms, show_cell, particle_size, opacity, val_val, val_act, x_val, x_act,
                    y_val, y_act, z_val, z_act, up_store, cam_store):
    """
    Takes values of all configurations (settings, tools, cam) and stores them in a JSON-file, which is then sent to user
    ----------
    Parameters
    ----------
    click: Int (number of button presses)
    show_outline: Boolean
    show_atoms: Boolean
    show_cell: Boolean
    particle_size: Int
    opacity: Float between 0.1 and 1.0
    val_val: Float
    val_act: Float
    x_val: Float
    x_act: Float
    y_val: Float
    y_act: Float
    z_val: Float
    z_act: Float
    up_store: dict
    cam_store: dict

    Returns
    -------
    File-Download
    """
    # TODO could use better type/null checks
    if type(up_store["ID"]) is not str:
        raise PreventUpdate
    else:
        session_id = up_store['ID']
        session_path = f"session/{session_id}".format(session_id=session_id)
        # parse settings-file
        config = {
            'settings': {
                'outline': show_outline,
                'atoms': show_atoms,
                'cell': show_cell,
                'size': particle_size,
                'opacity': opacity
            },
            'tools': {
                'val_val': val_val,
                'val_act': val_act,
                'x_val': x_val,
                'x_act': x_act,
                'y_val': y_val,
                'y_act': y_act,
                'z_val': z_val,
                'z_act': z_act,
            },
            'cam': cam_store
        }
        with open(Path(session_path + "/settings.json"), "w") as f:
            json.dump(config, f)
        return dcc.send_file(path=Path(session_path + "/settings.json"), filename="settings.json")


@app.callback(
    [
        Output("slider-x", "min"),
        Output("slider-x", "max"),
        Output("slider-x", "step"),
        Output("slider-y", "min"),
        Output("slider-y", "max"),
        Output("slider-y", "step"),
        Output("slider-z", "min"),
        Output("slider-z", "max"),
        Output("slider-z", "step"),
        Output("slider-val", "min"),
        Output("slider-val", "max"),
        Output("slider-val", "step"),
    ],
    [
        Input("unique_df", "data"),
        Input("import-settings", "last_modified"),
    ],
)
def update_tools(data, config_imported):
    """
    Updates the slider-ranges according to the imported config or the data uploaded by the user
    TODO: Check if imported tool-config is compatible with uploaded data
    """
    if data is None:  # in case of reset:
        raise PreventUpdate
    else:
        return (
            0,
            len(data["x"]) - 1,
            1,
            0,
            len(data["y"]) - 1,
            1,
            0,
            len(data["z"]) - 1,
            1,
            0,
            len(data["val"]) - 1,
            1,
        )


@app.callback(
    Output("x-min-indicator", "children"),
    Output("x-max-indicator", "children"),
    Input("slider-x", "value"),
    State("unique_df", "data"),
)
def update_indicators_x(value, unique_data):
    """
    Updates the slider-range indicators for slider-x
    """
    if unique_data is None:  # in case of reset:
        raise PreventUpdate

    u_data = np.array(unique_data["x"])

    if value is None:
        min_val = round(min(u_data), ndigits=5)
        max_val = round(max(u_data), ndigits=5)
    else:
        min_v, max_v = value
        min_val = round(u_data[min_v], ndigits=5)
        max_val = round(u_data[max_v], ndigits=5)
    return min_val, max_val


@app.callback(
    Output("y-lower-bound", "children"),
    Output("y-higher-bound", "children"),
    Input("slider-y", "value"),
    State("unique_df", "data"),
)
def update_indicators_y(value, unique_data):
    """
    Updates the slider-range indicators for slider-y
    """
    if unique_data is None:  # in case of reset:
        raise PreventUpdate

    u_data = np.array(unique_data["y"])

    if value is None:
        min_val = round(min(u_data), ndigits=5)
        max_val = round(max(u_data), ndigits=5)
    else:
        min_v, max_v = value
        min_val = round(u_data[min_v], ndigits=5)
        max_val = round(u_data[max_v], ndigits=5)
    return min_val, max_val


@app.callback(
    Output("z-lower-bound", "children"),
    Output("z-higher-bound", "children"),
    Input("slider-z", "value"),
    State("unique_df", "data"),
)
def update_indicators_z(value, unique_data):
    """
    Updates the slider-range indicators for slider-z
    """
    if unique_data is None:  # in case of reset:
        raise PreventUpdate

    u_data = np.array(unique_data["z"])

    if value is None:
        min_val = round(min(u_data), ndigits=5)
        max_val = round(max(u_data), ndigits=5)
    else:
        min_v, max_v = value
        min_val = round(u_data[min_v], ndigits=5)
        max_val = round(u_data[max_v], ndigits=5)
    return min_val, max_val


@app.callback(
    Output("dense-lower-bound", "children"),
    Output("dense-higher-bound", "children"),
    Input("slider-val", "value"),
    State("unique_df", "data"),
)
def update_indicators_dense(value, unique_data):
    """
    Updates the slider-range indicators for slider-val
    """
    if unique_data is None:  # in case of reset:
        raise PreventUpdate

    u_data = np.array(unique_data["val"])

    if value is None:
        min_val = round(min(u_data), ndigits=5)
        max_val = round(max(u_data), ndigits=5)
    else:
        min_v, max_v = value
        min_val = round(u_data[min_v], ndigits=5)
        max_val = round(u_data[max_v], ndigits=5)
    return min_val, max_val


# LAYOUT CALLBACKS
# UPDATING CONTENT-CELL 0


@app.callback(
    Output("mc0", "children"),
    Input("page_state", "data"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def update_main_content(state, data):
    """
    Updates the content of the main-content cell 0
    """
    if data is None or state == "landing":
        return main.landing

    elif state == "plotting":
        return main.plot


@app.callback(
    Output("scatter-plot", "figure", allow_duplicate=True),
    [
        # Settings
        Input("plot_settings", "data"),
        Input("default-cam", "n_clicks"),
        Input("x-y-cam", "n_clicks"),
        Input("x-z-cam", "n_clicks"),
        Input("y-z-cam", "n_clicks"),
        State("cam_store", "data"),
        Input("df_store", "data"),
        State("scatter-plot", "figure"),
        State("BOUNDARIES_STORE", "data"),
    ],
    prevent_initial_call="initial_duplicate",
)
def update_plot(
        settings,
        cam_default,
        cam_xy,
        cam_xz,
        cam_yz,
        stored_cam_settings,
        f_data,
        fig,
        boundaries_fig,
):
    """
    Updates the scatter-plot
    - cam-position buttons have to stay as Inputs, so they trigger an update.
    - cam_store can't be an Input or else it triggers an update everytime the cam is moved by user
    - cam_store is needed, so that the cam-position is not reset on f.e. update by settings
    """
    # TODO: make this function more efficient
    print("PLOT UPDATE", dash.callback_context.triggered_id)
    patched_fig = Patch()

    # DATA
    # the density-Dataframe that we're updating, taken from df_store (=f_data)
    if f_data is None:
        raise PreventUpdate

    # Last Camera-Pos
    new_cam = stored_cam_settings

    # INIT PLOT
    if dash.callback_context.triggered[0]["prop_id"] == "." or dash.callback_context.triggered_id == "df_store":
        """
        INIT PLOT
        Create a Figure that overwrites the default figure (a single blue dot)
        This is only run on the initial call of this callback (id ".")
        All following operations are optional and only triggered if their parameters change (they are trigger of this CB)
        They do not overwrite the figure, but patch their respective parameters of the initialised figure
        -> better performance
        """
        print("INIT Plot")
        # Our main figure = scatter plot

        df = pd.DataFrame(f_data["MALA_DF"]["scatter"])
        # sheared coordinates

        # atoms-Dataframe also taken from f_data
        atoms = pd.DataFrame(f_data["INPUT_DF"])
        no_of_atoms = len(atoms)

        # Cell
        fig_bound = boundaries_fig

        patched_fig = px.scatter_3d(
            df,
            x="x",
            y="y",
            z="z",
            color="val",
            hover_data=["val"],
            color_continuous_scale=px.colors.sequential.Inferno_r,
            range_color=[min(df["val"]), max(df["val"])],
        )
        patched_fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            paper_bgcolor="#f8f9fa",
            showlegend=False,
            modebar_remove=["zoom", "resetcameradefault", "resetcameralastsave"],
            template=templ1,
        )

        patched_fig.update_coloraxes(
            colorbar={"thickness": 10, "title": "", "len": 0.9}
        )
        patched_fig.update_traces(
            patch={"marker": {"size": settings["size"], "line": settings["outline"]}}
        )

        # adding helper-figure to keep camera-zoom the same, regardless of data(-slicing)-changes
        # equals the cell boundaries, but has slight offset to the main plot (due to not voxels, but ertices being scatter plotted)
        for i in fig_bound:
            patched_fig.add_trace(i)
        patched_fig.update_traces(
            patch={"line": {"width": settings["cell"]}}, selector=dict(name="cell")
        )
        patched_fig.update_scenes(removeHoverLines)

        atom_colors = []
        for i in range(0, int(no_of_atoms)):
            atom_colors.append("green")
        patched_fig.add_trace(
            go.Scatter3d(
                name="Atoms",
                x=atoms["x"],
                y=atoms["y"],
                z=atoms["z"],
                mode="markers",
                marker=dict(
                    size=10,
                    color=atom_colors,
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
            )
        )

    # SETTINGS
    elif dash.callback_context.triggered_id == "plot_settings":
        """
        SETTINGS
        Set:
            outline (width), 
            size (in px), opacity (0.1 - 1), 
            visibility of cell boundaries (width 1 / 0) and 
            visibility of atoms
        """
        print("PLOT-Settings")
        patched_fig["data"][0]["marker"]["line"] = settings["outline"]
        patched_fig["data"][0]["marker"]["size"] = settings["size"]
        patched_fig["data"][0]["marker"]["opacity"] = settings["opacity"]
        for i in [1, 2, 3, 4]:
            patched_fig["data"][i]["line"]["width"] = settings["cell"]
        patched_fig["data"][5]["visible"] = settings["atoms"]

        patched_fig["layout"]["scene"]["camera"] = new_cam

    # CAMERA

    elif "cam" in dash.callback_context.triggered_id:
        print("PLOT-Cam")
        """
        CAMERA
            set camera-position according to the clicked button, 
                                        OR 
                        - if no button has been clicked - 
            to the most recently stored manually adjusted camera position
        """
        if dash.callback_context.triggered_id == "default-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5),
            )
        elif dash.callback_context.triggered_id == "x-y-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=0, z=3.00),
            )
        elif dash.callback_context.triggered_id == "x-z-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0, y=3.00, z=0),
            )
        elif dash.callback_context.triggered_id == "y-z-cam":
            new_cam = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=3.00, y=0, z=0),
            )
        patched_fig["layout"]["scene"]["camera"] = new_cam
    return patched_fig


# TODO optimize by using relayout to update camera instead of cam_store (or smth else entirely)
@app.callback(
    Output("scatter-plot", "figure"),
    # Tools
    Input("slider-val", "value"),
    Input("filter-val", "active"),
    Input("slider-x", "value"),
    Input("slice-x", "active"),
    Input("slider-y", "value"),
    Input("slice-y", "active"),
    Input("slider-z", "value"),
    Input("slice-z", "active"),
    # Data
    State("df_store", "data"),
    State("cam_store", "data"),
    prevent_initial_call=True,
)
def slice_plot(
    slider_range,
    dense_inactive,
    slider_range_cs_x,
    cs_x_inactive,
    slider_range_cs_y,
    cs_y_inactive,
    slider_range_cs_z,
    cs_z_inactive,
    f_data,
    cam,
):
    """
    Updates the scatter-plot according to the tools by filtering the data
    TODO: Try doing this Clientside for performance improvements
    """
    if f_data is None:
        raise PreventUpdate
    df = pd.DataFrame(f_data["MALA_DF"]["scatter"])
    dfu = (
        df.copy()
    )  # this is a subset of df after one if-case is run. For every if-case, we need the subset+the original

    # TOOLS
    # filter-by-density
    if slider_range is not None and dense_inactive:  # Any slider Input there? Do:
        low, high = slider_range
        mask = (dfu["val"] >= np.unique(df["val"])[low]) & (
                dfu["val"] <= np.unique(df["val"])[high]
        )
        dfu = dfu[mask]

    # slice X
    if slider_range_cs_x is not None and cs_x_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_x
        mask = (dfu["x"] >= np.unique(df["x"])[low]) & (
                dfu["x"] <= np.unique(df["x"])[high]
        )
        dfu = dfu[mask]

    # slice Y
    if slider_range_cs_y is not None and cs_y_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_y
        mask = (dfu["y"] >= np.unique(df["y"])[low]) & (
                dfu["y"] <= np.unique(df["y"])[high]
        )
        dfu = dfu[mask]

    # slice Z
    if slider_range_cs_z is not None and cs_z_inactive:  # Any slider Input there? Do:
        low, high = slider_range_cs_z
        mask = (dfu["z"] >= np.unique(df["z"])[low]) & (
                dfu["z"] <= np.unique(df["z"])[high]
        )
        dfu = dfu[mask]

    patched_fig = Patch()
    patched_fig["data"][0]["x"] = dfu["x"]
    patched_fig["data"][0]["y"] = dfu["y"]
    patched_fig["data"][0]["z"] = dfu["z"]
    patched_fig["data"][0]["marker"]["color"] = dfu["val"]
    # sadly the patch overwrites our cam positioning, which is why we have to re-patch it everytime
    patched_fig["layout"]["scene"]["camera"] = cam
    return patched_fig


@app.callback(
    Output("orientation", "figure"),
    Input("cam_store", "data"),
    prevent_initial_call=True,
)
def update_orientation(saved):
    """
    Updates the orientation-figure
    """
    eye = saved["eye"]
    # TODO make zoom-level static

    # Patching is definetly slower here! Tested!
    fig_upd = main.orient_fig
    fig_upd.update_scenes(camera={"eye": eye})
    return fig_upd


# TODO this can be optimized by patching
@app.callback(
    Output("dos-plot", "figure"),
    Output("bandEn", "children"),
    Output("totalEn", "children"),
    Output("fermiEn", "children"),
    [Input("df_store", "data"), Input("page_state", "data")],
    prevent_initial_call=True,
)
def update_footer(f_data, state):
    """
    Updates the footer content: Energy-table and DOS-plot
    """
    if state == "landing":
        raise PreventUpdate

    if f_data is not None:
        # PLOT data
        dOs = f_data["MALA_DATA"]["density_of_states"]
        df = pd.DataFrame(dOs)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[0],
                name="densityOfstate",
                line=dict(color="#f15e64", width=2, dash="dot"),
            )
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            modebar_remove=[
                "zoom2d",
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
            ],
            paper_bgcolor="#f8f9fa",
            plot_bgcolor="#f8f9fa",
            xaxis={"gridcolor": "#D3D3D3", "dtick": 1, "linecolor": "black"},
            yaxis={"gridcolor": "#D3D3D3", "linecolor": "black"},
        )

        # TABLE data
        band_en = f_data["MALA_DATA"]["band_energy"]
        total_en = f_data["MALA_DATA"]["total_energy"]
        fermi_en = f_data["MALA_DATA"]["fermi_energy"]

    else:
        # Defaults in case of reset or data missing for some reaso
        fig = px.scatter()
        band_en = "-"
        total_en = "-"
        fermi_en = "-"

    return fig, band_en, total_en, fermi_en


@app.callback(
    Output("settings-offcanvas", "is_open"),
    Input("page_state", "data"),
    Input("open-settings-button", "n_clicks"),
    [State("settings-offcanvas", "is_open")],
    prevent_initial_call=True,
)
def toggle_settings_bar(page_state, n1, is_open):
    """
    Opens the settings-offcanvas on click of open-settings-button
    """
    if dash.callback_context.triggered_id == "page_state" and page_state == "plotting":
        return True
    elif dash.callback_context.triggered_id[0:4] == "open":
        return not is_open
    else:
        return is_open


@app.callback(
    Output("open-settings-button", "style"),
    Input("page_state", "data"),
    prevent_initial_call=True,
)
def toggle_settings_button(state):
    """
    Toggles the visibility of the settings-button depending on page-state
    """
    if state == "plotting":
        return {
            "visibility": "visible",
            "marginTop": "40vh",
            "position": "absolute",
            "right": "0",
        }
    else:
        return {
            "visibility": "hidden",
        }


@app.callback(
    Output("menu-offcanvas", "is_open"),
    Input("open-menu-button", "n_clicks"),
    prevent_initial_call=True,
)
def open_menu(open_menu_click):
    return True


# END OF CALLBACKS FOR SIDEBAR

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8050")
