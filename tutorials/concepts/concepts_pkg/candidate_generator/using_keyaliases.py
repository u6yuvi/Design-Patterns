import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.ref_search import QuickSearch

# from ..doc_config import coqn_eng_config
from concepts_pkg.utils.string_match import StringMatch
from .utils.diagonal_contours import search_within_limited_contours
from .utils.entity_extraction import get_entity
from .utils.utils_gen_search import search_within_associations
from .utils.utils_gen_search import search_all_contours_ref,search_all_words, get_values, find_date, clean_forwardeditems,search_all_words_ref
from concepts.concepts_pkg.entities.utils import get_keywords

logger = logging.getLogger("Using Keyaliases")


class CAND_GEN(ABC):
    """
    Interface to Candidate Generation.
    """

    # @abstractmethod
    # def _quick_search(self, n_best=5):
    #     """Instantiate the Quick Search with clw hierarchy"""

    @abstractmethod
    def generate_candidates(self, keywords_found: Dict[str, StringMatch]):
        """
        Abstract Method to generate candidates using keyaliases."""


@dataclass
class CAND_GEN_USING_KEYALIASES(CAND_GEN):
    """
    Candidate Generation Strategy which uses keyword keyaliases and search \
        for nearby candidates in neighbouring and within contours.
    """

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

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)

    # def get_keyword_config(
    #     self,
    # ):
    #     """
    #     Get the keyword config.
    #     """
    #     return self.config_settings

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Searches for candidates in the within and neighbour contours
        w.r.t to the keyaliase contour.
        Candidates are selected at a line level.
        """
        logger.debug(
            f"<<{self.keyword}>>: Keyword Then Value based Extraction Started"
        )
        candidate_logger = []
        self.cand_generated_values = {}
        for search_word, kw_locs in keywords_found.items():
            search_word_result = []
            # Within contours
            for kw_found in kw_locs:
                # if self.value_func is not None:
                result = get_entity(
                    kw_found.contour, kw_found, self.config_settings, None
                )
                for val_found, conf in result:
                    search_word_result.append(
                        KeyValueFound(kw_found, val_found, conf)
                    )
                    if val_found.cid not in candidate_logger:
                        candidate_logger.append(val_found.cid)
            # Within Associations
            # values = get_values(config_settings, clw_hierarchy)
            for kw_found in kw_locs:
                ass_contours = search_within_associations(
                    self.data["clw"],
                    kw_found.cid,
                    kw_found.lids[-1],
                    useful_directions=self.directions,
                )
                #
                if self.diagonal_contours:
                    try:
                        ass_contours = search_within_limited_contours(
                            self.data["clw"],
                            ass_contours,
                            kw_found.cid,
                            kw_found.lids[-1],
                            candidate_logger,
                        )
                    except Exception as e:
                        logger.warning(
                            f"exception in diagonal contour {str(e)}"
                        )
                for contour_dir, ass_contours_list in ass_contours.items():
                    for ass_contour in ass_contours_list:
                        ass_id = list(ass_contour.keys())[0]

                        # if self.value_func is not None:
                        result = get_entity(
                            ass_contour[ass_id],
                            kw_found,
                            self.config_settings,
                            self._quick_search(),
                        )
                        for val_found, conf in result:
                            search_word_result.append(
                                KeyValueFound(kw_found, val_found, conf)
                            )
                            if val_found.cid not in candidate_logger:
                                candidate_logger.append(val_found.cid)
            values = sorted(
                search_word_result, key=lambda x: (-x.conf, x.key_val_dist)
            )
            self.cand_generated_values[search_word] = values
        return self._format_result(self.cand_generated_values)

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict


# @dataclass
# class SEARCH_CANDIDATE_HEURISTIC:


@dataclass
class CAND_GENERATOR_HANDLER:
    """
    Interface to Candidate Generation Step."""

    cand_generator_obj: CAND_GEN

    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Interface method to generate candidates.
        """

        return self.cand_generator_obj.generate_candidates(keywords_found)

