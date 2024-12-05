from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class CLW(ABC):
    """
    Interface to CLW Hierarchy.
    """

    @abstractmethod
    def get_clw(self):
        """
        Abstract Method to get clw hierarchcy.
        """

        pass


@dataclass
class CLWData(CLW):
    """
    Heuristic based CLW Hierarchy Generation Strategy.
    """

    clw: Dict

    def get_clw(self):
        """
        Method to get clw hierarchy
        """
        return self.clw

    def get_clw_external(
        self,
    ):
        """
        Method to get clw hierarchy after convert str keys to int keys \
            of clw hierarchy loaded from external file.
        """
        clw_hierarchy = {int(key): value for key, value in self.clw.items()}

        for _, value in clw_hierarchy.items():
            for key1, value1 in value.items():
                if key1 == "line":
                    value[key1] = {int(i): k for i, k in value1.items()}

        return clw_hierarchy

    def reorder_clw_with_lwlid(
        self,key_type = "str"
    ):
        """
        Restructure the clw hierarachy where line lids are substituted by inner line_id.
        Done to avoid one nested loop while querying for inner line_id.
        """
        new_lvalues = {}
        new_clw = {}
        if key_type =="str":
            clw = self.get_clw_external()
        else:
            clw = self.clw
        for cid, cvalues in clw.items():
            new_lvalues = {}
            for lid, lvalues in cvalues["line"].items():
                new_lvalues[str(lvalues["page_num"])+"_"+str(lvalues["line_id"])] = lid
            new_clw[cid] = new_lvalues
        return new_clw


# if __name__ == "__main__":
#     import json
#     from pathlib import Path

#     import concepts_pkg

#     __PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
#     __DATASET_DIR = __PACKAGE_ROOT / "artifacts/datasets/test_suites/"
#     with open(__DATASET_DIR / "clw_hierarchy.json", "r") as f:
#         clw_data = json.load(f)
#     assert CLWData(clw_data).get_clw() == clw_data
