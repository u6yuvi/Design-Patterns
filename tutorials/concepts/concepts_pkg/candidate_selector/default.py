import logging
from dataclasses import dataclass
from typing import Dict, List

from concepts_pkg.utils.keyvaluefound import KeyValueFound

logger = logging.getLogger("CAND_SELECTOR-DEFAULT")

from .k2v import CAND_SELECTOR


@dataclass
class DEFAULT_CAND_SELECTOR(CAND_SELECTOR):

    keyword: str
    # generated_candidates : Dict
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        """
        Method to run candidate selection strategy
        """
        # TODO  : Extract the generate candidate results to match the CAND_SELECTOR_Output Schema
        #logger.info(generated_candidates)
        if len(generated_candidates) == 1:
            logger.info(f" One Strategy result found")
            # only one stgy result found
            if len(generated_candidates[0].keys()) == 1:
                logger.info(f" One Keyalias result found")
                # one one keyalias found
                if [
                    len(value)
                    for key, value in generated_candidates[0].items()
                ][0] == 1:
                    logger.info(f" One CAND_GEN result found")
                    # only one result found for the keyalias
                    return list(generated_candidates[0].values())[0]
                # currently no strategy--return 1st result
                logger.info(f"More than One CAND_GEN result found")
                return list(generated_candidates[0].values())[0]
            # topk to top1 keyalias - currently no strategy
            logger.info(f"Multiple keyalias result found")
            return list(generated_candidates[0].values())[0]
        if len(generated_candidates) == 0:
            logger.info(f"No strategy result found.")
            return []
        # result from multiple strategy
        logger.info(f"Multiple strategy result found")
        return [list(generated_candidates[0].values())[0][0]]
        # return generated_candidates
