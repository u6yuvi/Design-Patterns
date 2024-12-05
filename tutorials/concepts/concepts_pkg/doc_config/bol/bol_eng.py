import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

import concepts_pkg
from concepts_pkg.utils.io import load_document_config_json

__PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
__DOC_CONFIG_DIR = __PACKAGE_ROOT / "doc_config/bol/"


class BOL_ENG_KEYWORD_CONFIG(BaseModel):
    """Field specific configuration"""

    keyword_search: List[str]
    number_of_lines_to_extract: int
    reject_list: Dict
    # value_function: str
    selection_type: str
    values_file: List
    diagonal_flag: bool
    # use_k2k: bool
    # use_k2k_only: bool
    # use_handler: Dict
    cand_rejector_stgy: Dict
    extraction_stgy: Dict
    key_extraction_stgy: Dict
    cand_generator_stgy: Dict
    cand_selector_stgy: Dict


class BOL_ENG_CONFIG(BaseModel):
    """Doc Level Configuration"""

    field: str
    field_config: BOL_ENG_KEYWORD_CONFIG



# def load_doc_config_bol():
#     """
#     Load BOL Document Configuration.
#     """

#     bol_config_json = load_document_config_json("bol", "bol_eng")


#     bol_eng_config = [
#         BOL_ENG_CONFIG(
#             field=key, field_config=BOL_ENG_KEYWORD_CONFIG(**value)
#         )
#         for key, value in bol_config_json["fields_to_extract"].items()
#     ]
#     return bol_eng_config

def load_bol_config():
    """
    Load BOL Document Configuration.
    """

    bol_config_json = load_document_config_json("bol", "bol_eng")


    bol_eng_config = [
        BOL_ENG_CONFIG(
            field=key, field_config=BOL_ENG_KEYWORD_CONFIG(**value)
        )
        for key, value in bol_config_json["fields_to_extract"].items()
    ]
    return bol_eng_config


if __name__ == "__main__":
    bol_config=load_bol_config()

    for config in bol_config:
        print(config.field)
        # if config.field == "shipper":
            
        #     print(config.field_config.cand_generator_stgy)
