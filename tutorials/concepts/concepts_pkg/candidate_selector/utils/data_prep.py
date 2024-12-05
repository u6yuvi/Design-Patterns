from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch


def k2v_doc_meta(data, doc_type):
    """
    Collect doc_meta for K2V Model.
    """
    doc_name = "test"
    batch_id = "test"
    # doc_type = "coquantity_eng"
    page_height = data["doc_meta"][
        "page_height"
    ]  # Take input from clw or page_data
    page_width = data["doc_meta"][
        "page_width"
    ]  # Take input from clw or page_data
    doc_meta = [doc_name, doc_type, batch_id, page_height, page_width]
    return doc_meta, doc_type


def list_to_keyfound_obj_virtual_contour(clw_hierarchy, final_result):
    """
    when amt and currency line ids are returned , it gets them and create a virtual contour to get key value found
    """
    result = []
    if len(final_result) > 0:
        
        for candidate in final_result:
            candidate['cand_lwhlid']=[i for i in candidate['cand_lwhlid']]
            candidate["key_lwhlid"]=[i for i in candidate["key_lwhlid"]]
            vir_contour_=create_virtual_contour(clw_hierarchy[candidate["cand_cid"][0]],clw_hierarchy[candidate["cand_cid"][1]])
            k2k_confidence = 100
            key_obj = StringMatch(
                len(candidate["key_anchor_text"]),
                k2k_confidence,
                0,
                candidate["key_anchor_text"],
            )
            value_obj = StringMatch(
                len(candidate["candidate_text"]),
                candidate["confidence"],
                0,
                candidate["candidate_text"],
            )

            key_line_ids = []

            for k in range(len(candidate["key_lwhlid"])):
                for key_line, key_info in vir_contour_['line'].items():
                    if key_info["line_id"] == candidate["key_lwhlid"][k]:
                        key_line_ids.append(key_line)
         

            cand_line_ids = []

            for k in range(len(candidate["cand_lwhlid"])):
                for cand_line, cand_info in vir_contour_['line'].items():
                    if cand_info["line_id"] == candidate["cand_lwhlid"][k]:
                        cand_line_ids.append(cand_line)
                        break
         
            key_info_temp = StringFound(
                clw_hierarchy[candidate["key_cid"][0]], key_line_ids, key_obj
            )
            
            val_info_temp = StringFound(
                vir_contour_, cand_line_ids, value_obj
            )
            result.append(
                KeyValueFound(
                    key_info_temp, val_info_temp, candidate["confidence"]
                )
            )

        return result
        
    return {}

def list_to_keyfound_obj(clw_hierarchy, final_result):
    """
    Pack the input to a custom defined String Match and KeyValue Found Objects.
    """
    result = []
    if len(final_result) > 0:
        for candidate in final_result:
            k2k_confidence = 100
            key_obj = StringMatch(
                len(candidate["key_anchor_text"]),
                k2k_confidence,
                0,
                candidate["key_anchor_text"],
            )
            value_obj = StringMatch(
                len(candidate["candidate_text"]),
                candidate["confidence"],
                0,
                candidate["candidate_text"],
            )
            # TODO convert data
            key_line_ids = [
                key_line
                for key_line, key_info in clw_hierarchy[candidate["key_cid"]][
                    "line"
                ].items()
                if key_info["line_id"] == candidate["key_lwhlid"]
            ]
            cand_line_ids = [
                cand_line
                for cand_line, cand_info in clw_hierarchy[
                    candidate["cand_cid"]
                ]["line"].items()
                if cand_info["line_id"] == candidate["cand_lwhlid"]
            ]
            key_info_temp = StringFound(
                clw_hierarchy[candidate["key_cid"]], key_line_ids, key_obj
            )
            val_info_temp = StringFound(
                clw_hierarchy[candidate["cand_cid"]], cand_line_ids, value_obj
            )
            result.append(
                KeyValueFound(
                    key_info_temp, val_info_temp, candidate["confidence"]
                )
            )
        return result
    return {}


# clw_hierarchy[candidate["key_cid"][0]],clw_hierarchy[candidate["key_cid"][1]]
def create_virtual_contour(dict1,dict2):
    virtual_contour={}
    # virtual_contour['bbox']={'top_left':{'x': min(dict1['bbox']['top_left']['x']),'y': min(dict2['bbox']['top_left']['y']),
    #  'bottom_right':{'x': max(dict1['bottom_right']['x']),'y': max(dict2['bottom_right']['y'])}}}

    virtual_contour['bbox']={'top_left': {'x': min(dict1['bbox']['top_left']['x'],dict2['bbox']['top_left']['x']), 'y': min(dict1['bbox']['top_left']['y'],dict2['bbox']['top_left']['y']), },
          'bottom_right': {'x': max(dict1['bbox']['bottom_right']['x'],dict2['bbox']['bottom_right']['x']), 'y': max(dict1['bbox']['bottom_right']['y'],dict2['bbox']['bottom_right']['y']),}}

    virtual_contour['text']=dict1['text']+" "+dict2['text']
    virtual_contour['line']=merge_2_dicts(dict1['line'],dict2['line'])
    virtual_contour['contour_id']=dict1['contour_id']
    virtual_contour['page_num']=dict1['page_num']
    virtual_contour['offset']=0
    virtual_contour['old_cid']=dict1['old_cid']

    return virtual_contour

def merge_2_dicts(d1,d2):
    d3=d1.copy()
    l=len(d3)+1

    for key, value in d2.items():
        d3[l]=value
        l+=1
    return d3
