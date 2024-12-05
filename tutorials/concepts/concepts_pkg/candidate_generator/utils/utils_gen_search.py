import logging, os, sys, json
from collections import deque
from concepts_pkg.utils.string_match import (
    StringFound,
    StringMatch,
    clean_text,
)

from .association import association, get_contour_in_useful_dir
from .contour_trimming import get_associated_lines
from .diagonal_contours import search_within_limited_contours
from .utils_contourizing import calculate_font_size
from .entity_extraction import clean_text_nsa
from copy import deepcopy
import re

logger = logging.getLogger("Keyword Value Genesis and Search")

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


def discard_keyword(query_string, match_obj):
    # TODO: Make thresholds configurable
    query_words_len = len(query_string.split())
    words_before = len(query_string[: match_obj.start].split())
    if words_before >= 5 or (query_words_len > 15):
        return True
    return False


complete_reg = re.compile(
    r"((From:|To:|Sent:|Cc?C:)(.)*(Cc?C:|To:|From:|Sent:)(.)*(To:|From:|Sent:|Cc?C:)(.)*)|(Van:(.)*Verzonden:(.)*Aan:(.)*)"
)

def clean_forwardeditems(clw_h):
    for _, vals in clw_h.items():
        if re.search(complete_reg, vals["text"]):
            vals["text"] = ""
            for _, line in vals["line"].items():
                line["text"] = ""
                for _, word in line["words"].items():
                    word["text"] = ""
            break

    return clw_h


def search_within_contours(
    clw_hierarchy, contour_ids, search_word, find_fuzzy=True, use_discard=False
):
    """Search a keyword within the specified contours.

    :param clw_hierarchy: contour line word hierarchy of the document's text
    :type clw_hierarchy: dict
    :param contour_ids: ids of contours within which the keyword needs to be
        searched
    :type contour_ids: list
    :param search_word: keyword to be searched for
    :type search_word: str
    :param find_fuzzy: try keyword search using fuzzy match, defaults to False
    :type find_fuzzy: bool, optional
    :return: contour ids and location where the keyword is found
    :rtype: list
    """
    found = deque()
    perfect_match = False

    for cid in contour_ids:
        # TODO: Search word in contour text instead of line
        for lid, line in clw_hierarchy[cid]["line"].items():
            query_string = line["text"]
            if find_fuzzy:
                match_obj = StringMatch.string_match(
                    clean_text(search_word), clean_text(query_string)
                )
                if not match_obj:
                    continue
                if discard_keyword(query_string, match_obj) and use_discard:
                    continue
                if match_obj.similarity != 100:
                    # aliasing = findwholeword_aliasing(search_word, query_string)
                    # logger.debug(f"Checking aliasing for '{search_word}' and "
                    #              f"'{query_string}'")
                    # if aliasing:
                    found.append(
                        StringFound(clw_hierarchy[cid], [lid], match_obj)
                    )
                    logger.debug(f"For '{search_word}' {found[-1]}")
                else:
                    found.append(
                        StringFound(clw_hierarchy[cid], [lid], match_obj)
                    )
                    logger.debug(f"For '{search_word}' {found[-1]}")
                    perfect_match = True
            else:
                match_obj = StringMatch.findwholeword(
                    search_word, query_string
                )
                if not match_obj:
                    continue
                if discard_keyword(query_string, match_obj) and use_discard:
                    continue
                found.append(StringFound(clw_hierarchy[cid], [lid], match_obj))
                logger.debug(f"For '{search_word}' {found[-1]}")
                perfect_match = True
    if perfect_match:
        found = [
            found_obj
            for found_obj in found
            if found_obj.match.similarity == 100
        ]
    found_sorted = sorted(found, key=lambda x: -x.match.similarity)
    return found_sorted


def search_within_associations(
    clw_hierarchy,
    contour_id,
    line_id,
    search_word=None,
    useful_directions=None,
    use_discard=False,
):
    if useful_directions is None:
        useful_directions = ["bottom", "right"]
    logger.debug(f"Search within association started for cid {contour_id} ")
    # mapping = association(contour_id, clw_hierarchy, line_id)
    # cids = [cont_id for direction in mapping for cont_id in mapping[direction]]
    # logger.debug(f"Associated contours for cid {contour_id} are {nearest_cids} ")
    if search_word is not None:
        mapping = association(contour_id, clw_hierarchy, line_id)
        cids = [
            cont_id for direction in mapping for cont_id in mapping[direction]
        ]
        return search_within_contours(
            clw_hierarchy, cids, search_word, use_discard=use_discard
        )
    elif line_id is None:
        mapping = association(contour_id, clw_hierarchy, line_id)
        cids = [
            cont_id for direction in mapping for cont_id in mapping[direction]
        ]
        return cids
    else:
        # TODO change this mapping data structure
        # TODO change positioni of this snippet
        mapping = get_associated_lines(clw_hierarchy, contour_id, line_id)
        nearest_cids = get_contour_in_useful_dir(mapping, useful_directions)
        return nearest_cids


