import logging
from dataclasses import dataclass
from typing import Dict, List

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .k2v import CAND_SELECTOR
from .rejector_factory import CAND_REJ_FACTORY

logger = logging.getLogger("PRS-Selector")

from collections import defaultdict

# @dataclass
# class PRS_CAND_SELECTOR(CAND_SELECTOR):
#     """
#     Candidate Selection Strategy based on K2V Model and SPV Tags.
#     """

#     keyword: str
#     keyword_config: Dict
#     data: Dict
#     doc_type: str

#     def select_candidates(
#         self, generated_candidates: Dict[str, List[KeyValueFound]]
#     ):
#         """
#         Selection of the candidate based on the following strategy:
#         Case-1 If single line, text_region return the line_id
#         """
#         logger.info(generated_candidates)
#         if len(generated_candidates) == 1:
#             logger.info(f" One Strategy result found")
#             # only one stgy result found
#             if len(generated_candidates[0].keys()) == 1:
#                 logger.info(f" One Keyalias result found")
#                 # one one keyalias found
#                 if [
#                     len(value)
#                     for key, value in generated_candidates[0].items()
#                 ][0] == 1:
#                     logger.info(f" One CAND_GEN result found")
#                     # only one result found for the keyalias
#                     return list(generated_candidates[0].values())[0]
#                 # currently no strategy--return 1st result
#                 logger.info(f"More than One CAND_GEN result found")
#                 return [list(generated_candidates[0].values())[0][0]]
#             # topk to top1 keyalias - currently no strategy
#             logger.info(f"Multiple keyalias result found")
#             return [list(generated_candidates[0].values())[0][0]]
#         if len(generated_candidates) == 0:
#             logger.info(f"No strategy result found.")
#             return []
#         # result from multiple strategy
#         logger.info(f"Multiple strategy result found")
#         return [list(generated_candidates[0].values())[0][0]]


@dataclass
class PRS_CAND_SELECTOR(CAND_SELECTOR):
    """
    Candidate Selection Strategy based on K2V Model and SPV Tags.
    """

    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ):
        """
        Selection of the candidate based on the following strategy:
        Case-1 If single line, text_region return the line_id
        """
        logger.info(generated_candidates)
        results = self.unpack_results(generated_candidates)
        if results:
            return self.get_result(results)
        return []

    @staticmethod
    def unpack_results(results):
        """
        Unpack CAND_GEN results in the following Dict structure

        {"Kealias:{Layout_type:[result1,result2]}}
        """
        single = defaultdict(lambda: defaultdict(list))
        # single = namedtuple("Text_single",["res"])
        for stgy_res in results:
            for keyword, key_res in stgy_res.items():
                for keyalais_res in key_res:
                    single[keyword][keyalais_res.value.meta].append(
                        keyalais_res
                    )
        return single

    @staticmethod
    def get_text_single(result, label="Text_single"):
        """
        Select candidate from PRS-Text Single Layout region.
        """
        if result:
            for keyword, keyword_res in result.items():
                if keyword_res.get(label, False):
                    if len(keyword_res[label]) == 1:
                        # one candidate for this keyalias
                        return keyword_res[label]
                    if len(keyword_res[label]) > 1:
                        return keyword_res[label][:1]
                    return []
                return []
        return []

    @staticmethod
    def get_text_multi(result, label="Text_multi"):
        """
        Select candidate from PRS-Text-Multi Layout region.
        """
        if result:
            for keyword, keyword_res in result.items():
                if keyword_res.get(label, False):
                    if len(keyword_res[label]) == 1:
                        # one candidate for this keyalias
                        return keyword_res[label]
                    if len(keyword_res[label]) > 1:
                        return keyword_res[label][:1]
                    return []
                return []
        return []

    @staticmethod
    def get_title_iou_single(result):
        """
        Select candidate from PRS-Title-IOU Single Layout region.
        """
        if result:
            for keyword, keyword_res in result.items():
                if keyword_res.get("Title_iou_single", False):
                    if len(keyword_res["Title_iou_single"]) == 1:
                        return keyword_res["Title_iou_single"]
                    if len(keyword_res["Title_iou_single"]) > 1:
                        return keyword_res["Title_iou_single"][:1]
                    return []
                return []
        return []

    @staticmethod
    def get_title_single(result):
        """
        Select candidate from PRS-Title Single Layout region.
        """
        if result:
            for keyword, keyword_res in result.items():
                if keyword_res.get("Title_single", False):
                    if len(keyword_res["Title_single"]) == 1:
                        return keyword_res["Title_single"]
                    if len(keyword_res["Title_single"]) > 1:
                        return keyword_res["Title_single"][:1]
                    return []
                return []
        return []

    def get_result(self, result):
        """
        Run Candidate Selection logic
        """
        f_result = self.get_text_single(result)
        if f_result:
            logger.info(f"Found result in Text-Single")
            return f_result
        f_result = self.get_title_iou_single(result)
        if f_result:
            logger.info(f"Found result in Title-IOU-Single")
            return f_result
        f_result = self.get_text_multi(result = result,label="Text_multi")
        if f_result:
            logger.info(f"Found result in Text-Multi")
            return f_result
        f_result = self.get_title_single(result)
        if f_result:
            logger.info(f"Found result in Title-Single")
            return f_result
        f_result = self.get_text_multi(result = result,label="Title_multi")
        if f_result:
            logger.info(f"Found result in Title-Multi")
            return f_result
        return []

