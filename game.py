"""Логика игры: связывает питомца, кликер, еду и лекарства."""
from abc import ABC, abstractmethod
from dataclasses import replace

from game.clicker import AbstractClicker
from game.exceptions import (
    GameOverError,
    InvalidChoiceError,
    NoFoodError,
    NoMedicineError,
    NotEnoughCoinsError,
)
from game.models import Food, Medicine
from game.tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Интерфейс сущности игры."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует игру."""

    @property
    @abstractmethod
    def tamagochi(self) -> AbstractTamagochi:
        """Питомец, участвующий в игре."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Еда в сумке игрока."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Лекарства в сумке игрока."""

    @property
    @abstractmethod
    def shop_food(self) -> list[Food]:
        """Еда, доступная для покупки."""

    @property
    @abstractmethod
    def shop_medicine(self) -> list[Medicine]:
        """Лекарства, доступные для покупки."""

    @abstractmethod
    def work(self) -> int:
        """Действие «пойти на работу»; возвращает заработанные монеты."""

    @abstractmethod
    def buy_food(self, index: int = 0) -> None:
        """Действие «купить еду»."""

    @abstractmethod
    def buy_medicine(self, index: int = 0) -> None:
        """Действие «купить лекарство»."""

    @abstractmethod
    def feed_tamagochi(self, index: int = 0) -> None:
        """Действие «покормить питомца»."""

    @abstractmethod
    def heal_tamagochi(self, index: int = 0) -> None:
        """Действие «вылечить питомца»."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Действие «отдохнуть»."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Действие «поиграть с питомцем»."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Возвращает статус игры."""

    @abstractmethod
    def is_over(self) -> bool:
        """Проверяет, закончилась ли игра."""


class SimpleGame(AbstractGame):
    """Реализация игры: деньги, магазин, сумка и действия с питомцем."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Создаёт игру.

        Args:
            tamagochi: питомец.
            clicker: кликер, приносящий монеты.
            all_food: еда, которую можно купить.
            all_medicine: лекарства, которые можно купить.
        """
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._shop_food = list(all_food)
        self._shop_medicine = list(all_medicine)
        self._food_bag: list[Food] = []
        self._medicine_bag: list[Medicine] = []
        self._coins = 0

    @property
    def tamagochi(self) -> AbstractTamagochi:
        """Питомец, участвующий в игре."""
        return self._tamagochi

    @property
    def food(self) -> list[Food]:
        """Еда в сумке игрока."""
        return self._food_bag

    @property
    def medicine(self) -> list[Medicine]:
        """Лекарства в сумке игрока."""
        return self._medicine_bag

    @property
    def shop_food(self) -> list[Food]:
        """Еда, доступная для покупки."""
        return self._shop_food

    @property
    def shop_medicine(self) -> list[Medicine]:
        """Лекарства, доступные для покупки."""
        return self._shop_medicine

    def is_over(self) -> bool:
        """Проверяет, закончилась ли игра.

        Returns:
            True, если питомец погиб.
        """
        return not self._tamagochi.is_alive()

    def _ensure_running(self) -> None:
        """Проверяет, что игра ещё идёт.

        Raises:
            GameOverError: если игра окончена.
        """
        if self.is_over():
            raise GameOverError('Питомец погиб. Игра окончена')

    @staticmethod
    def _pick(items: list, index: int):
        """Возвращает элемент списка по индексу с проверкой границ.

        Args:
            items: список предметов.
            index: номер предмета (с нуля).

        Returns:
            Выбранный предмет.

        Raises:
            InvalidChoiceError: если индекс вне диапазона.
        """
        if not 0 <= index < len(items):
            raise InvalidChoiceError('Предмета с таким номером нет')
        return items[index]

    def _spend(self, price: int) -> None:
        """Списывает монеты.

        Args:
            price: сумма к списанию.

        Raises:
            NotEnoughCoinsError: если монет недостаточно.
        """
        if price > self._coins:
            raise NotEnoughCoinsError(
                f'Не хватает монет: нужно {price}, есть {self._coins}'
            )
        self._coins -= price

    def work(self) -> int:
        """Идёт на работу: кликер приносит монеты.

        Returns:
            Количество заработанных монет.

        Raises:
            GameOverError: если игра окончена.
        """
        self._ensure_running()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def buy_food(self, index: int = 0) -> None:
        """Покупает еду из магазина и кладёт в сумку.

        Args:
            index: номер еды в магазине (с нуля).

        Raises:
            GameOverError: если игра окончена.
            InvalidChoiceError: если номер неверный.
            NotEnoughCoinsError: если не хватает монет.
        """
        self._ensure_running()
        food = self._pick(self._shop_food, index)
        self._spend(food.price)
        self._food_bag.append(replace(food))

    def buy_medicine(self, index: int = 0) -> None:
        """Покупает лекарство из магазина и кладёт в сумку.

        Args:
            index: номер лекарства в магазине (с нуля).

        Raises:
            GameOverError: если игра окончена.
            InvalidChoiceError: если номер неверный.
            NotEnoughCoinsError: если не хватает монет.
        """
        self._ensure_running()
        medicine = self._pick(self._shop_medicine, index)
        self._spend(medicine.price)
        self._medicine_bag.append(replace(medicine, uses=0))

    def feed_tamagochi(self, index: int = 0) -> None:
        """Кормит питомца едой из сумки; еда расходуется.

        Args:
            index: номер еды в сумке (с нуля).

        Raises:
            GameOverError: если игра окончена.
            NoFoodError: если сумка с едой пуста.
            InvalidChoiceError: если номер неверный.
        """
        self._ensure_running()
        if not self._food_bag:
            raise NoFoodError('В сумке нет еды')
        food = self._pick(self._food_bag, index)
        self._tamagochi.feed(food)
        self._food_bag.pop(index)
        self._tamagochi.update()

    def heal_tamagochi(self, index: int = 0) -> None:
        """Лечит питомца лекарством из сумки.

        Закончившееся лекарство удаляется из сумки.

        Args:
            index: номер лекарства в сумке (с нуля).

        Raises:
            GameOverError: если игра окончена.
            NoMedicineError: если сумка с лекарствами пуста.
            InvalidChoiceError: если номер неверный.
        """
        self._ensure_running()
        if not self._medicine_bag:
            raise NoMedicineError('В сумке нет лекарств')
        medicine = self._pick(self._medicine_bag, index)
        self._tamagochi.heal(medicine)
        if medicine.is_empty():
            self._medicine_bag.pop(index)
        self._tamagochi.update()

    def rest_tamagochi(self) -> None:
        """Даёт питомцу отдохнуть.

        Raises:
            GameOverError: если игра окончена.
        """
        self._ensure_running()
        self._tamagochi.rest()
        self._tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем.

        Raises:
            GameOverError: если игра окончена.
            TooTiredError: если питомцу не хватает энергии.
        """
        self._ensure_running()
        self._tamagochi.play()
        self._tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """Возвращает статус игры: показатели питомца и монеты.

        Returns:
            Словарь с показателями питомца и ключом coins.
        """
        status = dict(self._tamagochi.status())
        status['coins'] = self._coins
        return status
