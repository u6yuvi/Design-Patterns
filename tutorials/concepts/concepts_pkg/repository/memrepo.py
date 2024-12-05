from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List
import logging

logger = logging.getLogger("MemRepo")

from concepts_pkg.entities.clw import CLWData
from concepts_pkg.entities.lw import LWData


class Data(ABC):

    """Abstract class for Data Access"""

    @abstractmethod
    def get_data():
        pass


@dataclass
class LWCLWDATA(Data):

    lw_obj: LWData
    clw_obj: CLWData
    doc_results: Dict
    doc_meta: Dict


    def __post_init__(
        self,
    ):

        self.data = self.get_data_external()
        
    def get_data(
        self,
    ) -> Dict:
        """
        The method to construct data using lw and clw from in memory
        lw and clw.
        """

        data = {}
        data["lw"] = self.lw_obj.get_lw()
        data["clw"] = self.clw_obj.get_clw()
        data["clw_reordered"] = self.clw_obj.reorder_clw_with_lwlid(
            key_type="int"
        )
        if self.doc_results.get("address_model_result", False):
            data["spv_address"] = self.doc_results["address_model_result"]
        data["doc_meta"] = self.doc_meta
        if self.doc_results.get("bank_model_result", False):
            data["bank_results"] = self.doc_results["bank_model_result"][
                "result"
            ]
            data["bank_result_meta"] = self.doc_results["bank_model_result"][
                "tag_set"
            ]
        return data

    def get_doc_meta(
        self,
    ):
        """
        The method to add document level information to be utilised in
        the downstream tasks.
        """

        doc_meta = {"page_height": 2170, "page_width": 1570}
        return doc_meta

    def get_data_external(
        self,
    ) -> Dict:
        """
        The method to construct data using lw and clw and prs results loaded
        from file which requires conversion of keys from str to int for
        Sara Engine processing
        """
        data = {}
        data["lw"] = self.lw_obj.get_lw()
        data["clw"] = self.clw_obj.get_clw_external()
        data["clw_lw_lid_map"] = self.clw_obj.reorder_clw_with_lwlid(
            key_type="str"
        )
        logger.info(f'Data used for Concepts : {self.doc_results.keys()}')

        if self.doc_results.get("prs_data", False):
            data["prs_data"] = self.doc_results.get("prs_data",{})
        #     prs_obj = PRSData(self.doc_results["prs_model_result"])
        #     data["prs_text"] = {
        #         "Text": prs_obj.get_text_regions(layout_tag="Text"),
        #         "Title": prs_obj.get_text_regions(layout_tag="Title"),
        #     }
        if self.doc_results.get("address_model_result", False):
            data["spv_address"] = self.doc_results["address_model_result"]
        if self.doc_results.get("bank_model_result", False):
            data["bank_results"] = self.doc_results["bank_model_result"][
                "result"
            ]
            data["bank_result_meta"] = self.doc_results["bank_model_result"][
                "tag_set"
            ]
        data["doc_meta"] = self.doc_meta
        return data


# @dataclass
# class MemData(Data):

#     data : List


#     def get_data():
#         return lwclw.


if __name__ == "__main__":
    import json
    from pathlib import Path

    import concepts_pkg

    __PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
    __DATASET_DIR = __PACKAGE_ROOT / "artifacts/datasets/test_suites/"
    with open(__DATASET_DIR / "lw_hierarchy_meta.json", "r") as f:
        lw_data = json.load(f)
    lw_obj = LWData(lw_data)

    with open(__DATASET_DIR / "clw_hierarchy.json", "r") as f:
        clw_data = json.load(f)
    clw_obj = CLWData(clw_data)
    doc_meta = {"page_height": 0, "page_width": 0}
    print(LWCLWDATA(lw_obj, clw_obj, doc_meta).get_data().keys())
