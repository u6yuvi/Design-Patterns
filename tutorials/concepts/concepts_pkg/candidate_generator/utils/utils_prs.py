import logging
from collections import namedtuple
from typing import Dict, List

from concepts_pkg.utils.string_match import StringFound, StringMatch

logger = logging.getLogger("Utils-PRS")


key_cand_meta = namedtuple(
    "Keycand_meta", ["layout", "page_id", "key_lid", "cand_lids"]
)


def get_key_cand_meta(single_result: Dict[int, Dict], key_lid: int):
    """
    Associate keyanchor lids with the candidate lids using prs single
    line result.
    """
    key_cand_results = []
    logger.info(f"Key lid :{key_lid}")
    # logger.info(f'Single PRS results: {single_result}')
    for page_no, results in single_result.items():
        for region_id, cand_lids in results.items():
            if key_lid in cand_lids:
                logger.info(f"Key id{key_lid} found in PRs results {results}")
                key_cand_results.append(
                    key_cand_meta(page_no, key_lid, cand_lids)
                )
    return key_cand_results


def get_key_cand_meta_test(
    result: Dict[int, Dict],
    key_page_num: int,
    key_lid: int,
    lw_hierarchy: Dict[int, Dict],
    label: str,
    layout_config,
):
    """
    Associate keyanchor lids with the candidate lids for Text and Title PRS layout
    results.

    When next_line_flag is true,it would extract candidate form the next line
    based on IOU threshold for both Text and Table PRS Results.

    """

    next_line_flag = layout_config[label].get("next_line", False)
    iou_threshold = layout_config[label].get("iou_threshold", 0.10)
    key_cand_results = []
    # logger.info(f"Key lid :{key_lid}, Key Page num:{key_page_num}")
    #logger.info(f" Finding PRS results for {label} in {result}")
    for page_no, prs_results in result.items():
        for region_id, cand_lids in prs_results.items():
            # logger.info(f'cand_lid {cand_lids},page_num {page_no}')
            if key_lid in cand_lids and int(page_no) == int(key_page_num):
                logger.info(
                    f"Key id {key_lid} found in page: {page_no} of PRS results {prs_results}"
                )
                if next_line_flag:  # if label == "Text":
                    found_cand_lids = get_cand_cid(
                        lw_hierarchy, key_lid,int(key_page_num), iou_threshold
                    )
                    if found_cand_lids:
                        # logger.info(f'Key lid - candlids {key_lid} {cand_lids}')
                        logger.info(f"Appending results of IOU-Single type")
                        key_cand_results.append(
                            key_cand_meta(
                                str(label) + "_iou_single",
                                page_no,
                                key_lid,
                                found_cand_lids,#[i for i in found_cand_lids if i!=key_lid],
                            )
                        )
                logger.info(f"Appending results of Single type")
                # if [i for i in cand_lids if i!= key_lid]:
                #     #ignore keylid from cand line ids if candlids has more lines
                #     cand_lids = [ i for i in cand_lids if i!= key_lid]
                key_cand_results.append(
                    key_cand_meta(
                        str(label) + "_single", page_no, key_lid, cand_lids
                    )
                )
    return key_cand_results


def get_key_cand_meta_multi(single_result: Dict[int, Dict], key_lid: int):
    """
    Associate keyanchor lids with the candidate lids using prs single
    line result.
    """
    key_cand_results = []
    logger.info(f"Key lid :{key_lid}")
    # logger.info(f'Single PRS results: {single_result}')
    for page_no, results in single_result.items():
        for region_id, cand_res in results.items():
            if key_lid in cand_res.all_lines:
                logger.info(f"Key id{key_lid} found in PRs results {results}")
                key_cand_results.append(
                    key_cand_meta(page_no, key_lid, [key_lid])
                )
    return key_cand_results


def get_key_cand_meta_multi_test(
    result: Dict[int, Dict],
    key_page_num: int,
    key_lid: int,
    label: str,
    data: Dict,
):
    """
    Associate keyanchor lids with the candidate lids using prs single
    line result.
    """
    key_cand_results = []
    logger.info(f"Key lid :{key_lid} key_page_num {key_page_num}")
    # logger.info(f'Single PRS results: {result}')
    for page_no, prs_results in result.items():
        for region_id, cand_res in prs_results.items():
            # logger.info(f'Cand res: {cand_res}')
            if key_lid in cand_res.all_lines and int(page_no) == int(
                key_page_num
            ):
                logger.info(
                    f"Key id {key_lid} found in page: {page_no} of PRS results {prs_results}"
                )
                # check if candlid can be associated
                cand_lids = find_multiline_candlids(
                    key_lid, key_page_num, page_no, cand_res.all_lines, data
                )
                if cand_lids:
                    key_cand_results.append(
                        key_cand_meta(
                            str(label) + "_multi", page_no, key_lid, cand_lids
                        )
                    )
    return key_cand_results


