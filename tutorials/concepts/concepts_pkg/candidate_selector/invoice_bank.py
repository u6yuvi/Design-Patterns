import logging
from collections import namedtuple
from dataclasses import dataclass
# from tkinter import font
from typing import Dict, List
from concepts_pkg.utils.keyvaluefound import KeyValueFound
# from concepts_pkg.utils.string_match import StringFound,StringMatch

from .k2v import CAND_SELECTOR
from .rejector_factory import CAND_REJ_FACTORY
from .utils.invoice_bank_utils import filter_bankresults, get_spv_output,stitch_next_line

logger = logging.getLogger("Invoice Bank CAND Selector")

key_cand_meta = namedtuple("Keycand_meta", ["page_id", "lid", "wid"])


@dataclass
class INV_BANK_CAND_SELECTOR(CAND_SELECTOR):
    """
    Candidate Selection Strategy based on K2V Model and SPV Tags.
    """

    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str        

    def unique_output(self,output):
        if output is not None:
            unq_lid = []
            all_lid = [i.value.lids for i in output]
            try:
                max_len = max(all_lid,key=len)
                sort_lst = []
                if len(max_len)>1:
                    sort_lst.append(max_len)
                    for i in all_lid:
                        if len(i)>1:
                            for j in i:
                                if j not in max_len and i not in sort_lst:
                                    sort_lst.append(i)
                        else:
                            if i[0] not in max_len and i not in sort_lst:
                                sort_lst.append(i)
                    for i in output:
                        if i.value.lids in sort_lst:
                            unq_lid.append(i)
                    return unq_lid
                if output:
                    return output
            except:
                logger.info(f'No Candidate with lids more than 1')
                return output
        return output
        

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]], stgy_info
    ):
        """
        Selection of the candidate based on the following strategy:
        Case-1 If candidate generation result has prs_result, and spv_model results,
        filter prs_result using spv model
        If Case-1 fails,then
        Case-2 If candidate generation result has contour based results and spv_model results,
        filter contour based results using spv_model
        If Case-2 fails, then
        Case-3 If candidate generation result has prs_result, return all prs results.
        If Case-3 fails, then
        Case -4  Return all bak_spv results.
        If Case-4 fails, then
        Case-5 If candidate generation has only contour based results,filter the results
               using some heurisitic (candidate on the right with minimum distance in y)
        """
        # stgy_info = self.keyword_config.field_config.cand_selector_stgy["INV_BANK"]["cand_generator_stgy"]
        combine_results = []
        output = []
        data = self.data["clw"]
        stitch_line = self.keyword_config.field_config.cand_selector_stgy["INV_BANK"].get(
            "stitch_line", None)
        logger.info(f'Cand Results{generated_candidates}')
        logger.info(f"Cand Stgy info {stgy_info}")

        assert len(generated_candidates) == len(stgy_info)
        # collect CAND_GEN_RESULTS with the Stgy Name
        stgy_result = {}
        for stgy_name, cand in zip(stgy_info, generated_candidates):
            combine_results = {}
            for key, matched_results in cand.items():
                # TODO - Find unique and append
                combine_results[key] = matched_results
            stgy_result[stgy_name] = combine_results
        
        # Run Candidate Rejection Stgy
        logger.info(f'Stgy result {stgy_result}')
        for stgy_name, results in stgy_result.items():
            filtered_result = {}
            for keyalias, key_res in results.items():
                logger.info(f'Stgy Name: {stgy_name} Key: {keyalias} \n No of results: {len(key_res)}')
                rejector_output = self.candidate_rejector(key_res)
                if rejector_output:
                    filtered_result[keyalias] = rejector_output
            stgy_result[stgy_name] = filtered_result

        logger.info(f'Stgy result {stgy_result}')
        # collect spv_results from bank_ner model
        spv_tag = self.keyword_config.field_config.cand_selector_stgy["INV_BANK"].get(
            "spv_tag", None)
        spv_result = self.data["bank_results"].get(spv_tag, None)
        # logger.info(f'Collected spv result: {spv_result}')
        all_spv_result = []
        if spv_result:
            for res in spv_result:
                result = []
                result = [key_cand_meta(i[0], i[1], i[2]) for i in res]
                all_spv_result.extend(result)
        logger.info(f"spv_results: {all_spv_result}")

        # Case-1 Filter PRS_CAND Result using SPV Model Result
        logger.info(f"CAND_GEN_PRS + Bank SPV Strategy started..")
        if all_spv_result and stgy_result.get("CAND_GEN_PRS", False):
            for key, res_lst in stgy_result["CAND_GEN_PRS"].items():
                for res in res_lst:
                    # logger.info(f"Result: {res.value}")
                    for i in all_spv_result:
                        if int(i.page_id) == int(res.value.contour["line"][res.value.lids[-1]]["page_num"]):
                            if len(res.value.lids)==1 and i.lid == res.value.lids[0]:
                                output.append(res)
                            if len(res.value.lids)>1 and i.lid in res.value.lids:
                                for k in get_spv_output([i],self.data):
                                    output.append(k)
                  
            if output:
                if len(output)>1: 
                    logger.info(f"Results found in CAND_GEN_PRS + Bank SPV Strategy: {output}")
                    unq_output =  self.unique_output(output)
                    if len(unq_output)>1 and stitch_line:
                        return stitch_next_line(data,unq_output)
                    return unq_output
                logger.info(f"Results found in CAND_GEN_PRS + Bank SPV Strategy: {output}")
                return output
            

        # Case-2 Filter using_keyalaises result using SPV Model Result
        logger.info(f"CAND_GEN_USING_KEYALIASES + Bank SPV Strategy started..")
        if all_spv_result and stgy_result.get(
            "CAND_GEN_USING_KEYALIASES", False
        ):
            for key, res_lst in stgy_result[
                "CAND_GEN_USING_KEYALIASES"
            ].items():
                for res in res_lst:
                    res_lids = [k["line_id"] for i,k in res.value.contour["line"].items()]
                    for i in all_spv_result:
                        if int(i.page_id) == int(res.value.contour["line"][res.value.lids[-1]]["page_num"]):
                            if len(res.value.lids)==1 and i.lid == res_lids[0]:
                                output.append(res)
                            if len(res.value.lids)>1 and i.lid in res_lids:
                                for k in get_spv_output([i],self.data):
                                    output.append(k)        
            if output:
                if len(output)>1:
                    if len(self.unique_output(output))>1 and stitch_line:
                        return stitch_next_line(data,self.unique_output(output))
                    return self.unique_output(output)
                return output

        # Case -3 return all result from PRS Result
        logger.info(f"CAND_GEN_PRS Strategy started..")
        if stgy_result.get("CAND_GEN_PRS", None) is not None:
            for key, res_lst in stgy_result["CAND_GEN_PRS"].items():
                output.extend(res_lst)
            if output:
                if len(output)>1: 
                    if len(self.unique_output(output))>1 and stitch_line:
                        return stitch_next_line(data,self.unique_output(output))
                    return self.unique_output(output)
                return output
        
        # Case -4 return all spv result
        logger.info(f"Bank SPV Strategy started..")
        if all_spv_result:
            if len(get_spv_output(all_spv_result, self.data))>1:
                if len(self.unique_output(get_spv_output(all_spv_result, self.data)))>1 and stitch_line:
                    output = self.unique_output(get_spv_output(all_spv_result, self.data))
                    return stitch_next_line(data,output)
                return self.unique_output(get_spv_output(all_spv_result, self.data))
            return get_spv_output(all_spv_result, self.data)

        # Case-5 - Filter CAND_GEN_USING_KEYALIASES RESULT
        logger.info(f"CAND_GEN_USING_KEYALIASES Strategy started..")
        if stgy_result.get("CAND_GEN_USING_KEYALIASES", None) is not None:
            new_op = filter_bankresults(stgy_result["CAND_GEN_USING_KEYALIASES"], self.data)
            if new_op:
                if len(new_op)>1:
                    if len(self.unique_output(new_op))>1 and stitch_line:
                        return stitch_next_line(data,self.unique_output(new_op))
                    return self.unique_output(new_op)
                return new_op
        if len(output)>1:
            if len(self.unique_output(output))>1 and stitch_line:
                return stitch_next_line(data,self.unique_output(output))
            return self.unique_output(output)
        return output


    def candidate_rejector(self, result):
        """
        Rejection strategy to remove false positive.
        """
        #logger.info(f'Rejection started')
        if len(self.keyword_config.field_config.cand_rejector_stgy.keys()) > 0:
            #logger.info('rejection kicked in')
            for (
                cand_rej_stgy,
                cand_rej_config,
            ) in self.keyword_config.field_config.cand_rejector_stgy.items():
                if cand_rej_stgy in CAND_REJ_FACTORY.keys():
                    cand_ana_rej_obj = CAND_REJ_FACTORY[cand_rej_stgy](
                        cand_rejection_config=cand_rej_config,
                        clw_hierarchy=self.data["clw"],
                        keyword=self.keyword,
                    )
                    request, dropped_result = cand_ana_rej_obj.handle(
                        result, None
                    )
                    result = request
            return result
        return result
