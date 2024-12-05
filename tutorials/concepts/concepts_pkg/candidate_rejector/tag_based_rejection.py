import logging
from dataclasses import dataclass
from typing import Dict, List
from copy import deepcopy

from concepts_pkg.utils.keyvaluefound import KeyValueFound

from .base_reject_handler import REJECTHANDLER

logger = logging.getLogger("Tag Based Rejection")


@dataclass
class CAND_REJECT_ANA(REJECTHANDLER):
    """
    Candidate Rejection base on ANA Tags of Text Tokens.
    """

    cand_rejection_config: Dict = None
    clw_hierarchy: Dict = None
    keyword: str = None

    def handle(self, request: List, dropped_result=None):
        """
        Method to reject candidates using threshold on the % of
        ANA token tags in a line. If the candiate text has all ANA tags
         as "Anchor" i.e 100% of tags are "Anchor" , the candidate will be rejected.
        """
        logger.info("ANA Based Rejection Started...")
        if dropped_result is None:
            dropped_result = []
        drop_idx_list = []

        if len(request) > 0:
            threshold = self.cand_rejection_config["reject"]["threshold"]
            if isinstance(request[0],dict):
                for idx, candidate in enumerate(request):
                    logger.info(f'ana rejection ')
                    nonanchor_conf_percent = get_anchor_confidence(
                        self.clw_hierarchy, [candidate], self.cand_rejection_config
                    )

                    logger.debug(f"Non Anchor Conf % : {nonanchor_conf_percent}")
                    # print(nonanchor_conf_percent)

                    if nonanchor_conf_percent == threshold:
                        dropped_result.append(candidate)
                        drop_idx_list.append(idx)
                request = [
                    cand
                    for idx, cand in enumerate(request)
                    if idx not in drop_idx_list
                ]
            elif isinstance(request[0],KeyValueFound):
                result = []
                for idx, candidate in enumerate(request):
                    # logger.info(f'Start dropping anchor lids from result {candidate}')
                    candidate_updated = drop_anchor_lids([candidate], self.cand_rejection_config,threshold)
                    if candidate_updated:
                        result.extend(candidate_updated)
                request = result
                dropped_result =[]

        return super().handle(request, dropped_result)


@dataclass
class CAND_REJECT_SPV(REJECTHANDLER):
    """
    Candidate Rejection base on SPV Tags of Text tokens.
    """

    cand_rejection_config: Dict = None
    clw_hierarchy: Dict = None
    keyword: str = None

    def handle(self, request: List, dropped_result=None):
        """
        Method to reject candidates using threshold on the % of
        ANA token tags in a line. If the candiate text has all ANA tags
         as "O" i.e 100% , the candidate will be rejected.
        """
        logger.info("SPV Based Rejection Started...")
        if dropped_result is None:
            dropped_result = []

        drop_idx_list = []
        if len(request) > 0:
            threshold = self.cand_rejection_config["reject"]["threshold"]
            if isinstance(request[0],dict):
                for idx, candidate in enumerate(request):
                    spv_reject_percent = get_spv_confidence(
                        self.clw_hierarchy, [candidate], self.cand_rejection_config
                    )

                    logger.debug(f"SPV Reject % : {spv_reject_percent}")

                    if spv_reject_percent > threshold:
                        dropped_result.append(candidate)
                        drop_idx_list.append(idx)
                # print(drop_idx_list)
                request = [
                    cand
                    for idx, cand in enumerate(request)
                    if idx not in drop_idx_list
                ]
            elif isinstance(request[0],KeyValueFound):
                result = []
                for idx, candidate in enumerate(request):
                    logger.info(f'Start dropping other spv tags lids from result {candidate}')
                    new_candidate = deepcopy(candidate)
                    candidate_updated = drop_other_spv_lids([new_candidate], self.cand_rejection_config,threshold)
                    if candidate_updated:
                        result.extend(candidate_updated)
                request = result
                dropped_result =[]
            
        return super().handle(request, dropped_result)


