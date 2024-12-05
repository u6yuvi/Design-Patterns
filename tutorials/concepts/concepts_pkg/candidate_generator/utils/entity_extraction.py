#!/usr/bin/env python
import json
import logging
import os
import re
from copy import deepcopy

# from post_processing.utils import entity_recognition
from concepts_pkg.utils.string_match import StringFound, StringMatch

# from post_processing.template_embedding import is_anchor
# from post_processing.utils_gen_search import StringFound
from .utils_contourizing import calculate_font_size

# from .ref_search import RefCosSim, RefNearNBR
# from collections import defaultdict,Counter
# from post_processing.ml_utils import entity_model_classification

logger = logging.getLogger("Entity Extractor")
WORK_DIR = os.path.dirname(os.path.abspath(__file__))


# def read_ref_file(values_file):
#     values_path = os.path.join(WORK_DIR, '..', 'values', values_file)
#     with open(values_path, mode="r") as f:
#         values = json.load(f)
#     return values["values"]

# # initialise all the reference
# ref_data = {
#     "barge_name.json": RefCosSim(read_ref_file("barge_name.json")),
#     "vessel.json": RefCosSim(read_ref_file("vessel.json")),
#     "organization.json": RefCosSim(read_ref_file("organization.json")),
#     "legal_entity.json": RefCosSim(read_ref_file("legal_entity.json")),
#     "ports.json": RefCosSim(read_ref_file("ports.json")),
#     "commodity.json": RefCosSim(read_ref_file("commodity.json")),
#     "country.json": RefCosSim(read_ref_file("country.json"))
#     }

# # TODO Hack specific for getting anchor non anchors
def clean_text_nsa(text):
    """
    This function converts text to lowercase, removes punctuations and returns list by splitting text on spaces
    :param text: string
    :return: list
    """
    # text = re.sub(r'[\.]', '', text)
    text = re.sub(r"[^a-zA-Z0-9#:\s]", " ", text)
    return " ".join(text.split())


# def get_conf_labels(labels, settings):
#     confidence = 0
#     for label in labels:
#         if label in settings:
#             confidence += settings[label]
#     return confidence


# def get_conf_tags(pos_tags, settings):
#     confidence = 0
#     for tag in pos_tags:
#         if tag in settings:
#             confidence += settings[tag]
#     return confidence


# def form_lw_heirarchy(clw_hierarchy):
#     heirarchy = {100*c_key+l_key: l_value for c_key, c_value in
#                     clw_hierarchy.items() for l_key, l_value in
#                     c_value['line'].items()}
#     return heirarchy


# def get_conf_value_based(value, settings):
#     confidence = 0
#     discard_list = settings["discard"]["values"]
#     discard_conf = settings["discard"]["confidence"]
#     settings_conf = settings["conf"]
#     conf_list = settings_conf["values"]
#     conf = settings_conf["confidence"]

#     if "values_file" in settings_conf:
#         for values_file in settings_conf["values_file"]:
#             # using ref search first and then string match
#             if values_file in ref_data:
#                 matcher = ref_data[values_file]
#                 candidates = matcher.find_best_match(value.lower())
#                 if candidates:
#                     conf_list += [val for val, conf in candidates]
#             else:
#                 conf_list += read_ref_file(values_file)

#     for word in discard_list:
#         if StringMatch.string_match(word, value):
#             confidence += discard_conf

#     for word in conf_list:
#          if StringMatch.string_match(word, value):
#             confidence += conf

#     return confidence


# def get_conf_length_based(value, settings):
#     confidence = 0
#     conf = settings["confidence"]
#     thresh = settings["threshold"]
#     if len(value.split()) >= thresh:
#         confidence += conf
#     return confidence


# def get_conf_reference_based(value, settings, threshold=0.8):
#     """
#     Function is called when we need to override the value extracted to different value from the json value file.
#     :param threshold: Threshold match needed for overriding value
#     :param value: str
#     :param settings: configuration
#     :return:
#     confidence: confidence with or without overriding
#     mod_value: modified value
#     """
#     search_list = list()
#     if "values_file" in settings:
#         for values_file in settings["values_file"]:
#             if values_file in ref_data:
#                 matcher = ref_data[values_file]
#                 candidates = matcher.find_best_match(value.lower())
#                 if candidates:
#                     search_list += [val for val, conf in candidates]
#             else:
#                 search_list += read_ref_file(values_file)
#         search_list = [str(var).upper() for var in search_list]

#     values = []
#     for search_word in search_list:
#         match = StringMatch.string_match(clean_text(search_word), clean_text(value))
#         if match and match.similarity>80:
#             values.append((match.similarity, search_word))

#     if values:
#         values = sorted(values , key=lambda elem: elem[0], reverse=True)
#         max_conf = values[0][0]
#         if max_conf == 100:
#             mod_value_list = [value for conf, value in values if conf == 100.0]
#         else:
#             mod_value_list = [values[0][1]]

