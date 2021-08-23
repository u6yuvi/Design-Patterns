from typing import Callable, List, Dict
from concepts.response_objects import response_objects as res
from concepts.domain import keyword as K
from concepts.domain.lwclw import LWCLWDATA, LWCLWInterface
from concepts.repository.memrepo import MemRepo

# class RoomListUseCase:
#     def __init__(self, repo):
#         self.repo = repo
#     def execute(self,request):
#         rooms = self.repo.list()
#         return res.ResponseSuccess(rooms)


# class RoomListUseCase(object):
#     def __init__(self, repo):
#         self.repo = repo
#     def execute(self, request_object):
#         if not request_object:
#             return res.ResponseFailure.build_from_invalid_request_object(
#             request_object)
#         try:
#             rooms = self.repo.list(filters=request_object.filters)
#             return res.ResponseSuccess(rooms)
#         except Exception as exc:
#             return res.ResponseFailure.build_system_error(
#             "{}: {}".format(exc.__class__.__name__, "{}".format(exc)))


#strategy1
def stgy1_extractcandidate(keyword: str , memrepo: MemRepo):
    print(f'Extracting Candidate for keyword {keyword} ')
    return memrepo.list().getallines()





class GETKEYWORDTHANVALUE:
    def __init__(self,memrepo, keyword_name: str, keyword_handler_obj) -> None:
        self.memrepo = memrepo
        self.keyword_name = keyword_name
        self.keyword_handler_obj = keyword_handler_obj


    def getkeyword(self,):
        #key_handler_obj = self.KeywordHandler(self.keyword_fn())
        matched_keys = self.keyword_handler_obj.return_keyword(self.keyword_name)

        return matched_keys

    # def getallkeywords(self,):
        
    #     return self.KeywordInterface.getallkeyword()
    
    def getcandidates(self, extractcandidate_fn):

        self.found_keywords = self.getkeyword()

        if "No key" in self.found_keywords:
            print(f'No candidates found')
            return ['No result']

        found_candidates = extractcandidate_fn(self.found_keywords, self.memrepo)
        
        print(f'Candidates found: {found_candidates}')
        
        return found_candidates