@dataclass
class CAND_GEN_COUNTRY(CAND_GEN):
    
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):

        # self.extraction_stgy = {}
        self.config_settings = self.keyword_config.field_config.dict()
        # self.value_func = self.config_settings.get("value_function", None)
        self.directions = self.config_settings.get(
            "useful_directions", ["top", "right", "bottom", "left"]
        )
        self.diagonal_contours = self.config_settings.get(
            "diagonal_flag", False
        )
        self.cand_generated_values = dict()


        self.extraction_stgy = (
            self.keyword_config.field_config.cand_generator_stgy["USING_VALUE"]
        )

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)


    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the spv and relative locations result for both
        single line and multiline results.
        """
        logger.debug(f"<<{self.keyword}>>: Value Then Keyword based Extraction Started")
        # value_func = config_settings.get('value_function', None)
        # directions = config_settings.get("useful_directions", ["top", "left", "bottom", "right"])
        # return_wo_keyword = config_settings.get("return_wo_keyword", "True")

        # keywords_found = get_keywords(clw_hierarchy, config_settings, quick_search)
        values = get_values(self.config_settings, self.data["clw"])
        result_values = list()
        value_locs = list()

        self.cand_generated_values = {}
        # Find values in document first
        for val in values:
            found = search_all_contours_ref(self.data["clw"], val, self._quick_search())
            # TODO make value confidence configurable
            for val_found in found:
                val_found.conf = 15
                value_locs.append(val_found)
        
        for search_word, kw_locs in keywords_found.items():
        # Within contours
            for val_found in value_locs:
                kw_found = [kw_found for kw_found in kw_locs if kw_found.cid == val_found.cid]
                if kw_found:
                    result_values.append(KeyValueFound(kw_found[0], val_found, val_found.conf))
                    logger.debug(f"Value found within contour {result_values[-1]}")   

            if result_values:
                values = sorted(result_values, key=lambda x: (-x.conf, x.key_val_dist))
                # final_val = KeyValueFound(None, values[0], values[0].conf)
                self.cand_generated_values["None"] = [values[0]]

                # self.cand_generated_values["None"] = final_val
                return self._format_result(self.cand_generated_values)

            # Within Associations
            for val_found in value_locs:
                ass_ids = search_within_associations(self.data["clw"], val_found.cid, line_id=None,
                                                        useful_directions=self.directions)
                kw_found = [kw_found for kw_found in kw_locs if kw_found.cid in ass_ids]
                if kw_found:
                    result_values.append(KeyValueFound(kw_found[0], val_found, val_found.conf))
                    logger.debug(f"Value found in asssociation {result_values[-1]}") 

            if result_values:
                values = sorted(result_values, key=lambda x: (-x.conf, x.key_val_dist))
                # final_val = KeyValueFound(None, values[0], values[0].conf)
                self.cand_generated_values[search_word] = [values[0]]
                return self._format_result(self.cand_generated_values)

        if value_locs:
            values = sorted(value_locs, key=lambda x: (-x.conf, x.cid))
            logger.debug(f"Value found witout keyword {values[0]}")
            final_val = KeyValueFound(None, values[0], values[0].conf)
            # self.cand_generated_values["None"] = final_val
            # final_val =[values[0]]
            self.cand_generated_values["None"] = [final_val]
            return self._format_result(self.cand_generated_values)

        return self.cand_generated_values




    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict


@dataclass
class CAND_DATE_ISSUE(CAND_GEN):
    
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):

        # self.extraction_stgy = {}
        self.config_settings = self.keyword_config.field_config.dict()
        # self.value_func = self.config_settings.get("value_function", None)
        self.directions = self.config_settings.get(
            "useful_directions", ["top", "right", "bottom", "left"]
        )
        self.diagonal_contours = self.config_settings.get(
            "diagonal_flag", True
        )
        self.cand_generated_values = dict()


        self.extraction_stgy = (
            self.keyword_config.field_config.cand_generator_stgy["USING_DATE"]
        )

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)


    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the spv and relative locations result for both
        single line and multiline results.
        """
        self.cand_generated_values = {}
        logger.debug(f"<<{self.keyword}>>: Value Then Keyword based Extraction Started")
        # config_settings = doc_settings['fields_to_extract'][keyword]
        value_func = "find_date"
        result_values = list()
        value_locs = list()

        # Find values in document first
        # for val in values:
        #     found = search_all_contours_ref(self.data["clw"], val, self._quick_search())
        #     # TODO make value confidence configurable
        #     for val_found in found:
        #         val_found.conf = 15
        #         value_locs.append(val_found)

        if value_func is not None:
            for cid, contour in self.data["clw"].items():
                result = eval(value_func)(contour, None, self.config_settings)
                for val_found, conf in result:
                    val_found.conf = conf
                    value_locs.append(val_found)
        logger.debug("Found %d values \n %s", len(value_locs), [str(val) for val in value_locs])

        # Now look for keywords near values found
        for search_word, kw_locs in keywords_found.items():
            # Within contours
            for val_found in value_locs:
                kw_found = [kw_found for kw_found in kw_locs if kw_found.cid == val_found.cid]
                if kw_found:
                    result_values.append(KeyValueFound(kw_found[0], val_found, val_found.conf))
                    logger.debug(f"Value found within contour {result_values[-1]}")

            # Within Associations
            for val_found in value_locs:
                ass_ids = search_within_associations(self.data["clw"], val_found.cid, line_id=None,
                                                    useful_directions=self.directions)
                kw_found = [kw_found for kw_found in kw_locs if kw_found.cid in ass_ids]
                if kw_found:
                    result_values.append(KeyValueFound(kw_found[0], val_found, val_found.conf))
                    logger.debug(f"Value found in asssociation {result_values[-1]}")
                    
        if value_locs and not result_values:
            values = sorted(value_locs, key=lambda x: (-x.conf, x.cid))
            values = sorted(value_locs, key=lambda x: (x.contour['bbox']['top_left']['y']),reverse=True)
            for val_found in values:
                result_values.append(KeyValueFound(None, val_found, val_found.conf))
        self.cand_generated_values["Value_then_keyword"] = result_values

        return self._format_result(self.cand_generated_values)


    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict



