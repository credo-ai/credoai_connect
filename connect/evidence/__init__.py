"""
Everything needed to generate inputs for the Credo AI Platform

All the logic defined here is in order to standardize communication with 
Credo AI Platform API
"""
from .containers import EvidenceContainer, MetricContainer, TableContainer
from .evidence import Evidence, MetricEvidence, TableEvidence
from .evidence_requirement import EvidenceRequirement
