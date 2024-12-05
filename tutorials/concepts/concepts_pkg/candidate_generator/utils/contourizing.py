import operator
from collections import defaultdict
from copy import deepcopy

import cv2
from .utils_contourizing import (
    calculate_font_size,
    get_contour_coords,
    get_coords,
    group_lines,
    iom,
    iom_1d,
    iou,
    sort_xy,
)


def iom_1d_contour(hierarchy, query_contour, contour, direction="x"):
    """Intersection over minimum of the two contours (one dimension) i.e.
    percentage overlap in a particular (x or y) direction

    :param hierarchy: line word hierarchy
    :type hierarchy: dict
    :param query_contour: id of the query contour
    :type query_contour: int
    :param contour: id of the contour against which overlap to be checked
    :type contour: int
    :param direction: overlap direction, defaults to "x"
    :type direction: str, optional
    :return: percentage overlap
    :rtype: float
    """
    left1 = min(
        [
            hierarchy[_id]["bbox"]["top_left"][direction]
            for _id in query_contour
        ]
    )
    right1 = max(
        [
            hierarchy[_id]["bbox"]["bottom_right"][direction]
            for _id in query_contour
        ]
    )
    left2 = min(
        [hierarchy[_id]["bbox"]["top_left"][direction] for _id in contour]
    )
    right2 = max(
        [hierarchy[_id]["bbox"]["bottom_right"][direction] for _id in contour]
    )
    return iom_1d((left1, right1), (left2, right2))


def get_near_contours(hierarchy, query_contour, contours, thresh):
    """Get the list of contour ids which are within the threshold range
    (vertical gap) of the query_contour

    :param hierarchy: line word hierarchy
    :type hierarchy: dict
    :param query_contour: id of the query contour
    :type query_contour: int
    :param contour: dict of contours
    :return: ids of nearby contours
    :rtype: list
    """
    output = list()
    top = min(
        [hierarchy[_id]["bbox"]["top_left"]["y"] for _id in query_contour]
    )
    for cid, contour in contours.items():
        bottom = max(
            [hierarchy[_id]["bbox"]["bottom_right"]["y"] for _id in contour]
        )
        if top - bottom < thresh:
            output.append(cid)
    return output


def check_contour_overlap(hierarchy, query_contour, contours, settings):
    """Checks if the query_contoue overlaps with any of the contours by some
    threshold

    :param hierarchy: line word hierarchy
    :type hierarchy: dict
    :param query_contour: id of the query contour
    :type query_contour: int
    :param contours: list of contour ids with which the overlappingis checked
    :type contours: list
    :return: True if any ovelapping contour is found else False
    :rtype: bool
    """
    CONTOURS_OVERLAP = settings["CONTOURS_OVERLAP"]
    for contour in contours.values():
        bbox_a = get_contour_coords(hierarchy, query_contour)
        bbox_b = get_contour_coords(hierarchy, contour)
        box_a = (
            bbox_a["top_left"]["x"],
            bbox_a["top_left"]["y"],
            bbox_a["bottom_right"]["x"],
            bbox_a["bottom_right"]["y"],
        )
        box_b = (
            bbox_b["top_left"]["x"],
            bbox_b["top_left"]["y"],
            bbox_b["bottom_right"]["x"],
            bbox_b["bottom_right"]["y"],
        )
        overlap = iom(box_a, box_b)
        if overlap > CONTOURS_OVERLAP:
            return True
    return False


