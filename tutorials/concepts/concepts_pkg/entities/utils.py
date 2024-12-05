from concepts_pkg.candidate_generator.utils.association import association
from concepts_pkg.candidate_generator.utils.utils_gen_search import (
    search_all_contours_ref,
    search_within_contours,
    verify_keyword,
)


def get_keywords(clw_hierarchy, keyword_settings, quick_search):
    indep_words = keyword_settings["keyword_search"]
    find_fuzzy = keyword_settings.get("find_fuzzy", True)
    discard_setting = keyword_settings.get("reject_list", {})
    length_based_discard = keyword_settings.get("length_based_discard", True)
    dep_words = keyword_settings.get("dependent_words", [])
    supporting_words = keyword_settings.get("supporting_words", [])
    lines_to_search = keyword_settings.get("lines_to_search", 2)
    preference = keyword_settings.get("preference", "independent")

    # Find independent words first
    ind_keywords_found = {}
    for search_word in indep_words:
        iw_found = search_all_contours_ref(
            clw_hierarchy, search_word, quick_search
        )
        found = []
        for found_obj in iw_found:
            # TODO: Verify keyword to accept found_obj
            line_text = found_obj.contour["line"][found_obj.lids[-1]]["text"]
            if not verify_keyword(line_text, discard_setting):
                found.append(found_obj)
        if found:
            ind_keywords_found[search_word] = found

    # Find dependent words suppported by other words
    dep_keywords_found = {}
    # TODO: Only in upper direction as of now
    for d_word in dep_words:
        # dw_found = search_all_contours_ref(clw_hierarchy, d_word, find_fuzzy,
        #                                length_based_discard)
        dw_found = search_all_contours_ref(clw_hierarchy, d_word, quick_search)
        found = []
        for found_obj in dw_found:
            sw_found_any = False
            cid, lid = found_obj.cid, found_obj.lids[-1]

            # Search Within Contours for supporting words
            if lid > 1:  # Dependent word is not the first line
                for s_word in supporting_words:
                    sw_found = search_within_contours(
                        clw_hierarchy,
                        [cid],
                        s_word,
                        find_fuzzy,
                        length_based_discard,
                    )
                    # Check if any supporting word is found within range
                    for sw_found_obj in sw_found:
                        if 0 < lid - sw_found_obj.lids[-1] <= lines_to_search:
                            sw_found_any = True
                            found.append(found_obj)
                            break
                    if sw_found_any:
                        break

            # Search In Association for supporting words
            if (lid <= lines_to_search) and not sw_found_any:
                lines_left = lines_to_search - lid + 1
                next_cid, next_lid = cid, lid
                while lines_left > 0 and not sw_found_any:
                    association_mapping = association(
                        next_cid, clw_hierarchy, next_lid
                    )
                    ass_ids = association_mapping.get("top", [])
                    for s_word in supporting_words:
                        sw_found = search_within_contours(
                            clw_hierarchy,
                            ass_ids,
                            s_word,
                            find_fuzzy,
                            length_based_discard,
                        )
                        for sw_found_obj in sw_found:
                            max_lid = max(sw_found_obj.contour["line"].keys())
                            if max_lid - sw_found_obj.lids[-1] <= lines_left:
                                sw_found_any = True
                                found.append(found_obj)
                                break
                        if sw_found_any:
                            break
                    if ass_ids:
                        next_cid, next_lid = ass_ids[0], 1
                        max_lid = max(clw_hierarchy[next_cid]["line"].keys())
                        lines_left -= max_lid
                    else:
                        break

        if found:
            dep_keywords_found[d_word] = found

    if preference == "dependent":
        return {**dep_keywords_found, **ind_keywords_found}
    else:
        return {**ind_keywords_found, **dep_keywords_found}


def find_text_regions(text_regions):
    """
    Extract single line and multiline results from prs results
    """
    single_line = {}
    multi_line = {}
    for region_id, region_vals in text_regions.items():
        # print(f' \n \n Region ID: {region_id}')
        all_hlines = []

        # for single line results
        if len(region_vals["values"]) == 1:

            # check for no of horizontal lines
            if len(region_vals["values"][0]) == 1:
                # single horizontal line
                # print(f'Result for {region_vals["values"]} is  \n Single line with single lids:{[region_vals["values"][0][0][1]]}')

                all_hlines = region_vals["values"][0][0][1]
                single_line[region_id] = [all_hlines]

            else:
                # multiple horizontal lines
                all_hlines = HorizontalLines(
                    region_vals["values"][0]
                ).stich_h_lines()
                # print(f'Result for {region_vals["values"]} is  \n Single line with multiple lids:{region_vals["values"][0]}')
                # print(all_hlines)
                single_line[region_id] = all_hlines

        else:
            # for multiple line results for eg: address
            multi_line_result = Multi_Line(region_vals["values"])
            multi_line[region_id] = multi_line_result
    return {"single": single_line, "multiple": multi_line}


class Multi_Line:
    """
    Schema to store multiline prs result information.
    """

    def __init__(self, result):
        self.result = result
        self.no_vlines = len(result)
        self.all_lines, self.all_lines_rep = self._unpacklids()
        self.h_line_cnt = [len(i) for i in self.all_lines_rep]

    def _unpacklids(
        self,
    ):
        all_lines = []
        all_lines_rep = []
        for vline in self.result:
            stiched_lines = HorizontalLines(vline).stich_h_lines()
            all_lines.extend(stiched_lines)
            all_lines_rep.append(stiched_lines)
        return all_lines, all_lines_rep


class HorizontalLines:
    """
    Schema to store Information on Horizontal Lines in prs result.
    """

    def __init__(self, hlines):
        self.hlines = hlines
        self.no_hlines = len(hlines)

    def stich_h_lines(
        self,
    ):
        lids = []
        # print(f'No of hlines: {len(self.hlines)}')
        for line in self.hlines:
            lids.append(line[1])
        # print(lids)
        return lids


class VerticalLines:
    """
    Schema to store Information on Vertical Lines in prs result.
    """

    def __init__(self, vlines):
        self.vlines = vlines
        self.no_vlines = len(vlines)

    def stich_vlines(
        self,
    ):
        """
        Stich all vertical lines (lids) of a single prs detected region
        """
        #         lids = []
        #         for line in self.vlines:
        #             lids.append(line)
        #         print(lids)
        # print(f'Number of vertical lines: {len(self.vlines)}')
        return self.vlines
