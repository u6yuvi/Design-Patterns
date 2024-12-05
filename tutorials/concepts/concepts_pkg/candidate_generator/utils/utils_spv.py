import logging
from collections import Counter, defaultdict

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .utils_prs import (
    create_new_clw,
    get_value_obj,
    get_virtual_contours,
    key_cand_meta,
)

logger = logging.getLogger("Utils-SPV")




def extract_qty_unit_qty_type_from_spv(clw_logical_json, extraction_tag, tags):
    extraction_data = defaultdict(list)
    
    for contour_id , contour_info in clw_logical_json.items():
        for line_id, line_info in contour_info["line"].items():

            clean_tags = line_info["meta"]["spv"]["clean_text_tags"]
            clean_tokens = line_info["meta"]["spv"]["clean_text_tokens"]
            
            if extraction_tag in tags and extraction_tag in clean_tags:
                # the tag which needs to extracted is there in spv
                text = line_info["text"]
                c = Counter([i if i in tags else "O" for i in clean_tags])
                tag, count = c.most_common(1)[0]
                template = check_the_continuos_template(clean_tags)
                if ((tag == extraction_tag and count/sum(c.values())>=0.55 and "O" in c) 
                    or 
                    (tag == extraction_tag and count/sum(c.values())==1.0)
                    or  
                    ("O" not in c and len(tags.intersection(set(c.keys())))!=0 and 
                        len(template)==0 and count/sum(c.values())>=0.75)
                ):
                    """
                    unit, unit, unit, o, cardinal -> unit
                    unit, unit, o, cardinal -> unit
                    unit, unit, O -> unit
                    
                    unit, unit, unit -> unit
                    cardinal -> cardinal

                    Unit, Unit, cardinal, unit -> Unit
                    """
                    extraction_data[tag].append({"text":text,
                                    "contour_id":contour_id,
                                    "line_id":line_id,
                                    "start":0,
                                    "end":len(text)})
                    
                elif c[extraction_tag]==1 and len(tags.intersection(set(c.keys()))) ==2 and "O" in c:
                    """
                    equal ratio with one unit and one cardinal
                    o ,o ,o ,o ,o , unit, cardinal -> unit cardinal
                    unit , o, cardinal -> unit, cardinal
                    """
                    c.pop("O")
                    if c[extraction_tag]/sum(c.values())==0.5:
                        word_text = clean_tokens[clean_tags.index(extraction_tag)]
                        start_index = text.find(word_text) # index of word token with respect to the line text
                        extraction_data[extraction_tag].append({"text":word_text,
                                                                "line_id":line_id,
                                                                "contour_id":contour_id,
                                                                "start":start_index,
                                                                "end": start_index+len(word_text)})

                elif ("O" not in c and len(tags.intersection(set(c.keys())))!=0 and len(template)>0):
                    """
                    unit, unit, cardinal, cardinal ->  unit. cardinal
                    unit, cardinal -> unit, cardinal
                    qty_type, unit, cardinal -> qty_type, unit, cardinal
                    unit, cardinal cardinal -> unit, cardinal
                    """
                    word_text = " ".join(clean_tokens[i] for i in template[extraction_tag])
                    start_index = text.find(word_text)
                    end_index = start_index + len(word_text)- len(template[extraction_tag])-1
                    extraction_data[extraction_tag].append({"text":word_text,
                                                            "line_id":line_id,
                                                            "contour_id":contour_id,
                                                            "start":start_index,
                                                            "end": end_index})
    return extraction_data

def check_the_continuos_template(clean_tags):
    """
    ["unit", "unit", "cardinal"] -> {'unit': [0, 0], 'cardinal': [2]} 
    ["unit", "unit", "cardinal", "cardinal"] -> {'unit': [0, 0], 'cardinal': [2, 2]}
    ["qty_type","qty_type","cardinal","unit"] ->  {'qty_type': [0, 0], 'cardinal': [2], 'unit': [3]}
    ["unit","unit","cardinal","unit"] -> {}
    ["unit","unit","cardinal","unit","cardinal"] -> {}
    ["unit","unit","cardinal","qty","cardinal"] -> {}
    """
    s = defaultdict(list)
    index =0
    ss = set()
    while True:
        for ind , tag in enumerate(clean_tags[index:], index):
            if clean_tags[index] in ss:
                return {}
            if tag == clean_tags[index]:
                s[clean_tags[index]].append(ind)
                continue
            else:
                ss.add(clean_tags[index])
                index = ind
                break
        else :
            return s