def make_segments_l1(
    hierarchy,
    settings,
    font_size,
):
    """Make level 1 (covering most of the cases) virtual contours based on
    spacing (vert gaps and hor overlaps)

    :param hierarchy: line word hierarchy
    :type hierarchy: dict
    :param font_size: average font size of document
    :type font_size: float
    :return: segments formed based on spacing
    :rtype: list
    """
    THRESH_VER_GAP = settings["THRESH_VER_GAP"]
    THRESH_IOU = settings["THRESH_IOU"]

    thresh_ver_gap = THRESH_VER_GAP * font_size
    lines_sorted_v = sorted(
        hierarchy.keys(),
        key=lambda key: hierarchy[key]["bbox"]["top_left"]["y"],
    )
    contours = dict()
    contour_num = -1

    for line in lines_sorted_v:
        # Get narby contours for this line
        intersecting_contours = list()
        near_contour_ids = get_near_contours(
            hierarchy, [line], contours, thresh_ver_gap
        )

        for ncid in near_contour_ids:
            iou = iom_1d_contour(hierarchy, [line], contours[ncid])
            if iou > THRESH_IOU:
                intersecting_contours.append(ncid)

        if intersecting_contours:
            # merge all intersecting contours and add the line too
            contours_orig = deepcopy(contours)
            min_id = intersecting_contours[0]

            for icid in intersecting_contours[1:]:
                contours[min_id] += contours[icid]
                del contours[icid]
            contours[min_id].append(line)
            cur_contour = contours.pop(min_id)

            # Check if the merged contour doesn't overlap with any other
            # non-nearby contours.
            if check_contour_overlap(
                hierarchy, cur_contour, contours, settings
            ):
                # pass
                contours = contours_orig
                contour_num += 1
                contours[contour_num] = [line]
            else:
                contours[min_id] = cur_contour
        else:
            # make a new contour containing the line.
            contour_num += 1
            contours[contour_num] = [line]
    return contours.values()


def get_bbox_virtual_contours(segmentation, hierarchy, start_id):
    rect_co_ords = dict()
    for _id, segmentation_group in enumerate(segmentation):
        bbox = get_contour_coords(hierarchy, segmentation_group)
        rect_co_ords[start_id + 1 + _id] = {
            "bbox": bbox,
            "line": segmentation_group,
        }
    return rect_co_ords


def get_virtual_contours(lw_hierarchy, settings, font_size, area, _id):
    contour_line_association = dict()
    lines_virtual = list(lw_hierarchy.keys())
    if len(lines_virtual) > 0:
        segments = make_segments_l1(lw_hierarchy, settings, font_size)
        contour_line_association = get_bbox_virtual_contours(
            segments, lw_hierarchy, _id
        )
    return contour_line_association


def same_contour(rectangular_coords, line_coords):
    same_criterion_flag = False
    (
        contour_top,
        contour_left,
        contour_right,
        contour_bottom,
    ) = rectangular_coords
    line_top, line_left, line_right, line_bottom = line_coords

    top_criterion = line_top >= contour_top
    left_criterion = line_left >= contour_left
    bottom_criterion = line_right <= contour_right
    right_criterion = line_bottom <= contour_bottom

    iou_criterion = iou(line_coords, rectangular_coords)

    if (
        all([top_criterion, left_criterion, bottom_criterion, right_criterion])
        or iou_criterion >= 0.75
    ):
        same_criterion_flag = True
    return same_criterion_flag


def check_biggest_contour(area, rectangular_coords):
    (
        contour_top,
        contour_left,
        contour_bottom,
        contour_right,
    ) = rectangular_coords
    height = contour_right - contour_left
    width = contour_bottom - contour_top
    if height * width >= (0.75 * area):
        return False
    return True


def remove_heirarchy(hierarchy, line_ids):
    for line in line_ids:
        hierarchy.pop(line, None)
    return hierarchy


def association(rectangular_coords, hierarchy, area, _id):
    contour_line_mapping = defaultdict(dict)
    line_ids = []
    for (
        contour_top,
        contour_left,
        contour_bottom,
        contour_right,
    ) in rectangular_coords:
        _id += 1
        contour_line_mapping[_id]["bbox"] = {}
        contour_line_mapping[_id]["bbox"]["bottom_right"] = {
            "x": contour_bottom,
            "y": contour_right,
        }
        contour_line_mapping[_id]["bbox"]["top_left"] = {
            "x": contour_top,
            "y": contour_left,
        }
        contour_line_mapping[_id]["line"] = []

        rectangular_coords = [
            contour_top,
            contour_left,
            contour_bottom,
            contour_right,
        ]
        not_biggest_contour = check_biggest_contour(area, rectangular_coords)

        if not_biggest_contour:
            for line in hierarchy:
                if line not in line_ids:
                    line_top, line_left, line_bottom, line_right = get_coords(
                        hierarchy, line
                    )
                    line_coords = [
                        line_top,
                        line_left,
                        line_bottom,
                        line_right,
                    ]

                    criterion = same_contour(rectangular_coords, line_coords)
                    if criterion is True:
                        # TODO : remove redundancy of appending lines at a time and then substituting their corresponding hierarchy
                        contour_line_mapping[_id]["line"].append(line)
                        line_ids.append(line)

    # TODO : remove overlapping line sbetween rectangular contours
    hierarchy = remove_heirarchy(hierarchy, line_ids)
    return contour_line_mapping, hierarchy, _id


