"""
Everything needed to generate inputs for the Credo AI Platform

All the logic defined here is in order to standardize communication with 
Credo AI Platform API
"""
from .containers import (
    EvidenceContainer,
    MetricContainer,
    TableContainer,
    StatisticTestContainer,
)
from .evidence import Evidence, MetricEvidence, TableEvidence, StatisticTestEvidence
from .evidence_requirement import EvidenceRequirement