def get_anchor_confidence(
    clw_hierarchy: Dict, cand_list: List, doc_settings: Dict
):

    """
    Method to calculate Non Anchor Confidence % for a candidate.
    """
    if doc_settings.get("reject", None).get("tags"):
        anchor_tag = doc_settings["reject"]["tags"]
        anchor_count = 0
        anchor_percent = 0
        anchor_len = 0
        for line in clw_hierarchy[cand_list[0]["cand_cid"]]["line"].items():
            if line[1]["line_id"] == cand_list[0]["cand_lwhlid"]:
                ana_labels = line[1]["meta"]["ana"]["clean_text_tags"]
                anchor_len = len(ana_labels)
                anchor_count = len(
                    [label for label in ana_labels if label in anchor_tag]
                )
                anchor_percent = (
                    (anchor_count / anchor_len) * 100 if anchor_len != 0 else 0
                )
                return anchor_percent
        return 0
            #logger.info(f'Start elimination...')
    return -99


def get_spv_confidence(
    clw_hierarchy: Dict, cand_list: List, doc_settings: Dict
):
    """
    Method to calculate SPV Reject Tag Confidence % for a candidate.
    """
    if doc_settings.get("reject", None).get("tags"):
        spv_tag = doc_settings["reject"]["tags"]
        spv_rej_count = 0
        tags_len = 0
        for line in clw_hierarchy[cand_list[0]["cand_cid"]]["line"].items():
            if line[1]["line_id"] == cand_list[0]["cand_lwhlid"]:
                spv_labels = line[1]["meta"]["spv"]["clean_text_tags"]
                tags_len = len(spv_labels)
                spv_rej_count = len(
                    [label for label in spv_labels if label in spv_tag]
                )
                spv_rej_percent = (
                    (spv_rej_count / tags_len) * 100
                    if spv_rej_count != 0
                    else 0
                )
                return spv_rej_percent
        return 0
    return -99

def drop_other_spv_lids(cand_list: List, doc_settings: Dict,threshold: int
):
    """
    Drop lines with reject spv tags in the Multiline result based on a given threshold.
    """
    if doc_settings.get("reject", None).get("tags"):
        spv_tag = doc_settings["reject"]["tags"]
        spv_rej_count = 0
        tags_len = 0
        drop_lids = []
        contour_res = cand_list[0].value.contour
        for lid, res in contour_res["line"].items():
            spv_labels =res["meta"]["spv"]["clean_text_tags"]
            logger.info(f'SPV Labels: {spv_labels} {res["text"]}')
            tags_len = len(spv_labels)
            spv_rej_count = len(
                [label for label in spv_labels if label in spv_tag]
            )
            spv_rej_percent = (
                (spv_rej_count / tags_len) * 100
                if spv_rej_count != 0
                else 0
            )
            if spv_rej_percent>= threshold:
                drop_lids.append(lid)
        logger.info(f'{drop_lids} getting dropped from {cand_list[0].value.lids}')
        cand_list[0].value.lids = [i for i in cand_list[0].value.lids if i not in drop_lids]
        if cand_list[0].value.lids:
            updated_contour = {}
            for lid , res in contour_res['line'].items():
                if lid not in drop_lids:
                    updated_contour[lid] = res
            cand_list[0].value.contour["line"] = updated_contour
            #logger.info(f'Updated result {cand_list}')
        else:
            cand_list = []
    return  cand_list