def get_text_contours(line_word_hierarchy, lines):
    order = sort_xy(line_word_hierarchy, lines)
    return " ".join([line_word_hierarchy[line]["text"] for line in order])


def get_text_from_contours(
    contour_line_association_3, line_word_hierarchy_copy
):
    contour_line_association = deepcopy(contour_line_association_3)
    for contour in contour_line_association_3:
        contour_line_association[contour].pop("line", None)
        lines = contour_line_association_3[contour]["line"]
        if len(lines) > 0:
            text = get_text_contours(line_word_hierarchy_copy, lines)
            contour_line_association[contour]["line"] = defaultdict(dict)
            contour_line_association[contour]["text"] = text
            for line in lines:
                contour_line_association[contour]["line"][
                    line
                ] = line_word_hierarchy_copy[line]
    return contour_line_association


def naming_ordered_dict(hierarchy, order):
    return {_id + 1: hierarchy[element] for _id, element in enumerate(order)}


def get_format(contour_line_association, line_word_hierarchy):
    contour_line_association_copy = deepcopy(contour_line_association)
    contour_ids = []
    for contour in contour_line_association:
        if "line" in contour_line_association[contour]:
            contour_ids.append(contour)
            if len(contour_line_association[contour]["line"]) > 0:
                lines = contour_line_association[contour]["line"]
                for line in lines:
                    if (
                        "words"
                        in contour_line_association[contour]["line"][line]
                    ):
                        words = contour_line_association[contour]["line"][
                            line
                        ]["words"]
                        word_ids = list(words.keys())
                        word_order = sort_xy(
                            line_word_hierarchy[line]["words"], word_ids
                        )
                        named_word_order = naming_ordered_dict(
                            line_word_hierarchy[line]["words"], word_order
                        )
                        contour_line_association_copy[contour]["line"][line][
                            "words"
                        ] = named_word_order

                line_ids = list(lines.keys())
                line_order = sort_xy(
                    contour_line_association_copy[contour]["line"], line_ids
                )
                named_line_order = naming_ordered_dict(
                    contour_line_association_copy[contour]["line"], line_order
                )
                contour_line_association_copy[contour][
                    "line"
                ] = named_line_order

    contour_order = sort_xy(contour_line_association_copy, contour_ids)
    contour_line_association = naming_ordered_dict(
        contour_line_association_copy, contour_order
    )
    # ToDo: Add cid while initialising, store the state
    cl_copy = deepcopy(contour_line_association)
    for cid, contour in cl_copy.items():
        contour_line_association[cid]["contour_id"] = cid
    return contour_line_association


def get_contours_within_contours(query_contour, settings):
    lw_hierarchy = deepcopy(query_contour["line"])
    font_size = calculate_font_size(query_contour["line"])
    bbox = query_contour["bbox"]
    w = bbox["bottom_right"]["x"] - bbox["top_left"]["x"]
    h = bbox["bottom_right"]["y"] - bbox["top_left"]["y"]
    within_contours = get_virtual_contours(
        query_contour["line"], settings, font_size, w * h, _id=0
    )
    # within_contours = {**{}, **{}, **within_contours}
    contour_line_association = get_text_from_contours(
        within_contours, lw_hierarchy
    )
    contour_line_association = get_format(
        contour_line_association, lw_hierarchy
    )
    return contour_line_association


def find_area_rect(rect_contour):
    top, left, bottom, right = rect_contour
    height = right - left
    width = bottom - top
    return height * width


def sort_contours(rect_contours):
    cnt_areas = {
        index: find_area_rect(rect) for index, rect in enumerate(rect_contours)
    }
    sorted_cnt = sorted(cnt_areas.items(), key=operator.itemgetter(1))
    sorted_rect_contours = [
        rect_contours[cnt_index] for cnt_index, area in sorted_cnt
    ]
    return sorted_rect_contours


