from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class LW(ABC):
    """
    Interface to Lw Hierarchy.
    """

    @abstractmethod
    def get_lw(self):
        """
        Method to get lw hierarchy.
        """

        pass


@dataclass
class LWData(LW):

    lw: Dict

    def get_lw(
        self,
    ):
        return self.lw

    def get_alllines(
        self,
    ):

        raise NotImplementedError


# if __name__ == "__main__":
#     import json
#     from pathlib import Path

#     import concepts_pkg

#     __PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
#     __DATASET_DIR = __PACKAGE_ROOT / "artifacts/datasets/test_suites/"
#     with open(__DATASET_DIR / "lw_hierarchy_meta.json", "r") as f:
#         lw_data = json.load(f)
#     assert LWData(lw_data).get_lw() == lw_data
