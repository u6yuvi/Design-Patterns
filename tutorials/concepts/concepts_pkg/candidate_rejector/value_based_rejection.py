import logging
from dataclasses import dataclass
from typing import Dict, List

from rapidfuzz import fuzz

from .base_reject_handler import REJECTHANDLER
from .load_value_json import REF_VALUES
from .utils import RefCosSim
from concepts_pkg.utils.keyvaluefound import KeyValueFound

logger = logging.getLogger("Value Based Rejection")


@dataclass
class CAND_REJECT_VALUE(REJECTHANDLER):
    """
    Candidate Rejection base on Reserved Values in Text.
    """

    cand_rejection_config: Dict = None
    clw_hierarchy: Dict = None
    keyword: str = None
    ref_values: List = None
 
    def __post_init__(
        self,
    ):
        self.ref_values = REF_VALUES[self.cand_rejection_config["filename"]][
            "values"
        ]
        self.ref_values = [i.lower() for i in self.ref_values]
        self.threshold = self.cand_rejection_config["threshold"]
        self.quicksearch = RefCosSim(self.ref_values)

    def handle(self, request: List, dropped_result=None):
        """
        Method to reject candidates using reserved values in json file.
        If the candiate text has the reserved text in the line
        i.e some threshold% cosine match, the candidate will be rejected.
        """
        logger.info("Candidate -Value Based Rejection Started...")
        if dropped_result is None:
            dropped_result = []

        dropped_idx_list = []

        if len(request)>0 and len(self.ref_values) > 0:
            if isinstance(request[0],KeyValueFound):
                for idx, candidate in enumerate(request):
                    text_query = candidate.value.match.match_string.lower()
                    #candidate.value.match.match_string
                    logger.info(f'Start dropping values from result {text_query}')

                    matched_result = self.quicksearch.find_best_match_arr(
                        [text_query], thresh=self.threshold / 100
                    )
                    if len(matched_result) > 0:
                        matched_result = {
                            i: j for i, j in matched_result.items() if len(j) > 0
                        }
                        dropped_idx_list = [
                            sorted(j, key=lambda x: x[2], reverse=True)[0][0]
                            for i, j in matched_result.items()
                        ]

                        dropped_result = [
                            cand
                            for idx, cand in enumerate(request)
                            if idx in dropped_idx_list
                        ]

                        request = [
                            cand
                            for idx, cand in enumerate(request)
                            if idx not in dropped_idx_list
                        ]
                        # print(matched_result)
            elif isinstance(request[0],dict):
                text_query = [i["candidate_text"].lower() for i in request]
                #text_query = text_query + ["abc"]
                matched_result = self.quicksearch.find_best_match_arr(
                        text_query, thresh=self.threshold / 100
                    )
                if len(matched_result) > 0:
                    matched_result = {
                            i: j for i, j in matched_result.items() if len(j) > 0
                            }
                    dropped_idx_list = [
                            sorted(j, key=lambda x: x[2], reverse=True)[0][0]
                            for i, j in matched_result.items()
                        ]

                    dropped_result = [
                            cand
                            for idx, cand in enumerate(request)
                            if idx in dropped_idx_list
                        ]

                    request = [
                            cand
                            for idx, cand in enumerate(request)
                            if idx not in dropped_idx_list
                        ]
                        # print(matched_result)

        return super().handle(request, dropped_result)
