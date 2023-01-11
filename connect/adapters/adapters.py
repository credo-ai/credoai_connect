from functools import partial
from typing import Optional

import pandas as pd

from connect.evidence import EvidenceContainer, MetricContainer, TableContainer
from connect.governance import Governance
from connect.utils import ValidationError, wrap_list


class Adapter:
    """Basic adapter to connect with governance

    Parameters
    ----------
    governance : Governance
        the Governance instance to use for connection
    model_name : str
        Name of model
    model_tags : dict, optional
        List of key:value pairs specifying model tags. These are typically
        used to pair the model with tagged governance requirements,
        which are defined in a Governance instance's assessment_plan
    assessment_dataset_name : dict, optional
        Name of dataset used to assess the model
    """

    def __init__(
        self,
        governance: Governance,
        model_name: str,
        model_tags: Optional[dict] = None,
        assessment_dataset_name: str = None,
    ):

        self.governance = governance
        self.governance.set_artifacts(model_name, model_tags, assessment_dataset_name)

    def metrics_to_governance(
        self,
        metrics: dict,
        source: str,
        labels: dict = None,
        metadata: dict = None,
        overwrite_governance: bool = True,
    ):
        """
        Packages metrics as evidence and sends them to governance

        Parameters
        ---------
        metrics : dict or pd.DataFrame
            Dictionary of metrics. Form: {metric_type: value, ...}
        source : str
            Label for what generated the metrics. Added to metadata
        labels : dict
            Additional key/value pairs to act as labels for the evidence
        metadata : dict
            Metadata to pass to underlying evidence
        overwrite_governance : bool
            When adding evidence to a Governance object, whether to overwrite existing
            evidence or not, default False.
        """
        self._evidence_to_governance(
            self._metrics_to_evidence,
            metrics,
            source,
            labels,
            metadata,
            overwrite_governance,
        )

    def table_to_governance(
        self,
        data: dict,
        source: str,
        labels: dict = None,
        metadata: dict = None,
        overwrite_governance: bool = True,
    ):
        """
        Packages metrics as evidence and sends them to governance

        Parameters
        ---------
        data: pd.DataFrame
            Dataframe to pass to evidence_fun. The DataFrame must have a "name" attribute
        source : str
            Label for what generated the table. Added to metadata
        labels : dict
            Additional key/value pairs to act as labels for the evidence
        metadata : dict
            Metadata to pass to underlying evidence
        overwrite_governance : bool
            When adding evidence to a Governance object, whether to overwrite existing
            evidence or not, default False.
        evidence_fun : callable
            Function to pass data, labels and metadata. The function should return a list of
            evidence. Default: self._to_evidence
        """
        self._evidence_to_governance(
            TableContainer, data, source, labels, metadata, overwrite_governance
        )

    def _evidence_to_governance(
        self,
        evidence_fun,
        data,
        source,
        labels,
        metadata,
        overwrite_governance=True,
    ):
        """
        Packages data as evidence and sends to governance

        Parameters
        ---------
        evidence_fun : callable or Container
            Function to pass data, labels and metadata. The function should return a list of
            evidence. If a Container, use self._to_evidence with the specified container
        data
            data to pass to evidence_fun
        source : str
            Label for what generated the evidence. Added to metadata
        labels : dict
            Additional key/value pairs to act as labels for the evidence
        metadata : dict
            Metadata to pass to underlying evidence
        overwrite_governance : bool
            When adding evidence to a Governance object, whether to overwrite existing
            evidence or not, default False.
        """
        try:
            if issubclass(evidence_fun, EvidenceContainer):
                evidence_fun = partial(self._to_evidence, container_class=evidence_fun)
        except TypeError:
            pass
        metadata = {**(metadata or {}), "source": source}
        evidence = evidence_fun(data=data, labels=labels, metadata=metadata)
        if overwrite_governance:
            self.governance.set_evidence(evidence)
        else:
            self.governance.add_evidence(evidence)

    def _get_artifact_meta(self):
        model = self.governance.model
        if model is not None:
            model = model.copy()
            model["model_name"] = model.pop("name")
            del model["tags"]
        return model or {}

    def _metrics_to_evidence(self, data, labels=None, metadata=None):
        """Converts a dictionary of metrics to evidence

        Parameters
        ----------
        data : dict or pd.DataFrame
            Dictionary of metrics. Form: {metric_type: value, ...}
        labels : dict
            Additional labels to pass to underlying evidence
        metadata : dict
            Metadata to pass to underlying evidence

        Returns
        -------
        List
            list of Evidence
        """
        if isinstance(data, dict):
            data = pd.DataFrame(data.items(), columns=["type", "value"])
        elif not isinstance(data, pd.DataFrame):
            raise ValidationError("Metrics must be a dictionary or a dataframe")
        return self._to_evidence(MetricContainer, data, labels, metadata)

    def _to_evidence(self, container_class, data, labels, metadata):
        meta = self._get_artifact_meta()
        meta.update(metadata or {})
        container = container_class(data, labels, meta)
        return wrap_list(container.to_evidence())
