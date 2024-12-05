import json
import logging
from pathlib import Path
from typing import Dict

import concepts_pkg

logger = logging.getLogger("IO")

__PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
__DATASET_DIR = __PACKAGE_ROOT / "doc_config/"
__VALUE_DIR = __PACKAGE_ROOT / "candidate_rejector/values"


def load_document_config_json(doc_config_folder: str, doc_type: str) -> Dict:

    """
    Load document configuration json file given the doc_config folder path \
        and doc_config file path.
    """

    file_name = f"{doc_type}.json"
    file_path = Path(__DATASET_DIR / doc_config_folder / file_name)
    if not file_path.exists():
        logger.info(
            f"Loading Document Configuration Failed for doc_type: {doc_type} from path : {file_path}"
        )
        return {}

    with open(file_path, "r") as f:
        doc_config = json.load(f)

        logger.info(
            f"Successfully loaded Document Configuration for doc_type: {doc_type}"
        )
    return doc_config


def load_value_json(filename: str):
    """
    Load the value json files used in candidate rejection -> value based rejection module.
    """
    filename = f"{filename}.json"
    with open(__VALUE_DIR / filename, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    from pathlib import Path

    __PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
    __DATASET_DIR = __PACKAGE_ROOT / "doc_config/"
    doc_config = load_document_config_json("coqn", "coquantity_eng")
    print(doc_config)