@dataclass
class CAND_DATE_OF_ISSUE_KEYWORD_THEN_VALUE(CAND_GEN):
    
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict

    def __post_init__(
        self,
    ):

        # self.extraction_stgy = {}
        self.config_settings = self.keyword_config.field_config.dict()
        # self.value_func = self.config_settings.get("value_function", None)
        self.directions = self.config_settings.get(
            "useful_directions", ["top", "right", "bottom", "left"]
        )
        self.diagonal_contours = self.config_settings.get(
            "diagonal_flag", True
        )
        self.cand_generated_values = dict()


        self.extraction_stgy = (
            self.keyword_config.field_config.cand_generator_stgy["USING_DATE_BOL"]
        )

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)


    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the spv and relative locations result for both
        single line and multiline results.
        """
        self.cand_generated_values = {}

        logger.debug(f"<<{self.keyword}>>: Keyword Then Value based Extraction Started")
        value_func = "find_date"
        clw_hierarchy = self.data["clw"]
        values = get_values(self.config_settings, clw_hierarchy)
        result_values = list()
        value_ref_obj = QuickSearch(clw_hierarchy, ref_data=values,ngm=None, n_best=5)

        for search_word, kw_locs in keywords_found.items():
            # Within contours
            for kw_found in kw_locs:
                value_locs = search_all_words_ref(clw_hierarchy, kw_found.cid, values, value_ref_obj)
                for val_found in value_locs:
                    # TODO make value confidence configurable
                    # TODO make sure values are found only after the keyword loc
                    result_values.append(KeyValueFound(kw_found, val_found, 15))
                    logger.debug(f"Value found within contour {result_values[-1]}")

                if value_func is not None:
                    result = eval(value_func)(kw_found.contour,
                                            kw_found, self.config_settings, value_ref_obj)
                    count = 0
                    for val_found, conf in result:
                        if len(result_values) > 0:
                            for val in result_values:
                                # count=0
                                if val_found.lids[0] != val.value.lids[0]:
                                    count += 1
                                    if count == len(result_values):
                                        result_values.append(
                                            KeyValueFound(kw_found, val_found, conf))
                                        logger.debug(
                                            f"Value found within contour {result_values[-1]}")
                                else:
                                    break

                        else:
                            result_values.append(
                                KeyValueFound(kw_found, val_found, conf))
                            logger.debug(
                                f"Value found within contour {result_values[-1]}")
            # Within Associations
            for kw_found in kw_locs:
                ass_contours = search_within_associations(
                    clw_hierarchy, kw_found.cid, kw_found.lids[-1], useful_directions=self.directions)
                for _, ass_contours_list in ass_contours.items():
                    for ass_contour in ass_contours_list:
                        ass_id = list(ass_contour.keys())[0]
                        value_locs = search_all_words(clw_hierarchy, ass_id, values)
                        for val_found in value_locs:
                            result_values.append(KeyValueFound(kw_found, val_found, 15))
                            logger.debug(f"Value found in asssociation {result_values[-1]}")

                        if value_func is not None:
                            result = eval(value_func)(ass_contour[ass_id],
                                                    kw_found, self.config_settings, self._quick_search())
                            for val_found, conf in result:
                                result_values.append(KeyValueFound(kw_found, val_found, conf))
                                logger.debug(f"Value found in asssociation {result_values[-1]}")
        
        self.cand_generated_values["keyword_then_value"] = result_values
        return self._format_result(self.cand_generated_values)


    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
 