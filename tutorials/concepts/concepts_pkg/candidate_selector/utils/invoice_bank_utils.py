import logging
from typing import Dict,List
from collections import namedtuple
from ...utils.keyvaluefound import KeyValueFound
from ...utils.string_match import StringFound, StringMatch
from concepts_pkg.candidate_generator.utils.utils_contourizing import calculate_font_size
logger = logging.getLogger("Invoice Bank Utils")


def filter_bankresults(result_dict: Dict,data):
    '''
    Filter Candidates using spatial representation.
    Select candidates which is on the right and sort them based on the closest distance
    in y w.r.t keyalias
    '''
    all_cands = []
    #fetch all candidates
    
    lids_result = []
    logger.info('Collect and Convert contour based results to line results')
    for key, res_lst in result_dict.items():
        for res in res_lst:
            for lid in res.value.lids:
                # dropping candidate which is a keyalias
                if (res.keyword.cid!= res.value.cid) or (lid !=res.keyword.lids[0]):
                    lids_result.append((res.keyword.cid,res.keyword.lids[0],res.value.cid,lid))

    if lids_result:
        logger.info(f'Candidate Selection started..')
        result = []
        for idx , keycand_info in enumerate(lids_result):
            key_xordinate = data["clw"][keycand_info[0]]["line"][keycand_info[1]]["bbox"][
            "top_left"
            ]["x"]
            cand_xordinate = data["clw"][keycand_info[2]]["line"][keycand_info[3]]["bbox"][
                "top_left"
                ]["x"]
            #canddiate on the right
            if cand_xordinate >= key_xordinate:
                #select candidate which is closer in y ordinate w.r.t keyalias
                key_yordinate = data["clw"][keycand_info[0]]["line"][keycand_info[1]]["bbox"][
                    "top_left"
                    ]["y"]
                cand_yordinate = data["clw"][keycand_info[2]]["line"][keycand_info[3]]["bbox"][
                    "top_left"
                ]["y"]
                distance = abs(key_yordinate - cand_yordinate)
                result.append((idx,distance))
        if result:
            sorted_result = sorted(result,key = lambda x : x[1])
            lids_result = list(map(lids_result.__getitem__,[i[0] for i in sorted_result]))
        #logger.info(f'all_cand :{lids_result}')

        for cand in lids_result[:1]:
            return [KeyValueFound(None,get_line_value_obj(data["clw"], cand[2],cand[3]),
                                    100)]
            #logger.info(f'Text  {cand} {data["clw"][cand[2]]["line"][cand[3]]["text"]}')

    logger.info(f'Returning default results.')
    for key, res_lst in result_dict.items():
        all_cands.extend(res_lst)
    for cand in all_cands[0:1]:
        #logger.info(f'cand_info {cand.value.lids} {cand.value.match.match_string}')
        return all_cands[0:1]
    
    
    
    # for returning contour based results
    # for key, res_lst in result_dict.items():
    #     all_cands.extend(res_lst)

    # if all_cands:
    #     result = []
    #     for idx , cand in enumerate(all_cands):
    #         key_xordinate = cand.keyword.contour["line"][cand.keyword.lids[-1]]["bbox"][
    #         "top_left"
    #         ]["x"]
    #         cand_xordinate = cand.value.contour["line"][cand.value.lids[-1]]["bbox"][
    #         "top_left"
    #         ]["x"]
    #         #candidates on the right
    #         if cand_xordinate > key_xordinate:
    #             # select candidates which is right to the keyword
    #             key_yordinate = cand.keyword.contour["line"][cand.keyword.lids[-1]]["bbox"][
    #     "top_left"
    # ]["y"]
    #             cand_yordinate = cand.value.contour["line"][cand.value.lids[-1]]["bbox"][
    #     "top_left"
    # ]["y"]
    #             dist = abs(key_yordinate- cand_yordinate)
    #             result.append((idx,dist))
    #     sorted_result = sorted(result, key=lambda x: x[1])
    #     #logger.info(f'sorted_result :{sorted_result}')
    #     all_cands = list(map(all_cands.__getitem__,[i[0] for i in sorted_result]))
    #     logger.info(f'all_cand :{all_cands}')
    
    # for cand in all_cands[0:1]:
    #     logger.info(f'cand_info {cand.value.lids} {cand.value.match.match_string}')
    # return all_cands[0:1]


