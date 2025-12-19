from abc import ABC, abstractmethod
from typing import Dict


class CardStrategy(ABC):
    @abstractmethod
    def price_factor(self, amount: float) -> float:
        """Return multiplier for product price (1.0 = no discount)."""

    @abstractmethod
    def delivery_factor(self, shipping: float) -> float:
        """Return multiplier for delivery price (1.0 = no discount)."""


class StandardCard(CardStrategy):
    def price_factor(self, amount: float) -> float:
        return 1.0

    def delivery_factor(self, shipping: float) -> float:
        return 1.0


class SocialCard(CardStrategy):
    def price_factor(self, amount: float) -> float:
        return 0.90

    def delivery_factor(self, shipping: float) -> float:
        return 1.0


class GoldCard(CardStrategy):
    def price_factor(self, amount: float) -> float:
        return 0.90

    def delivery_factor(self, shipping: float) -> float:
        return 0.0


class CardService:
    """Factory and helpers for card strategies.

    This module is intentionally isolated from bouquet logic; it provides
    simple strategy objects to be composed by other modules later.
    """

    _map: Dict[str, CardStrategy] = {
        'standard': StandardCard(),
        'social': SocialCard(),
        'gold': GoldCard(),
    }

    @classmethod
    def get_strategy(cls, name: str) -> CardStrategy:
        try:
            print(name)
            strategy_name = (name or 'standard')
            if not isinstance(strategy_name, str):
                strategy_name = str(strategy_name)
            key = strategy_name.lower()
        except Exception:
            key = 'standard'
        return cls._map.get(key, StandardCard())

    @staticmethod
    def pricing_note() -> None:
        """Placeholder: pricing is applied in application layer.

        The module exposes strategy instances and multipliers. Calculation of
        final totals should happen in the caller using those multipliers.
        """
        return None
