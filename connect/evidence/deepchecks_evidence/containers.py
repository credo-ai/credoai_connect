import pandas as pd
from deepchecks.core import SuiteResult

from connect.evidence import EvidenceContainer, TableEvidence
from connect.utils import ValidationError

from .evidence import DeepchecksEvidence


class DeepchecksContainer(EvidenceContainer):
    """Container for all Table type evidence"""

    def __init__(
        self, name: str, data: SuiteResult, labels: dict = None, metadata: dict = None
    ):
        super().__init__(DeepchecksEvidence, data, labels, metadata)
        self.name = name

    def to_evidence(self, **metadata):
        checks_2_df = {"Check_Name": list(), "Status": list()}
        for check in self._data.get_not_passed_checks():
            checks_2_df["Check_Name"].append(check.header)
            checks_2_df["Status"].append("Not Passed")
        for check in self._data.get_passed_checks():
            checks_2_df["Check_Name"].append(check.header)
            checks_2_df["Status"].append("Passed")
        for check in self._data.get_not_ran_checks():
            checks_2_df["Check_Name"].append(check.header)
            checks_2_df["Status"].append("Not Run")

        check_results_df = pd.DataFrame.from_dict(checks_2_df, orient="columns")
        check_results_df.name = "Lens_Deepchecks_SuiteResult"
        return [
            TableEvidence(
                self.name, check_results_df, self.labels, **self.metadata, **metadata
            )
        ]

    def _validate_inputs(self, data):
        if not isinstance(data, SuiteResult):
            raise ValidationError("'data' must be a deepchecks.core.SuiteResult object")

    def _validate(self, data):
        pass
