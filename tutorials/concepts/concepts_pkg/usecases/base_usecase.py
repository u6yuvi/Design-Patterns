from abc import ABC, abstractmethod


class Extraction(ABC):
    @abstractmethod
    def execute(
        self,
    ):
        """
        Method to exectue to End to End Extraction Pipeline.
        """