#         # Check if both short names and long names are present
#         if len(mod_value_list) > 1:
#             mod_value_list = list(set(mod_value_list))
#             sort_values_len = sorted(mod_value_list, key=lambda elem: len(elem))
#             remove_list = list()
#             for i, entity_extracted in enumerate(sort_values_len):
#                 for compare_entity_extracted in sort_values_len[i + 1:]:
#                     if entity_extracted.lower() not in compare_entity_extracted.lower(): continue
#                     remove_list.append(i)
#                     break

#             mod_value_list = [entity_extracted for i, entity_extracted in enumerate(sort_values_len)
#                               if i not in remove_list]

#         return 50, mod_value_list
#     else:
#         return 0, [value]


# def get_confidence(value, val_contour, settings):
#     confidence = 0

#     if "labels" in settings:
#         for lid, line_val in val_contour['line'].items():
#             labels = line_val['meta']['spv']['clean_text_tags']
#             confidence += get_conf_labels(labels, settings["labels"])
#         logger.debug(f"SPV entities found for: '{value}' is {labels}")

#         # print("confidence_1.0", confidence)
#     if "pos_tags" in settings:
#         doc = entity_recognition(value.strip())
#         pos_tags = [token.pos_ for token in doc]
#         logger.debug(f"POS tags found for: '{doc.text}' is {pos_tags}")
#         confidence += get_conf_tags(pos_tags, settings["pos_tags"])
#         # print("confidence_2.0",confidence)
#     if "value_based" in settings:
#         confidence += get_conf_value_based(value, settings["value_based"])
#         # print("confidence_3.0",confidence)
#     if "length_based" in settings:
#         confidence += get_conf_length_based(value, settings["length_based"])
#         # print("confidence_4.0",confidence)
#     if "reference_based" in settings:
#         conf, mod_value = get_conf_reference_based(
#             value.lower(), settings["reference_based"])
#         confidence += conf
#     # if "ml_model_based" in settings:
#     #     logger.debug(f'Running ML Model for confidence..')
#     #     conf = entity_model_classification(value)
#     #     logger.debug(f'Confidence score:{conf}')
#     #     confidence += conf
#     # #     print("confidence_5.0",confidence)
#     # # print("---", mod_val)
#     return confidence, value


def get_entity(val_contour, kw_found, settings, ref_obj):
    lines_to_extract = settings["number_of_lines_to_extract"]
    lines_to_extract_wo_ref = settings.get(
        "number_of_lines_wo_ref", lines_to_extract
    )
    # settings_conf = settings['confidence']
    # use_ana = settings_conf["value_based"]["discard"].get("use_ana", False)

    line_ordinate = kw_found.contour["line"][kw_found.lids[-1]]["bbox"][
        "top_left"
    ]["y"]
    font_size = calculate_font_size(val_contour["line"])
    line_count = 0
    entities = list()

    res = list()
    for lid, line in val_contour["line"].items():
        dist = abs(
            line["bbox"]["top_left"]["y"]
            - kw_found.contour["line"][kw_found.lids[0]]["bbox"]["top_left"][
                "y"
            ]
        )
        res.append([lid, dist])
    res = sorted(res, key=lambda x: x[1])

    for lid, _ in res:
        line = val_contour["line"][lid]

        # for lid, line in val_contour['line'].items():
        l_oridinate = line["bbox"]["top_left"]["y"]
        if (line_ordinate - l_oridinate) <= 2 * font_size:
            line_count += 1
            if line_count > lines_to_extract + 3:
                break

            raw_value = line["text"].strip().lstrip(":")
            value = clean_text_nsa(raw_value)

            # if kw_found.cid==val_contour["contour_id"] and l_oridinate==line_ordinate:
            #     value = value[kw_found.match.end:]
            #     raw_value = raw_value[kw_found.match.end:]

            if value.isspace() or len(value) < 3:
                continue

            # Commented in this version-------------Check for any discrepancy
            # if use_ana and is_anchor(raw_value):
            #     continue

            # Get confidences of lines
            # TODO: Use raw value for getiing confidence, do cleaning inside
            # confidence, value = get_confidence(value, val_contour, settings_conf)
            # logger.debug(f"Total confidence of '{value}' is: {confidence}")
            # if confidence>0:
            entities.append((value, lid, 100))

    if entities:
        values = " ".join([value for value, _, _ in entities])
        lids = [lid for _, lid, _ in entities]
        conf = max([conf for _, _, conf in entities])
        out_contour = deepcopy(val_contour)
        for value, lid, _ in entities:
            out_contour["line"][lid]["text"] = value.strip().strip(":")
        str_match = StringMatch(-1, 100, 0, values)
        return [(StringFound(out_contour, lids, str_match), conf)]
    else:
        return []


if __name__ == "__main__":
    pass
