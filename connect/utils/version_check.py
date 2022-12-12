import requests

import connect
from connect.utils import global_logger


def get_version():
    return connect.__version__


def validate_version():
    current_version = get_version()

    package = "credoai-connect"
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    latest_version = response.json()["info"]["version"]

    on_latest = current_version == latest_version

    if not on_latest:
        global_logger.warning(
            """
            You are using credoai-connect version %s, however a newer version is available.
            Lens is updated regularly with major improvements and bug fixes.
            Please upgrade via the command: "python -m pip install --upgrade credoai-connect"
            """,
            current_version,
        )
