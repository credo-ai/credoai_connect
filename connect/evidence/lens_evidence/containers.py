import numpy as np

from connect.evidence import EvidenceContainer
from connect.utils import Scrubber, ValidationError

from .evidence import DataProfilerEvidence, ModelProfilerEvidence
from .utils import get_pandas_profile_type

PandasProfileType = get_pandas_profile_type()


class DataProfilerContainer(EvidenceContainer):
    """Container for all profiler type evidence"""

    def __init__(self, data, labels: dict = None, metadata: dict = None):
        super().__init__(DataProfilerEvidence, data, labels, metadata)

    @property
    def scrubbed_data(self):
        return Scrubber.remove_NaNs(self.data.get_description())

    def to_evidence(self, **metadata):
        return [
            self.evidence_class(
                self.scrubbed_data, self.labels, **self.metadata, **metadata
            )
        ]

    def _validate(self, data):
        pass

    def _validate_inputs(self, data):
        if not isinstance(data, PandasProfileType):
            raise ValidationError(
                "'data' must be a pandas_profiling.profile_report.ProfileReport"
            )


class ModelProfilerContainer(EvidenceContainer):
    """Container for Model Profiler type evidence"""

    def __init__(self, data, labels=None, metadata=None):
        super().__init__(ModelProfilerEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        return [
            self.evidence_class(
                self.scrubbed_data, self.labels, **self.metadata, **metadata
            )
        ]

    def _validate(self, data):
        necessary_index = ["parameters", "model_name"]
        if list(data.columns) != ["results"]:
            raise ValidationError(
                "Model profiler data must only have one column: 'results'"
            )
        if sum(data.index.isin(necessary_index)) != 2:
            raise ValidationError(f"Model profiler data must contain {necessary_index}")
