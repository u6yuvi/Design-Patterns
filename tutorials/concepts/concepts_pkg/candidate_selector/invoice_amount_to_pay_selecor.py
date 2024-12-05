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



logger = logging.getLogger("AMOUNT_TO_PAY$$")
from .k2v_ref import K2V_REF_CAND_SELECTOR as rej

from .utils.amount_pay1 import *
from .utils.data_prep import  list_to_keyfound_obj
from .utils.Invoice_number import get_dict
@dataclass
class INVO_AMT_TO_PAY_SELECTOR(CAND_SELECTOR):
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

        combine_results = []
        if len(generated_candidates) > 1:
            combine_results = {}
            for cand in generated_candidates:
                for key, matched_results in cand.items():
                    combine_results[key] = matched_results

        elif len(generated_candidates) == 1:
            combine_results = generated_candidates[0]

        if combine_results:
            data = get_dict(combine_results)

            if self.keyword=="amount_to_pay":
                final_dict=can_gen_n_filter(data,self.data["clw"])
                final_dict=amt_filter(final_dict)
            
            if self.keyword=="currency_of_amount":
                # final_dict=can_gen_currency_fil(data,self.data["clw"])
                final_dict=can_gen_n_filter(data,self.data["clw"])
                final_dict=curr_filter(final_dict)


            request = rej.candidate_rejector(self, final_dict)
            request = list_to_keyfound_obj(self.data["clw"], request)
            if len(request) != 0:
                if len(request) > 1:
                    return [request[0]]
                return request
            return []
        return []

