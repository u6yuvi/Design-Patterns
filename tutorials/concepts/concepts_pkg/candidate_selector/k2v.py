import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from k2v_pkg.final_output import run_k2v_ml

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .rejector_factory import CAND_REJ_FACTORY
from .utils.data_prep import k2v_doc_meta, list_to_keyfound_obj

logger = logging.getLogger("K2V")

def get_conf_labels(labels, settings):
    confidence = 0
    for label in labels:
        if label in settings:
            confidence += settings[label]
    return confidence


class CAND_SELECTOR(ABC):
    @abstractmethod
    def select_candidates(
        self,
    ):
        """
        Abstract Method for calling candidate selection strategy
        """

def get_value_using_spv(keyword,clw_hierarchy):
    '''
    if labels as unit then can confirm existing cardinal is quantity.based on labels buildup confidence then
    To extract correct commodity based on max length of value
    '''
    # settings = config_settings.get('use_handler', None)
    ref_using_spv= True
    ref_using_spv_label= True
    ref_using_spv_conf= True
    lst_result = []
    length_dict = {}
    tag_conf = []
    temp_labels = {"vessel": "VESSEL", "commodity": "COMMODITY"}
    config_settings = {"confidence":
                        {"labels":{temp_labels.get(keyword, None): 10}}}
    if ref_using_spv and ref_using_spv_label:
        if "labels" in config_settings['confidence']:
            for cid, contour_info in clw_hierarchy.items():
                for lid, line_val in contour_info['line'].items():
                    labels = line_val['meta']['spv']['clean_text_tags']
                    confidence = get_conf_labels(
                        labels, config_settings['confidence']["labels"])
                    if confidence > 0:
                        temp_string_obj = StringMatch(end=len(
                            line_val["text"]), text=line_val["text"], similarity=100)
                        temp_val_obj = StringFound(
                            clw_hierarchy[cid], [lid], temp_string_obj)
                        lst_result.append(KeyValueFound(
                            None, temp_val_obj, 100))
                        tag_conf.append(confidence)
            if ref_using_spv_conf is False:
                return lst_result
        if ref_using_spv_conf :                 
            if lst_result:
                tag_conf_sorted = [i for i in reversed(sorted(enumerate(tag_conf), key=lambda x:x[1]))]
                length = 0
                index = 0
                for i in range(len(tag_conf_sorted)-1):
                    if tag_conf_sorted[i][0] == 0:
                        index = tag_conf_sorted[i][0]
                        for j in range(len(tag_conf_sorted)-1):
                            if tag_conf_sorted[i][1] == tag_conf_sorted[j][1]:
                                if length < len(lst_result[i].value.match.match_string):
                                    length = len(
                                        lst_result[i].value.match.match_string)
                                    index = tag_conf_sorted[i][0]
                                if length < len(lst_result[j].value.match.match_string):
                                    length = len(
                                        lst_result[j].value.match.match_string)
                                    index = tag_conf_sorted[j][0]
                            else:
                                break
                length_dict[tag_conf_sorted[index][0]
                    ] = lst_result[tag_conf_sorted[index][0]]
                return [length_dict[tag_conf_sorted[index][0]]]
            else:
                return []
    else:
        return []