def drop_anchor_lids(cand_list: List, doc_settings: Dict,threshold: int
):
    """
    Drop Anchor lines in the Multiline result based on a given threshold.
    """
    if doc_settings.get("reject", None).get("tags"):
        anchor_tag = doc_settings["reject"]["tags"]
        anchor_count = 0
        anchor_percent = 0
        anchor_len = 0
        drop_lids = []
        contour_res = cand_list[0].value.contour
        for lid, res in contour_res['line'].items():
            ana_labels = res["meta"]["ana"]["clean_text_tags"]
            logger.info(f'ANA Labels: {ana_labels} {res["text"]}')
            anchor_len = len(ana_labels)
            anchor_count = len(
                [label for label in ana_labels if label in anchor_tag]
            )
            anchor_percent = (
                (anchor_count / anchor_len) * 100 if anchor_len != 0 else 0
            )
            if anchor_percent == threshold:
                drop_lids.append(lid)
        logger.info(f'{drop_lids} getting dropped from {cand_list[0].value.lids}')
        cand_list[0].value.lids = [i for i in cand_list[0].value.lids if i not in drop_lids]
        if cand_list[0].value.lids:
            updated_contour = {}
            for lid , res in contour_res['line'].items():
                if lid not in drop_lids:
                    updated_contour[lid] = res
            cand_list[0].value.contour["line"] = updated_contour
            #logger.info(f'Updated result {cand_list[0].value}')
        else:
            cand_list = []
    return  cand_list

# @dataclass
# class CAND_ANA_REJ(ABSTRACTHANDLER):
#     """
#     Candidate Rejection base on ANA Tags of Text Tokens.
#     """
#     cand_rejection_config : Dict = None
#     clw_hierarchy : Dict = None
#     keyword : str =  None

#     def handle(self,request, result):
#         """
#         Method to reject candidates using threshold on the % of
#         ANA token tags in a line. If the candiate text has all ANA tags
#          as "O" i.e 100% , the candidate will be rejected.
#         """
#         print('ANA Rejection Started...')
#         if result is None:
#             result = []

#         if len(request)>0:
#             for candidate in request:
#                 #print("key",candidate)
#                 nonanchor_conf_percent = get_nonanchor_confidence(self.clw_hierarchy, [candidate], self.cand_rejection_config)

#                 print('ana score',nonanchor_conf_percent)
#                 if nonanchor_conf_percent < 100:
#                     result.append(candidate)

#         return super().handle(request,result)


# @dataclass
# class CAND_SPV_REJ(ABSTRACTHANDLER):
#     """
#     Candidate Rejection base on SPV Tags of Text tokens.
#     """

#     cand_rejection_config : Dict = None
#     clw_hierarchy : Dict = None
#     keyword : str =  None

#     def handle(self,request, result):
#         """
#         Method to reject candidates using threshold on the % of
#         ANA token tags in a line. If the candiate text has all ANA tags
#          as "O" i.e 100% , the candidate will be rejected.
#         """
#         print('SPV Rejection Started...')
#         if result is None:
#             result = []
#         else:
#             request = result
#             result = []

#         if len(request)>0:
#             for candidate in request:
#                 #print("key",candidate)
#                 spv_reject_percent = get_spv_confidence(self.clw_hierarchy, [candidate], self.cand_rejection_config)
#                 print('score',spv_reject_percent)
#                 if spv_reject_percent < 70:
#                     result.append(candidate)
#         print("spv_res",result)
#         return super().handle(request,result)


# def rejection_based_on_spv(cand_list, doc_settings, clw_hierarchy, keyword):
#     spv_final_result= []
#     for candidate in cand_list:
#         spv_rej_percent = get_spv_confidence(clw_hierarchy, [candidate], doc_settings)
#         if spv_rej_percent < 70:
#             spv_final_result.append(candidate)
#     return spv_final_result


# def rejection_based_on_ana(cand_list, doc_settings, clw_hierarchy, keyword):
#     ana_final_result = list()
#     for candidate in cand_list:
#         nonanchor_conf_percent = get_nonanchor_confidence(clw_hierarchy, [candidate], doc_settings)
#         if nonanchor_conf_percent < 100:
#             ana_final_result.append(candidate)
#     return ana_final_result
