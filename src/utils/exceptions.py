from dash import dash


def upload_exception():
    """
    Exception giving return values for when the user uploads a file that is not supported by ASE.
    """
    return None, "File not supported", dash.no_update, dash.no_update, "session-failure"
