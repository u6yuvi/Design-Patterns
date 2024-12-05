from collections import defaultdict

from .utils_contourizing import get_coords, iom_1d


def sort_lines(target_contour, contours, contour_line_association, co_ord):
    """
    This function sorts contours in one specific direction, based on their
    distance from the target contour.

    :param target_contour: contour for which association needs to be done
    :type target_contour: string
    :param contours: contours associated with target contour in one direction
    :type contours: list
    :param contour_line_association: contour, line and word level hierarchy
    :type contour_line_association: dictionary
    :param co_ord: identifier for checking if the contours must be sorted
                   according to vertical/horizontal distance
    :type co_ord: string
    :return: associated contours in one direction, which are closest to the
             target contour.
    :rtype: list
    """
    rec = dict()
    for contour in contours:
        left, top, _, _ = get_coords(contour_line_association, contour)
        target_left, target_top, _, _ = get_coords(
            contour_line_association, target_contour
        )
        if co_ord == "left":
            rec[contour] = abs(target_left - left)
        elif co_ord == "top":
            rec[contour] = abs(target_top - top)
    minimum_distance = min(rec.values())
    sorted_contours = [
        cont_num
        for cont_num, cord_dist in rec.items()
        if cord_dist <= ((0.02 * minimum_distance) + minimum_distance)
    ]
    return sorted_contours


def sort_directionwise(target_contour, mapping, clw_heirarchy):
    """
    This function accepts a dictionary of contours associated in all
    directions, and returns contours sorted according to distance in
    each direction.
    :param target_contour: contour for which association needs to be done
    :type target_contour: string
    :param mapping: contours associated in each direction
    :type mapping: dictionary
    :param clw_heirarchy: contour, line and word level hierarchy
    :type clw_heirarchy: dictionary
    :return: contours sorted according to distance in each direction
    :rtype: dictionary
    """
    sorted_contours = dict()
    for direction in mapping:
        if direction == "bottom" or direction == "top":
            sorted_contours[direction] = sort_lines(
                target_contour, mapping[direction], clw_heirarchy, "top"
            )
        elif direction == "right" or direction == "left":
            sorted_contours[direction] = sort_lines(
                target_contour, mapping[direction], clw_heirarchy, "left"
            )
    return sorted_contours


def association(target_contour, clw_heirarchy, line_id):
    """
    This function takes the target contour and identifies and associates
    contours in all directions using IOU and distance.

    :param target_contour: contour for which association needs to be done
    :type target_contour: string
    :param clw_heirarchy: contour, line and word level hierarchy
    :type clw_heirarchy: dictionary
    :return: contours associated in all directions of the target contour
    :rtype: dictionary
    """
    mapping = defaultdict(list)
    margin = 0
    if line_id is not None:
        lwh = clw_heirarchy[target_contour]["line"]
        target_left, target_top, target_right, target_bottom = get_coords(
            lwh, line_id
        )
    else:
        target_left, target_top, target_right, target_bottom = get_coords(
            clw_heirarchy, target_contour
        )
    # contour_line_association = deepcopy(clw_heirarchy)
    # contour_line_association.pop(target_contour)
    contour_line_association = clw_heirarchy

    for contour in contour_line_association:
        if contour != target_contour:
            if check_useful_contour(contour, clw_heirarchy):
                (
                    contour_left,
                    contour_top,
                    contour_right,
                    contour_bottom,
                ) = get_coords(contour_line_association, contour)
                if (
                    iom_1d(
                        (target_left, target_right),
                        (contour_left, contour_right),
                    )
                    > 0.2
                ):
                    if contour_top >= (target_top - margin):
                        mapping["bottom"].append(contour)
                    elif target_top >= (contour_top - margin):
                        mapping["top"].append(contour)
                elif (
                    iom_1d(
                        (target_top, target_bottom),
                        (contour_top, contour_bottom),
                    )
                    > 0.2
                ):
                    if contour_right <= (target_right - margin):
                        mapping["left"].append(contour)
                    elif target_left <= (contour_left - margin):
                        mapping["right"].append(contour)
    mapping_sorted = sort_directionwise(target_contour, mapping, clw_heirarchy)
    return mapping_sorted


def check_useful_contour(contour, clw_heirarchy):
    """
    This function is used to remove contours without valid text.

    :param mapping:  mapping of contour in all directions
    :type mapping: dictionary
    :param clw_heirarchy: contour, line and word level hierarchy
    :type clw_heirarchy: dictionary
    :return: valid contours in bottom and right directions
    :rtype: dictionary
    """

    text = clw_heirarchy[contour]["text"]
    punctuation_removed = text.translate(
        str.maketrans("", "", "!\"'()*+,-./:;<=>?@[\\]^_`{|}~")
    )
    space_removed = punctuation_removed.replace(" ", "")
    if len(space_removed) > 1:
        if space_removed.isascii():
            return True
        return False
    else:
        return False


def get_contour_in_useful_dir(contours, useful_directions):
    useful_contours = {
        direction: contours[direction]
        for direction in contours
        if direction in useful_directions
    }
    return useful_contours


if __name__ == "__main__":
    import json
    import os

    import cv2 as cv
    from utils import get_coords, iou_1d

    folders = os.listdir("/home/rajathcurl/Desktop/Sara/sara-backend/debug")
    for folder_name in folders:
        try:
            json_file_path = "/home/rajathcurl/Desktop/Sara/sara-backend/debug/clw_heirarchy.json"
            image_file_path = "/home/rajathcurl/Desktop/Sara/sara-backend/debug/0_Enhanced.png"

            with open(json_file_path, mode="r") as f:
                contour_line_association = json.load(f)

            image = cv.imread(image_file_path)

            for contour in contour_line_association:
                img = image.copy()
                target_contour = contour
                mapping = association(target_contour, contour_line_association)
                mapping = remove_useless_contours(
                    mapping, contour_line_association
                )
                img = cv.rectangle(
                    img,
                    (
                        contour_line_association[target_contour]["bbox"][
                            "top_left"
                        ]["x"],
                        contour_line_association[target_contour]["bbox"][
                            "top_left"
                        ]["y"],
                    ),
                    (
                        contour_line_association[target_contour]["bbox"][
                            "bottom_right"
                        ]["x"],
                        contour_line_association[target_contour]["bbox"][
                            "bottom_right"
                        ]["y"],
                    ),
                    (0, 255, 0),
                    10,
                )
                for direction in mapping:
                    for cont in mapping[direction]:
                        img = cv.rectangle(
                            img,
                            (
                                contour_line_association[cont]["bbox"][
                                    "top_left"
                                ]["x"],
                                contour_line_association[cont]["bbox"][
                                    "top_left"
                                ]["y"],
                            ),
                            (
                                contour_line_association[cont]["bbox"][
                                    "bottom_right"
                                ]["x"],
                                contour_line_association[cont]["bbox"][
                                    "bottom_right"
                                ]["y"],
                            ),
                            (255, 0, 0),
                            10,
                        )
                cv.imwrite(
                    "test/"
                    + folder_name
                    + "_"
                    + str(target_contour)
                    + "_.png",
                    img,
                )
        except:
            pass
