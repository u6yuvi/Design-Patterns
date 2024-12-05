import re
import pandas as pd
from concepts_pkg.candidate_generator.utils.utils_contourizing import iom_1d, iou_1d

from concepts_pkg.candidate_selector.k2v_ref import K2V_REF_CAND_SELECTOR as rej
from concepts_pkg.candidate_selector.rejector_factory import CAND_REJ_FACTORY
from concepts_pkg.candidate_selector.utils.data_prep import  list_to_keyfound_obj

regex_1 = re.compile("[a-zA-Z][a-zA-Z :#]+[a-zA-Z:# ]$")
regex_2 = re.compile("(([0-9]+.[A-Za-z]+.)|[A-Za-z]+.)|([0-9]+.*)")
pattern = "(?<!(\/|\d))((\d{1,3} ?)((of)|(\/))( ?\d{1,4})) ?(?!(\/|\d))"




def get_dict(invo):
    Final_output = []
    for invo in list(invo.values()):          # gets all keyvalue found object   #gets all keyvalue found object
        
        for i in range(len(invo)):            # iterates through string found object
            contours_ = invo[i] 
                                              # get the keyword contour and its respective feilds of values
            for key in contours_.keyword.contour["line"].keys():
                if key in invo[i].keyword.lids:
                    k_cid ,k_c2= contours_.keyword.contour["contour_id"],contours_.keyword.contour["line"][key]["line_id"]
                    k_tl_x,k_tl_y= contours_.keyword.contour["line"][key]["bbox"]["top_left"]["x"],contours_.keyword.contour["line"][key]["bbox"]["top_left"]["y"]
                    k_br_x,k_br_y= contours_.keyword.contour["line"][key]["bbox"]["bottom_right"]["x"],contours_.keyword.contour["line"][key]["bbox"]["bottom_right"]["y"]
                    k_text = contours_.keyword.contour["line"][key]["text"]
                    k_ana ,k_spv= list(
                        contours_.keyword.contour["line"][key]["meta"]["ana"]["clean_text_tags"]
                    ),list(
                        contours_.keyword.contour["line"][key]["meta"]["spv"]["clean_text_tags"]
                    )
                                              # get the value contour and its respective feilds of values
            for key in contours_.value.contour["line"].keys():# get the contour and its respective feilds of values
                if key in invo[i].value.lids:
                    dict_ = {}

                    dict_["key_cid"],dict_["key_lwhlid"],dict_["key_anchor_text"]=k_cid,k_c2,k_text
                    dict_["k_ana"],dict_["k_spv"] = k_ana,k_spv

                    dict_["cand_cid"],dict_["cand_lwhlid"],dict_["bboxx"] = contours_.value.contour["contour_id"],contours_.value.contour["line"][key]["line_id"],contours_.value.contour["line"][key]["bbox"]
                    dict_["k_top_x"],dict_["k_top_y"],dict_["k_bottom_x"], dict_["k_bottom_y"] = k_tl_x,k_tl_y,k_br_x,k_br_y
                                        
                    dict_["top_x"] = contours_.value.contour["line"][key]["bbox"]["top_left"][
                        "x"
                    ]
                    dict_["top_y"] = contours_.value.contour["line"][key]["bbox"]["top_left"][
                        "y"
                    ]
                    dict_["bottom_x"] = contours_.value.contour["line"][key]["bbox"][
                        "bottom_right"
                    ]["x"]
                    dict_["bottom_y"] = contours_.value.contour["line"][key]["bbox"][
                        "bottom_right"
                    ]["y"]
                    
                    dict_["candidate_text"],dict_["ana"],dict_["spv"],dict_["confidence"]=contours_.value.contour["line"][key]["text"],list(
                        contours_.value.contour["line"][key]["meta"]["ana"]["clean_text_tags"]
                    ),list(
                        contours_.value.contour["line"][key]["meta"]["spv"]["clean_text_tags"]
                    ),100


                    Final_output.append(dict_)
    return Final_output 










# def get_dict(invo):
#     # invo = output
#     invoicez = []
#     for key in invo.keys():
#         invoicez.append(
#             invo[key]
#         )  # gets all keyvalue found object   #gets all keyvalue found object

#     F = []
#     for i in invoicez:  # iterates through string found object
#         invo = i

