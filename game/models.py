"""Модели игры: еда и лекарства."""
from dataclasses import dataclass

from game.exceptions import MedicineEmptyError


@dataclass(repr=False)
class Food:
    """Еда, которой можно кормить питомца.

    Attributes:
        name: наименование еды.
        satiety: сколько насыщения даёт еда.
        price: стоимость еды в монетах.
    """

    name: str
    satiety: int
    price: int

    def __repr__(self) -> str:
        """Возвращает короткое читаемое описание еды."""
        return (
            f'{self.name} (сытость +{self.satiety}, '
            f'цена {self.price})'
        )


@dataclass(repr=False)
class Medicine:
    """Лекарство, которым можно лечить питомца.

    Attributes:
        name: наименование лекарства.
        price: стоимость лекарства в монетах.
        heal_hp: сколько здоровья восстанавливает одно использование.
        number_of_uses: максимальное количество использований.
        uses: текущее количество использований.

    Raises:
        ValueError: если uses выходит за пределы [0, number_of_uses].
    """

    name: str
    price: int
    heal_hp: int
    number_of_uses: int
    uses: int = 0

    def __post_init__(self) -> None:
        """Проверяет корректность количества использований."""
        if not 0 <= self.uses <= self.number_of_uses:
            raise ValueError(
                'uses должно быть в пределах от 0 до number_of_uses'
            )

    def is_empty(self) -> bool:
        """Проверяет, остались ли использования у лекарства.

        Returns:
            True, если лекарство использовано полностью.
        """
        return self.uses >= self.number_of_uses

    def use(self) -> None:
        """Тратит одно использование лекарства.

        Raises:
            MedicineEmptyError: если использований не осталось.
        """
        if self.is_empty():
            raise MedicineEmptyError(
                f'Лекарство «{self.name}» закончилось'
            )
        self.uses += 1

    def __repr__(self) -> str:
        """Возвращает короткое читаемое описание лекарства."""
        left = self.number_of_uses - self.uses
        return (
            f'{self.name} (здоровье +{self.heal_hp}, '
            f'осталось доз {left}/{self.number_of_uses}, '
            f'цена {self.price})'
        )
