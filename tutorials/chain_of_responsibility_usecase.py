from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request, result) -> Optional[str]:
        pass


class AbstractHandler(Handler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # monkey.set_next(squirrel).set_next(dog)
        return handler

    @abstractmethod
    def handle(self, request: Any, result =  None) -> str:
        if self._next_handler:
            return self._next_handler.handle(request,result)

        return result

class KeyRemoval(AbstractHandler):
    def handle(self, request: Any, result) -> str:
        if result is None:
            result = dict()
            print(f'Creating new dict')
        for key, items in request.items():
            if key == 'key1':
                result['key1'] = f'Keyword found at key {key}'
        
        return super().handle(request,result)
                


class ValRemoval(AbstractHandler):
    def handle(self, request: Any, result) -> str:
        if result is None:
            result = dict()
        for key, items in request.items():
            for i in items:
                if i==4:
                    result[key] = f'Item found for Key {key}'
        
        return super().handle(request,result)




def call_fnc(request):
    result = keyh.handle(request,None)
    print(result)



if __name__ == "__main__":
    res_dict = {'key1':[1,2,3],'key2':[4,5,6],'key3':[7,8,9]}

    keyh = KeyRemoval()
    valh = ValRemoval()

    keyh.set_next(valh)

    call_fnc(res_dict)


