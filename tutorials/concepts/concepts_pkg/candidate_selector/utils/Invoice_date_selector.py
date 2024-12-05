import logging
import calendar
import numpy as np

import datefinder
from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch
from concepts_pkg.candidate_generator.utils.utils_contourizing import calculate_font_size


logger = logging.getLogger()


def is_date(text):
    """
    Function to check if given string has DATE value
    """
    try:
        len_date = len(list(datefinder.find_dates(text.replace(":", ""))))
    except (calendar.IllegalMonthError, TypeError):  # pylint disable W0702
        logger.info("Bad Month Error")
        len_date = 0
    return len_date


def gen_all_cand(self, generated_candidates):
    """
    Collate all candidates in separate list based on their generation strategy.
    TODO : Look into this function when k2k gets retrained and gives false positives.
    """
    clw = self.data["clw"]
    k2k_cand = []
    only_k2k = []
    only_spv = []
    all_spv_cand = []
    if len(generated_candidates) == 2:
        try:
            for key, value in generated_candidates[0].items():
                if key != "spv":  # it's K2K output
                    for j in value:
                        if len(j.value.lids) > 1:
                            for line in j.value.lids[:]:
                                res = {
                                    "Keyword": j.keyword,
                                    "key-alias": j.keyword.match.match_string,
                                    "contour":j.value.contour,
                                    "Value": clw[j.value.cid]["line"][line][
                                        "text"
                                    ],
                                    "lid": [line],
                                    "cid": j.value.cid,
                                }
                                if res not in k2k_cand:
                                    k2k_cand.append(res)
                        else:
                            res = {
                                "Keyword": j.keyword,
                                "key-alias": j.keyword.match.match_string,
                                "contour":j.value.contour,
                                "Value": clw[j.value.cid]["line"][
                                    j.value.lids[0]
                                ]["text"],
                                "lid": [j.value.lids[0]],
                                "cid": j.value.cid,
                            }
                            if res not in k2k_cand:
                                k2k_cand.append(res)

                else:
                    all_spv_cand = [
                        (j.value.cid, j.value.lids[0]) for j in value
                    ]
                    break
            for k, candidate in generated_candidates[1].items():
                if k == "spv":
                    all_spv_cand = [
                        (j.value.cid, j.value.lids[0]) for j in candidate
                    ]
                else:
                    for j in candidate:
                        if len(j.value.lids) > 1:
                            for candidate_line in j.value.lids[:]:
                                res = {
                                    "Keyword": j.keyword,
                                    "key-alias": j.keyword.match.match_string,
                                    "contour":j.value.contour,
                                    "Value": clw[j.value.cid]["line"][
                                        candidate_line
                                    ]["text"],
                                    "lid": [candidate_line],
                                    "cid": j.value.cid,
                                }
                                if res not in k2k_cand:
                                    k2k_cand.append(res)
                        else:
                            res = {
                                "Keyword": j.keyword,
                                "key-alias": j.keyword.match.match_string,
                                "contour":j.value.contour,
                                "Value": clw[j.value.cid]["line"][
                                    j.value.lids[0]
                                ]["text"],
                                "lid": [j.value.lids[0]],
                                "cid": j.value.cid,
                            }
                            if res not in k2k_cand:
                                k2k_cand.append(res)

        except (calendar.IllegalMonthError, TypeError):
            logger.info("Bad Month Error")

    elif len(generated_candidates) == 1:
        try:
            for k, value in generated_candidates[0].items():
                if k != "spv":  # it's K2K output
                    for j in value:
                        if len(j.value.lids) > 1:
                            for cand_line in j.value.lids[:]:
                                if (
                                    is_date(
                                        clw[j.value.cid]["line"][cand_line][
                                            "text"
                                        ]
                                    )
                                    > 0
                                ):
                                    res = {
                                        "Keyword": j.keyword,
                                        "key-alias": j.keyword.match.match_string,
                                        "Value": clw[j.value.cid]["line"][
                                            cand_line
                                        ]["text"],
                                        "lid": [cand_line],
                                        "cid": j.value.cid,
                                    }
                                    if res not in only_k2k:
                                        only_k2k.append(res)
                        else:
                            res = {
                                "Keyword": j.keyword,
                                "key-alias": j.keyword.match.match_string,
                                "Value": clw[j.value.cid]["line"][
                                    j.value.lids[0]
                                ]["text"],
                                "lid": [j.value.lids[0]],
                                "cid": j.value.cid,
                            }
                            if (
                                res not in only_k2k
                                and is_date(res["Value"]) > 0
                            ):
                                only_k2k.append(res)

                else:
                    for i in value:
                        if (
                            is_date(
                                clw[i.value.cid]["line"][i.value.lids[0]][
                                    "text"
                                ]
                            )
                            > 0
                        ):
                            res = {
                                "Keyword": i.keyword,
                                "key-alias": i.keyword,
                                "Value": clw[i.value.cid]["line"][
                                    i.value.lids[0]
                                ]["text"],
                                "lid": [i.value.lids[0]],
                                "cid": i.value.cid,
                            }
                            if res not in k2k_cand:
                                only_spv.append(res)

        except (calendar.IllegalMonthError, TypeError):
            logger.info("Bad Month Error")

    return k2k_cand, only_k2k, only_spv, all_spv_cand


