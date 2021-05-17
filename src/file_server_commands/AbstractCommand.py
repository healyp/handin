from abc import ABC, abstractmethod
from handin_messaging import Request

class AbstractCommand(ABC):
    @abstractmethod
    def handleRequest(self, request: Request):
        pass
