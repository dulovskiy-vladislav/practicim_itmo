"""Логика питомца."""
import random
from abc import ABC, abstractmethod

from game.exceptions import TooTiredError
from game.models import Food, Medicine


class AbstractTamagochi(ABC):
    """Интерфейс тамагочи."""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """Кормит питомца."""

    @abstractmethod
    def play(self) -> None:
        """Играет с питомцем."""

    @abstractmethod
    def rest(self) -> None:
        """Даёт питомцу отдохнуть."""

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """Лечит питомца лекарством."""

    @abstractmethod
    def status(self) -> dict[str, int]:
        """Возвращает все показатели питомца."""

    @abstractmethod
    def is_alive(self) -> bool:
        """Проверяет, жив ли питомец."""

    @abstractmethod
    def is_sick(self) -> bool:
        """Проверяет, болен ли питомец."""

    @abstractmethod
    def update(self) -> None:
        """Обновляет состояние питомца (один игровой тик)."""


class SimpleTamagochi(AbstractTamagochi):
    """Простая реализация питомца.

    Показатели лежат в диапазоне 0..100. Голод и усталость —
    «плохие» (чем больше, тем хуже), здоровье и энергия — «хорошие».
    """

    MAX_VALUE = 100
    PLAY_ENERGY_COST = 15
    FEED_ENERGY_COST = 5
    REST_ENERGY_GAIN = 30
    REST_FATIGUE_RELIEF = 20
    SICK_REST_FACTOR = 0.5
    HUNGER_PER_TICK = 5
    ENERGY_PER_TICK = 3
    SICKNESS_HP_LOSS = 5
    SICKNESS_FATIGUE_GAIN = 5
    STARVATION_HP_LOSS = 10
    EXHAUSTION_HP_LOSS = 5

    def __init__(
        self,
        name: str = 'Тамагочи',
        sickness_chance: float = 0.05,
        rng: random.Random | None = None,
    ) -> None:
        """Создаёт питомца.

        Args:
            name: имя питомца.
            sickness_chance: вероятность заболеть за тик (от 0 до 1).
            rng: генератор случайных чисел (для воспроизводимости).
        """
        self.name = name
        self._sickness_chance = sickness_chance
        self._rng = rng or random.Random()
        self._hunger = 30
        self._fatigue = 0
        self._hp = self.MAX_VALUE
        self._energy = self.MAX_VALUE
        self._sick = False

    @staticmethod
    def _clamp(value: float, low: int = 0, high: int = 100) -> int:
        """Ограничивает значение диапазоном [low, high].

        Args:
            value: исходное значение.
            low: нижняя граница.
            high: верхняя граница.

        Returns:
            Целое значение внутри диапазона.
        """
        return int(max(low, min(high, value)))

    def feed(self, food: Food) -> None:
        """Кормит питомца: голод падает, энергия немного тратится.

        Args:
            food: съедаемая еда.
        """
        self._hunger = self._clamp(self._hunger - food.satiety)
        self._energy = self._clamp(self._energy - self.FEED_ENERGY_COST)

    def play(self) -> None:
        """Играет с питомцем: растут голод и усталость, падает энергия.

        Raises:
            TooTiredError: если энергии не хватает на игру.
        """
        if self._energy < self.PLAY_ENERGY_COST:
            raise TooTiredError('Питомец слишком устал для игры')
        self._energy = self._clamp(self._energy - self.PLAY_ENERGY_COST)
        self._hunger = self._clamp(self._hunger + 10)
        self._fatigue = self._clamp(self._fatigue + 10)

    def rest(self) -> None:
        """Отдых: восстанавливает энергию и снимает усталость.

        У больного питомца отдых действует вдвое слабее.
        """
        factor = self.SICK_REST_FACTOR if self._sick else 1
        self._energy = self._clamp(
            self._energy + self.REST_ENERGY_GAIN * factor
        )
        self._fatigue = self._clamp(
            self._fatigue - self.REST_FATIGUE_RELIEF * factor
        )

    def heal(self, medicine: Medicine) -> None:
        """Лечит питомца: прибавляет здоровье и снимает болезнь.

        Args:
            medicine: используемое лекарство.

        Raises:
            MedicineEmptyError: если лекарство закончилось.
        """
        medicine.use()
        self._hp = self._clamp(self._hp + medicine.heal_hp)
        self._sick = False

    def status(self) -> dict[str, int]:
        """Возвращает показатели питомца.

        Returns:
            Словарь с ключами hunger, fatigue, hp, energy.
        """
        return {
            'hunger': self._hunger,
            'fatigue': self._fatigue,
            'hp': self._hp,
            'energy': self._energy,
        }

    def is_alive(self) -> bool:
        """Проверяет, жив ли питомец (здоровье выше нуля).

        Returns:
            True, если питомец жив.
        """
        return self._hp > 0

    def is_sick(self) -> bool:
        """Проверяет, болен ли питомец.

        Returns:
            True, если питомец болеет.
        """
        return self._sick

    def update(self) -> None:
        """Один игровой тик: растёт голод, падает энергия, возможна болезнь."""
        if not self.is_alive():
            return
        self._hunger = self._clamp(self._hunger + self.HUNGER_PER_TICK)
        self._energy = self._clamp(self._energy - self.ENERGY_PER_TICK)

        if not self._sick and self._rng.random() < self._sickness_chance:
            self._sick = True

        hp_loss = 0
        if self._sick:
            hp_loss += self.SICKNESS_HP_LOSS
            self._fatigue = self._clamp(
                self._fatigue + self.SICKNESS_FATIGUE_GAIN
            )
        if self._hunger >= self.MAX_VALUE:
            hp_loss += self.STARVATION_HP_LOSS
        if self._energy == 0 or self._fatigue >= self.MAX_VALUE:
            hp_loss += self.EXHAUSTION_HP_LOSS
        self._hp = self._clamp(self._hp - hp_loss)