#         for i in range(len(invo)):

#             filter_cid = invo[i].keyword.lids
#             contour = invo[
#                 i
#             ].keyword.contour  # get the contour and its respective feilds of values

#             c1 = contour["contour_id"]
#             for key in contour["line"].keys():
#                 if key in filter_cid:
#                     dict_ = {}
#                     k_cid ,k_c2= contour["contour_id"],contour["line"][key]["line_id"]
#                     k_tl_x,k_tl_y= contour["line"][key]["bbox"]["top_left"]["x"],contour["line"][key]["bbox"]["top_left"]["y"]
#                     k_br_x,k_br_y= contour["line"][key]["bbox"]["bottom_right"]["x"],contour["line"][key]["bbox"]["bottom_right"]["y"]
#                     k_text = contour["line"][key]["text"]
#                     k_ana ,k_spv= list(
#                         contour["line"][key]["meta"]["ana"]["clean_text_tags"]
#                     ),list(
#                         contour["line"][key]["meta"]["spv"]["clean_text_tags"]
#                     )
        

#             filter_lid = invo[i].value.lids
#             contour = invo[
#                 i
#             ].value.contour  # get the contour and its respective feilds of values
#             c1 = contour["contour_id"]
#             for key in contour["line"].keys():

#                 if key in filter_lid:
#                     dict_ = {}

#                     dict_["key_cid"],dict_["key_lwhlid"],dict_["key_anchor_text"]=k_cid,k_c2,k_text
#                     dict_["k_ana"],dict_["k_spv"] = k_ana,k_spv

#                     dict_["cand_cid"],dict_["cand_lwhlid"],dict_["bboxx"] = contour["contour_id"],contour["line"][key]["line_id"],contour["line"][key]["bbox"]
#                     dict_["k_top_x"],dict_["k_top_y"],dict_["k_bottom_x"], dict_["k_bottom_y"] = k_tl_x,k_tl_y,k_br_x,k_br_y
                                        
#                     dict_["top_x"] = contour["line"][key]["bbox"]["top_left"][
#                         "x"
#                     ]
#                     dict_["top_y"] = contour["line"][key]["bbox"]["top_left"][
#                         "y"
#                     ]
#                     dict_["bottom_x"] = contour["line"][key]["bbox"][
#                         "bottom_right"
#                     ]["x"]
#                     dict_["bottom_y"] = contour["line"][key]["bbox"][
#                         "bottom_right"
#                     ]["y"]
                    
#                     dict_["candidate_text"],dict_["ana"],dict_["spv"],dict_["confidence"]=contour["line"][key]["text"],list(
#                         contour["line"][key]["meta"]["ana"]["clean_text_tags"]
#                     ),list(
#                         contour["line"][key]["meta"]["spv"]["clean_text_tags"]
#                     ),100


#                     F.append(dict_)
#     return F


def get_centroid(cords):
    centroid = ((cords[0] + cords[2]) / 2, (cords[1] + cords[3]) / 2)
    c_x = centroid[0]
    c_y = centroid[1]
    return c_x, c_y


def falls_on_same_line(data):
    result = []
    for i in range(len(data)):
        row = data[i]    
        match = regex_1.match(row["candidate_text"])
        if not match:
            if (row["key_lwhlid"] == row["cand_lwhlid"]) and (len(row["key_anchor_text"].split()) <= 7):
                result.append(row)

    res = []
    [res.append(x) for x in result if x not in res]
    return res