@dataclass
class K2V_CAND_SELECTOR(CAND_SELECTOR):

    keyword: str
    # generated_candidates : Dict
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:
        """
        Method to run candidate selection strategy
        """

        combine_results = []
        if len(generated_candidates) > 1:
            combine_results = {}
            for cand in generated_candidates:
                for key, matched_results in cand.items():
                    # TODO - Find unique and append
                    combine_results[key] = matched_results

        elif len(generated_candidates) == 1:
            combine_results = generated_candidates[0]

        if combine_results:
            doc_meta, doc_type = k2v_doc_meta(self.data, self.doc_type)

            sample_test = {
                "results": combine_results,
                "clw_hierarchy": self.data["clw"],
                "doc_meta": doc_meta,
            }
            pred_df = run_k2v_ml(sample_test, doc_type, self.keyword)

            final_df = pred_df[pred_df["pred"] == 1]
            final_df["confidence"] = 100
            final_dict = final_df.to_dict(orient="record")
            request = self.candidate_rejector(final_dict)
            request = list_to_keyfound_obj(self.data["clw"], request)
            if len(request) != 0:
                if len(request) > 1:
                    return [request[0]]
                return request
            
            else:
                if self.keyword in ["commodity", "vessel","transport_name","commodity_name"]:
                    try:
                        request = get_value_using_spv(self.keyword, self.data["clw"])
                    except:
                        request = []
                    if len(request) != 0:
                        if len(request) > 1:
                            return [request[0]]
                        return request
                    return []
            return []
        else:
            if self.keyword in ["commodity", "vessel","transport_name","commodity_name"]:
                try:
                    request = get_value_using_spv(self.keyword, self.data["clw"])
                except:
                    request = []
                if len(request) != 0:
                    if len(request) > 1:
                        return [request[0]]
                    return request
            return []
        return []

    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict

    def candidate_rejector(self, result):
        """
        Rejection strategy to remove false positive.
        """
        if len(self.keyword_config.field_config.cand_rejector_stgy.keys()) > 0:
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


@dataclass
class CAND_SELECTOR_HANDLER:
    """
    Interface to Candidate Selection Step using K2V Model.
    """

    cand_selector_obj: CAND_SELECTOR
    cand_selector_config: Dict

    def __post_init__(
        self,
    ):
        self.cand_gen_stgys = self.cand_selector_config["cand_generator_stgy"]
        self.cand_selector_handler_config = self.cand_selector_config.get(
            "pass_stgy", None
        )

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ) -> List[Dict]:

        """
        Run Candidate Selection Strategy.
        """
        cand_gen_results = []
        # result = []
        # if len(generated_candidates) > 0:
        #     cand_gen_results,stgy_info = self._collect_results(generated_candidates)
        #     result = self.cand_selector_obj.select_candidates(cand_gen_results)
        #     return {self.cand_selector_obj.__class__.__name__: result}
        # return {self.cand_selector_obj.__class__.__name__: {}}

        if len(generated_candidates) > 0:
            cand_gen_results, stgy_info = self._collect_results(
                generated_candidates
            )
            if self.cand_selector_handler_config:
                result = self.cand_selector_obj.select_candidates(
                    cand_gen_results, stgy_info
                )
            else:
                result = self.cand_selector_obj.select_candidates(
                    cand_gen_results
                )
            return {self.cand_selector_obj.__class__.__name__: result}
        return {self.cand_selector_obj.__class__.__name__: {}}

    def _collect_results(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ):
        """
        Iterate over different Candidate Generation Strategies and
        collect their respective results in a list.
        """
        cand_gen_results = []
        stgy_info = []
        for cand_gen_stgy in self.cand_gen_stgys:
            logger.info(
                f"Searching {cand_gen_stgy} stgy results in CAND_GEN results."
            )
            for res in generated_candidates["CAND_GENERATOR_HANDLER"]:
                # logger.info(f"res{res}")
                if cand_gen_stgy in res.keys() and len(res) > 0:
                    # check if strategy gave any result and not {}
                    for res_key, res_value in res.items():
                        if len(res_value) > 0:
                            logger.info(
                                f"CAND_GEN_STGY mapping and results found.Apending the results now.."
                            )
                            cand_gen_results.append(res[cand_gen_stgy])
                            stgy_info.append(cand_gen_stgy)
                else:
                    logger.info(
                        f"No correct CAND_GEN_STGY mapping found or result is None"
                    )
        logger.info(
            f"{len(cand_gen_results)} CAND_GEN results going in CAND_GEN_SELECTION"
        )
        return cand_gen_results, stgy_info
