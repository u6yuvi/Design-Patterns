import logging
import re
from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch
from .tax_reg_id_utils import tax_reg_pattern ,tax_reg_pattern_1

logger = logging.getLogger()

def extract_tax_reg_id(self, generated_candidates):
    """
    Selector logic of tax_reg_id field
    params : generated_candidates
    Code searches through the generated candidates and looks for correct value based
    on regex pattern
    """
    clw = self.data["clw"]
    result_values = []
    result_dict = []
    logger.info("Extraction of Tax Registration ID started")
    if len(generated_candidates) > 0:
        for _, j in generated_candidates[0].items():
            for value in j:
                if len(value.value.lids) > 1:
                    for line_ids in value.value.lids[:]:
                        res = re.search(
                            tax_reg_pattern,
                            clw[value.value.cid]["line"][line_ids]["text"],
                        )
                        if res is not None:
                            result_dict.append(
                                {
                                    "text": res.group(0),
                                    "contour_id": value.value.cid,
                                    "line_id": [line_ids],
                                    "start": 0,
                                    "end": len(res.group(0)),
                                }
                            )
                            break
                            
                        else:
                            res = tax_reg_pattern_1.fullmatch(clw[value.value.cid]["line"][line_ids]["text"])
                            if res:
                                result_dict.append(
                                {
                                    "text": res.group(0),
                                    "contour_id": value.value.cid,
                                    "line_id": [line_ids],
                                    "start": 0,
                                    "end": len(res.group(0)),
                                })
                                
                else:
                    res = re.search(
                        tax_reg_pattern,
                        clw[value.value.cid]["line"][value.value.lids[0]][
                            "text"
                        ],
                    )
                    if res is not None:
                        result_dict.append(
                            {
                                "text": res.group(0),
                                "contour_id": value.value.cid,
                                "line_id": [value.value.lids[0]],
                                "start": 0,
                                "end": len(res.group(0)),
                            }
                        )
                        break
    else:
        return []

    if result_dict:
        for val in result_dict:
            temp_match_obj = StringMatch(
                val["end"], 100, val["start"], val["text"]
            )
            temp_value_obj = StringFound(
                clw[val["contour_id"]],
                val["line_id"],
                temp_match_obj,
            )
            result_values.append(KeyValueFound(None, temp_value_obj, 100))
            logger.debug("{%s} value is {%s}", self.keyword, val["text"])
            return result_values
    return []
