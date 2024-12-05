import logging
from dataclasses import dataclass, field
from typing import Dict

from pydantic import BaseModel

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.ref_search import QuickSearch
from concepts_pkg.utils.string_match import StringMatch , StringFound

from .using_keyaliases import CAND_GEN
from .utils.utils_spv import spv_extraction_stgy_map, extract_qty_unit_qty_type_from_spv

logger = logging.getLogger("Using SPV tags")


@dataclass
class CAND_GEN_SPV(CAND_GEN):
    """
    Candidate Generation using SPV Tags
    """

    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):

        # self.extraction_stgy = {}

        self.extraction_stgy = (
            self.keyword_config.field_config.cand_generator_stgy["USING_SPV"]
        )

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the spv result for both
        single line and multiline results.
        """

        extaction_stgy_name = list(self.extraction_stgy.keys())[0]
        logger.info(f"{extaction_stgy_name} : SPV-Extraction Strategy Found")
        result = spv_extraction_stgy_map[extaction_stgy_name](
            self.extraction_stgy, self.data
        )
        return self._format_result(result)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict

@dataclass
class CAND_GEN_QTY_SPV(CAND_GEN):
    
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):

        # self.extraction_stgy = {}

        self.extraction_stgy = (
            self.keyword_config.field_config.cand_generator_stgy["USING_SPV_QTY"]
        )

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the spv and relative locations result for both
        single line and multiline results.
        """
        keyword_dict ={ "quantity":"CARDINAL","unit_of_measurement":"UNIT","quantity_type":"QUANTITY_TYPE"}
        keyword_tag = keyword_dict[self.keyword]
        tags = set(keyword_dict.values())
        result_values = list()
        self.cand_generated_values = {}
        # extaction_stgy_name = list(self.extraction_stgy.keys())[0]
        # logger.info(f"{extaction_stgy_name} : SPV-Extraction Strategy Found")
        result_dict = extract_qty_unit_qty_type_from_spv(self.data["clw"],keyword_tag,tags)
        for _, values in result_dict.items():
            for value in values:
                temp_match_obj = StringMatch(value["end"],100,value["start"],value["text"])
                temp_value_obj = StringFound(self.data["clw"][value["contour_id"]],[value["line_id"]],temp_match_obj)
                result_values.append(KeyValueFound(None,temp_value_obj,100))
        self.cand_generated_values["no_keyword"] = result_values
        return self._format_result(self.cand_generated_values)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
 
