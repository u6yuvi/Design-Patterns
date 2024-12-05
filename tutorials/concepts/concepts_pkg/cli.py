"""
Main Method to Run E2E Extraction
"""

import json
from pathlib import Path

from extraction_factory import EXTRACTION_FACTORY

import concepts_pkg
from concepts_pkg.candidate_generator import (
    CAND_GEN_KEYALIASES_SPV,
    CAND_GEN_USING_KEYALIASES,
    CAND_GENERATOR_HANDLER,
)

# from concepts_pkg.candidate_rejector import (
#     CAND_REJECT_ANA,
#     CAND_REJECT_SPV,
#     CAND_REJECT_VALUE,
# )
from concepts_pkg.candidate_selector.k2v import CAND_SELECTOR_HANDLER, K2V_CAND_SELECTOR
from concepts_pkg.doc_config import coqn_config
from concepts_pkg.entities.keyword import KeywordHandler, KeywordHeuristic, KeywordK2K
from concepts_pkg.repository.memrepo import LWCLWDATA, CLWData, LWData
from concepts_pkg.usecases.values_using_keyaliases import VALUES_USING_KEYALIASES

__PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
__DATASET_DIR = __PACKAGE_ROOT / "artifacts/datasets/test_suites/"


def load_lw_clw():
    """
    Loads LW and CLW Hierarchy from json files
    """

    with open(__DATASET_DIR / "lw_hierarchy_meta.json", "r") as file:
        lw_data = json.load(file)
    # lw_obj = LWData(lw_data)

    with open(__DATASET_DIR / "clw_hierarchy.json", "r") as file:
        clw_data = json.load(file)
    # clw_obj = CLWData(clw_data)

    return lw_data, clw_data


# print(LWCLWDATA(lw_obj,clw_obj).get_data().keys())
def get_k2k_data():
    """Get K2K Data."""
    with open(__DATASET_DIR / "k2k_results.json", "r") as file:
        k2k_results = json.load(file)
    return k2k_results


# get_data
lw, clw = load_lw_clw()
# Memrepo Object
doc_meta = {"page_height": 2170, "page_width": 1570}
lwclw_obj = LWCLWDATA(LWData(lw), CLWData(clw), doc_meta)


# get_config --loadport
# keyword_config = [i for i in coqn_config if i.field == "load_port"][0]
# --doc_issuer
# keyword_config = [i for i in coqn_config if i.field == "document_issuer"][0]
# commodity
keyword_config = [i for i in coqn_config if i.field == "commodity"][0]
# print(load_port_config.dict())

#############################Create Objects##############################

# Insantiate the  key_extraction_strategy
# keyword_k2k = KeywordK2K(get_k2k_data(), lwclw_obj.get_data_external()["clw"])
# #keyword_k2k = KeywordHeuristic(get_k2k_data,keyword_config,lwclw_obj.get_data_external()["clw"])

# # Pass the key extraction strategy object to Keyword Handler
# keyword_obj = KeywordHandler(keyword_k2k)


# Instantiate the Candidate Generation Strategy
# candidate_gen_obj = CAND_GEN_USING_KEYALIASES(
#     keyword="load_port",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_gen_obj = CAND_GEN_SPV_KEY(keyword="document_issuer",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external())

# candidate_gen_obj = CAND_GEN_USING_KEYALIASES(
#     keyword="commodity",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_gen_handler = CAND_GENERATOR_HANDLER(candidate_gen_obj)

# Instantiate the Candidate Selection Strategy
# candidate_sel_obj = K2V_CAND_SELECTOR(
#     keyword="load_port",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_sel_obj = K2V_CAND_SELECTOR(
#     keyword="document_issuer",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_sel_obj = K2V_CAND_SELECTOR(
#     keyword="commodity",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_sel_handler = CAND_SELECTOR_HANDLER(candidate_sel_obj)


# Instantiate the UseCase using the keyword extraction strategy
# usecase1_obj = VALUES_USING_KEYALIASES(
#     data=lwclw_obj,
#     keyword="load_port",
#     keyword_handler=keyword_obj,
#     doc_config=keyword_config,
#     candidate_gen_handler=candidate_gen_handler,
#     candidate_sel_handler=candidate_sel_handler,
# )

# usecase1_obj = VALUES_USING_KEYALIASES(
#     data=lwclw_obj,
#     keyword="document_issuer",
#     keyword_handler=keyword_obj,
#     doc_config=keyword_config,
#     candidate_gen_handler=candidate_gen_handler,
#     candidate_sel_handler=candidate_sel_handler,
# )

# usecase1_obj = VALUES_USING_KEYALIASES(
#     data=lwclw_obj,
#     keyword="commodity",
#     keyword_handler=keyword_obj,
#     doc_config=keyword_config,
#     candidate_gen_handler=candidate_gen_handler,
#     candidate_sel_handler=candidate_sel_handler,
# )


# Running UseCase

#  Get the candidates using one of the candidate generation strategy
# print(usecase1_obj.get_candidates())
# print(usecase1_obj.select_candidates())
# print(usecase1_obj.execute())
# usecase1_obj.get_candidates()
# usecase1_obj.get_candidates(CS)
# print(usecase1_obj.ca)


