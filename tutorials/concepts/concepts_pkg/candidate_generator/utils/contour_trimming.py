import logging
from copy import deepcopy

# from post_processing.template_embedding import is_anchor
from .association import association
from .contourizing import get_text_contours
from .utils_contourizing import calculate_font_size, sort_xy

logger = logging.getLogger("Value line estimation")


def get_associated_lines(clw_hierarchy, key_cid, key_lid):
    """Get associated trimmed contour in each direction

    :param clw_hierarchy: [description]
    :type clw_hierarchy: dict
    """
    contour_lines = clw_hierarchy[key_cid]["line"]
    key_ord = contour_lines[key_lid]["bbox"]["top_left"]["y"]
    sorted_lids = sort_xy(contour_lines, contour_lines.keys())
    keya_idx = sorted_lids.index(key_lid)

    # Check other keywords in that contour bottom to key-anchor
    bottom_keyword_present = False

    # Commentng Anchor based rejection .-----------------Check for discrepancy
    # for lid in sorted_lids[keya_idx+1:]:
    #     # TODO: Will fail if single keyword is spanned across multiple lines
    #     if is_anchor(contour_lines[lid]["text"]):
    #         bottom_keyword_present = True
    #         next_keya_lid = lid
    #         break

    association_mapping = association(key_cid, clw_hierarchy, key_lid)
    font_size = calculate_font_size(clw_hierarchy[key_cid]["line"])

    # For right associated contours
    right_cids = association_mapping.get("right", [])
    bottom_cids = association_mapping.get("bottom", [])

    stripped_clws = []
    for cid in right_cids:
        stripped_contour = {cid: deepcopy(clw_hierarchy[cid])}
        stripped_contour[cid]["line"] = {}
        for lid, line in clw_hierarchy[cid]["line"].items():
            ass_line_ord = line["bbox"]["top_left"]["y"]
            if (
                key_ord - ass_line_ord
            ) >= font_size * 2:  # skip lines infront of and above
                continue
            reverse_mapping = association(cid, clw_hierarchy, lid)
            left_cids = reverse_mapping.get("left", [])

            if bottom_keyword_present and key_cid in left_cids:
                if (
                    contour_lines[next_keya_lid]["bbox"]["top_left"]["y"]
                    - ass_line_ord
                    < font_size / 2
                ):
                    break

            is_bottom = [lcid for lcid in left_cids if lcid in bottom_cids]
            if is_bottom:
                # TODO: double check for presence of keyanchor
                break
            stripped_contour[cid]["line"][lid] = line

        stripped_contour[cid]["text"] = get_text_contours(
            stripped_contour[cid]["line"], stripped_contour[cid]["line"].keys()
        )
        stripped_clws.append(stripped_contour)
    association_mapping["right"] = stripped_clws

    # For bottom associated contours
    if bottom_keyword_present:
        association_mapping["bottom"] = []
    else:
        association_mapping["bottom"] = [
            {cid: clw_hierarchy[cid]} for cid in bottom_cids
        ]

    association_mapping["top"] = [
        {cid: clw_hierarchy[cid]} for cid in association_mapping.get("top", [])
    ]
    association_mapping["left"] = [
        {cid: clw_hierarchy[cid]}
        for cid in association_mapping.get("left", [])
    ]

    return association_mapping
