"""
Wrappers formatting results of evaluator runs for the Credo AI Platform
"""
import pprint
from abc import ABC, abstractproperty
from datetime import datetime
from typing import Tuple

from pandas import DataFrame

from connect.utils import ValidationError


class Evidence(ABC):
    """Abstract class defining Evidence"""

    def __init__(self, type: str, additional_labels: dict = None, **metadata):
        self.type = type
        self.additional_labels = additional_labels or {}
        self.metadata = metadata
        self.creation_time: str = datetime.utcnow().isoformat()
        self._label = None
        self._validate()

    def __str__(self):
        return pprint.pformat(self.struct())

    def struct(self):
        """Structure of evidence"""
        structure = {
            "type": self.type,
            "label": self.label,
            "data": self.data,
            "generated_at": self.creation_time,
            "metadata": self.metadata,
        }
        return structure

    @property
    def label(self):
        """
        Adds evidence type specific label
        """
        # additional_labels prioritized
        if self._label is None:
            self._label = {**self.base_label, **self.additional_labels}
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @abstractproperty
    def base_label(self):
        pass

    @abstractproperty
    def data(self):
        """
        Adds data reflecting additional structure of child classes
        """
        return {}

    def _validate(self):
        pass


class MetricEvidence(Evidence):
    """
    Evidence for Metric:value result type

    Parameters
    ----------
    type : string
        short identifier for metric.
    value : float
        metric value
    confidence_interval : [float, float]
        [lower, upper] confidence interval
    confidence_level : int
        Level of confidence for the confidence interval (e.g., 95%)
    metadata : dict, optional
        Arbitrary keyword arguments to append to metric as metadata. These will be
        displayed in the governance app
    """

    def __init__(
        self,
        type: str,
        value: float,
        confidence_interval: Tuple[float, float] = None,
        confidence_level: int = None,
        additional_labels=None,
        **metadata
    ):
        self.metric_type = type
        self.value = value
        self.confidence_interval = confidence_interval
        self.confidence_level = confidence_level
        super().__init__("metric", additional_labels, **metadata)

    @property
    def data(self):
        return {
            "value": self.value,
            "confidence_interval": self.confidence_interval,
            "confidence_level": self.confidence_level,
        }

    @property
    def base_label(self):
        label = {"metric_type": self.metric_type}
        return label

    def _validate(self):
        if self.confidence_interval and not self.confidence_level:
            raise ValidationError


class StatisticTestEvidence(Evidence):
    """
    Evidence for Statistical Test:value result type

    Parameters
    ----------
    statistic_type : string
        Short identifier for statistical test.
    value : float
        Test calculation result
    p_value : float
        p_value associated to the calculation
    significance_threshold : float
        p_value threshold to consider test significant, e.g., 0.01
    additional_labels: dict, opional
        Extra info to be added to the label section.
    metadata : dict, optional
        Arbitrary keyword arguments to append to metric as metadata. These will be
        displayed in the governance app
    """

    def __init__(
        self,
        statistic_type: str,
        test_statistic: float,
        significance_threshold: float,
        p_value: float,
        additional_labels=None,
        **metadata
    ):
        self.statistic_type = statistic_type
        self.test_statistic = test_statistic
        self.significance_threshold = significance_threshold
        self.p_value = p_value
        self.significant = (
            True if self.p_value <= self.significance_threshold else False
        )
        super().__init__("statisticTest", additional_labels, **metadata)

    @property
    def data(self):
        return {
            "test_statistic": self.test_statistic,
            "significance_threshold": self.significance_threshold,
            "p_value": self.p_value,
            "significant": self.significant,
        }

    @property
    def base_label(self):
        label = {"statistic_type": self.statistic_type}
        return label


class TableEvidence(Evidence):
    """
    Evidence for tabular data

    Parameters
    ----------
    data : str
        a pandas DataFrame to use as evidence
    metadata : dict, optional
        Arbitrary keyword arguments to append to metric as metadata. These will be
        displayed in the governance app
    """

    def __init__(
        self, name: str, table_data: DataFrame, additional_labels=None, **metadata
    ):
        self.name = name
        self._data = table_data
        super().__init__("table", additional_labels, **metadata)

    @property
    def data(self):
        columns = [
            {"value": k, "type": self._transform_type(v)}
            for k, v in self._data.dtypes.iteritems()
        ]
        return {
            "columns": columns,
            "value": self._data.values.tolist(),
        }

    @property
    def base_label(self):
        label = {"table_name": self.name}
        return label

    def _transform_type(self, pandas_type):
        lookup = {
            "int64": "number",
            "float64": "number",
            "object": "string",
            "category": "string",
            "datetime64": "datetime",
        }
        final_type = str(pandas_type)
        return lookup.get(final_type, final_type)
