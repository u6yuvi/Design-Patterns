# class Room:
#     def __init__(self, code, size, price, longitude, latitude):
#         self.code = code
#         self.size = size
#         self.price = price
#         self.latitude = latitude
#         self.longitude = longitude

#     @classmethod
#     def from_dict(cls, adict):
#         return cls(
#         code=adict['code'],
#         size=adict['size'],
#         price=adict['price'],
#         latitude=adict['latitude'],
#         longitude=adict['longitude'],
#         )

#     def to_dict(self,):
#         return {
#         'code': self.code,
#         'size': self.size,
#         'price': self.price,
#         'latitude': self.latitude,
#         'longitude': self.longitude,
#         }

#     def __eq__(self, other):
#         if isinstance(other,Room):
#             return self.to_dict() == other.to_dict()

#         return False


from abc import abstractmethod, ABC

# from typing import Dict


class KeywordInterface:
    def getallkeyword():
        pass

    @abstractmethod
    def getmatchedkeyword():
        pass


class KeywordHeuristic(KeywordInterface):
    def __init__(self) -> None:
        super().__init__()

    def findkeyword(self,):
        return {"load": [1, 2, 3]}

    def getmatchedkeyword(self, key: str):
        print(f"Heuristic Result..")
        return self.findkeyword()[key]


class KeywordK2K(KeywordInterface):
    def __init__(self, k2kresults) -> None:

        self.k2kresults = k2kresults

    def getmatchedkeyword(self, key: str):
        print(f"Using K2K Result..")
        if key in self.k2kresults.keys():
            return self.k2kresults[key]
        return ["No key"]


class KeywordHandler:
    def __init__(self, keywordk2k_result) -> None:
        self.keywordk2k_result = keywordk2k_result

    def return_keyword(self, key):
        return self.keywordk2k_result.getmatchedkeyword(key)


if __name__ == "__main__":

    # ithk2k
    # k2kresults = {'loadk2k':[1,2]}
    # keyword_obj = KeywordK2K(k2kresults)
    # key_handler_obj = KeywordHandler(keyword_obj)
    # print(key_handler_obj.return_keyword('loadk2k'))

    # withoutk2k
    keyword_obj = KeywordHeuristic()
    key_handler_obj = KeywordHandler(keyword_obj)
    print(key_handler_obj.return_keyword("load"))
