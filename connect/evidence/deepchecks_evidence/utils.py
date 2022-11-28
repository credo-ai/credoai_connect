#
from typing import TYPE_CHECKING, TypeVar


def get_deepchecks_type():
    """check if deepchecks is imported. If not, define object for type checking"""
    if TYPE_CHECKING:
        try:
            from deepchecks.core import SuiteResult

            deep_checks_type = SuiteResult
        except ImportError:
            deep_checks_type = TypeVar("SuiteResult")
    else:
        from deepchecks.core import SuiteResult

        deep_checks_type = SuiteResult
    return deep_checks_type
