import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

logger = logging.getLogger("Base_Reject_Handler")


# class CANDIDATE_REJECTION:
#     """
#     Abstract Class to Impelement Candidate Rejection Strategies.
#     """

#     @abstractmethod
#     def reject_candidates(
#         self,
#     ):
#         """
#         Method to reject the candidates based on defined
#         conditions for a keyword.
#         """


class HANDLER(ABC):
    """
    The Handler Interface
    """

    @abstractmethod
    def set_next(self, handler):
        """
        Method to assign the next strategy in the chain.
        """
        pass

    @abstractmethod
    def handle(self, request: List, dropped_result=None):
        """
        Method to run the rejection strategy.
        """
        pass


@dataclass
class REJECTHANDLER(ABC):
    """
    Abstract Class to Implement Candidate Rejection Strategy.
    Based on Chain of Responsibility Design Pattern.
    """

    _next_handler: HANDLER = None

    def set_next(self, handler: HANDLER):
        """
        Method to assign the next strategy in the chain.
        """
        self._next_handler = handler

        return handler

    @abstractmethod
    def handle(self, request: List, dropped_result=None):
        """
        Method to run the rejection strategy.
        If there is another strategy in the chain, pass on the request
        and dropped results or if this strategy is the only strategy or
        is the final strategy in the pipeline then return result and dropped result
        """
        if self._next_handler:
            return self._next_handler.handle(request, dropped_result)

        return request, dropped_result
