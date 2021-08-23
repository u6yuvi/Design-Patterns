from dataclasses import dataclass


@dataclass(init=True, repr=True)
class test_dataclass:
    x : int
    y: int 

    def returnxy(self,):
        print(f'{self.x,self.y}')

if __name__ == "__main__":
    print(test_dataclass(20,30))