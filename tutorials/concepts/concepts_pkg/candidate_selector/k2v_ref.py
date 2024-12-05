import logging
from dataclasses import dataclass
from typing import Dict, List

from k2v_pkg.final_output import run_k2v_ml

from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.string_match import StringFound, StringMatch

from .k2v import CAND_SELECTOR
from .rejector_factory import CAND_REJ_FACTORY
from .utils.data_prep import k2v_doc_meta, list_to_keyfound_obj

logger = logging.getLogger("K2V-REF")


@dataclass
class K2V_REF_CAND_SELECTOR(CAND_SELECTOR):
    """
    Candidate Selection Strategy based on K2V Model and SPV Tags.
    """

    keyword: str
    keyword_config: Dict
    data: Dict
    doc_type: str

    def select_candidates(
        self, generated_candidates: Dict[str, List[KeyValueFound]]
    ):
        """
        Selection of the candidate based on the following strategy:
        Case-1 If candidate generation result has spv_result,return spv_result
        Case-2 If candidate generation result has no spv_result,
        run K2V model result.
        """
        # if spv result found ,return the result
        combine_results = []
        for cand in generated_candidates:
            filtered_cand = []
            for key, matched_results in cand.items():
                if key in ["spv"]:
                    logger.info(f"spv strategy found in CAND_GEN_results..")
                    # if len(cand["spv"]) > 1:
                    for res in matched_results:
                        logger.info(f"Running Candidate rejector")
                        filtered_request = self.candidate_rejector([res])
                        if filtered_request:
                            filtered_cand.append(res) 
                    if filtered_cand:
                        return filtered_cand[0:1]



                    #     return [cand["spv"][0]]
                    return [cand["spv"][0]]

        # if result came from multiple cand_gen strategies,combine into one
        
        if len(generated_candidates) > 1:
            combine_results = {}
            for cand in generated_candidates:
                for key, matched_results in cand.items():
                    # TODO - Find unique and append
                    combine_results[key] = matched_results

        elif len(generated_candidates) == 1:
            combine_results = generated_candidates[0]

        # to handle scenario--- [{}]
        if combine_results:
            # run k2v
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
            # print("request",request)
            if len(request) != 0:
                if len(request) > 1:
                    return [request[0]]
                return request
            return []
        return []

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