def get_line_value_obj(clw,value_cid,value_lid):

    """
    Given a clw,candidate cid and lid create a key value object to be passed to
    KeyValueFound Class
    """
    cand_text =  clw[value_cid]["line"][value_lid]["text"]
    #cand_lids = value_lid
    logger.info(f"Candidate lids {value_lid}")
    value_obj = StringMatch(len(cand_text), 100, 0, cand_text)
    logger.info(f"Candidate text associated {value_obj.match_string}")
    return StringFound(clw[value_cid], [value_lid], value_obj, None)


def get_spv_output(spv_result,data):
    output = []
    new_clw = create_new_clw(data["clw"])
    for result in spv_result:
        virtual_clw = get_virtual_contours(result,new_clw)
        output.append(KeyValueFound(None,get_value_obj(virtual_clw, None),
                                    100,
        ))
    return output



    
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

def single_list_from_list_of_lists(line_ids):
    merged_list = []
    for i in line_ids:
        if isinstance(i,list):
            for j in i:
                merged_list.append(j)
        else:
            merged_list.append(i)
    return merged_list

def stitch_next_line(data,output):
        ''' Stitch next line if line_ids are consecutive based 
            on it's distance majorly for bank_names  '''
        font_size = list(set([calculate_font_size(i.value.contour["line"]) for i in output]))
        font_size = [sum(font_size)/len(font_size) if len(font_size)>1 else font_size[0]][0]
        top_left_y_diff = sorted([i.value.contour["line"][i.value.lids[0]]["bbox"]["top_left"]["y"] for i in output])
        new_c = create_new_clw(data)
        if (1.5*font_size > (top_left_y_diff[1]-top_left_y_diff[0])):
            lids = [i.value.lids[0] for i in output if i.value.contour["line"][i.value.lids[0]]["bbox"]["top_left"]["y"] in top_left_y_diff]
            lids = single_list_from_list_of_lists(lids)
            return get_virtual_contours_from_lids(top_left_y_diff,lids,new_c)
        return output


def get_virtual_contours_from_lids(bbox_cord:list,
    key_cand_results: List[namedtuple], new_clw: Dict[int, Dict]
):
    """
    Virtual contours with cid represented by -1 and results appended as lines
    with auto increment line_ids.
    KeyValue Found class can work on single cid. However as PRS Layout
    region can belong to multiple contours,fixing the issue using virtual contours.
    """
    output = []
    all_lid_result = []
    for cid, cvalues in new_clw.items():
        result = [
            lvalues
            for lid, lvalues in cvalues.items()
            if ((int(lid) in key_cand_results) and (int(lvalues["bbox"]["top_left"]["y"]) in bbox_cord)) 
        ]
        all_lid_result.extend(result)
    # virtual_clw = {"line": dict(enumerate(all_lid_result))}
    '''
    Create virtual contour with line_id as same as old_line_id'''
    res = {}
    for i in all_lid_result:
        res[i["line_id"]] = i
    virtual_clw = {"line":res}
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
    output.append(KeyValueFound(None,get_value_obj(virtual_clw, None),
                                    100,))
    return output

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
    for cid, cvalues in new_clw.items():
        result = [
            lvalues
            for lid, lvalues in cvalues.items()
            if int(lid) == int(key_cand_results.lid) and int(lvalues["page_num"]) == int(key_cand_results.page_id)
        ]
        all_lid_result.extend(result)
    # virtual_clw = {"line": dict(enumerate(all_lid_result))}
    '''
    Create virtual contour with line_id as same as old_line_id'''
    res = {}
    for i in all_lid_result:
        res[i["line_id"]] = i
    virtual_clw = {"line":res}
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
