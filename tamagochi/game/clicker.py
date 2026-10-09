"""Кликер: логика получения монет."""
import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    """Интерфейс кликера."""

    @abstractmethod
    def __init__(self) -> None:
        """Инициализирует кликер."""

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """Количество монет, заработанных последним кликом."""

    @abstractmethod
    def click(self) -> None:
        """Выполняет клик и обновляет заработанное количество монет."""


class SimpleRandomClicker(AbstractClicker):
    """Кликер, где доход за клик случаен в заданном диапазоне."""

    def __init__(self, min_income: int = 10, max_income: int = 20) -> None:
        """Инициализирует кликер.

        Args:
            min_income: минимальный доход за клик.
            max_income: максимальный доход за клик.

        Raises:
            ValueError: если диапазон некорректен.
        """
        if min_income < 0 or max_income < min_income:
            raise ValueError('Некорректный диапазон дохода за клик')
        self._min_income = min_income
        self._max_income = max_income
        self._income_per_click = 0

    @property
    def income_per_click(self) -> int:
        """Количество монет, заработанных последним кликом."""
        return self._income_per_click

    def click(self) -> None:
        """Делает клик: доход выбирается случайно из диапазона."""
        self._income_per_click = random.randint(
            self._min_income, self._max_income
        )
