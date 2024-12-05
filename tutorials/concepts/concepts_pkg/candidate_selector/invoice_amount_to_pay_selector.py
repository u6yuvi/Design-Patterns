# invoice amt_to_pay_selector.py


import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, final
import pandas as pd
from k2v_pkg.final_output import run_k2v_ml
from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch
from .k2v import CAND_SELECTOR
from .rejector_factory import CAND_REJ_FACTORY
from .utils.data_prep import  list_to_keyfound_obj_virtual_contour
from .k2v_ref import K2V_REF_CAND_SELECTOR as rej
from .utils.amount_pay1 import amt_n_curr_filter,can_gen_n_filter
from .utils.Invoice_number import get_dict
logger = logging.getLogger("AMOUNT_TO_PAY$$")
# FILTER_FUNCTIONS ={"amount_filter":amt_n_curr_filter}

# from .utils.amount_pay1 import amt_filter, curr_filter, can_gen_n_filter,amt_n_curr_filter
# from .utils.data_prep import  list_to_keyfound_obj
FILTER_FUNCTIONS ={"currency_filter":amt_n_curr_filter,"amount_filter":amt_n_curr_filter}

@dataclass
class INVO_AMT_TO_PAY_SELECTOR(CAND_SELECTOR):
    """
    Candidate Selection Strategy for invoice number.
    """

    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str

    def __post_init__(self):
        self.filter_function = FILTER_FUNCTIONS[
            self.keyword_config.field_config.cand_selector_stgy["INV_AMT_PAY"][
                "filter_function"
            ]
        ]

    def __post_init__(self):
        self.filter_function = FILTER_FUNCTIONS[
            self.keyword_config.field_config.cand_selector_stgy["INV_AMT_PAY"][
                "filter_function"
            ]
        ]

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]):

        combine_results = []
        if len(generated_candidates) > 1:
            combine_results = {}
            for cand in generated_candidates:
                for key, matched_results in cand.items():
                    combine_results[key] = matched_results

        elif len(generated_candidates) == 1:
            combine_results = generated_candidates[0]

        if combine_results and self.keyword=="amount_to_pay":
            data = get_dict(combine_results)                           #gets dictionary structure key w.r.to its value 
            final_can_gen_dict=can_gen_n_filter(data,self.data["clw"])         #getting candidates that falls along given key anchors from clw
            final_dict=self.filter_function(final_can_gen_dict,self.data["clw"],self.keyword,relax_thresh=False,key_y_can_y_diff_relax=None)  # filter out candidates
            if len(final_dict)==0:                                     # with more relaxed thresh with k2k given given results filtering candidates
                final_dict=self.filter_function(data,self.data["clw"],self.keyword,relax_thresh=True,key_y_can_y_diff_relax=None)
                if len(final_dict)==0:
                    final_dict=self.filter_function(final_can_gen_dict,self.data["clw"],self.keyword,relax_thresh=True,key_y_can_y_diff_relax=True)

            final_dict = list_to_keyfound_obj_virtual_contour(self.data["clw"],final_dict)
            
            if len(final_dict) != 0:
                # if len(request) > 1:
                #     return [request[0]]
                return final_dict
            return []

        return []

