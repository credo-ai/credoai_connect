"""
Everything needed to generate inputs for the Credo AI Platform

All the logic defined here is in order to standardize communication with 
Credo AI Platform API
"""
from .containers import (
    EvidenceContainer,
    MetricContainer,
    TableContainer,
    helper_df_remove_NaNs,
    helper_list_remove_NaNs,
    helper_array_remove_NaNs,
    helper_dict_remove_NaNs,
)
from .evidence import Evidence, MetricEvidence, TableEvidence
from .evidence_requirement import EvidenceRequirement