# def get_key_cand_meta_title(
#     single_result: Dict[int, Dict], key_lid: int, lw_hierarchy: Dict[int, Dict]
# ):
#     """
#     Associate keyanchor lids with the candidate lids using prs single
#     line result.
#     """
#     key_cand_results = []
#     for page_no, results in single_result.items():
#         for region_id, cand_lids in results.items():
#             if key_lid in cand_lids:
#                 found_cand_lids = get_cand_cid(lw_hierarchy, key_lid)
#                 key_cand_results.append(
#                     key_cand_meta(page_no, key_lid, found_cand_lids)
#                 )
#     return key_cand_results


def create_virtual_contours(
    key_cand_results: List[namedtuple], new_clw: Dict[int, Dict]
):
    """
    Virtual contours with cid represented by -1 and results appended as lines
    with auto increment line_ids.
    KeyValue Found class can work on single cid. However as PRS Layout
    region can belong to multiple contours,fixing the issue using virtual contours.
    """
    all_lid_result = []
    for i in key_cand_results:
        for cid, cvalues in new_clw.items():
            result = [
                lvalues
                for lid, lvalues in cvalues.items()
                if lid in i.cand_lids
            ]
            all_lid_result.extend(result)
    #logger.info(f'All lid result: {all_lid_result}')
    virtual_clw = {"line": dict(enumerate(all_lid_result))}
    # required as clw is not sorted on the line_ids
    virtual_clw = {
        "line": dict(
            sorted(
                virtual_clw["line"].items(),
                key=lambda x: (
                    x[1]["bbox"]["top_left"]["y"],
                    x[1]["bbox"]["top_left"]["x"],
                ),
            )
        )
    }
    return virtual_clw


def get_virtual_contours(
    key_cand_results: List[namedtuple], new_clw: Dict[int, Dict]
):
    """
    Virtual contours with cid represented by -1 and results appended as lines
    with auto increment line_ids.
    KeyValue Found class can work on single cid. However as PRS Layout
    region can belong to multiple contours,fixing the issue using virtual contours.
    """
    all_lid_result = []
    # for i in key_cand_results:
    logger.info(f'Debug..{key_cand_results.page_id}')
    
    #Address spv-results return keycand page_num as a list
    if isinstance(key_cand_results.page_id,list):
        key_page_id = key_cand_results.page_id[0]
    else:
        key_page_id = key_cand_results.page_id
    for cid, cvalues in new_clw.items():
        result = [
            lvalues
            for lid, lvalues in cvalues.items()
            if lid in key_cand_results.cand_lids
            and int(lvalues["page_num"]) == int(key_page_id)
        ]
        all_lid_result.extend(result)
    #logger.info(f'All lid result: {all_lid_result}')
    #virtual_clw = {"line": dict(enumerate(all_lid_result))}
    '''
    Create virtual contour with line_id as same as old_line_id'''
    res = {}
    for i in all_lid_result:
        res[i["line_id"]] = i
    virtual_clw = {"line":res}
    #logger.info(f'virtual_clw{virtual_clw}:')
    # required as clw is not sorted on the line_ids
    virtual_clw = {
        "line": dict(
            sorted(
                virtual_clw["line"].items(),
                key=lambda x: (
                    x[1]["bbox"]["top_left"]["y"],
                    x[1]["bbox"]["top_left"]["x"],
                ),
            )
        )
    }
    return virtual_clw


def get_value_obj(virtual_clw: Dict, layout_label: str):
    """
    Given a contour create a key value object to be passed to
    KeyValueFound Class
    """
    cand_text = "".join([j["text"] for i, j in virtual_clw["line"].items()])
    cand_lids = list(virtual_clw["line"].keys())
    logger.info(f"Candidate lids {cand_lids}")
    value_obj = StringMatch(len(cand_text), 100, 0, cand_text)
    logger.info(f"Candidate text associated {value_obj.match_string}")
    return StringFound(virtual_clw, cand_lids, value_obj, layout_label)


def create_new_clw(clw_hierarchy: Dict[int, Dict]):
    """
    Restructure the clw hierarachy where line lids are substituted by inner line_id.
    Done to avoid one nested loop while querying for inner line_id.
    """
    new_lvalues = {}
    new_clw = {}
    for cid, cvalues in clw_hierarchy.items():
        new_lvalues = {}
        for lid, lvalues in cvalues["line"].items():
            new_lvalues[lvalues["line_id"]] = lvalues
        new_clw[cid] = new_lvalues
    return new_clw


