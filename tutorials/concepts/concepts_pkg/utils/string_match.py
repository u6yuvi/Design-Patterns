import re
from collections import namedtuple
import concepts_pkg
from pathlib import Path
import editdistance
import Levenshtein
from Bio import pairwise2

import logging

import json
import os

__PACKAGE_ROOT = Path(concepts_pkg.__file__).resolve().parent
__DOC_CONFIG_DIR = __PACKAGE_ROOT / "utils/"

logger = logging.getLogger()

tess_error_path = Path(__DOC_CONFIG_DIR)
with open(tess_error_path/"tesseract_error.json", "r") as f:
    tess_error = json.load(f)


def replace_letter(letter):
    alias_letters = tess_error[letter] + [letter]
    regex = '('
    for i, alias in enumerate(alias_letters):
        regex += alias
        if i+1 != len(alias_letters):
            regex += '|'
    return regex + '){1}'


def gen_regex(text):
    regex = text
    replaced = ''
    for letter in text:
        if letter in tess_error and letter not in replaced:
            replacement = replace_letter(letter)
            regex = regex.replace(letter, replacement)
            replaced += letter
    return '\\b' + regex + '\\b'


def clean_text(text):
    """
    This function converts text to lowercase, removes punctuations and returns list by splitting text on spaces
    :param text: string
    :return: list
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text


def findwholeword_aliasing(keyword, search_text):
    keyword, search_text = clean_text(keyword), clean_text(search_text)
    regex = re.compile(gen_regex(keyword))
    return regex.search(search_text)

# def clean_text(text):
#     """
#     This function converts text to lowercase, removes punctuations and returns
#     list by splitting text on spaces
#     TODO: Add reverse search to get matched string before clean
#     :param text: string
#     :return: list
#     """
#     # text = re.sub(r'[\.]', '', text)
#     text = re.sub(r"[^a-zA-Z0-9#\s]", " ", text)
#     return " ".join(text.split())


