from dateutil.parser import parse
import calendar

from concepts_pkg.utils.string_match import StringFound, StringMatch
from concepts_pkg.utils.keyvaluefound import KeyValueFound

import logging
logger = logging.getLogger()


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.
    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def extract_dates(self,generated_candidates):
    logger.info(f"Invoice date selector started")
    result_dict = []
    result_values = []
    if self.keyword == "invoice_date": 
        ser_list = ["invoice date","invoice/tax date","tax date"]
    elif self.keyword == "delivery_date":
        ser_list = ["job date","execution date","date of delivery"]
    elif self.keyword == "due_date":
        ser_list = ["due date","payment","due"]
    # print(len(generated_candidates))
    # print("Entry point gen candidates:", generated_candidates)
    clw_hierarchy = self.data['clw']
    if len(generated_candidates)>1:
        for key_p,val_p in generated_candidates[0].items():
            for val in val_p:
                # print(val)
                for k_spv,v_spv in generated_candidates[1].items():
                    for val_s in v_spv:
                        # print(val_s)
                        try:
                            if val.keyword.match.match_string in ser_list and is_date(val.value.match.match_string):
                                val1 = clw_hierarchy[val_s.value.cid]['line'][val_s.value.lids[0]]['text']
                                key1 = clw_hierarchy[val.keyword.cid]['line'][val.keyword.lids[0]]['text']
                                cid = val_s.value.cid
                                lid = val_s.value.lids[0]
                                if is_date(val1) is True:
                                    result_dict.append({"text":val1,
                                                    "contour_id":cid,
                                                    "line_id":[lid],
                                                    "start":0,
                                                    "end":len(key1)})
                                    break
                            elif val_s.value.cid==val.value.cid and val_s.value.lids[0]==val.value.lids[0]:                            
                                val1 = clw_hierarchy[val_s.value.cid]['line'][val_s.value.lids[0]]['text']
                                key1 = clw_hierarchy[val.keyword.cid]['line'][val.keyword.lids[0]]['text']
                                cid = val_s.value.cid
                                lid = val_s.value.lids[0]
                                if is_date(val1) is True:
                                    result_dict.append({"text":val1,
                                                    "contour_id":cid,
                                                    "line_id":[lid],
                                                    "start":0,
                                                    "end":len(key1)})
                                    break
                                else:
                                    logger.info(f"Need to generate results from spv")
                        except:
                            logger.info(f"Bad Month Error")
    else:
        try:
            for spv_K,spv_V in generated_candidates[0].items():
                for val_spv in spv_V:
                    # print(val_spv)
                    val1 = clw_hierarchy[val_spv.value.cid]['line'][val_spv.value.lids[0]]['text']
                    key1 = "Invoice date"
                    cid = val_spv.value.cid
                    lid = val_spv.value.lids[0]
                    if is_date(val1) is True:
                        result_dict.append({"text":val1,
                                        "contour_id":cid,
                                        "line_id":[lid],
                                        "start":0,
                                        "end":len(key1)})
                    break

        except:
            logger.info(f"Exception Bad Month Error")                
    if result_dict :
        for val in result_dict:
            temp_match_obj = StringMatch(val["end"],100,val["start"],val["text"])
            temp_value_obj = StringFound(clw_hierarchy[val["contour_id"]],val["line_id"],temp_match_obj)
            result_values.append(KeyValueFound(None,temp_value_obj,100))
            logger.debug(f'''{self.keyword} value is {val["text"]}''')
            return result_values        
    return []



