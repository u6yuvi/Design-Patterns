from dataclasses import dataclass
from typing import Dict, Type

from pydantic import BaseModel

from concepts_pkg.candidate_generator import (
    CAND_GEN,
    CAND_GEN_KEYALIASES_SPV,
    CAND_GEN_PRS,
    CAND_GEN_SPV,
    CAND_GEN_USING_KEYALIASES,
    CAND_GENERATOR_HANDLER,
    CAND_GEN_QTY_SPV,
    CAND_GEN_CONT,
    CAND_GEN_COUNTRY,
)
from concepts_pkg.candidate_generator.using_keyaliases import (
    CAND_DATE_ISSUE,
    CAND_DATE_OF_ISSUE_KEYWORD_THEN_VALUE,
)

from concepts_pkg.candidate_selector import (
    CAND_SELECTOR_HANDLER,
    DEFAULT_CAND_SELECTOR,
    HEURISTIC_CAND_SELECTOR,
    INV_DATE_CAND_SELECTOR,
    INVO_NUM_CAND_SELECTOR,
    K2V_CAND_SELECTOR,
    K2V_REF_CAND_SELECTOR,
    PRS_CAND_SELECTOR,
    INVO_AMT_TO_PAY_SELECTOR,
    TAX_REG_ID_CAND_SELECTOR,
    INV_BANK_CAND_SELECTOR,
    BOL_DATE_CAND_SELECTOR,
)

# from concepts_pkg.candidate_rejector import CAND_REJECT_ANA
from concepts_pkg.entities.keyword import (
    Keyword,
    KeywordHandler,
    KeywordHeuristic,
    KeywordK2K,
)
from concepts_pkg.repository.memrepo import LWCLWDATA
from concepts_pkg.usecases import KEYVALUEPAIR, VALUES_USING_KEYALIASES

KEYWORD_FACTORY = {"K2K": KeywordK2K, "Heuristic": KeywordHeuristic}

CAND_GEN_FACTORY = {
    "USING_KEYALIASES": CAND_GEN_USING_KEYALIASES,
    "USING_KEYALIASES_SPV": CAND_GEN_KEYALIASES_SPV,
    "USING_SPV": CAND_GEN_SPV,
    "USING_SPV_QTY": CAND_GEN_QTY_SPV,
    "USING_PRS": CAND_GEN_PRS,
    "USING_VALUE": CAND_GEN_COUNTRY,
    "USING_DATE": CAND_DATE_ISSUE,
    "USING_DATE_BOL": CAND_DATE_OF_ISSUE_KEYWORD_THEN_VALUE,
    "USING_CONTOUR":CAND_GEN_CONT,
}

CAND_SEL_FACTORY = {
    "K2V": K2V_CAND_SELECTOR,
    "passthrough": DEFAULT_CAND_SELECTOR,
    "K2V_REF": K2V_REF_CAND_SELECTOR,
    "PRS_SELECTOR": PRS_CAND_SELECTOR,
    "INV_DATE_SELECTOR": INV_DATE_CAND_SELECTOR,
    "Heuristic": HEURISTIC_CAND_SELECTOR,
    "INV_REF": INVO_NUM_CAND_SELECTOR,
    "INV_AMT_PAY": INVO_AMT_TO_PAY_SELECTOR,
    "TAX_REG_ID": TAX_REG_ID_CAND_SELECTOR,
    "INV_BANK": INV_BANK_CAND_SELECTOR,
    "BOL_DATE": BOL_DATE_CAND_SELECTOR,
}


