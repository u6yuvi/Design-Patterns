#!/usr/bin/env python
import uuid
from concepts.repository import memrepo as mr
from concepts.use_cases import room_list_use_case as uc
from concepts.request_objects import room_list_request_object as req

from concepts.domain import keyword as k
from concepts.use_cases.room_list_use_case import stgy1_extractcandidate

# repo = mr.MemRepo([])
# use_case = uc.RoomListUseCase(repo)
# result = use_case.execute()
# print(result)

# code = uuid.uuid4()


# incoming data
lw = {"1": ["l1", "l2", "l3"], "2": ["l4", "l5", "l6"]}
clw = {"1": ["c1", "c2", "c3"], "2": ["c4", "c5", "c6"]}

# Incoming keyword name from configuration
keyword_name = "load"


# Step-1 Input Interface
data = mr.MemRepo([lw, clw])

# Step-2 select the keyword_extraction_logic_function from the pool \
# of keyword_extraction_logic_functions.
# Let's say we pick Heurisitc approach..
keyword_fn_obj = k.KeywordHeuristic()

# 2nd alternative to keyword_extraction_logic_function
# keyword_fn_obj = k.KeywordK2K({'loadk2k':[1,2]})

# Step-3 Instantiate the KeyHandler-Interface with keyword_extraction_logic
keyword_handler_ob = k.KeywordHandler(keyword_fn_obj)

# Step-4 Instantiate the usecase with data,keyword_name, Keywordhandler_obj
keywordthanvalue_obj = uc.GETKEYWORDTHANVALUE(
    data, keyword_name, keyword_handler_ob)

# execute the usecase with one of the strategy from the available strategy_list
keywordthanvalue_obj.getcandidates(stgy1_extractcandidate)


# keyword = k.KeywordK2K(repo.list()).getmatchedkeyword('load')


# room = k.Room(code, size=200, price=10,
# longitude=-0.09998975,
# latitude=51.75436293)
# room_list_use_case = uc.RoomListUseCase(room)
# request = req.RoomListRequestObject()
# #print(request)
# response = room_list_use_case.execute(request)
