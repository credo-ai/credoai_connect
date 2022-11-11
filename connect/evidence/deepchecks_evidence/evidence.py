from connect.evidence import Evidence

from .utils import get_deepchecks_type

DeepChecksType = get_deepchecks_type()


class DeepchecksEvidence(Evidence):
    """
    Evidence for deepchecks SuiteResult objects

    Underlying evidence is passed as a JSON-formatted string. Other

    Parameters
    ----------
    name: string
        Name of the suite of deepchecks checks run by the Deepchecks evaluator
    result : SuiteResult object
        The output of a call to a deepchecks.Suite object's run() function.
    additional_labels : dict, optional
        Additional labels to be passed to, and displayed by the Credo AI Governance platform
    metadata : dict, optional
        Arbitrary keyword arguments to append to metric as metadata. These will be
        displayed in the governance app
    """

    def __init__(
        self,
        name: str,
        result: DeepChecksType,
        additional_labels: dict = None,
        **metadata,
    ):
        self.name = name
        self._result = result
        super().__init__("deepchecks_result", additional_labels, **metadata)

    @property
    def data(self):
        return self._result.to_json()

    @property
    def base_label(self):
        label = {"suite_result_name": self.name}
        return label
