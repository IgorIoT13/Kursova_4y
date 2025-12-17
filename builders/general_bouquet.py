from builders.builder_interface import BuilderInterface
from typing import Dict


class GeneralBouquet(BuilderInterface):
    def __init__(self):
        self.reset()

    def reset(self):
        self._data = {
            'name': None,
            'flower_id': None,
            'wrapping_id': None,
            'type_id': None,
            'flowers_count': 0,
        }
        return self

    def set_name(self, name: str):
        self._data['name'] = name
        return self

    def set_flower(self, flower_id: int):
        self._data['flower_id'] = flower_id
        return self

    def set_wrapping(self, wrapping_id: int):
        self._data['wrapping_id'] = wrapping_id
        return self

    def set_type(self, type_id: int):
        self._data['type_id'] = type_id
        return self

    def set_flowers_count(self, count: int):
        self._data['flowers_count'] = count
        return self

    def build(self) -> Dict:
        # Optionally add validation here
        return dict(self._data)