def strategy_on_obtained_can(data):
    result = []
    for i in range(len(data)):
        regex_fil = {}
        row = data[i]
        match = regex_1.match(row["candidate_text"])
        if not match:
            if ((len(row["candidate_text"].split()) <= 6 and len(row["key_anchor_text"].split()) <= 6) and row["bottom_y"] < 1754):
                iou = iou_1d(
                    [row["k_top_y"], row["k_bottom_y"]],
                    [row["top_y"], row["bottom_y"]],
                )
                io = iou_1d(
                    [row["k_top_x"], row["k_bottom_x"]],
                    [row["top_x"], row["bottom_x"]],
                )
                k_cent_x, k_cent_y = get_centroid(
                    (
                        row["k_top_x"],
                        row["k_top_y"],
                        row["k_bottom_x"],
                        row["k_bottom_y"],
                    )
                )
                v_cent_x, v_cent_y = get_centroid(
                    (
                        row["top_x"],
                        row["top_y"],
                        row["bottom_x"],
                        row["bottom_y"],
                    )
                )
                if ((int(v_cent_y) - int(k_cent_y)) >= -20 and (int(v_cent_x) - int(k_cent_x)) >= -20) and not (io <= 0.2 and iou <= 0.2):

                    c_ana = len(row["ana"])
                    c_spv = len(row["spv"])

                    if "LOC" in row["spv"]:
                        ratio=row["spv"].count("LOC")/c_spv
                    else:
                        ratio = 0.0

                    if "Anchor" in row["ana"]:
                        ratio_ = row["ana"].count("Anchor")/ c_ana
                    else:
                        ratio_ = 0.0

                    if (ratio_ <= 0.5 and ratio <= 0.5) and (v_cent_y - k_cent_y <=150):    
                        text = re.sub(
                            "\s+", " ", row["candidate_text"]
                        )
                        match_val = re.search(
                            pattern, row["candidate_text"]
                        )
                        if match_val is None:
                            result.append(row)

    res = []
    [res.append(x) for x in result if x not in res]
    return res


def invo_num(datas):
    data=get_dict(datas)
    result_ = falls_on_same_line(data)
    if len(result_) == 1:
        return result_  # when line_id of contour and line are same
    else:
        results = strategy_on_obtained_can(data) # on given candidates for key filters are applied
        return results


def strategy_on_getting_key_n_can(datas, clwh):
    """ when first strategy fails to get any result, getting canidates that falls along same line from clw for 
    respective key anchors given """
    data = get_dict(datas)

    final_dict = []
    datas = []
    [datas.append(x) for x in data if x not in datas]
    key_text = []
    for i in datas:
        k_tex = i["key_anchor_text"]
        if k_tex not in key_text:
            key_text.append(k_tex)

            if len(i["key_anchor_text"].split()) <= 5:
                k1 = i["k_top_y"]
                k2 = i["k_bottom_y"]

                for k in clwh:
                    for key in clwh[k]["line"].keys():
                        if (regex_2.match(clwh[k]["line"][key]["text"]) is not None) and (regex_1.match(clwh[k]["line"][key]["text"]) is None):
                            ioy = iom_1d((k1, k2), (clwh[k]["line"][key]["bbox"]["top_left"]["y"], clwh[k]["line"][key]["bbox"]["bottom_right"]["y"]))
                            
                            if ioy >= 0.9 and "DATE" not in clwh[k]["line"][key]["meta"]["spv"]["clean_text_tags"] :
                                i["cand_cid"] = clwh[k]["contour_id"]
                                i["cand_lwhlid"] = clwh[k]["line"][key]["line_id"]
                                i["top_x"] = clwh[k]["line"][key]["bbox"]["top_left"]["x"]
                                i["top_y"] = clwh[k]["line"][key]["bbox"]["top_left"]["y"]
                                i["bottom_x"] = clwh[k]["line"][key]["bbox"]["bottom_right"]["x"]
                                i["bottom_y"] = clwh[k]["line"][key]["bbox"]["bottom_right"]["y"]
                                i["candidate_text"] = clwh[k]["line"][key]["text"]
                                i["ana"] = clwh[k]["line"][key]["meta"]["ana"]["clean_text_tags"]
                                i["spv"] = clwh[k]["line"][key]["meta"]["spv"]["clean_text_tags"]
                                final_dict.append(i)

    final_dict2 = []
    [final_dict2.append(x) for x in final_dict if x not in final_dict2]
    finalz = strategy_on_obtained_can(final_dict2)
    return finalz


def get_can(self,combine_results,clw):
    final_dict=invo_num(combine_results)
    if len(final_dict) == 0:
        final_dict = strategy_on_getting_key_n_can(combine_results, clw)
    request = rej.candidate_rejector(self, final_dict)
    request = list_to_keyfound_obj(self.data["clw"], request)
    if len(request) != 0:
        if len(request) > 1:
            return [request[0]]
        return request
    return []

if __name__ == "__main__":
    print("please do check invoice num strategy")
