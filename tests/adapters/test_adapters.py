import pytest

from connect.adapters import Adapter
from connect.governance import Governance

METRICS = {"precision": 0.5, "recall": 0.4}
ADAPTER = Adapter(Governance(), "model")

LABELS = [
    ({}, [{"metric_type": "precision"}, {"metric_type": "recall"}]),
    (
        {"test": "test"},
        [
            {"metric_type": "precision", "test": "test"},
            {"metric_type": "recall", "test": "test"},
        ],
    ),
]


@pytest.mark.parametrize("labels,expectation", LABELS, ids=["no_label", "label"])
def test_metrics_to_evidence(labels, expectation):
    out = ADAPTER._metrics_to_evidence(METRICS, labels)
    evidence_labels = [l.label for l in out]
    assert evidence_labels == expectation