def final_all_cand(self, k2k_cand, only_k2k, only_spv, all_spv_cand):
    """
    Using above collated list create a list of all candidates which has ,
    intersection : intersection of k2k and spv results,
    only spv : only spvcandidates,
    only k2k : only k2k candidates,
    difference : k2k candidates which are not present in spv
    """
    keyword = self.keyword
    clw = self.data["clw"]
    intrsec = [
        i
        for i in k2k_cand
        if ((i["cid"], i["lid"][0]) in all_spv_cand)
        and ((is_date(i["Value"]) > 0) or ((is_date(i["Value"].split(' - ')[0]))>0))
    ]
    try:
        if len(intrsec) > 0:
            dif_key = [
                j
                for j in [i["key-alias"].lower().strip() for i in intrsec]
                if j != "date"
            ]
            for k in intrsec:
                if (
                    keyword in ["invoice_date", "delivery_date"]
                    and k["key-alias"].lower().strip() in dif_key
                ):
                    intrsec = k
                    break
                elif (
                    keyword == "invoice_date"
                    or (
                        keyword == "delivery_date"
                        and self.doc_type == "coquantity_eng"
                    )
                ) and k["key-alias"].lower().strip() == "date":
                    if keyword == "delivery_date":
                        intrsec = k
                    else:
                        intrsec = k
                        break

    except (calendar.IllegalMonthError, TypeError):
        logger.info("Bad Month Error")

    difference = [
        i
        for i in k2k_cand
        if (i["cid"], i["lid"][0]) not in all_spv_cand
        and (len(intrsec) < 0)
        and (is_date(i["Value"]) > 0)
    ]
    try:
        if (
            len(intrsec) == 0
            and len(all_spv_cand) > 0
            and keyword == "invoice_date"
        ):
            for spv_cand in all_spv_cand:
                if is_date(clw[spv_cand[0]]["line"][spv_cand[1]]["text"]) > 0:
                    only_spv = {
                        "Keyword": "Invoice date",
                        "key-alias": "Invoice date",
                        "Value": clw[spv_cand[0]]["line"][spv_cand[1]]["text"],
                        "lid": [spv_cand[1]],
                        "cid": spv_cand[0],
                    }
                    break
        if (
            len(intrsec) == 0
            and len(all_spv_cand) > 0
            and keyword in ["delivery_date","service_provided_date"]
        ):
            if keyword == "service_provided_date" : #selecting nearest contour element
                keyword_cid = int(np.unique([(i["Keyword"].cid) for i in k2k_cand]))
                arr = np.asarray([ele[0] for ele in all_spv_cand])
                min_dist = arr[(np.abs(arr-keyword_cid)).argmin()]
                for end_list in all_spv_cand[::-1]:
                    if end_list[0] == min_dist:                    
                        only_spv = {
                            "Keyword": keyword,
                            "key-alias": None,
                            "Value": clw[end_list[0]]["line"][end_list[1]]["text"],
                            "lid": [end_list[1]],
                            "cid": end_list[0],
                        }
                        break
            else:
                for end_list in all_spv_cand[::-1]:
                    only_spv = {
                        "Keyword": keyword,
                        "key-alias": None,
                        "Value": clw[end_list[0]]["line"][end_list[1]]["text"],
                        "lid": [end_list[1]],
                        "cid": end_list[0],
                    }
                    break
    except (calendar.IllegalMonthError, TypeError):
        logger.info("Bad Month Error")

    all_cand = {
        "intersection": intrsec,
        "only_spv": only_spv,
        "only_k2k": only_k2k,
        "difference": difference,
    }
    return all_cand

def spatial_based_value_selection(intersection_list):
        for i in intersection_list:
            res=[]
            values = [[k['text'],k['bbox']] for m,k in i["contour"]["line"].items()  if i["Value"] in k['meta']['ana']['clean_text']]
            keysss = [[k['text'],k['bbox']] for m,k in i["Keyword"].contour["line"].items() if i["key-alias"].lower() in k['text'].lower()]
            if not keysss:
                keysss = [[i["key-alias"],i["Keyword"].contour['bbox']]]
            font_size = list(set([calculate_font_size(i["contour"]["line"]) for i in intersection_list]))
            font_size = [sum(font_size)/len(font_size) if len(font_size)>1 else font_size[0]][0]
            # value present to the right
            if values and keysss:
                if (values[0][1]['top_left']['x'] > keysss[0][1]['top_left']['x']) and (values[0][1]['top_left']['y'] == keysss[0][1]['top_left']['y']) :
                    res.append(
                        {
                            "text": i["Value"],
                            "contour_id": i["cid"],
                            "line_id": i["lid"],
                            "start": 0,
                            "end": len(i["Value"]),
                        }
                    )
                    return res
                    break
                # value present below
                elif (1.5*font_size >= abs(values[0][1]['top_left']['x']-i["Keyword"].contour['bbox']["top_left"]["x"])) and (values[0][1]['top_left']['y'] > keysss[0][1]['top_left']['y']) :
                    res.append(
                        {
                            "text": i["Value"],
                            "contour_id": i["cid"],
                            "line_id": i["lid"],
                            "start": 0,
                            "end": len(i["Value"]),
                        }
                    )
                    return res
            else:
                continue
        intersection_list1 = [{
                            "text": intersection_list[0]["Value"],
                            "contour_id": intersection_list[0]["cid"],
                            "line_id": intersection_list[0]["lid"],
                            "start": 0,
                            "end": len(intersection_list[0]["Value"]),
                        }]
        return intersection_list1

