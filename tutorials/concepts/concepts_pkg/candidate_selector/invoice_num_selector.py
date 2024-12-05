import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from k2v_pkg.final_output import run_k2v_ml

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .k2v import CAND_SELECTOR
from .rejector_factory import CAND_REJ_FACTORY
from .utils.data_prep import  list_to_keyfound_obj
from .utils.Invoice_number import *


logger = logging.getLogger("IN#")
from .k2v_ref import K2V_REF_CAND_SELECTOR as rej



@dataclass
class INVO_NUM_CAND_SELECTOR(CAND_SELECTOR):
    """
    Candidate Selection Strategy for invoice number.
    """

    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str


    
    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ):  
        combine_results = {}
        # if result came from multiple cand_gen strategies,combine into one
        if len(generated_candidates) > 1:
            combine_results = {}
            for cand in generated_candidates:
                for key, matched_results in cand.items():
                    combine_results[key] = matched_results
        elif len(generated_candidates) == 1:
            combine_results = generated_candidates[0]

        if combine_results:
            return get_can(self,combine_results,self.data["clw"])

        return []


    