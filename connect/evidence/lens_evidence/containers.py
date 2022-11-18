from connect.evidence import (
    EvidenceContainer,
    helper_df_remove_NaNs,
    helper_dict_remove_NaNs,
)
from connect.utils import ValidationError

from .evidence import DataProfilerEvidence, ModelProfilerEvidence
from .utils import get_pandas_profile_type

import numpy as np

PandasProfileType = get_pandas_profile_type()


class DataProfilerContainer(EvidenceContainer):
    """Container for all profiler type evidence"""

    def __init__(self, data, labels: dict = None, metadata: dict = None):
        super().__init__(DataProfilerEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        return [
            self.evidence_class(
                self._data.get_description(), self.labels, **self.metadata, **metadata
            )
        ]

    def _validate(self, data):
        pass

    def _validate_inputs(self, data):
        if not isinstance(data, PandasProfileType):
            raise ValidationError(
                "'data' must be a pandas_profiling.profile_report.ProfileReport"
            )

    def remove_NaNs(self, data):
        return helper_dict_remove_NaNs(data)


class ModelProfilerContainer(EvidenceContainer):
    """Container for Model Profiler type evidence"""

    def __init__(self, data, labels=None, metadata=None):
        super().__init__(ModelProfilerEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        self.remove_NaNs()
        return [
            self.evidence_class(self._data, self.labels, **self.metadata, **metadata)
        ]

    def _validate(self, data):
        necessary_index = ["parameters", "feature_names", "model_name"]
        if list(data.columns) != ["results"]:
            raise ValidationError(
                "Model profiler data must only have one column: 'results'"
            )
        if sum(data.index.isin(necessary_index)) != 3:
            raise ValidationError(f"Model profiler data must contain {necessary_index}")

    def remove_NaNs(self, data):
        return helper_df_remove_NaNs(data)