# Testing Candidate Rejection
# request = usecase1_obj.execute()
# print(request)

# Testing CAND_ANA_REJECT - Results
# print(CAND_ANA_REJ(
#     cand_rejection_config=keyword_config.field_config.cand_reject['ana_rejection'],
#     clw_hierarchy=lwclw_obj.get_data_external()['clw'],
#     keyword='load_port').handle(request, result=None)
#     )

# print(CAND_SPV_REJ(
#     cand_rejection_config=keyword_config.field_config.cand_reject['spv'],
#     clw_hierarchy=lwclw_obj.get_data_external()['clw'],
#     keyword='load_port').handle(request, result=None)
#     )

# print(
#     CAND_REJECT_VALUE(
#         cand_rejection_config=keyword_config.field_config.cand_reject["value"],
#         clw_hierarchy=lwclw_obj.get_data_external()["clw"],
#         keyword="load_port",
#     ).handle(request, dropped_result=None)
# )

# print(
#     CAND_REJECT_VALUE(
#         cand_rejection_config=keyword_config.field_config.cand_reject["value"],
#         clw_hierarchy=lwclw_obj.get_data_external()["clw"],
#         keyword="load_port",
#     ).handle(request, None)
# )


# print(obj.quicksearch.find_best_match_arr(["LUKoil KNT, Svetly, Russia".lower(),
# "abcd"]))

# print(request)

# with open( "cand_rejector_data.json", 'w') as f:
#     json.dump(request[0],f)


# cand_ana_rej_obj = CAND_REJECT_ANA(
#     cand_rejection_config=keyword_config.field_config.cand_reject["ana"],
#     clw_hierarchy=lwclw_obj.get_data_external()["clw"],
#     keyword="load_port",
# )

# cand_spv_rej_obj = CAND_REJECT_SPV(
#     cand_rejection_config=keyword_config.field_config.cand_reject["spv"],
#     clw_hierarchy=lwclw_obj.get_data_external()["clw"],
#     keyword="load_port",
# )

# cand_ana_rej_obj.set_next(cand_spv_rej_obj)

# Run CAND ANA Rejection and CAND SPV Rejection as chain of responsibility
# request, dropped_results = cand_ana_rej_obj.handle(request, None)
# print(request,dropped_results)
# print(len(request), len(dropped_results))


###########################################################################
# In Progress
# Exploring the Interface for Concepts 2.0 - Main Function


# keyword = ["load_port", "terminal"]
# cand_sel_config = "K2V"
# cand_gen_config = "USING_KEYALIASES"
# E2E_Usecase = "VALUES_USING_KEYALIASES"

# extraction_stgy, config = list(
#     keyword_config.field_config.extraction_stgy.items()
# )[0]

# factory_cls = EXTRACTION_FACTORY[extraction_stgy]
# factory_obj = factory_cls(
#     lwclw_obj=lwclw_obj,
#     keyword=keyword_config.field,
#     k2k_data=get_k2k_data(),
#     keyword_config=keyword_config,
# )

# usecase1_obj = factory_obj("VALUES_USING_KEYALIASES")

# print(usecase1_obj.execute())


########################################MultiStgy Usecase#####################

# keyword_config = [i for i in coqn_config if i.field == "commodity"][0]

# keyword_k2k = KeywordK2K(get_k2k_data(), lwclw_obj.get_data_external()["clw"])
# keyword_heurisitc = KeywordHeuristic(get_k2k_data,keyword_config,lwclw_obj.get_data_external()["clw"])

# keyword_obj1 = KeywordHandler(keyword_k2k)

# keyword_obj2 = KeywordHandler(keyword_heurisitc)


# candidate_gen_obj1 = CAND_GEN_SPV_KEY(keyword="commodity",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external())

# candidate_gen_obj2 = CAND_GEN_USING_KEYALIASES(
#     keyword="commodity",
#     keyword_config=keyword_config,
#     data=lwclw_obj.get_data_external(),
# )

# candidate_gen_handler2 = CAND_GENERATOR_HANDLER(candidate_gen_obj1)

# print(candidate_gen_obj2.generate_candidates(keyword_obj1.get_keyaliases_meta_legacy("commodity")))

# print(candidate_gen_handler2.generate_candidates(keyword_obj1.get_keyaliases_meta_legacy("commodity")))
# print(candidate_gen_handler2.generate_candidates(keyword_obj1.get_keyaliases_meta_legacy("commodity")))

# print(candidate_gen_obj2.__class__.__name__)
# candidate_gen_handler2 = CAND_GENERATOR_HANDLER(candidate_gen_obj2)


keyword = ["commodity", "terminal"]
cand_sel_config = "K2V"
cand_gen_config = "USING_KEYALIASES"
E2E_Usecase = "VALUES_USING_KEYALIASES"

extraction_stgy, config = list(
    keyword_config.field_config.extraction_stgy.items()
)[0]

factory_cls = EXTRACTION_FACTORY[extraction_stgy]

factory_obj = factory_cls(
    lwclw_obj=lwclw_obj,
    keyword=keyword_config.field,
    k2k_data=get_k2k_data(),
    keyword_config=keyword_config,
)

factory_obj(E2E_Usecase)