def search_all_contours_ref(clw_hierarchy, search_word, quick_search):
    found, perfect_match = deque(), False
    candidates = quick_search.ref_obj.find_best_match(search_word.lower())
    conf_list = [val for val, conf in candidates] if candidates else []

    for ref_text in conf_list:
        match_obj = StringMatch.string_match(
            clean_text(search_word), clean_text(ref_text)
        )
        if match_obj:
            if match_obj.similarity == 100:
                perfect_match = True
            clid_list = quick_search.text_map[ref_text]
            for clid in clid_list:
                cid, lid = map(int, clid.split("_"))
                found.append(
                    StringFound(clw_hierarchy[int(cid)], [lid], match_obj)
                )

    found = (
        [found_obj for found_obj in found if found_obj.match.similarity == 100]
        if perfect_match
        else found
    )
    found_sorted = sorted(found, key=lambda x: -x.match.similarity)
    return found_sorted


def verify_keyword(text, discard_setting):
    # TODO: Use pre and post substrings but not complete text
    for rejects_pos in discard_setting.keys():
        for rej_word in discard_setting[rejects_pos]:
            rej_match = StringMatch.findwholeword(rej_word, text)
            if rej_match:
                return True
    return False


def get_values(value_settings, clw_hierarchy):

    values = value_settings.get("value_search", [])

    if "values_file" in value_settings:
        values_files_all = value_settings["values_file"]
        for values_file in values_files_all:
            values_path = os.path.join(WORK_DIR, "values", values_file)
            with open(values_path, mode="r") as f:
                values += json.load(f)["values"]
        logger.debug(f"Found fixed values of size: {len(values)}")
    return values


def find_date(
    val_contour, kw_found=None, settings_conf=None, value_ref_obj=None
):
    """Method for getting date stringh in a query data string.

    :param data: query string
    :type data: str
    :return: list of dates found
    :rtype: list
    """
    settings_conf = {"confidence": {"labels": {"DATE": 10}}}
    data_lines = list()
    if kw_found:
        line_ordinate = kw_found.contour["line"][kw_found.lids[-1]]["bbox"][
            "top_left"
        ]["y"]
        font_size = calculate_font_size(val_contour["line"])
        # TODO: make no. of lines to extract configurable
        line_count, lines_to_extract = 0, 1
        for lid, line in val_contour["line"].items():
            if (
                line_ordinate - line["bbox"]["top_left"]["y"]
            ) <= font_size / 2:
                line_count += 1
                data_lines.append((lid, clean_text(line["text"])))
                if line_count > lines_to_extract + 2:
                    break
    else:
        data_lines = [
            (lid, clean_text(line["text"]))
            for lid, line in val_contour["line"].items()
        ]

    result = []
    Date_label = "DATE"
    # get the date based on spv tag
    for lid, line_val in val_contour["line"].items():
        date = " "
        labels = line_val["meta"]["spv"]["clean_text_tags"]
        tokens = line_val["meta"]["spv"]["clean_text_tokens"]
        confidence = 0
        # If any lable has "date" nearby allother cardinal condidered as date
        for i, lbls in enumerate(labels):
            if lbls == Date_label:
                for j, lbl in enumerate(labels):
                    if lbl == "CARDINAL":
                        if len(tokens[i]) < 6:
                            labels[j] = "DATE"
        for i, label in enumerate(labels):
            if label in settings_conf["confidence"]["labels"]:
                # if labels token less than 22.then considered as date
                if len(tokens[i]) < 22:
                    if confidence == 0:
                        date = tokens[i]
                    else:
                        date = date + " " + tokens[i]
                    confidence += settings_conf["confidence"]["labels"][label]
        out_contour = deepcopy(val_contour)
        if confidence > 0:
            out_contour["line"][lid]["text"] = date
            temp_string_obj = StringMatch(
                len(out_contour["line"][lid]["text"]),
                100,
                0,
                out_contour["line"][lid]["text"],
            )
            result.append(
                (StringFound(out_contour, [lid], temp_string_obj), confidence)
            )

    return result


def search_all_words_ref(
    clw_hierarchy, contour_id, search_words, quick_search, use_discard=False
):
    found, perfect_match = deque(), False
    if not search_words:
        return found

    for lid, line in clw_hierarchy[contour_id]["line"].items():
        query_string = line["text"]
        candidates = quick_search.ref_obj.find_best_match(query_string.lower())
        conf_list = [val for val, conf in candidates] if candidates else []

        for ref_text in conf_list:
            match_obj = StringMatch.string_match(
                clean_text(query_string), clean_text(ref_text)
            )
            if match_obj:
                if match_obj.similarity == 100:
                    perfect_match = True
                clid_list = quick_search.text_map[query_string.lower()]
                for clid in clid_list:
                    cid, lid = map(int, clid.split("_"))
                    found.append(
                        StringFound(clw_hierarchy[int(cid)], [lid], match_obj)
                    )

        found = (
            [
                found_obj
                for found_obj in found
                if found_obj.match.similarity == 100
            ]
            if perfect_match
            else found
        )
        found_sorted = sorted(found, key=lambda x: -x.match.similarity)
        return found_sorted


def search_all_words(
    clw_hierarchy, contour_id, search_words, use_discard=False
):
    found = list()
    for search_word in search_words:
        found += search_within_contours(
            clw_hierarchy, [contour_id], search_word, use_discard=use_discard
        )
    return found


# def get_discard_list(doc_settings):
#     discard_list = list()
#     print(doc_settings['keyword_search'])
#     for keyword in doc_settings['keyword_search']:
#         keyword_settings = doc_settings['keyword_search'][keyword]
#         discard_list.extend(keyword_settings.get('keyword_search', []))
#         # discard_list.extend(keyword_settings.get('value_search', []))
#     return discard_list
