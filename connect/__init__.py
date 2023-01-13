"""
Credo AI Connect package
"""
from connect.adapters import Adapter
from connect.governance import Governance
from connect.utils.version_check import validate_version

__version__ = "0.0.7"

__all__ = ["governance", "evidence", "utils"]

validate_version()
