"""
Everything needed to generate inputs for the Credo AI Platform

All the logic defined here is in order to standardize communication with 
Credo AI Platform API
"""
from .containers import (
    EvidenceContainer,
    FigureContainer,
    MetricContainer,
    StatisticTestContainer,
    TableContainer,
)
from .evidence import (
    Evidence,
    FigureEvidence,
    MetricEvidence,
    StatisticTestEvidence,
    TableEvidence,
)
from .evidence_requirement import EvidenceRequirement
