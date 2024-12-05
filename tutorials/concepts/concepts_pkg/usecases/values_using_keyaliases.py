from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from pydantic import BaseConfig

from concepts_pkg.candidate_generator.using_keyaliases import CAND_GENERATOR_HANDLER
from concepts_pkg.candidate_selector.k2v import CAND_SELECTOR_HANDLER
from concepts_pkg.entities import keyword as K
from concepts_pkg.repository import memrepo as M
from concepts_pkg.utils.keyvaluefound import KeyValueFound

from .base_usecase import Extraction


class KEYVALUEPAIR(Extraction):

    """
    Base Class to Run E2E Extraction for Key Value Based Layouts.
    """

    data: M.LWCLWDATA
    keyword: str
    keyword_handler: K.KeywordHandler
    doc_config: BaseConfig
    candidate_gen_handler: CAND_GENERATOR_HANDLER
    candidate_sel_handler: CAND_SELECTOR_HANDLER

    @abstractmethod
    def _get_keyaliases(self):
        """
        Get keyaliases from one of the key generation strategy.
        """
        pass

    @abstractmethod
    def get_candidates(self):
        """
        Get candidates from one of the candidate generation strategy.
        """
        pass

    # @abstractmethod
    # def execute(
    #     self,
    # ):
    #     """
    #     Method to run End to End Extraction Pipeline.
    #     """


@dataclass
class VALUES_USING_KEYALIASES(KEYVALUEPAIR):
    """
    E2E Extraction Pipeline to find the value candidate using keyword keyaliases.
    This usecase works on the following strategies:
    Step1: Keyalias Extraction - Extract keyword keyaliases using
        one of the Keyword Extract strategy.
    Step2: Value Candidate Generation - Find candidates around keyaliases
         using one of the Candidate extraction strategy.\
             Generates top-k candidates around each keyalias.
    In-progress
    Step3: Value Candidate Selection - Select the top-1 candidate using
            one or more Candidate Selection strategy.
    """

    data: M.LWCLWDATA
    keyword: str
    keyword_handler: K.KeywordHandler
    doc_config: BaseConfig
    candidate_gen_handler: CAND_GENERATOR_HANDLER
    candidate_sel_handler: CAND_SELECTOR_HANDLER

    def _get_keyaliases(
        self,
    ) -> Dict[str, List]:
        """
        Returns the keyaliases to be used for candidate generation.
        """

        return self.keyword_handler.get_keyaliases_meta_legacy(self.keyword)

    def get_candidates(self) -> Dict[str, List[KeyValueFound]]:
        """
        Method to run candidate genration strategy with the required configuration
        """

        found_candidates = self.candidate_gen_handler.generate_candidates(
            self._get_keyaliases()
        )

        return found_candidates

    def select_candidates(self) -> List[Dict]:

        """Method to run candidate selection strategy with the required configuration."""

        selected_candidate = self.candidate_sel_handler.select_candidates(
            self.get_candidates()
        )
        return selected_candidate

    def execute(
        self,
    ):
        """
        Pipeline to run the End to End Extraction
        """

        # self.keywords = self._get_keyaliases()
        # self.generated_candidates = self.get_candidates()
        self.selected_candidates = self.select_candidates()

        return self.selected_candidates
