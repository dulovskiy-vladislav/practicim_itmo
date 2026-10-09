"""Логика игры: связывает питомца, кликер, еду и лекарства."""
from abc import ABC, abstractmethod
from dataclasses import replace

from game.clicker import AbstractClicker
from game.exceptions import (
    InvalidChoiceError,
    NoFoodError,
    NoMedicineError,
    NotEnoughMoney,
    TamagochiIsGone,
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

    @abstractmethod
    def work(self) -> int:
        """Действие «пойти на работу»; возвращает заработанные монеты."""

    @abstractmethod
    def buy_food(self) -> None:
        """Действие «купить еду»."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Действие «купить лекарство»."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Действие «покормить питомца»."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
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

    def is_over(self) -> bool:
        """Проверяет, закончилась ли игра.

        Returns:
            True, если питомец погиб.
        """
        return not self._tamagochi.is_alive()

    def _ensure_running(self) -> None:
        """Проверяет, что игра ещё идёт.

        Raises:
            TamagochiIsGone: если игра окончена.
        """
        if self.is_over():
            raise TamagochiIsGone('Питомец погиб. Игра окончена')

    @staticmethod
    def _resolve_index(
        items: list, title: str, index: int | None
    ) -> int:
        """Определяет индекс выбранного предмета.

        Если индекс не передан, показывает список и спрашивает игрока:
        можно ввести номер (с единицы) или название предмета. Если ввод
        недоступен (нет stdin), выбирается первый предмет.

        Args:
            items: список предметов на выбор.
            title: заголовок списка.
            index: готовый индекс (с нуля) или None для интерактивного
                выбора.

        Returns:
            Индекс выбранного предмета (с нуля).

        Raises:
            InvalidChoiceError: если выбор некорректен.
        """
        if index is None:
            print(title)
            for number, item in enumerate(items, start=1):
                print(f'{number}. {item!r}')
            try:
                answer = input('Введите номер: ').strip()
            except (EOFError, OSError):
                answer = '1'
            if answer.isdigit():
                index = int(answer) - 1
            else:
                names = [item.name.lower() for item in items]
                if answer.lower() not in names:
                    raise InvalidChoiceError('Такого предмета нет')
                index = names.index(answer.lower())
        if not 0 <= index < len(items):
            raise InvalidChoiceError('Предмета с таким номером нет')
        return index

    def _select(self, items: list, title: str, index: int | None):
        """Возвращает выбранный предмет из списка.

        Args:
            items: список предметов на выбор.
            title: заголовок списка.
            index: индекс (с нуля) или None для интерактивного выбора.

        Returns:
            Выбранный предмет.

        Raises:
            InvalidChoiceError: если выбор некорректен.
        """
        return items[self._resolve_index(items, title, index)]

    def _spend(self, price: int) -> None:
        """Списывает монеты.

        Args:
            price: сумма к списанию.

        Raises:
            NotEnoughMoney: если монет недостаточно.
        """
        if price > self._coins:
            raise NotEnoughMoney(
                f'Не хватает монет: нужно {price}, есть {self._coins}'
            )
        self._coins -= price

    def work(self) -> int:
        """Идёт на работу: кликер приносит монеты.

        Returns:
            Количество заработанных монет.

        Raises:
            TamagochiIsGone: если игра окончена.
        """
        self._ensure_running()
        self._clicker.click()
        income = self._clicker.income_per_click
        if callable(income):  # реализация, где это метод, а не свойство
            income = income()
        self._coins += income
        return income

    def buy_food(self, index: int | None = None) -> None:
        """Покупает еду из магазина и кладёт в сумку.

        Args:
            index: номер еды в магазине (с нуля); None — спросить игрока.

        Raises:
            TamagochiIsGone: если игра окончена.
            InvalidChoiceError: если номер неверный.
            NotEnoughMoney: если не хватает монет.
        """
        self._ensure_running()
        food = self._select(self._shop_food, 'Магазин еды:', index)
        self._spend(food.price)
        self._food_bag.append(replace(food))

    def buy_medicine(self, index: int | None = None) -> None:
        """Покупает лекарство из магазина и кладёт в сумку.

        Args:
            index: номер лекарства (с нуля); None — спросить игрока.

        Raises:
            TamagochiIsGone: если игра окончена.
            InvalidChoiceError: если номер неверный.
            NotEnoughMoney: если не хватает монет.
        """
        self._ensure_running()
        medicine = self._select(
            self._shop_medicine, 'Аптека:', index
        )
        self._spend(medicine.price)
        self._medicine_bag.append(replace(medicine, uses=0))

    def feed_tamagochi(self, index: int | None = None) -> None:
        """Кормит питомца едой из сумки; еда расходуется.

        Args:
            index: номер еды в сумке (с нуля); None — спросить игрока.

        Raises:
            TamagochiIsGone: если игра окончена.
            NoFoodError: если сумка с едой пуста.
            InvalidChoiceError: если номер неверный.
        """
        self._ensure_running()
        if not self._food_bag:
            raise NoFoodError('В сумке нет еды')
        index = self._resolve_index(
            self._food_bag, 'Сумка с едой:', index
        )
        food = self._food_bag[index]
        self._tamagochi.feed(food)
        self._food_bag.pop(index)
        self._tamagochi.update()

    def heal_tamagochi(self, index: int | None = None) -> None:
        """Лечит питомца лекарством из сумки.

        Закончившееся лекарство удаляется из сумки.

        Args:
            index: номер лекарства (с нуля); None — спросить игрока.

        Raises:
            TamagochiIsGone: если игра окончена.
            NoMedicineError: если сумка с лекарствами пуста.
            InvalidChoiceError: если номер неверный.
        """
        self._ensure_running()
        if not self._medicine_bag:
            raise NoMedicineError('В сумке нет лекарств')
        index = self._resolve_index(
            self._medicine_bag, 'Сумка с лекарствами:', index
        )
        medicine = self._medicine_bag[index]
        self._tamagochi.heal(medicine)
        if medicine.is_empty():
            self._medicine_bag.pop(index)
        self._tamagochi.update()

    def rest_tamagochi(self) -> None:
        """Даёт питомцу отдохнуть.

        Raises:
            TamagochiIsGone: если игра окончена.
        """
        self._ensure_running()
        self._tamagochi.rest()
        self._tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем.

        Raises:
            TamagochiIsGone: если игра окончена.
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
