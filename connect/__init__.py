"""
Credo AI Connect package
"""
from connect.adapters import Adapter
from connect.governance import Governance
from connect.utils.version_check import validate_version
from connect._version import __version__


__all__ = ["governance", "evidence", "utils"]

validate_version()
