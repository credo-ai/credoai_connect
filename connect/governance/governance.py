"""
Credo Governance
"""

import json
import sys
import time
from pprint import pprint
from typing import List, Optional, Union

from json_api_doc import deserialize, serialize

from connect.evidence import Evidence, EvidenceRequirement
from connect.utils import (
    check_subset,
    get_version,
    global_logger,
    json_dumps,
    wrap_list,
)

from .credo_api import CredoApi
from .credo_api_client import CredoApiClient


class Governance:
    """Class to store governance data.

    Governance is used to interact with the CredoAI Governance(Report) App.
    It has two main jobs.
    1. Get evidence_requirements of use_case and policy pack.
    2. Upload evidences gathered with evidence_requirements

    Parameters
    ----------
    credo_api_client: CredoApiClient, optional
        Credo API client. Uses default Credo API client if it is None
        Default Credo API client uses `~/.credo_config` to read API server configuration.
        Please prepare `~/.credo_config` file by downloading it from CredoAI Governance App.(My Settings > Tokens)

    Examples
    --------
    If you want to use your own configuration:

        from connect.governance.credo_api_client import CredoApiClient, CredoApiConfig
        from connect.governance.goverance import Governance

        config = CredoApiConfig(
            api_key="API_KEY", tenant="credo", api_server="https://api.credo.ai"
        )
        # or using credo_config file
        config = CredoApiConfig()
        config.load_config("CREDO_CONFIG_FILE_PATH")

        client = CredoApiClient(config=config)
        governace = Governance(credo_api_client=client)

    """

    def __init__(
        self, config_path: str = None, credo_api_client: CredoApiClient = None
    ):
        """Governance object to connect Lens with Credo AI Platform

        Parameters
        ----------
        config_path : str, optional
            path to .credoconfig file. If None, points to ~/.credoconfig, by default None
        credo_api_client : CredoApiClient, optional
            If provided, overrides the API configuration defined by
            the config path, by default None
        """
        self._use_case_id: Optional[str] = None
        self._policy_pack_id: Optional[str] = None
        self._evidence_requirements: List[EvidenceRequirement] = []
        self._evidences: List[Evidence] = []
        self._model = None
        self._plan: Optional[dict] = None
        self._unique_tags: List[dict] = []

        if credo_api_client:
            client = credo_api_client
        else:
            client = CredoApiClient(config_path=config_path)

        self._api = CredoApi(client=client)

    @property
    def model(self):
        return self._model

    @property
    def requirements_satisified(self):
        return self._match_requirements()

    @property
    def registered(self):
        return bool(self._plan)

    def add_evidence(self, evidences: Union[Evidence, List[Evidence]]):
        """
        Add evidences
        """
        self._evidences += wrap_list(evidences)

    def clear_evidence(self):
        self.set_evidence([])

    def export(self, filename=None):
        """
        Upload evidences to CredoAI Governance(Report) App

        Returns
        -------
        True
            When uploading is successful with all evidence
        False
            When it is not registered yet, or evidence is insufficient
        """
        if not self._validate_export():
            return False
        to_return = self._match_requirements()

        if filename is None:
            self._api_export()
        else:
            self._file_export(filename)

        if to_return:
            export_status = "All requirements were matched."
        else:
            export_status = "Partial match of requirements."

        global_logger.info(export_status)
        return to_return

    def get_evidence(self, verbose=False):
        """
        Returns evidence that has been send to the governance object

        Parameters
        ----------
        verbose : bool, False
            if True, print out human-readable evidence requirements
        """
        if verbose:
            self._print_evidence(self._evidences)
        return self._evidences

    def get_evidence_requirements(self, tags: dict = None, verbose=False):
        """
        Returns evidence requirements. Each evidence requirement can have optional tags
        (a dictionary). Returns requirements whose tags are a subset of the model's tags.

        For example, imagine a model has two tags: {'risk': 'high', 'model_type': 'binary'}
        and three requirements with the following tags:
            req1 = {}
            req2 = {'risk': 'high'}
            req3 = {'risk': 'high', 'model_type': 'binary'}
        In this case all requirements will apply. If the model risk was was 'low' only req_1 would
        apply. If the 'model_type' was not 'binary' then only req1 and req2 would apply.

        Parameters
        ----------
        tags : dict, optional
            Tags to subset evidence requirements. If a model has been set, will default
            to the model's tags. Evidence requirements will be returned that have no
            tags or have the same tag as provided.
        verbose : bool, False
            if True, print out human-readable evidence requirements

        Returns
        -------
        List[EvidenceRequirement]
        """
        if tags is None:
            tags = self.get_model_tags()

        reqs = [e for e in self._evidence_requirements if check_subset(e.tags, tags)]
        if verbose:
            self._print_evidence(reqs)
        return reqs

    def get_requirement_tags(self):
        """Return the unique tags used for all evidence requirements"""
        return self._unique_tags

    def get_model_tags(self):
        """Get the tags for the associated model"""
        if self._model:
            return self._model["tags"]
        else:
            return {}

    def register(
        self,
        assessment_plan_url: str = None,
        use_case_name: str = None,
        policy_pack_key: str = None,
        assessment_plan: str = None,
        assessment_plan_file: str = None,
    ):
        """
        Parameters
        ----------
        assessment_plan_url : str
            assessment plan URL
        use_case_name : str
            use case name
        policy_pack_key : str
            policy pack key
        assessment_plan : str
            assessment plan JSON string
        assessment_plan_file : str
            assessment plan file name that holds assessment plan JSON string

        Examples
        --------
        Get assessment plan and register it.
        There are three ways to do it:

            1. With assessment_plan_url.

                gov.register(assessment_plan_url="https://api.credo.ai/api/v2/tenant/use_cases/{id}/assessment_plans/{pp_id}")

            2. With use case name and policy pack key.

                gov.register(use_case_name="Fraud Detection", policy_pack_key="FAIR")

            3. With assessment_plan json string or filename. It is used in the air-gap condition.

                gov.register(assessment_plan="JSON_STRING")
                gov.register(assessment_plan_file="FILENAME")

        After successful registration, `gov.registered` returns True and able to get evidence_requirements:

            gov.registered    # returns True
            gov.get_evidence_requirements()


        """
        self._plan = None

        plan = None
        if use_case_name:
            assessment_plan_url = self._api.get_assessment_plan_url(
                use_case_name, policy_pack_key
            )

        if assessment_plan_url:
            plan = self._api.get_assessment_plan(assessment_plan_url)

        if assessment_plan:
            plan = self.__parse_json_api(assessment_plan)

        if assessment_plan_file:
            with open(assessment_plan_file, "r") as f:
                json_str = f.read()
                plan = self.__parse_json_api(json_str)

        if plan:
            self._plan = plan
            self._use_case_id = plan.get("use_case_id")
            self._policy_pack_id = plan.get("policy_pack_id")
            self._evidence_requirements = list(
                map(
                    lambda d: EvidenceRequirement(d),
                    plan.get("evidence_requirements", []),
                )
            )

            # Extract unique tags
            for x in self._evidence_requirements:
                if x.tags not in self._unique_tags:
                    self._unique_tags.append(x.tags)
            self._unique_tags = [x for x in self._unique_tags if x]

            global_logger.info(
                f"Successfully registered with {len(self._evidence_requirements)} evidence requirements"
            )

            if self._unique_tags:
                global_logger.info(
                    f"The following tags have being found in the evidence requirements: {self._unique_tags}"
                )

            self.clear_evidence()

    def set_artifacts(
        self,
        model: str,
        model_tags: dict,
        training_dataset: str = None,
        assessment_dataset: str = None,
    ):
        """Sets up internal knowledge of model and datasets to send to Credo AI Platform


        Parameters
        ----------
        model : str
            model name
        model_tags : dict
            List of key:value pairs specifying model tags. These are typically
            used to pair the model with tagged governance requirements,
            which are defined in a Governance instance's assessment_plan
        training_dataset : str, optional
            training dataset name, by default None
        assessment_dataset : str, optional
            assessment dataset name, by default None
        """

        global_logger.info(
            f"Adding model ({model}) to governance. Model has tags: {model_tags}"
        )
        prepared_model = {"name": model, "tags": model_tags}
        if training_dataset:
            prepared_model["training_dataset_name"] = training_dataset
        if assessment_dataset:
            prepared_model["assessment_dataset_name"] = assessment_dataset
        self._model = prepared_model

    def set_evidence(self, evidences: List[Evidence]):
        """
        Update evidences
        """
        self._evidences = evidences

    def tag_model(self, model):
        """Interactive utility to tag a model tags from assessment plan"""
        tags = self.get_requirement_tags()
        print(f"Select tag from assessment plan to associated with model:")
        print("0: No tags")
        for number, tag in enumerate(tags):
            print(f"{number+1}: {tag}")
        selection = int(input("Number of tag to associate: "))
        if selection == 0:
            selected_tag = None
        else:
            selected_tag = tags[selection - 1]
        print(f"Selected tag = {selected_tag}. Applying to model...")
        model.tags = selected_tag
        if self._model:
            self._model["tags"] = selected_tag

    def _api_export(self):
        global_logger.info(
            f"Uploading {len(self._evidences)} evidences.. for use_case_id={self._use_case_id} policy_pack_id={self._policy_pack_id}"
        )

        assessment = self._api.create_assessment(
            self._use_case_id, self._prepare_export_data()
        )

        if assessment:
            # wait until uploading is finished
            progress = 1
            while assessment["result"] == "in_progress":
                time.sleep(1)
                sys.stdout.write("\r")
                sys.stdout.write("." * progress)
                sys.stdout.flush()
                progress = progress + 1
                assessment = self._api.get_assessment(
                    self._use_case_id, assessment["id"]
                )

            sys.stdout.write("\r")

            # print the result
            self._assessment = assessment
            if assessment["result"] == "success":
                evidences = assessment.get("details", {}).get("evidences", [])
                duration = assessment.get("duration", 0) / 1000
                global_logger.info(
                    f"{len(evidences)} evidences were successfuly uploaded, took {duration} ms"
                )
            else:
                error = assessment["error"]
                global_logger.error(f"Error in uploading evidences : {error}")

    def _check_inclusion(self, label, evidence):
        matching_evidence = []
        for e in evidence:
            if check_subset(label, e.label):
                matching_evidence.append(e)
        if not matching_evidence:
            global_logger.info(f"Missing required evidence with label ({label}).")
            return False
        if len(matching_evidence) > 1:
            stringified_evidence = [str(e.label) for e in matching_evidence]
            nl = "\n\t\t"
            global_logger.error(
                "Multiple evidence labels were found matching one requirement.\n"
                + f"\tRequirement: {label}\n"
                + f"\tEvidences: {nl}{nl.join(stringified_evidence)}"
            )
            return False
        return matching_evidence

    def _file_export(self, filename):
        global_logger.info(
            f"Saving {len(self._evidences)} evidences to {filename}.. for use_case_id={self._use_case_id} policy_pack_id={self._policy_pack_id} "
        )
        data = self._prepare_export_data()
        meta = {"client": "Credo AI Connect", "version": get_version()}
        data = json_dumps(serialize(data=data, meta=meta))
        with open(filename, "w") as f:
            f.write(data)

    def _match_requirements(self):
        missing = []
        required_labels = [e.label for e in self.get_evidence_requirements()]
        for label in required_labels:
            matching_evidence = self._check_inclusion(label, self._evidences)
            if not matching_evidence:
                missing.append(label)
            else:
                matching_evidence[0].label = label
        return not bool(missing)

    def __parse_json_api(self, json_str):
        return deserialize(json.loads(json_str))

    def _prepare_export_data(self):
        evidences = self._prepare_evidences()
        data = {
            "policy_pack_id": self._policy_pack_id,
            "models": [self._model] if self._model else None,
            "evidences": evidences,
            "$type": "assessments",
        }
        return data

    def _prepare_evidences(self):
        evidences = list(map(lambda e: e.struct(), self._evidences))
        return evidences

    def _print_evidence(self, evidence):
        for i, label in enumerate([e.label for e in evidence]):
            print(f"\nEvidence Requirement {i}:")
            pprint(label)

    def _validate_export(self):
        if not self.registered:
            global_logger.info("Governance is not registered, please register first")
            return False

        if 0 == len(self._evidences):
            global_logger.info(
                "No evidences added to governance, please add evidences first"
            )
            return False
        return True
