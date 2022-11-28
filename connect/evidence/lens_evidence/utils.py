#
from typing import TYPE_CHECKING, TypeVar


def get_pandas_profile_type():
    """check if deepchecks is imported. If not, define object for type checking"""
    if TYPE_CHECKING:
        try:
            from pandas_profiling import ProfileReport

            pandas_profile_type = ProfileReport
        except ImportError:
            pandas_profile_type = TypeVar("Profilereport")
    else:
        from pandas_profiling import ProfileReport

        pandas_profile_type = ProfileReport
    return pandas_profile_type