def extract_dates(self, generated_candidates):
    """Function to extract results for date field based on the
    results obtained from find_all_cand function"""

    logger.info("Invoice date selector started")
    k2k_cand, only_k2k, only_spv, all_spv_cand = gen_all_cand(
        self, generated_candidates
    )
    all_cand = final_all_cand(self, k2k_cand, only_k2k, only_spv, all_spv_cand)
    keyword = self.keyword
    result_dict = []
    result_values = []
    clw_hierarchy = self.data["clw"]
    result_dict = []

    if all_cand["intersection"]:
        if not isinstance(all_cand["intersection"], dict):
            if len(all_cand["intersection"])>1:
                result_dict.append(spatial_based_value_selection(all_cand['intersection'])[0])
            else:
                result_dict.append(
                    {
                        "text": all_cand["intersection"][0]["Value"],
                        "contour_id": all_cand["intersection"][0]["cid"],
                        "line_id": all_cand["intersection"][0]["lid"],
                        "start": 0,
                        "end": len(all_cand["intersection"][0]["Value"]),
                    }
                )
        else:
            result_dict.append(
                {
                    "text": all_cand["intersection"]["Value"],
                    "contour_id": all_cand["intersection"]["cid"],
                    "line_id": all_cand["intersection"]["lid"],
                    "start": 0,
                    "end": len(all_cand["intersection"]["Value"]),
                }
            )
    elif all_cand["only_k2k"]:
        if is_date(all_cand["only_k2k"][0]["Value"]) > 0:
            result_dict.append(
                {
                    "text": all_cand["only_k2k"][0]["Value"],
                    "contour_id": all_cand["only_k2k"][0]["cid"],
                    "line_id": all_cand["only_k2k"][0]["lid"],
                    "start": 0,
                    "end": len(all_cand["only_k2k"][0]["Value"]),
                }
            )

    elif all_cand["only_spv"]:
        if (keyword == "invoice_date") or (keyword == "service_provided_date" and len(generated_candidates) == 2):
            if not isinstance(all_cand["only_spv"], dict):
                result_dict.append(
                    {
                        "text": all_cand["only_spv"][0]["Value"],
                        "contour_id": all_cand["only_spv"][0]["cid"],
                        "line_id": all_cand["only_spv"][0]["lid"],
                        "start": 0,
                        "end": len(all_cand["only_spv"][0]["Value"]),
                    }
                )
            else:
                result_dict.append(
                    {
                        "text": all_cand["only_spv"]["Value"],
                        "contour_id": all_cand["only_spv"]["cid"],
                        "line_id": all_cand["only_spv"]["lid"],
                        "start": 0,
                        "end": len(all_cand["only_spv"]["Value"]),
                    }
                )

        if self.doc_type == "coquantity_eng" and keyword in [
            "coqn_date",
            "delivery_date",
        ]:
            if not isinstance(all_cand["only_spv"], dict):
                result_dict.append(
                    {
                        "text": all_cand["only_spv"][0]["Value"],
                        "contour_id": all_cand["only_spv"][0]["cid"],
                        "line_id": all_cand["only_spv"][0]["lid"],
                        "start": 0,
                        "end": len(all_cand["only_spv"][0]["Value"]),
                    }
                )
            else:
                result_dict.append(
                    {
                        "text": all_cand["only_spv"]["Value"],
                        "contour_id": all_cand["only_spv"]["cid"],
                        "line_id": all_cand["only_spv"]["lid"],
                        "start": 0,
                        "end": len(all_cand["only_spv"]["Value"]),
                    }
                )
    if result_dict:
        for val in result_dict:
            temp_match_obj = StringMatch(
                val["end"], 100, val["start"], val["text"]
            )
            temp_value_obj = StringFound(
                clw_hierarchy[val["contour_id"]],
                val["line_id"],
                temp_match_obj,
            )
            result_values.append(KeyValueFound(None, temp_value_obj, 100))
            logger.debug("{%s} value is {%s}", self.keyword, val["text"])
            return result_values
    return []