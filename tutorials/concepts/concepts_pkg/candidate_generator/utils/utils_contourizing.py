import re
import statistics
import string
from copy import deepcopy

import numpy as np
import pandas as pd


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


def iom_1d(lineA, lineB):
    """
    Intersection of minimum of two lines (one dimension)
    example : [100,200,150,250] and [125,275,175,325]
    if you want to find horizontal iou then, lineA = [100,150] and lineB = [125,175]
    for vertical iou, lineA = [200,250] and lineB = [275,325]
    :param lineA: co ordinates in above specified format
    :param lineB: co ordinates in above specified format
    :return: Intersection of union in one dimension
    """
    xA = max(lineA[0], lineB[0])
    xB = min(lineA[1], lineB[1])

    intersection = max(0, xB - xA)
    union = min(lineA[1] - lineA[0], lineB[1] - lineB[0])
    if union == 0:
        return intersection
    else:
        return intersection * 1.0 / union


def iou(box_a, box_b):
    """
    Function returns the intersection over union between two rectangles
    :param box_a: Rectangle on which the amount of intersection has to be found
    :param box_b: Rectangle for comparision
    :return: Intersection over union
    """
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    iou = inter_area / float(box_a_area)
    return iou


def iom(box_a, box_b):
    """
    Function returns the intersection over minimum between two rectangles
    :param box_a: Rectangle on which the amount of intersection has to be found
    :param box_b: Rectangle for comparision
    :return: Intersection over minimum
    """
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    box_b_area = (box_b[2] - box_b[0] + 1) * (box_b[3] - box_b[1] + 1)
    iom = inter_area / float(min(box_a_area, box_b_area))
    return iom


def get_coords(hierarchy, element):
    right = hierarchy[element]["bbox"]["bottom_right"]["x"]
    bottom = hierarchy[element]["bbox"]["bottom_right"]["y"]
    left = hierarchy[element]["bbox"]["top_left"]["x"]
    top = hierarchy[element]["bbox"]["top_left"]["y"]
    return left, top, right, bottom


def bbox_to_coords(bbox, tuple_of_tuple=False):
    x1, y1 = int(bbox["top_left"]["x"]), int(bbox["top_left"]["y"])
    x2, y2 = int(bbox["bottom_right"]["x"]), int(bbox["bottom_right"]["y"])
    if tuple_of_tuple:
        return (x1, y1), (x2, y2)
    return (x1, y1, x2, y2)


def get_contour_coords(hierarchy, elements):
    co_ords = [get_coords(hierarchy, line) for line in elements]
    height_coords, width_coords = list(), list()
    for x1, y1, x2, y2 in co_ords:
        height_coords += [y1, y2]
        width_coords += [x1, x2]
    bbox = {
        "top_left": {
            "x": abs(min(width_coords)),
            "y": abs(min(height_coords)),
        },
        "bottom_right": {"x": max(width_coords), "y": max(height_coords)},
    }
    return bbox


def group_nums(data, maxgap):
    uniq_vals = {data[0]: data[0]}
    for i in range(1, len(data)):
        if not data[i] in uniq_vals.keys():
            dis_grps = list(uniq_vals.values())
            diffs = np.abs(np.array(dis_grps) - data[i])
            if np.min(diffs) >= maxgap:
                uniq_vals[data[i]] = data[i]
            else:
                idx_min = np.argmin(diffs)
                uniq_vals[data[i]] = dis_grps[idx_min]
    return [uniq_vals[x] for x in data]


def sort_xy(hierarchy, contours, maxgap=5):
    loc = [
        {
            "_id": element,
            "x": hierarchy[element]["bbox"]["top_left"]["x"],
            "y": hierarchy[element]["bbox"]["top_left"]["y"],
        }
        for element in contours
    ]
    if loc:
        loc_df = pd.DataFrame.from_dict(loc)
        loc_df["y"] = group_nums(list(loc_df["y"]), maxgap)
        loc_df["x"] = group_nums(list(loc_df["x"]), maxgap)
        loc_df.sort_values(by=["y", "x"], ascending=True, inplace=True)
        order = list(loc_df["_id"])
    else:
        return []
    return order


def group_lines(sorted_lines, adjacent_gaps, max_gap=3):
    """
    This function sorts lines based on gap distance
    """
    line_groups = [[sorted_lines[0]]]
    for i, gap in enumerate(adjacent_gaps):
        if gap > max_gap:
            line_groups.append([sorted_lines[i + 1]])
        else:
            line_groups[-1].append(sorted_lines[i + 1])
    return line_groups


def calculate_font_size(lw_hierarchy):
    font_heights = []
    for line in lw_hierarchy:
        top, left, bottom, right = get_coords(lw_hierarchy, line)
        font_height = right - left
        font_heights.append(font_height)
    if not font_heights:
        return 0
    return statistics.median(font_heights)


def clean_hierarchy(lw_hierarchy):
    """
    Remove text which contains only punctuations or repeated letters (greater than or equal to 5)
    or having length less than or equal to one
    :param lw_hierarchy: line word hierarchy
    :return:
    """
    lw_hierarchy_copy = deepcopy(lw_hierarchy)
    for line_id, element in lw_hierarchy_copy.items():
        line_text = element["text"]
        remove = remove_text_lines(line_text)
        if remove:
            lw_hierarchy.pop(line_id)
    return lw_hierarchy


def remove_text_lines(text):
    """
    Helper function to remove text which contains only punctuations or repeated letters (greater than or equal to 5)
    or having length less than or equal to one
    :param text: string line text
    :return: True if line is to be removed
             False if line is to be retained
    """
    space_removed = "".join(text.split())
    punct_removed = space_removed.translate(
        str.maketrans("", "", string.punctuation)
    )
    repetition = re.search(r"(\D)\1{4,}", punct_removed)
    if not punct_removed.isnumeric() and (
        repetition or len(punct_removed) <= 1
    ):
        return True
    return False


def remove_unicode(text):
    """
    Remove unicode characters from the text string
    :param text: str
    :return: str
    """
    return (text.encode("ascii", "ignore")).decode("utf-8")
