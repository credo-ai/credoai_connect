#
from typing import TYPE_CHECKING, TypeVar


def get_ydata_profile_type():
    """check if ydata profiling is imported. If not, define object for type checking"""
    if TYPE_CHECKING:
        try:
            from ydata_profiling import ProfileReport

            ydata_profiling = ProfileReport
        except ImportError:
            ydata_profiling = TypeVar("ProfileReport")
    else:
        from ydata_profiling import ProfileReport

        ydata_profiling = ProfileReport
    return ydata_profiling
