import logging
from typing import Any


# from concepts_pkg.utils.keyvaluefound import KeyValueFound
# from concepts_pkg.utils.string_match import StringFound, StringMatch
from post_processing.pattern_value_extraction import (
    get_stiched_cont,
    check_year,
    get_date,
)

logger = logging.getLogger()


def get_keyword_then_value_date_of_issue(
    clw_hierarchy, keyword, result_values
):
    """
    Extracts date_of_issue field from the list of generated
    candidates being generated from strategy 1
    """
    logger.debug(
        "<<{%s}>>: Keyword Then Value based Extraction Started", keyword
    )
    # for i,m in generated_candidates[0].items():
    #     for k in m:
    #         print(k.value.match.match_string,k.value.lids,k.value.cid)
    # result_values = [m for i,k in generated_candidates[0].items() for m in k]
    if result_values:
        values = result_values
        # # to remove contour if it contains the text only year
        #     if sum(c.isdigit() for c in values[0].value.match.match_string)<5:
        #         return []

        new_values = values.copy()
        values = []
        check_date = []
        # to check multiple dates are available
        if len(new_values) > 1:
            for i, value in enumerate(new_values):
                result = check_year([value], value_attribute=True)

                if result:
                    values.append(result[0])
                # condition executes if date and month as seperate contour
                if (
                    sum(
                        char.isdigit()
                        for char in value.value.match.match_string
                    )
                    < 3
                ):
                    check_date.append([i, True])
                if len(new_values) - 1 == i and check_date:
                    values.insert(0, new_values[check_date[0][0]])
                    values = get_stiched_cont(
                        values, clw_hierarchy, with_val_flag=True
                    )

            # to get best date
            if len(values) > 1:
                values = sorted(
                    values,
                    key=lambda x: x.value.contour["bbox"]["top_left"]["y"],
                    reverse=True,
                )
        elif len(new_values) == 1:
            values = check_year(new_values, value_attribute=True)
        if not values:
            return []
        return [values[0]]
    return []


def get_value_then_keyword_date_of_issue(
    clw, keyword, config_settings, result_values
):
    """
    Extracts date_of_issue field from the list of generated
    candidates being generated from strategy 2
    """
    logger.debug(
        "<<%s>> : Value Then Keyword based Extraction Started", keyword
    )
    # to remove contour if it contains the text only year
    # if len(result_values)>0:
    #     if len(result_values[0].value.match.match_string)<5:
    #         result_values=[]

    if result_values:
        values = sorted(result_values, key=lambda x: (-x.conf, x.key_val_dist))
        values = get_date(values, config_settings, clw, value_attribute=True)
    if not values:
        return []
    return [values[0]]


def get_all_values(clw, config_settings, keyword: Any, generated_candidates):
    """
    Driving selector function to get field :-> date of issue
    Generator strategy : 
    1 -> Searching for keyword then associating values
    2 -> Getting values then searching for nearby keywords
    """
    res_values = []
    if generated_candidates[1]["keyword_then_value"]:
        res_values = get_keyword_then_value_date_of_issue(
            clw, keyword, generated_candidates[1]["keyword_then_value"]
        )
    if res_values:
        return res_values
    if generated_candidates[0]["Value_then_keyword"]:
        res_values = get_value_then_keyword_date_of_issue(
            clw,
            keyword,
            config_settings,
            generated_candidates[0]["Value_then_keyword"],
        )
    return res_values
