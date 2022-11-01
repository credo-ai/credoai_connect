from connect.evidence import EvidenceContainer
from connect.utils import ValidationError

from .evidence import DataProfilerEvidence, ModelProfilerEvidence


class ProfilerContainer(EvidenceContainer):
    """Container for al profiler type evidence"""

    def __init__(self, data, labels: dict = None, metadata: dict = None):
        super().__init__(DataProfilerEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        return [self.evidence_class(self._df, self.labels, **self.metadata, **metadata)]

    def _validate(self, df):
        if list(df.columns) != ["results"]:
            raise ValidationError("Profiler data must only have one column: 'results'")


class ModelProfilerContainer(EvidenceContainer):
    """Container for Model Profiler type evidence"""

    def __init__(self, df, labels=None, metadata=None):
        super().__init__(ModelProfilerEvidence, df, labels, metadata)

    def to_evidence(self, **metadata):
        return [self.evidence_class(self._df, self.labels, **self.metadata, **metadata)]

    def _validate(self, df):
        necessary_index = ["parameters", "feature_names", "model_name"]
        if list(df.columns) != ["results"]:
            raise ValidationError(
                "Model profiler data must only have one column: 'results'"
            )
        if sum(df.index.isin(necessary_index)) != 3:
            raise ValidationError(f"Model profiler data must contain {necessary_index}")
