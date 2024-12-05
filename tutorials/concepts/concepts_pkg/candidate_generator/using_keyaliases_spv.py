import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.ref_search import QuickSearch
from concepts_pkg.utils.string_match import StringMatch

from .using_keyaliases import CAND_GEN
from .utils.diagonal_contours import search_within_limited_contours
from .utils.entity_extraction import get_entity
from .utils.utils_gen_search import search_within_associations
from .utils.utils_spv import extract_candidate_spv

logger = logging.getLogger("Using SPV tags")


@dataclass
class CAND_GEN_KEYALIASES_SPV(CAND_GEN):
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict
    # config_settings : field(init = False)

    def __post_init__(
        self,
    ):
        # self.config_settings = self.doc_config['fields_to_extract'][self.keyword]
        self.config_settings = self.keyword_config.field_config.dict()
        # self.value_func = self.config_settings.get("value_function", None)
        self.directions = self.config_settings.get(
            "useful_directions", ["top", "right", "bottom", "left"]
        )
        self.diagonal_contours = self.config_settings.get(
            "diagonal_flag", False
        )
        self.cand_generated_values = dict()

        self.extraction_stgy_config = (
            self.keyword_config.field_config.cand_generator_stgy[
                "USING_KEYALIASES_SPV"
            ]
        )

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        logger.debug(
            f"<<{self.keyword}>>: Value then Keyword based Extraction Started"
        )

        value_locs = list()
        search_word_result = list()
        pointer_dict = defaultdict(list)
        # if self.value_func is not None:
        # for cid, contour in clw_hierarchy.items():
        result = extract_candidate_spv(
            self.data["clw"],
            input_tags=self.extraction_stgy_config["spv_tag"],
            tag_threshold=self.extraction_stgy_config["tag_threshold"],
        )
        for i, val_obj in enumerate(result):
            value_locs.append(val_obj)
        # Now look for keywords near values found
        for search_word, kw_locs in keywords_found.items():
            # Within contours
            #         print("search_word",search_word)
            for val_found in value_locs:
                #             print("check",val_found.__str__())
                kw_dir = "within_contour"
                kw_found = [
                    kw_found
                    for kw_found in kw_locs
                    if kw_found.cid == val_found.cid
                ]
                #             print("within_contour_keyword",kw_found[0].match.match_text)
                if kw_found:
                    search_word_result.append(
                        KeyValueFound(kw_found[0], val_found, 100)
                    )

                    pointer_dict[val_found.cid].extend(
                        [lid for lid in val_found.lids]
                    )
                    # print("within_contour",pointer_dict[val_found.cid])
                # print("DSFSDF",kw_found,val_found)
                ass_cnts = search_within_associations(
                    self.data["clw"],
                    (val_found.cid),
                    line_id=None,
                    useful_directions=self.directions,
                )
                # print("association_countor",ass_cnts,val_found.cid,val_found.__str__())
                kw_found = [
                    kw_found
                    for kw_found in kw_locs
                    if kw_found.cid in ass_cnts
                ]

                if kw_found:
                    for kw in kw_found:
                        # ass_ids = [(ass_id) for ass_dir, ass_id in ass_cnts]

                        if (kw.cid) in ass_cnts:
                            # kw_ass_id = ass_cnts.index((kw.cid))
                            # kw_dir = ass_ids_dir[kw_ass_id][0]
                            kw_dir = None
                            # print("keyword",kw ,val_found.match.match_string)
                            search_word_result.append(
                                KeyValueFound(kw, val_found, 100)
                            )
                            pointer_dict[val_found.cid].extend(
                                [lid for lid in val_found.lids]
                            )
            #                         print("Association",pointer_dict[val_found.cid])
            # logger.debug(f"Value found in asssociation {result_values[-1]}")

            # values = sorted(search_word_result, key=lambda x: (-x.conf, x.key_val_dist))
            self.cand_generated_values[search_word] = search_word_result

        search_word_result = list()
        cid_lst = list(pointer_dict.keys())
        if len(self.cand_generated_values) > 0:
            for i, val_obj in enumerate(result):
                # for val_obj in val_lst:
                if val_obj.cid in cid_lst:
                    for lid in val_obj.lids:
                        if lid in pointer_dict[val_obj.cid]:
                            # TODO change to multiline
                            pass
                        else:
                            search_word_result.append(
                                KeyValueFound(None, val_obj, 100)
                            )
                else:
                    search_word_result.append(
                        KeyValueFound(None, val_obj, 100)
                    )
            self.cand_generated_values["no_keyword"] = search_word_result
            return self._format_result(self.cand_generated_values)

        elif len(result) > 0:
            for i, val_obj in enumerate(result):
                # for val_obj in val_lst:
                search_word_result.append(KeyValueFound(None, val_obj, 100))
            self.cand_generated_values["no_keyword"] = search_word_result

            return self._format_result(self.cand_generated_values)

        else:
            return self._format_result(self.cand_generated_values)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
