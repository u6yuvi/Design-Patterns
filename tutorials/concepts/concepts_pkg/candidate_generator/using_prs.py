import logging
from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.ref_search import QuickSearch
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .using_keyaliases import CAND_GEN
from .utils.utils_prs import (
    create_new_clw,
    create_virtual_contours,
    get_key_cand_meta,
    get_key_cand_meta_multi,
    get_key_cand_meta_multi_test,
    get_key_cand_meta_test,
    #get_key_cand_meta_title,
    get_value_obj,
    get_virtual_contours,
)

logger = logging.getLogger("Using PRS")


@dataclass
class CAND_GEN_PRS(CAND_GEN):
    """
    Candidate Geneation using PRS Detected regions.
    """

    keyword: str
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):
        self.cand_generated_values = {}
        self.single_result = {}
        self.multi_result = {}
        self.layout_config = (
            self.keyword_config.field_config.cand_generator_stgy["USING_PRS"][
                "layout_tags"
            ]
        )
        # logger.info(self.keyword_config.field_config.cand_generator_stgy['USING_PRS']['layout_tags'])
        # logger.info(self.data["prs_text"])
        self.layout_tags = list(self.layout_config.keys())
        logger.info(f"Found Layout Configuration for : {self.layout_tags}")
        for label in self.layout_tags:
            if self.layout_config[label].get("single_line", False):
                self.single_result[label] = {
                    i: j["single"]
                    for i, j in self.data["prs_data"][label].items()#Changed due to change in data structure
                }
        logger.info(
            f"Single line results fetched for Labels : {list(self.single_result.keys())}"
        )
        # logger.info(f'line results fetched for Labels : {self.single_result}')

        for label in self.layout_tags:
            if self.layout_config[label].get("multi_line", False):
                multi_res = {
                    i: j["multiple"]
                    for i, j in self.data["prs_data"][label].items()#Changed due to change in data structure
                }
                if multi_res:
                    if list(multi_res.values())[0]:
                        self.multi_result[label] = multi_res
        logger.info(
            f"Multi line results fetched for Labels : {list(self.multi_result.keys())}"
        )

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Searches for candidates using the prs result
        w.r.t to the keyaliase region identifid.
        Candidates are selected at a line level.
        """
        logger.debug(f"<<{self.keyword}>>:PRS Based Extraction Started")
        new_clw = create_new_clw(self.data["clw"])

        if self.single_result:
            logger.info(f"PRS-Single Line Candidate Generation started...")
            #logger.info(f'Keyword Found {keywords_found}')
            for search_word, kw_locs in keywords_found.items():
                search_word_result = []
                for kw_found in kw_locs:
                    logger.info(
                        f"Candidate search starting for keyanchor {kw_found}"
                    )
                    key_cand_results = []
                    for single_label, single_res in self.single_result.items():
                        # logger.info(f'Key info:{kw_found.contour["line"][kw_found.lids[-1]]}')
                        key_cand_results.extend(
                            get_key_cand_meta_test(
                                single_res,
                                kw_found.contour["line"][kw_found.lids[-1]][
                                    "page_num"
                                ],
                                kw_found.contour["line"][kw_found.lids[-1]][
                                    "line_id"
                                ],
                                self.data["lw"],
                                single_label,
                                self.layout_config,
                            )
                        )
                    logger.info(f"Key Cand results {key_cand_results}")
                    # if prs single line results found
                    if key_cand_results:
                        for res in key_cand_results:
                            virtual_clw = get_virtual_contours(res, new_clw)
                            # logger.info(f'virtual contour {virtual_clw}')
                            search_word_result.append(
                                KeyValueFound(
                                    None,
                                    get_value_obj(virtual_clw, res.layout),
                                    100,
                                )
                            )
                values = sorted(
                    search_word_result, key=lambda x: (-x.conf, x.key_val_dist)
                )
                if values:
                    self.cand_generated_values[search_word] = values

        if self.multi_result:
            logger.info(f"PRS-Multi Line Candidate Generation started...")
            # logger.info(f'result {keywords_found}')
            for search_word, kw_locs in keywords_found.items():
                search_word_result = []
                for kw_found in kw_locs:
                    logger.info(
                        f"Candidate search starting for keyanchor {kw_found}"
                    )
                    key_cand_results = []
                    for multi_label, multi_res in self.multi_result.items():
                        multiline_res = get_key_cand_meta_multi_test(
                                multi_res,
                                kw_found.contour["line"][kw_found.lids[-1]][
                                    "page_num"
                                ],
                                kw_found.contour["line"][kw_found.lids[-1]][
                                    "line_id"
                                ],
                                multi_label,
                                self.data,
                            )
                        if multiline_res:
                            key_cand_results.extend(multiline_res
                            
                        )
                    logger.info(f"Key Cand results {key_cand_results}")
                    # if prs multi line results found
                    if key_cand_results:
                        for res in key_cand_results:
                            virtual_clw = get_virtual_contours(res, new_clw)
                            search_word_result.append(
                                KeyValueFound(
                                    None,
                                    get_value_obj(virtual_clw, res.layout),
                                    100,
                                )
                            )
                values = sorted(
                    search_word_result, key=lambda x: (-x.conf, x.key_val_dist)
                )
                if values:
                    self.cand_generated_values[search_word] = values
        return self._format_result(self.cand_generated_values)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