def get_cand_cid(lw_hierarchy, key_lid,key_page_num, iou_threshold=0.10):
    """
    Associate candidate lids based on IOU threshold and Minimum Distance
    w.r.t keyalias detected in Title Region.
    """
    # logger.info(f'LW Hierarchy:{lw_hierarchy}')
    bbox_info = []
    line_info = [li_ for l,li_ in lw_hierarchy.items() if li_["line_id"]==key_lid]
    if line_info:
        title_box = (
                    line_info[0]["bbox"]["top_left"]["x"],
                    line_info[0]["bbox"]["bottom_right"]["x"],
                )
        threshold = (
                line_info[0]["bbox"]["bottom_right"]["y"]
                    - line_info[0]["bbox"]["top_left"]["y"]
                )
    
    
        for i, j in lw_hierarchy.items():
            if j["page_num"] ==key_page_num:
            
                cand_box = j["bbox"]["top_left"]["x"], j["bbox"]["bottom_right"]["x"]
            
                iou = iou_1d(title_box, cand_box)
                #logger.info(f'iou {iou}')
                if iou > iou_threshold:
                    #logger.info(f'iou {iou} {j["text"]}')
                    y_dist = abs(
                        line_info[0]["bbox"]["bottom_right"]["y"]
                        - j["bbox"]["top_left"]["y"]
                        )
                    if y_dist < threshold:
                        #logger.info(f'y_dist {y_dist}')
                        bbox_info.extend([(i, iou, threshold, y_dist)])

        if bbox_info:
            bbox_info = sorted(bbox_info, key=lambda x: (x[2], [1]))
            return [i[0] for i in bbox_info]
    return []


def iou_1d(lineA, lineB):
    """
    Intersection of union of two lines (one dimension)
    example : [100,200,150,250] and [125,275,175,325]
    if you want to find horizontal iou then, lineA = [100,150] and lineB = [125,275]
    for vertical iou, lineA = [200,250] and lineB = [275,325]
    :param lineA: co ordinates in above specified format
    :param lineB: co ordinates in above specified format
    :return: Intersection of union in one dimension
    """
    xA = max(lineA[0], lineB[0])
    xB = min(lineA[1], lineB[1])

    intersection = max(0, xB - xA)
    union = lineA[1] - lineA[0]
    if union == 0:
        return intersection
    else:
        return intersection * 1.0 / union

    # for page_no, prs_results in result.items():
    #     for region_id, cand_lids in prs_results.items():
    #         if key_lid in cand_lids:
    #             logger.info(f'Key id{key_lid} found in PRS results {prs_results}')
    #             if label == "Text":
    #                 key_cand_results.append(
    #                     key_cand_meta(str(label) +"_single",page_no, key_lid, cand_lids)
    #                 )
    #             elif label == "Title":
    #                 found_cand_lids = get_cand_cid(lw_hierarchy, key_lid)
    #                 if found_cand_lids:
    #                     key_cand_results.append(
    #                     key_cand_meta(str(label)+"_single",page_no, key_lid, found_cand_lids)
    #                 )

    # return key_cand_results


def find_multiline_candlids(
    keylid, key_page_num, cand_page_num, cand_lids, data
):
    """
    Filtering Strategy from multiline region in case number of the following scenarios:
    1. Case -1
    Keyalais  ----- Cand1
                    Cand2
                    Cand3
                    Cand4
                    etc.
    In such cases limit the number of candidate lines to be picked based on multiple of font size.
    2. Case -2
                Cand1
                Cand2
                Cand3
                Cand4
    where Cand1 is also the keyalias,
        Case 2a - In case the candlist is more than 3 limit the candidate lines to 1.
        Case 2b - In case the candlist is upto 3 return all the candidate lines.

    """
    logger.info(f" Finding candidate lw lines in multitext region.")
    result = []
    for lw_lid, lw_values in data["lw"].items():
        if (
            key_page_num == lw_values["page_num"]
            and lw_values["line_id"] == keylid
        ):
            key_yordinate = lw_values["bbox"]["top_left"]["y"]
            key_xordinate = lw_values["bbox"]["top_left"]["x"]

    #logger.info(f"Keyalias line coordinates {key_yordinate}")
    for lid in cand_lids:
        # logger.info(f'Cand_lids {cand_lids}{ cand_page_num}')
        for lw_lid, lw_values in data["lw"].items():
            if int(cand_page_num) == int(lw_values["page_num"]) and int(
                lw_values["line_id"]
            ) == int(lid):
                cand_xordinate = lw_values["bbox"]["top_left"]["x"]
                # if candidate to the right of the keyalais
                if (cand_xordinate - key_xordinate) > 20:
                    logger.info(f"Found {lid} to the right of keyalias")
                    cand_yordinate = lw_values["bbox"]["top_left"]["y"]
                    cand_yordinate1 = lw_values["bbox"]["bottom_right"]["y"]
                    threshold = cand_yordinate1 - cand_yordinate
                    # logger.info(f'Threshold {threshold} {cand_yordinate}')
                    if (cand_yordinate - key_yordinate) < 1.5 * threshold:
                        result.append(lid)

    if len(result) >= 3:
        logger.info(f'Appending key id to cand lids{result}')
        result.append(keylid)  #Case-2
    # else:
    #     result = cand_lids
    # logger.info(f"Line ids found for the candidates {result}")
    result.append(keylid)
    return result
