from abc import ABC, abstractmethod
from typing import Any


class BuilderInterface(ABC):
    @abstractmethod
    def reset(self) -> 'BuilderInterface':
        pass

    @abstractmethod
    def set_name(self, name: str) -> 'BuilderInterface':
        pass

    @abstractmethod
    def set_flower(self, flower_id: int) -> 'BuilderInterface':
        pass

    @abstractmethod
    def set_wrapping(self, wrapping_id: int) -> 'BuilderInterface':
        pass

    @abstractmethod
    def set_type(self, type_id: int) -> 'BuilderInterface':
        pass

    @abstractmethod
    def set_flowers_count(self, count: int) -> 'BuilderInterface':
        pass

    @abstractmethod
    def build(self) -> Any:
        pass
