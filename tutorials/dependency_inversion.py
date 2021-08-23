'''
Usecase of creating Abstract Interfaces to Volatile Concrete Implentations'''

from abc import ABC, abstractmethod
from typing import KeysView

class Keyword(ABC):

    @abstractmethod
    def find_keywords():
        pass


class KeywordK2K(Keyword):
    def __init__(self,k2kresults) -> None:
        
        self.k2kresults = k2kresults

    def find_keywords(self,):
        for key,value in self.k2kresults.items():
            if key =='load_por':
                return self.k2kresults[key]
            print(f'Current key..{key}')
            continue

class KeywordHeuristic(Keyword):
    def __init__(self,k2kresults) -> None:
        
        self.k2kresults = k2kresults

    def find_keywords(self,):
        for key,value in self.k2kresults.items():
            if key =='dischargeport':
                print(f'Result found with scanned key: {key}')
                return self.k2kresults[key]
            print(f'No resulf found with scanned key: {key}')
            continue



class KeywordHandler:
    def __init__(self,keywordk2k_result) -> None:
        self.keywordk2k_result = keywordk2k_result

    def return_keyword(self,):
        return self.keywordk2k_result.find_keywords()



if __name__ == "__main__":
    keyresult = {'load_port':[1,2,3,4],'dischargeport':[1,2],'consignee':[1]}

    kk2k = KeywordK2K(keyresult)
    kk2kheu = KeywordHeuristic(keyresult)
    
    res = KeywordHandler(kk2kheu)
    print(res.return_keyword())