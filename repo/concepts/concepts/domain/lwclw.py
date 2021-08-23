from abc import abstractmethod

class LWCLWInterface:

    def getallkeyword():
        pass
    
    @abstractmethod
    def getlw():
        pass

    @abstractmethod
    def getclw():
        pass

    @abstractmethod
    def getalllines():
        pass

    @abstractmethod
    def getallcontours():
        pass

class LWCLWDATA(LWCLWInterface):
    def __init__(self,lw,clw) -> None:
        self.lw = lw
        self.clw = clw

    def getlw(self,):
        return self.lw
    
    def getclw(self):
        return self.clw

    def getallines(self,):
        alllines = []
        for _,value in self.lw.items():
            alllines.append(value)
        print(f'Returning all lines in lw hierarchy..')
        return alllines

    def getallcontours(self,):
        allcontours = []
        for _,value in self.clw.items():
            allcontours.append(value)
        print(f'Returning all contours in clw hierarchy..')
        return allcontours



if __name__ == "__main__":

    lw = {'1':['l1','l2','l3'],'2':['l4','l5','l6']}
    clw = {'1':['c1','c2','c3'],'2':['c4','c5','c6']}
    print(LWCLWDATA(lw,clw).getallines())