import abc
from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sparse_dot_topn import awesome_cossim_topn


class RefBase(abc.ABC):
    """
    Base Class from the Quick Search Classes
    """

    def __init__(self, data, ngm=[3], nbest=5):
        self.ngm = ngm
        self.data = data
        if nbest > len(data):
            raise Exception(
                "Nbest should be less than or equal to the length of the data"
            )
        self.nbest = nbest
        self.vectorizer = TfidfVectorizer(min_df=1, analyzer=self.ngrams)
        self.bow_vectorizer = CountVectorizer(
            analyzer="char", ngram_range=(1, 1), lowercase=True, min_df=1
        )
        # self.sc = StandardScaler()
        self.tf_idf = self.vectorizer.fit_transform(data)
        self.bow = self.bow_vectorizer.fit_transform(data).astype(np.double)

    def ngrams(self, string):
        """
        Create n grams from a string.
        """
        n_ret = []
        for j in self.ngm:
            ngs = zip(*[string[i:] for i in range(j)])
            n_ret += ["".join(ng) for ng in ngs]
        return n_ret

    @abc.abstractmethod
    def find_best_match(self, query_str, thresh):
        """
        Abstract method for finding the best match on a query string.
        """
        pass

    @abc.abstractmethod
    def find_best_match_arr(self, query_arr, thresh):
        """
        Abstract method for finding the best match on a query List[string] .
        """
        pass


class RefCosSim(RefBase):
    """
    Class for Cos Similarity based Ref match
    """

    def __init__(self, data, ngm=[3], nbest=5):
        super().__init__(data, ngm=ngm, nbest=nbest)

    def find_best_match(self, query_str: str, thresh=0.0):
        """
        Returns the nbest results closest to query_str with their similarity
         measures if the match is above thresh.
        """
        # try:
        queryTFIDF = self.vectorizer.transform([query_str])
        matches = awesome_cossim_topn(
            queryTFIDF, self.tf_idf.transpose(), self.nbest, thresh
        )
        # except:
        # return None
        ret = [
            (self.data[val], matches.data[i], val)
            for i, val in enumerate(matches.indices)
            if matches.data[i] > thresh
        ]
        if len(ret) == 0:
            return []
        return ret

    def find_best_match_arr(self, query_arr: List[str], thresh=0.0):
        """
        Returns the nbest results closest to each of the queries in query_arr
         with their similarity measures.
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
                    j,
                    self.data[matches.indices[i]],
                    matches.indices[i],
                    matches.data[i],
                )
                for i in range(matches.indptr[j], matches.indptr[j + 1])
            ]
        return ret