def get_contour_line_heirarchy(
    detections, lw_hierarchy, area, settings_post, page_category
):
    font_size = calculate_font_size(lw_hierarchy)
    lw_hierarchy_copy = deepcopy(lw_hierarchy)
    settings = settings_post["Contour_Formation"][page_category]

    rect_contours = detections["Rect_Contours"]

    # text_lines_mapping = marking_lines(
    #    line_word_hierarchy, hor_lines, ver_lines)
    # contours_list = rectangular_contours_using_lines(
    #     line_word_hierarchy, text_lines_mapping)

    rect_contours_sorted = sort_contours(rect_contours)

    contour_line_association_1, lw_hierarchy, _id = association(
        rect_contours_sorted, lw_hierarchy, area, _id=0
    )
    # contour_line_association_2, line_word_hierarchy, _id = association(
    #     contours_list, line_word_hierarchy, area, _id=_id)
    contour_line_association_2 = dict()
    contour_line_association_3 = get_virtual_contours(
        lw_hierarchy, settings, font_size, area, _id
    )

    contour_line_hierarchy = {
        **contour_line_association_1,
        **contour_line_association_2,
        **contour_line_association_3,
    }
    contour_line_association = get_text_from_contours(
        contour_line_hierarchy, lw_hierarchy_copy
    )
    contour_line_association = get_format(
        contour_line_association, lw_hierarchy_copy
    )
    return contour_line_association


if __name__ == "__main__":
    import json
    import os
    import sys

    import common
    import cv2
    import pytesseract
    from text_formatting import format_tess_out

    def drawLabel(
        imgcv,
        text,
        topleft,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        size=None,
        color=(0, 255, 0),
        thickness=None,
    ):
        """Draws text at topleft location."""
        h, w = imgcv.shape[:2]
        x, y = topleft
        if not thickness:
            thickness = max(1, (h + w) // 500)
        if not size:
            size = max(0.001 * h, 0.5)
        yoff = -10 if y > 20 else 20  # text remains inside image
        cv2.putText(
            imgcv,
            text,
            (x, y + yoff),
            font,
            size,
            color,
            thickness,
            cv2.LINE_AA,
        )
        return imgcv

    def drawObjects(imgcv, det, tid, color=(0, 255, 0), thickness=2):
        h, w = imgcv.shape[:2]
        if not thickness:
            thickness = max(1, (h + w) // 500)
        x1, y1 = det["bbox"]["top_left"]["x"], det["bbox"]["top_left"]["y"]
        x2, y2 = (
            det["bbox"]["bottom_right"]["x"],
            det["bbox"]["bottom_right"]["y"],
        )
        cv2.rectangle(imgcv, (x1, y1), (x2, y2), color, thickness)
        text = "id_%s" % (tid)
        imgcv = drawLabel(
            imgcv, text, (x1, y1), color=color, size=1.5, thickness=thickness
        )
        return imgcv

    WORK_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(WORK_DIR, "../../pre-processing"))
    import pre_processing as sara_pre

    settings_file = os.path.join(
        WORK_DIR, "../../pre-processing/pre_processing.json"
    )
    with open(settings_file, mode="r") as f:
        settings_pre = json.load(f)

    im_path = "/home/aesta/work/Sara/sara_data/test/1-7-8-12-11 -litasco1406770_0.png"
    config = '''-l eng --psm 11 --oem 1 -c tessedit_char_whitelist=
                ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
                0123456789/#-.+()@&%$,:\\'\\"'''
    imgcv = cv2.imread(im_path)
    imgcv_bw = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(imgcv_bw, (5, 5), 0)
    _, img_bin = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    h, w = imgcv.shape[:2]
    area = h * w

    detections = sara_pre.detect_contours(
        img_bin, settings_pre["Detect_Contours"]
    )
    # detections = {"Rect_Contours": [], "Hough_Lines": []}
    out = pytesseract.image_to_data(
        imgcv_bw, config=config, output_type=pytesseract.Output.DICT
    )
    line_word_hierarchy = format_tess_out(out, (h, w))

    clw_heirarchy = get_contour_line_heirarchy(
        detections, line_word_hierarchy, area
    )
    for _id, para in clw_heirarchy.items():
        imgcv = drawObjects(imgcv, para, _id)
        print(para)
        in_paras = get_contours_within_contours(para)
        for _id2, ipara in in_paras.items():
            imgcv = drawObjects(imgcv, ipara, _id2, (0, 0, 255))
            for _id3, line in ipara["line"].items():
                imgcv = drawObjects(imgcv, line, _id3, (255, 0, 0))

    # print(get_contours_within_contours(clw_heirarchy[3]))

    common.showImage(imgcv)
    cv2.waitKey(0)
