from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from concepts_pkg.utils.ref_search import QuickSearch
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .utils import get_keywords

# from concepts_pkg.entities.clw import CLWData


class Keyword(ABC):
    """
    Abstract class for creating Keyword Extraction Logic.
    """

    @abstractmethod
    def getallkeyword_meta(self):
        """
        Return keyword aliases fro all the keywords in a doc_type
        """
        raise NotImplementedError

    @abstractmethod
    def getkeyword_meta(self, keyword):
        """
        Return keyword aliases for a specific keyword
        """
        # raise NotImplementedError

    def get_keyword_meta_legacy(self, keyword):
        """
        Return keyword aliases for a specific keyword from Concepts 1.0 Design.
        """


@dataclass
class KeywordHeuristic(Keyword):
    """
    Keyword Extraction Logic run thrugh Heurisitic

    Args:
        Keyword (Keyword): Abstract Class
    """

    keyword_dict: Dict
    keyword_config: BaseModel
    clw_hierarchy: Dict

    def __post_init__(
        self,
    ):

        self.config_settings = self.keyword_config.field_config.dict()

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.clw_hierarchy, n_best=n_best)

    def getallkeyword_meta(
        self,
    ) -> Dict:
        """Return keyword aliases for all the keywords

        Returns:
            Dict: [Keyword:[Aliases]]
        """
        raise NotImplementedError

    def getkeyword_meta(self, keyword: str) -> Dict:
        """
        Return keyword aliases for a specific keyword

        Args:
            keyword (str,): Seach Keyword

        Returns:
            Dict: Keyword:[Aliases]
        """

        settings_keyword = self.config_settings
        return get_keywords(
            self.clw_hierarchy, settings_keyword, self._quick_search()
        )

    def get_keyword_meta_legacy(self, keyword):
        ##### Implement
        return self.getkeyword_meta(keyword)


@dataclass
class KeywordK2K(Keyword):

    """
    Keyword Extraction Logic run thrugh K2K Model
    """

    keyword_dict: Dict
    keyword_config: BaseModel
    clw_hierarchy: Dict

    def getallkeyword_meta(
        self,
    ) -> Dict:
        """
        Return keyword aliases for all the keywords

        Returns:
            Dict: [Keyword:Aliases]
        """
        return self.keyword_dict

    def getkeyword_meta(self, keyword: str) -> List:
        """
        Return keyword aliases for a specific keyword

        Args:
            keyword (str,): Seach Keyword

        Returns:
            List: Keyaliases meta information
        """
        return self.keyword_dict["k2k_model_result"].get(keyword, {})

    def get_keyword_meta_legacy(self, keyword: str):
        """
        Legacy function to meet the current api signature of get_ml_keyword
        """

        # TODO: get k2k signature corrected and modify the argument names in String Match
        # keyword_info = {}
        """ if self.k2kresult:
            if self.k2kresult.get(keyword, None):
                val_obj_list = []
                for val in self.k2kresult[keyword]:

                    match_obj_dict = val["match_obj"]

                    match_obj = StringMatch(**val["match_obj"])

                    clw_info_lines = self.clw_hierarchy[val["contour_id"]][
                        "line"
                    ]

                    # TODO Avoid dependency on lw and clw for findling line ids
                    line_indxs = [
                        k
                        for k in clw_info_lines.keys()
                        if clw_info_lines[k]["line_id"] in val["line_id"]
                    ]

                    # TODO convert val_obj into list outside instead of hard coding it

                    val_obj = StringFound(
                        self.clw_hierarchy[val["contour_id"]],
                        line_indxs,
                        match_obj,
                    )
                    val_obj_list.append(val_obj)

                    keyword_info[match_obj_dict["text"]] = val_obj_list

                return keyword_info
            return {}
        return {} """


@dataclass
class KeywordHandler:
    """
    Interface to extract Keyword related information.
    """

    keyword_obj: Keyword

    def get_keyaliases_meta(self, keyword: Optional[str] = None) -> List[Dict]:
        """
        Get the keyword aliases


        Args:
            keyword (Optional[str], optional): [description]. Defaults to None.

        Returns:
            Dict: List of aliases for a particualar keyword or aliases for all keyword
        """
        if keyword:
            return self.keyword_obj.getkeyword_meta(keyword)
        return self.keyword_obj.getallkeyword_meta()

    def get_keyaliases_meta_legacy(
        self, keyword: Optional[str] = None
    ) -> Union[None, List[Dict]]:
        """
        Get the keyword aliases

        Args:
            keyword (Optional[str], optional): [description]. Defaults to None.

        Returns:
            Dict: List of aliases for a particualar keyword or None
        """
        if keyword:
            return self.keyword_obj.get_keyword_meta_legacy(keyword)
        return None


if __name__ == "__main__":
    import json
    from pathlib import Path

    import concepts_pkg

    __PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
    __DATASET_DIR = __PACKAGE_ROOT / "artifacts/datasets/test_suites/"
    with open(__DATASET_DIR / "k2k_results.json", "r") as f:
        k2k_results = json.load(f)

    # k2k = {}
    # for field_res in k2k_results['k2k_model_result']:
    #     for id , value in field_res.items():
    #         for keyword, meta in value.items():
    #             k2k['keyword'] = meta
    # print(KeywordK2K(k2k_results).getallkeyword_meta())
    # print(KeywordK2K(k2k_results).getkeyword_meta("commodity"))
    # key_obj = KeywordK2K(k2k_results)
    # print(KeywordHandler(key_obj).get_keyaliases_meta())
    # print(KeywordHandler(key_obj).get_keyaliases_meta_legacy("load_port"))
