"""
Generic containers for evaluator results

The containers accept raw data from the evaluators and convert it into
suitable evidences.
"""
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from copy import deepcopy

from connect.utils import ValidationError

from .evidence import MetricEvidence, TableEvidence


def helper_df_remove_NaNs(data: pd.DataFrame):
    # Assume DataFrame is well-formed: does not contain lists, DFs, or other complex objects
    # returns copy of object --> no deep copy concern
    return data.fillna(np.nan).replace([np.nan], [None])


def helper_list_remove_NaNs(data: list):
    return_list = deepcopy(data)
    for idx, item in enumerate(return_list):
        if isinstance(item, pd.DataFrame):
            return_list[idx] = helper_df_remove_NaNs(item)
        elif isinstance(item, np.ndarray):
            return_list[idx] = helper_array_remove_NaNs(item)
        elif isinstance(item, dict):
            return_list[idx] = helper_dict_remove_NaNs(item)
        elif isinstance(item, list):
            return_list[idx] = helper_list_remove_NaNs(item)
        else:
            # Assume no other iterable data types could be stored in list
            if item is np.nan:
                return_list[idx] = None
    return return_list


def helper_array_remove_NaNs(data: np.ndarray):
    # Assume array is well-formed: does not contain lists or other complex objects
    # returns copy of object --> no deep copy concern
    return np.where(np.isnan(data), None, data)


def helper_dict_remove_NaNs(data: dict):
    return_dict = deepcopy(data)
    for key, val in return_dict.items():
        if isinstance(val, pd.DataFrame):
            return_dict[key] = helper_df_remove_NaNs(val)
        elif isinstance(val, np.ndarray):
            return_dict[key] = helper_array_remove_NaNs(val)
        elif isinstance(val, dict):
            return_dict[key] = helper_dict_remove_NaNs(val)
        elif isinstance(val, list):
            return_dict[key] = helper_list_remove_NaNs(val)
        else:
            # Assume no other iterable data types could be stored in dictionary
            if val is np.nan:
                return_dict[key] = None
    return return_dict


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
        self._data = self.remove_NaNs(data)
        self.labels = labels
        self.metadata = metadata or {}

    @property
    def data(self):
        return self._data

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

    @abstractmethod
    def remove_NaNs(self, data):
        """
        Converts NaNs in self._data to NoneType
        Method of removal depends on underlying type of self._data
        Force implementation in subclasses to ensure this sanitation happens
        """
        pass


class MetricContainer(EvidenceContainer):
    """Containers for all Metric type evidence"""

    def __init__(self, data: pd.DataFrame, labels: dict = None, metadata: dict = None):
        super().__init__(MetricEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        evidence = []
        for _, data in self._data.iterrows():
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

    def remove_NaNs(self, data):
        return helper_df_remove_NaNs(data)


class TableContainer(EvidenceContainer):
    """Container for all Table type evidence"""

    def __init__(self, data: pd.DataFrame, labels: dict = None, metadata: dict = None):
        super().__init__(TableEvidence, data, labels, metadata)

    def to_evidence(self, **metadata):
        return [
            self.evidence_class(
                self._data.name, self._data, self.labels, **self.metadata, **metadata
            )
        ]

    def _validate(self, data):
        try:
            data.name
        except AttributeError:
            raise ValidationError("DataFrame must have a 'name' attribute")

    def remove_NaNs(data):
        return data.fillna(np.nan).replace([np.nan], [None])
