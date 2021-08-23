from concepts.domain import lwclw


#Takes in lw,clw interface and instantiate the class to be used by usecase
class MemRepo:
    '''
    wrapper around a real database or any other storage
    type.'''
    def __init__(self, data):
        self.data = data
    def list(self):
        return lwclw.LWCLWDATA(self.data[0],self.data[1])