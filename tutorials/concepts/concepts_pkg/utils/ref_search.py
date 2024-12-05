"""
Use this code to search the reference dataset fast
Converts Ref dataset into N-gram and create TFIDF records for each data in ref list. This generally reduces the size of vocab for large datasets
The TFIDF matrix is the representation of all the records in a different (kind of linear) space 
The query is also converted into a vector using same kind of transformations.
Closest match is the one which is either nearest neighbour or has smaller cosine distance
"""
import abc
import logging
from collections import defaultdict
from typing import List

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sparse_dot_topn import awesome_cossim_topn

logger = logging.getLogger("Quick Search")


class QuickSearch:
    def __init__(self, clwh, ref_data=None, ngm=None, n_best=1):
        self.ngm = [2, 3] if not ngm else ngm
        self.n_best = n_best
        self.text_map = self.get_text_map(clwh)
        self.ref_obj = self.line_ref_obj(clwh, ref_data)

    def line_ref_obj(self, clwh, ref_data):
        """
        Helper function to take lw hierarchy as input and return reference object formed from these texts
        :param lwh: lw hierarchy
        :return: reference object
        """
        line_texts = (
            [
                line_elem["text"].lower()
                for cid, contour_elem in clwh.items()
                for lid, line_elem in contour_elem["line"].items()
            ]
            if not ref_data
            else ref_data
        )
        return RefCosSim(line_texts, ngm=self.ngm, nbest=self.n_best)

    def get_text_map(self, clwh):
        """
        Helper function to create hash map of line text (used to get text location in the document)
        :param clwh: clw_hierarchy
        :return:
        {
            "line_text" : ["cid_lid", "cid_lid"]
        }
        """
        text_map = defaultdict(list)
        for cid, contour_elem in clwh.items():
            for lid, line_elem in contour_elem["line"].items():
                text_map[line_elem["text"].lower()].append(f"{cid}_{lid}")
        return text_map


class RefBase(abc.ABC):
    """
    Base Class from the Quick Search Classes
    """

    def __init__(self, data, ngm=None, nbest=5):
        if ngm is None:
            ngm = [3]
        self.ngm = ngm
        self.data = data
        if nbest > len(data):
            nbest = len(data)
            logger.debug(f"Nbest has been changed and became {len(data)}")
            # raise Exception("Nbest should be less than or equal to the length of the data")
        self.nbest = nbest
        self.vectorizer = TfidfVectorizer(min_df=1, analyzer=self.ngrams)
        self.tf_idf = self.vectorizer.fit_transform(data)

    def ngrams(self, string):
        n_ret = []
        for j in self.ngm:
            ngs = zip(*[string[i:] for i in range(j)])
            n_ret += ["".join(ng) for ng in ngs]
        return n_ret

    @abc.abstractmethod
    def find_best_match(self, query_str, thresh):
        pass

    @abc.abstractmethod
    def find_best_match_arr(self, query_arr, thresh):
        pass


class RefCosSim(RefBase):
    """
    Class for Cos Similarity based Ref match
    """

    def __init__(self, data, ngm=None, nbest=5):
        super().__init__(data, ngm=ngm, nbest=nbest)
        if ngm is None:
            ngm = [3]

    def find_best_match(self, query_str: str, thresh=0.0):
        """
        Returns the nbest results closest to query_str with their similarity measures if the match is above thresh
        """
        try:
            queryTFIDF = self.vectorizer.transform([query_str])
            matches = awesome_cossim_topn(
                queryTFIDF, self.tf_idf.transpose(), self.nbest, thresh
            )
        except:
            return None
        ret = [
            (self.data[val], matches.data[i])
            for i, val in enumerate(matches.indices)
            if matches.data[i] > thresh
        ]
        if len(ret) == 0:
            return None
        return ret

    def find_best_match_arr(self, query_arr: List[str], thresh=0.0):
        """
        Returns the nbest results closest to each of the queries in query_arr with their similarity measures
        """
        try:
            queryTFIDF = self.vectorizer.transform(query_arr)
            matches = awesome_cossim_topn(
                queryTFIDF, self.tf_idf.transpose(), self.nbest, thresh
            )
        except:
            return None
        ret = {}
        for j, qu in enumerate(query_arr):
            ret[qu] = [
                (
                    self.data[matches.indices[i]],
                    matches.indices[i],
                    matches.data[i],
                )
                for i in range(matches.indptr[j], matches.indptr[j + 1])
            ]
        return ret
