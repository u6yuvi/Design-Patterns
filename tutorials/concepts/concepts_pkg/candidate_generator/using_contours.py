import os 
import sys 
import logging
from abc import ABC,abstractmethod
from unittest import result
from .using_keyaliases import CAND_GEN
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Dict
from concepts_pkg.utils.string_match import StringFound,StringMatch
from concepts_pkg.utils.keyvaluefound import KeyValueFound
from concepts_pkg.utils.ref_search import QuickSearch
import re

logger = logging.getLogger("Using Contours")

@dataclass
class CAND_GEN_CONT(CAND_GEN):
    
 
    keyword: str
    # keywords_found : Dict[str, StringMatch]
    keyword_config: BaseModel
    data: Dict
    # config_settings : field(init = False)

    def __post_init__(
        self,
    ):
        # self.config_settings = self.doc_config['fields_to_extract'][self.keyword]
        self.config_settings = self.keyword_config.field_config.dict()
        # self.value_func = self.config_settings.get("value_function", None)
        self.directions = self.config_settings.get(
            "useful_directions", ["top", "right", "bottom", "left"]
        )
        self.diagonal_contours = self.config_settings.get(
            "diagonal_flag", False
        )

    def _quick_search(self, n_best=5):
        """
        Instantiate the Quick Search with clw hierarchy
        """

        return QuickSearch(self.data["clw"], n_best=n_best)


    def generate_candidates(
        self, keywords_found: Dict[str, StringMatch]
    ) -> Dict:
        """
        Extract the candidates using the contours
        """
        self.cand_generated_values = {}
        extractions = []
        prev_text = None
        if keywords_found:
            keyword_contours = []
            lwh = self.data["lw"]
            for _, values in keywords_found.items():
                for value in values:
                    keyword_contours.append(value.contour)

            texts = []
            for keyword_contour in keyword_contours:
                m_ty = keyword_contour["bbox"]["top_left"]["y"] - 10
                m_by = keyword_contour["bbox"]["bottom_right"]["y"] + 10
                m_x = keyword_contour["bbox"]["top_left"]["x"] - 10

                # extract all lines present towards the right side of contour bbox
                if prev_text != keyword_contour["text"]: # handling duplicates in keyword_contours
                    for _, line_info in lwh.items():
                        ty = line_info["bbox"]["top_left"]["y"]
                        by = line_info["bbox"]["bottom_right"]["y"]
                        x = line_info["bbox"]["top_left"]["x"]
                        if x >= m_x:
                            if ty >= m_ty and by <= m_by:
                                # print(line_info["text"])
                                for cid,contour_info in self.data["clw"].items():
                                    for lid,ctr_line in contour_info["line"].items():
                                        if ctr_line["line_id"] == line_info["line_id"]:
                                            contour = contour_info
                                            line_id = lid
                                            texts.append((line_info["text"],line_id,contour)) 
                                            break
                                    
                        
                    prev_text = keyword_contour["text"]

            # get correct extraction
            multi_words = ['per contract','per agreement','due on receipt','net on receipt','at sight','cash on delivery','net receipt of',
            'net upon receipt','due upon receipt']
            # extractions = []
            found = False
            for words in multi_words:
                for text,l_id,line_contr in texts:
                    text_lower = text.lower()
                    if words in text_lower:
                        temp_match_obj = StringMatch(len(text),100,0,text)
                        temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                        extractions.append(KeyValueFound(None,temp_value_obj,100))
                        found = True
                        break
                if found:
                    break

            if not extractions:
                regexList = [r'[n][e][t]\s*[0-9]+', r'[0-9]+\s*bank\s*', r'[0-9]+\s*working\s*',r'[0-9]+\s*[d][a][y][s]*',
                r'[c]\.?[ao0]\.?[d]\.?$', r'[0-9]+\s*calendar\s*']
                for text,l_id,line_contr in texts:
                    text_lower = text.lower()
                    for regex in regexList:
                        s = re.search(regex,text_lower)
                        if s:
                            temp_match_obj = StringMatch(len(text),100,0,text)
                            temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                            extractions.append(KeyValueFound(None,temp_value_obj,100))
                            found = True
                            break

                    if found:
                        break
            if not extractions:

                words = ["ct","immediate"]
                # extractions = []
                found = False
                for word in words:
                    for text,l_id,line_contr in texts:
                        text_split = text.lower().split()
                        if word in text_split:
                            temp_match_obj = StringMatch(len(text),100,0,text)
                            temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                            extractions.append(KeyValueFound(None,temp_value_obj,100))
                            found = True
                            break
                    if found:
                        break

            # words = ["net", "day", "days", "cod", "cad","c.o.d.", "contract" , "agreement","calendar", "day(s)",
            # "latest", "please", "telegraph", "cfr" , "sight", "c.o.d" , "t/t", "cash","receipt", "immediately"]
            # # extractions = []
            # found = False
            # for word in words:
            #     for text,l_id,line_contr in texts:
            #         text_split = text.lower().split()
            #         if word in text_split:
            #             temp_match_obj = StringMatch(len(text),100,0,text)
            #             temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
            #             extractions.append(KeyValueFound(None,temp_value_obj,100))
            #             found = True
            #             break
            #     if found:
            #         break
            # if no correct extraction present towards the right side
            # expand contour bbox downwards
            if not extractions:
                prev_text = None
                texts = []
                for keyword_contour in keyword_contours:
                    m_ty = keyword_contour["bbox"]["top_left"]["y"] - 10
                    m_by = keyword_contour["bbox"]["bottom_right"]["y"] + 150
                    m_x = keyword_contour["bbox"]["top_left"]["x"] - 100

                    if prev_text != keyword_contour["text"]:
                        for _, line_info in lwh.items():
                            ty = line_info["bbox"]["top_left"]["y"]
                            by = line_info["bbox"]["bottom_right"]["y"]
                            x = line_info["bbox"]["top_left"]["x"]
                            if x >= m_x:
                                if ty >= m_ty and by <= m_by:
                                    # print(line_info["text"])
                                    for cid,contour_info in self.data["clw"].items():
                                        for lid,ctr_line in contour_info["line"].items():
                                            if ctr_line["line_id"] == line_info["line_id"]:
                                                contour = contour_info
                                                line_id = lid
                                                texts.append((line_info["text"],line_id,contour))
                                                break
                                        
                        prev_text = keyword_contour["text"]
                # found = False
                multi_words = ['per contract','per agreement','due on receipt','net on receipt','at sight','net upon receipt', 'net receipt of',
                'cash on delivery','due upon receipt']
                # extractions = []
                found = False
                for words in multi_words:
                    for text,l_id,line_contr in texts:
                        text_lower = text.lower()
                        if words in text_lower:
                            temp_match_obj = StringMatch(len(text),100,0,text)
                            temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                            extractions.append(KeyValueFound(None,temp_value_obj,100))
                            found = True
                            break
                    if found:
                        break

                if not extractions:
                    regexList = [r'[n][e][t]\s*[0-9]+', r'[0-9]+\s*bank\s*', r'[0-9]+\s*working\s*',r'[0-9]+\s*[d][a][y][s]*',
                    r'[c]\.?[ao0]\.?[d]\.?$', r'[0-9]+\s*calendar\s*']
                    for text,l_id,line_contr in texts:
                        text_lower = text.lower()
                        for regex in regexList:
                            s = re.search(regex,text_lower)
                            if s:
                                temp_match_obj = StringMatch(len(text),100,0,text)
                                temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                                extractions.append(KeyValueFound(None,temp_value_obj,100))
                                found = True
                                break

                        if found:
                            break
                if not extractions:

                    words = ["ct","immediate"]
                    # extractions = []
                    found = False
                    for word in words:
                        for text,l_id,line_contr in texts:
                            text_split = text.lower().split()
                            if word in text_split:
                                temp_match_obj = StringMatch(len(text),100,0,text)
                                temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                                extractions.append(KeyValueFound(None,temp_value_obj,100))
                                found = True
                                break
                        if found:
                            break


                # for word in words:
                #     for text,l_id,line_contr in texts:
                #         text_split = text.lower().split()
                #         if word in text_split:
                #             temp_match_obj = StringMatch(len(text),100,0,text)
                #             temp_value_obj = StringFound(line_contr,[l_id],temp_match_obj)
                #             extractions.append(KeyValueFound(None,temp_value_obj,100))
                #             found = True
                #             break
                #     if found:
                #         break
        self.cand_generated_values["no_keyword"] = extractions
        return self._format_result(self.cand_generated_values)
        
    def _format_result(self, result):
        """
        Wrap result in dictionary using classname as a key
        """
        result_dict = {}
        result_dict[self.__class__.__name__] = result
        return result_dict
