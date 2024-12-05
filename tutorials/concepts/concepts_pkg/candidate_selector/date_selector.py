import logging
# from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


from concepts_pkg.utils.keyvaluefound import KeyValueFound
# from concepts_pkg.utils.string_match import StringFound, StringMatch

from .k2v import CAND_SELECTOR
from .utils.Invoice_date_selector import extract_dates
from .utils.tax_reg_id_selector import extract_tax_reg_id
from .utils.bol_date_selector import get_all_values


@dataclass
class INV_DATE_CAND_SELECTOR(CAND_SELECTOR):
    """
    Instantiating Invoice Date Candidate Selector log
    """

    keyword: str
    # generated_candidates : Dict
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        """
        Method to run candidate selection strategy
        """
        return extract_dates(self, generated_candidates)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict


@dataclass
class TAX_REG_ID_CAND_SELECTOR(CAND_SELECTOR):

    keyword: str
    # generated_candidates : Dict
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        """
        Method to run candidate selection strategy
        """
        return extract_tax_reg_id(self, generated_candidates)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict


@dataclass
class BOL_DATE_CAND_SELECTOR(CAND_SELECTOR):

    keyword: str
    # generated_candidates : Dict
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        """
        Method to run candidate selection strategy
        """
        return get_all_values(
            self.data["clw"],
            self.keyword_config,
            self.keyword,
            generated_candidates,
        )

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
