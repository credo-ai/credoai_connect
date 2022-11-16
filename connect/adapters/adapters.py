import pandas as pd

from connect.evidence import MetricContainer
from connect.governance import Governance
from connect.utils import ValidationError


def metrics_to_governance(
    governance: Governance,
    metrics: dict,
    labels: dict = None,
    metadata: dict = None,
    overwrite_governance: bool = False,
):
    """
    Packages metrics as evidence and sends them to governance

    Parameters
    ---------
    governance : Governance
        instance of connect.Governance
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
    evidence = metrics_to_evidence(metrics, labels, metadata)

    if overwrite_governance:
        governance.set_evidence(evidence)
    else:
        governance.add_evidence(evidence)


def metrics_to_evidence(metrics, labels=None, metadata=None):
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
    if isinstance(metrics, dict):
        metrics = pd.DataFrame(metrics.items(), columns=["type", "value"])
    elif not isinstance(metrics, pd.DataFrame):
        raise ValidationError("Metrics must be a dictionary or a dataframe")
    container = MetricContainer(metrics, labels, metadata)
    return container.to_evidence()
