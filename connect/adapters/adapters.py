from typing import Optional

import pandas as pd

from connect.evidence import MetricContainer
from connect.governance import Governance
from connect.utils import ValidationError


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
        labels: dict = None,
        metadata: dict = None,
        overwrite_governance: bool = False,
    ):
        """
        Packages metrics as evidence and sends them to governance

        Parameters
        ---------
        metrics : dict or pd.DataFrame
            Dictionary of metrics. Form: {metric_type: value, ...}
        labels : dict
            Additional labels to pass to underlying evidence
        metadata : dict
            Metadata to pass to underlying evidence
        overwrite_governance : bool
            When adding evidence to a Governance object, whether to overwrite existing
            evidence or not, default False.
        """
        evidence = self._metrics_to_evidence(metrics, labels, metadata)

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

    def _metrics_to_evidence(self, metrics, labels=None, metadata=None):
        """Converts a dictionary of metrics to evidence

        Parameters
        ----------
        metrics : dict or pd.DataFrame
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
        meta = self._get_artifact_meta()
        meta.update(metadata or {})
        if isinstance(metrics, dict):
            metrics = pd.DataFrame(metrics.items(), columns=["type", "value"])
        elif not isinstance(metrics, pd.DataFrame):
            raise ValidationError("Metrics must be a dictionary or a dataframe")
        container = MetricContainer(metrics, labels, meta)
        return container.to_evidence()