@dataclass
class KEYVALUEPAIR_EXTRACTION_FACTORY:
    # usecase : Type[ KEYVALUEPAIR]
    lwclw_obj: Type[LWCLWDATA]
    keyword: str
    k2k_data: Dict
    # keyword_handler: Type[Keyword]
    keyword_config: BaseModel
    doc_type: str
    # candidate_gen_handler: Type[K2V_CAND_SELECTOR]
    # candidate_sel_handler: Type[CAND_SELECTOR]
    def __call__(self, usecase):

        # Instead of usecase we can pass strategy
        if usecase == "VALUES_USING_KEYALIASES":

            return run_keyvalue_pair_extraction(
                self.keyword,
                self.keyword_config,
                self.k2k_data,
                self.lwclw_obj,
                self.doc_type,
            )


def run_keyvalue_pair_extraction(
    keyword, keyword_config, k2k_data, lwclw_obj, doc_type
):

    """
    Key Value Pair Extraction pipeline for Values using Keyaliases
    extraction strategy.
    """

    extraction_results = {}
    # Step -1
    key_gen_results = []
    for (
        keyword_extraction_stgy,
        config,
    ) in keyword_config.field_config.key_extraction_stgy.items():

        # create keyword_obj,cand_gen_object,cand_sel_object etc

        keyword_obj = KEYWORD_FACTORY[keyword_extraction_stgy](
            k2k_data, keyword_config, lwclw_obj.data["clw"]
        )
        keyword_handler_obj = KeywordHandler(keyword_obj)

        key_gen_results.append(
            keyword_handler_obj.get_keyaliases_meta(keyword=keyword)
        )
    extraction_results[
        keyword_handler_obj.__class__.__name__
    ] = key_gen_results

    # Step -2
    cand_gen_results = []
    for (
        cand_gen_stgy,
        config,
    ) in keyword_config.field_config.cand_generator_stgy.items():
        cand_gen_obj = CAND_GEN_FACTORY[cand_gen_stgy](
            keyword=keyword,
            keyword_config=keyword_config,
            data=lwclw_obj.data,
        )
        cand_gen_handler_obj = CAND_GENERATOR_HANDLER(cand_gen_obj)
        cand_gen_results.append(
            cand_gen_handler_obj.generate_candidates(
                extraction_results[keyword_handler_obj.__class__.__name__][0]
            )
        )

    extraction_results[
        cand_gen_handler_obj.__class__.__name__
    ] = cand_gen_results

    # print(extraction_results)
    # Step -3
    cand_sel_result = []
    for (
        cand_sel_stgy,
        cand_sel_config,
    ) in keyword_config.field_config.cand_selector_stgy.items():

        candidate_sel_obj = CAND_SEL_FACTORY[cand_sel_stgy](
            keyword=keyword,
            keyword_config=keyword_config,
            data=lwclw_obj.data,
            doc_type=doc_type,
        )
        # print("Cand_sel_obj",candidate_sel_obj)
        candidate_sel_handler_obj = CAND_SELECTOR_HANDLER(
            candidate_sel_obj, cand_sel_config
        )
        # print(cand_sel_config)

        cand_sel_result.append(
            candidate_sel_handler_obj.select_candidates(extraction_results)
        )

    # TODO Make extraction result keyname static as curently it will break
    # if no cand_sel_handler is created
    extraction_results[
        candidate_sel_handler_obj.__class__.__name__
    ] = cand_sel_result

    # print(extraction_results)
    return extraction_results


def run_spv_threshold_extraction(
    keyword, keyword_obj, k2k_data, lwclw_obj, doc_type
):
    # TODO For new strategy in future for no selector no keyword strategy
    extraction_results = {}

    return extraction_results


def run_key_value_pair_heuristic():
    """
    key-gen/can-gen : This function takes lw/clw and generates candidates
    can-selection is based on regex and some SPV based conditions

    """
    extraction_result = {}
    return extraction_result


EXTRACTION_FACTORY = {
    "KEYVALUEPAIR_EXTRACTION": KEYVALUEPAIR_EXTRACTION_FACTORY,
}


# TODO  Selective Candidate Selector Strategy for different previous step in pipeline.
#
# Pass the object to the next step in the pipeline.
# Let the pipeline component internally call the previous component pipeline using Handler