def extract_candidate_spv(
    clw_logical_hierarchy,
    input_tags =["ORG"],
    tag_threshold=0.75,
):
    """
    With help of input_tag lable we can find the number of lines with that tag present in
    the document
    """
    # extraction_candidates = defaultdict(list)
    # keyword = "document_issuer"
    # keyword_dict = {keyword: input_tag}
    # extraction_tag = keyword_dict[keyword]
    # tags = set(keyword_dict.values())
    result = []
    for c_id, contour_info in clw_logical_hierarchy.items():
        for line_id, line_info in contour_info["line"].items():
            clean_tags = line_info["meta"]["spv"]["clean_text_tags"]
            # clean_tokens = line_info["meta"]["spv"]["clean_text_tokens"]
            for input_tag in input_tags:
                if input_tag in clean_tags:
                    text = line_info["text"]
                    cnt = Counter([i for i in clean_tags])
                    # tag, count = cnt.most_common(1)[0]
                    if cnt[input_tag]:
                        # tag = input_tag
                        count = cnt[input_tag]
                        if count / sum(cnt.values()) > tag_threshold:
                            temp_match_obj = StringMatch(len(text), 100, 0,text)
                            temp_value_obj = StringFound(
                                clw_logical_hierarchy[c_id],
                                [line_id],
                                temp_match_obj,
                            )
                            result.append(temp_value_obj)
    return result


def single_line_extraction(extraction_stgy_config, data):
    """
    Generate candidates using the given SPV Tag and % of SPV Tags
    present in a CLW Hierarchy Line.
    0 % - Extract all the lines which has atleast one given SPV Tag.
    100% - Extract all the lines which has no other token tags
    except the given SPV Tag.
    """
    logger.info(f"Running SPV SingleLine Extraction")
    spv_tag = extraction_stgy_config["single_line_extraction"]["spv_tag"]
    tag_threshold = extraction_stgy_config["single_line_extraction"][
        "tag_threshold"
    ]
    cand_generated_values = {}
    search_word_result = []
    spv_result = extract_candidate_spv(
        data["clw"], input_tags=spv_tag, tag_threshold=tag_threshold
    )
    if len(spv_result) > 0:
        for _, val_obj in enumerate(spv_result):
            search_word_result.append(KeyValueFound(None, val_obj, 100))
        cand_generated_values["spv"] = search_word_result
        # return cand_generated_values
    return cand_generated_values


def multi_line_extraction(extraction_stgy_config, data):
    """
    SPV Candidate Extraction working on multiline values
    with relevant spv tag.
    """
    # TODO  SPV Tag based result selection
    logger.info(f"Running SPV Multiline Extraction")
    spv_tag = extraction_stgy_config["multi_line_extraction"]["spv_tag"]
    cand_generated_values = {}
    search_word_result = []
    key_cand_results = []
    if data.get("spv_address", False):
        for result in data["spv_address"]:
            cand_results = [(line[0], line[1]) for line in result]
            key_cand_results.append(
                key_cand_meta(
                    "None",
                    [i[0] for i in cand_results],
                    "None",
                    [i[1] for i in cand_results],
                )
            )
        new_clw = create_new_clw(data["clw"])
        if key_cand_results:
            for res in key_cand_results:
                virtual_clw = get_virtual_contours(res, new_clw)
                search_word_result.append(
                    KeyValueFound(
                        None,
                        get_value_obj(virtual_clw, res.layout),
                        100,
                    )
                )
            cand_generated_values["spv"] = search_word_result
            # return cand_generated_values
    return cand_generated_values


spv_extraction_stgy_map = {
    "single_line_extraction": single_line_extraction,
    "multi_line_extraction": multi_line_extraction,
}
