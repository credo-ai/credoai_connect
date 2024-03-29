"""
Generic containers for evaluator results

The containers accept raw data from the evaluators and convert it into
suitable evidences.
"""
from abc import ABC, abstractmethod

import pandas as pd

from connect.utils import Scrubber, ValidationError

from .evidence import MetricEvidence, StatisticTestEvidence, TableEvidence


class EvidenceContainer(ABC):
    def __init__(self, evidence_class, data, labels=None, metadata=None):
        """Abstract Class defining Evidence Containers

        Evidence Containers are light wrappers around data objects that
        validate their format for the purpose of evidence export. They
        define a "to_evidence" function which transforms the
        data into a particular evidence format

        Parameters
        ----------
        evidence_class : Evidence
            An Evidence class
        data :
            The data, formatted appropriately for the evidence type
            Typing is variable depending on evidence being wrapped
                Most metrics will be pd.DataFrames
                Evidence generated by integrated packages (e.g. deepchecks) is dependent on
                package's output
        labels : dict
            Additional labels to pass to underlying evidence
        metadata : dict
            Metadata to pass to underlying evidence
        """
        self.evidence_class = evidence_class
        self._validate_inputs(data)
        self._validate(data)
        self._data = data
        self.labels = labels
        self.metadata = metadata or {}

    @property
    def data(self):
        return self._data

    @property
    def scrubbed_data(self):
        return Scrubber.remove_NaNs(self._data)

    @abstractmethod
    def to_evidence(self):
        pass

    def _validate_inputs(self, data):
        """Default validation assumes data is a dataframe"""
        if not isinstance(data, pd.DataFrame):
            raise ValidationError("'data' must be a dataframe")

    @abstractmethod
    def _validate(self, data):
        pass


class MetricContainer(EvidenceContainer):
    """Containers for all Metric type evidence"""

    def __init__(self, data: pd.DataFrame, labels: dict = None, metadata: dict = None):
        super().__init__(MetricEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        evidence = []
        for _, data in self.scrubbed_data.iterrows():
            evidence.append(
                self.evidence_class(
                    additional_labels=self.labels, **data, **self.metadata, **metadata
                )
            )
        return evidence

    def _validate(self, data):
        required_columns = {"type", "value"}
        column_overlap = data.columns.intersection(required_columns)
        if len(column_overlap) != len(required_columns):
            raise ValidationError(
                f"Metrics dataframe must have columns: {required_columns}"
            )


class StatisticTestContainer(EvidenceContainer):
    """Containers for all Statistic Test type evidence"""

    def __init__(self, data: pd.DataFrame, labels: dict = None, metadata: dict = None):
        super().__init__(StatisticTestEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        evidence = []
        for _, data in self.scrubbed_data.iterrows():
            evidence.append(
                self.evidence_class(
                    additional_labels=self.labels, **data, **self.metadata, **metadata
                )
            )
        return evidence

    def _validate(self, data):
        required_columns = {
            "statistic_type",
            "test_statistic",
            "significance_threshold",
            "p_value",
            "significant",
        }
        column_overlap = data.columns.intersection(required_columns)
        if len(column_overlap) != len(required_columns):
            raise ValidationError(
                f"Statistics dataframe must have columns: {required_columns}"
            )


class TableContainer(EvidenceContainer):
    """Container for all Table type evidence"""

    def __init__(self, data: pd.DataFrame, labels: dict = None, metadata: dict = None):
        super().__init__(TableEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        return [
            self.evidence_class(
                self.scrubbed_data.name,
                self.scrubbed_data,
                self.labels,
                **self.metadata,
                **metadata,
            )
        ]

    def _validate(self, data):
        try:
            data.name
        except AttributeError:
            raise ValidationError("DataFrame must have a 'name' attribute")
