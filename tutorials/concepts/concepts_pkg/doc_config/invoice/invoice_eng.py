import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

import concepts_pkg
from concepts_pkg.utils.io import load_document_config_json

__PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
__DOC_CONFIG_DIR = __PACKAGE_ROOT / "doc_config/invoice/"


class INVOICE_ENG_KEYWORD_CONFIG(BaseModel):
    """Field specific configuration"""

    keyword_search: List[str]
    number_of_lines_to_extract: int
    # extraction_function: str
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


class INVOICE_ENG_CONFIG(BaseModel):
    """Doc Level Configuration"""

    field: str
    field_config: INVOICE_ENG_KEYWORD_CONFIG


# with open(__DOC_CONFIG_DIR/"coquantity_eng.json",'r') as f:
#     coqn_config_json = json.load(f)


def load_invoice_config():
    """
    Load COQN Document Configuration.
    """

    invoice_config_json = load_document_config_json("invoice", "invoice_eng")
    invoice_eng_config = [
        INVOICE_ENG_CONFIG(
            field=key, field_config=INVOICE_ENG_KEYWORD_CONFIG(**value)
        )
        for key, value in invoice_config_json["fields_to_extract"].items()
    ]
    return invoice_eng_config
