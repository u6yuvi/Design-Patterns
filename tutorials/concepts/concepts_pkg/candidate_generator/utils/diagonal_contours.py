import os
import sys
from collections import defaultdict


def check_in_rectangle(target_contour, rectangle_xy):
    """Multiple if to check complexity over time as
    I can see if one condition is false then
    why to go for other return it's value directly
    """
    flag = False
    rectangle_xy_top = rectangle_xy[0]
    rectangle_xy_bottom = rectangle_xy[1]
    if target_contour["top_left"]["x"] >= rectangle_xy_top[0]:
        if target_contour["top_left"]["y"] >= rectangle_xy_top[1]:
            if target_contour["bottom_right"]["x"] <= rectangle_xy_bottom[0]:
                if (
                    target_contour["bottom_right"]["y"]
                    <= rectangle_xy_bottom[1]
                ):
                    flag = True
                    return flag
            else:
                return flag
        else:
            return flag
    else:
        return flag


def search_within_limited_contours(
    clw_hierarchy: dict,
    existing_contour: dict,
    anchor_cid: int,
    anchor_lid: int,
    candidate_logger: list,
):
    check_x = 0
    check_y = 0
    new_contour = defaultdict(list)
    new_contour["bottom_right"] = []
    associated_contour = []
    for contour_direction, ass_contour_info in existing_contour.items():
        # ass_contour_lst= list(ass_contour_info.keys())
        for ass_contour in ass_contour_info:
            ass_cid = list(ass_contour.keys())[0]
            associated_contour.append(ass_cid)
            if contour_direction == "right":
                if (
                    clw_hierarchy[ass_cid]["bbox"]["bottom_right"]["x"]
                    > check_x
                ):
                    check_x = clw_hierarchy[ass_cid]["bbox"]["bottom_right"][
                        "x"
                    ]
            # Assuming that other direction will be bottom
            elif contour_direction == "bottom":
                if (
                    clw_hierarchy[ass_cid]["bbox"]["bottom_right"]["y"]
                    > check_y
                ):
                    check_y = clw_hierarchy[ass_cid]["bbox"]["bottom_right"][
                        "y"
                    ]

    top_left_x = clw_hierarchy[anchor_cid]["bbox"]["top_left"]["x"]
    top_left_y = clw_hierarchy[anchor_cid]["bbox"]["top_left"]["y"]
    rectangle_xy = [(top_left_x, top_left_y), (check_x, check_y)]
    for target_cid, target_contour in clw_hierarchy.items():
        if check_in_rectangle(target_contour["bbox"], rectangle_xy):
            if (target_cid not in candidate_logger) and (
                target_cid not in associated_contour
            ):
                # check those cases when all these fails and bottom_right never appears
                new_contour["bottom_right"].append(target_cid)
                candidate_logger.append(target_cid)
    if new_contour["bottom_right"]:
        existing_contour["bottom_right"] = list()
        for cid in new_contour["bottom_right"]:
            existing_contour["bottom_right"].append({cid: clw_hierarchy[cid]})

    return existing_contour


if __name__ == "__main__":
    print(search_within_limited_contours({}, {}, 0, 0, []))