class StringMatch:
    """
    String match class to compare similarity between two strings
    TODO: Handle multiple match in a single query string
    TODO: Replace the argument name : start- > start_index , end -> end_index,text -> match_text\
         once the changes are incorportated in K2K. Issue -1 
    """

    similar = namedtuple("similar", ["is_match", "confidence"])

    def __init__(self, end, similarity, start=None, text=""):
        """
        :param match_end: match end index.
        :param similarity: (int) percentage similarity between two strings.
        :param start_index: index from which matching starts
        """
        self.start = start
        self.end = end
        self.match_string = text
        # self.search_string = keyword
        self.similarity = similarity

    @classmethod
    def string_match(
        cls, keyword, query_string, lowercase_comp=True, text_threshold=80
    ):
        """
        This function takes two strings as input and returns True if keyword is present in query string
        :param keyword: string to be searched in the text
        :param query_string: string where keyword is searched
        :param text_threshold: int
        :return: confidence and match end index
        Example:
        keyword: "Wonderland"
        query_string: "Alice is in wonderland"
        final_conf = 100, match_end = 22

        keyword: "Wonderland"
        query_string: "Alice is in wonderlnd"
        final_conf = 95, match_end = 21

        keyword: "Alice is in wonderland"
        query_string: "Are you Alice who is from wonderland"
        final_conf = 0, match_end = 0
        Corresponding words after first word in keyword in query string should match, else its penalised

        keyword: "Alice is in wonderland"
        query_string: "Are you Alie is in wonderlad"
        final_conf = 96, match_end = 21
        """
        if lowercase_comp:
            keyword, query_string = keyword.lower(), query_string.lower()
        keyword_words, query_words = keyword.split(), query_string.split()

        try:
            first_word = keyword_words[0]
        except IndexError:
            raise Exception("Empty string!")

        confidence, last_word = list(), None
        for i, word in enumerate(query_words):
            match_obj = StringMatch._is_similar(first_word, word)
            if not match_obj.is_match:
                continue
            confidence.append(match_obj.confidence)
            for key_w, query_w in zip(keyword_words[1:], query_words[i + 1 :]):
                match_obj = StringMatch._is_similar(key_w, query_w)
                confidence.append(match_obj.confidence)
                last_word = query_w
            final_conf = sum(confidence) / len(keyword_words)
            if final_conf > text_threshold:
                (
                    match_start,
                    match_end,
                    match_text,
                ) = StringMatch._get_match_meta(
                    query_string, first_word=word, last_word=last_word
                )
                return cls(match_end, final_conf, match_start, match_text)
            else:
                return None
        return None

    @staticmethod
    def _is_similar(text_1, text_2, word_threshold=70):
        """
        This function takes two strings as input and returns True
        (along with confidence) if they have fuzz ratio greater
        than the specified threshold, else it returns False along with confidence
        :param text_1: string
        :param text_2: string
        :param word_threshold: int
        :return:
        """
        # confidence = StringMatch._levenshtein_distance(text_1, text_2)
        confidence = (
            1 - (Levenshtein.distance(text_1, text_2) / len(text_1))
        ) * 100
        if confidence > word_threshold:
            return StringMatch.similar(True, confidence)
        return StringMatch.similar(False, confidence)

    @staticmethod
    def _levenshtein_distance(text_1, text_2):
        """
        Helper function to find string similarity using levenshtein distance
        :param text_1: string (text1 length is used for calculating confidence)
        :param text_2: string
        :return: percentage string match
        """
        edit_distance = editdistance.eval(text_1, text_2)
        confidence = (len(text_1) - edit_distance) * 100 / len(text_1)
        return confidence

    @staticmethod
    def _get_match_meta(text_string, first_word, last_word):
        """
        Helper function to get match start, match end and the string that is matched
        :param text_string: query string
        :param first_word: first word to be matched
        :param last_word: last word that is matched
        :return: match_start, match_end, match_string
        """
        match_start = text_string.find(first_word)
        if last_word is None:  # written for readability
            match_end = match_start + len(
                first_word
            )  # if only one word is present, then last word is none
        else:
            match_end = text_string.find(last_word) + len(last_word)
        match_string = text_string[match_start:match_end]
        return match_start, match_end, match_string
    @classmethod
    def string_match(cls, keyword, query_string, lowercase_comp=True, text_threshold=80):
        """
        This function takes two strings as input and returns True if keyword is present in query string
        :param keyword: string to be searched in the text
        :param query_string: string where keyword is searched
        :param text_threshold: int
        :return: confidence and match end index
        Example:
        keyword: "Wonderland"
        query_string: "Alice is in wonderland"
        final_conf = 100, match_end = 22

        keyword: "Wonderland"
        query_string: "Alice is in wonderlnd"
        final_conf = 95, match_end = 21

        keyword: "Alice is in wonderland"
        query_string: "Are you Alice who is from wonderland"
        final_conf = 0, match_end = 0
        Corresponding words after first word in keyword in query string should match, else its penalised

        keyword: "Alice is in wonderland"
        query_string: "Are you Alie is in wonderlad"
        final_conf = 96, match_end = 21
        """
        if lowercase_comp:
            keyword, query_string = keyword.lower(), query_string.lower()
        keyword_words, query_words = keyword.split(), query_string.split()

        try:
            first_word = keyword_words[0]
        except IndexError:
            raise Exception("Empty string!")

        confidence, last_word = list(), None
        for i, word in enumerate(query_words):
            match_obj = StringMatch._is_similar(first_word, word)
            if not match_obj.is_match: continue
            confidence.append(match_obj.confidence)
            for key_w, query_w in zip(keyword_words[1:], query_words[i + 1:]):
                match_obj = StringMatch._is_similar(key_w, query_w)
                confidence.append(match_obj.confidence)
                last_word = query_w
            final_conf = sum(confidence) / len(keyword_words)
            if final_conf > text_threshold:
                match_start, match_end, match_text = StringMatch._get_match_meta(
                    query_string, first_word=word, last_word=last_word)
                return cls(match_end, final_conf, match_start, match_text)
            else:
                return None
        return None

    @classmethod
    def string_match_local(cls, query, target, lowercase_comp=True, miss_thresh=2, text_threshold=80):
        '''
        Function to match two strings. Uses local alignment to match the strings.
        It is more robust than string_match and works for smaller strings.

        query: word to the searched
        target: text in which query has to be found
        lowercase_comp: bool to indicate if the comparison should happen in lower case
        miss_thresh: threshold number of character mismatches allowed. Use negative number to ignore it
        thresh_per: percentage match threshold above which results are sent. Use zero to ignore it

        return: StringMatch class object with start, end, confidence, and matched text (None if below the thresholds)
        '''
        if len(query) == 0 or len(target) == 0:
            return None
            # raise Exception("Empty Inputs to Sting Match")

        target_raw = target
        if lowercase_comp:
            query, target = query.lower(), target.lower()

        align = pairwise2.align.localms(query, target, 1, -1, -1, 0)

        if miss_thresh < 0:
            miss_thresh = len(query)

        if len(align) > 0:
            match_score = 100.0 * align[0].score / len(query)
            missmatch_char = len(query) - align[0].score

            if missmatch_char <= miss_thresh:
                if match_score >= text_threshold:
                    start = align[0].start
                    end = align[0].end
                    return cls(end, match_score, start, target_raw[start: end])

        return None

    @classmethod
    def findwholeword(cls, search_w, query_str):
        """
        Find the whole word in another string.
        :param search_w: string to be searched
        :param text_b: string in which string is to be searched
        :return: match object
        """
        # text_a = text_a.replace(".","")
        query_str = " %s " % query_str
        match = re.compile(r'\W{d}\W'.format(d=re.escape(search_w)),
                           flags=re.IGNORECASE).search(query_str)
        if match:
            match_str = query_str[match.start() + 1:match.end() - 1]
            return cls(end=match.end() - 1, similarity=100,
                       start=match.start(), text=match_str)
        return None

    @staticmethod
    def _match_logger(text_1, text_2, conf):
        """
        Add logging for match
        :param text_1: str
        :param text_2: str
        :param conf: confidence
        :return: None
        """
        logger.debug(f"Match found between '{text_1}' and '{text_2}' with confidence {conf}")

    @classmethod
    def lenient_match(cls, keyword, query_string, lowercase_comp=True):
        """
        Check similarity between two strings, if similarity is not 100%, check if the keywords are same using aliasing
        :param keyword: str
        :param query_string: str
        :return: match: True if there is a match else False
        match_end: index where match ends
        conf: Confidence of the match
        """
        match = False
        if lowercase_comp:
            keyword, query_string = keyword.lower(), query_string.lower()
        match_obj = StringMatch.string_match(keyword, query_string)
        if match_obj.similarity:
            if match_obj.similarity != 100:
                aliasing = findwholeword_aliasing(keyword, query_string)
                logger.debug(f"Checking aliasing for '{keyword}' and '{query_string}'")
                if aliasing:
                    match = True
                    StringMatch._match_logger(keyword, query_string, match_obj.similarity)
            else:
                match = True
                StringMatch._match_logger(keyword, query_string, match_obj.similarity)
        return match, match_obj

    @classmethod
    def complete_match(cls, keyword, query_string):
        '''
        Check for complete match between two strings
        :param keyword: str
        :param query_string: str
        :return: match: True if there is 100% match else False
        match_end: index where match ends
        conf: Confidence 100 for perfect match
        '''
        match_found = StringMatch.findwholeword(keyword, query_string)
        if match_found:
            StringMatch._match_logger(keyword, query_string, 100)
            return match_found
        return None

class StringFound:
    """
    String found class to store required information (location and string) of
    the text found within a contour
    """

    def __init__(self, contour, lids, string_match_obj, meta=None):
        """
        :param contour: complete countour of the text found
        :param lids: line ids within a contour which contains the text
                     (multiline string)
        :param match: (StringMatch) match object of the text found
        :meta: Store meta deta associated with results to be used by
                downstream strategies.
        """
        self.contour = contour
        self.lids = lids
        self.match = string_match_obj
        self.meta = meta

    @property
    def cid(self):
        return self.contour["contour_id"]

    def __str__(self):
        return (
            f"Match found ({self.match.match_string}, cid:{self.cid}, "
            f"lids:{self.lids}, similarity:{self.match.similarity})"
        )
