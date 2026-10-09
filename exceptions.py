"""Пользовательские исключения игры «Тамагочи»."""


class GameError(Exception):
    """Базовое исключение игры."""


class NotEnoughCoinsError(GameError):
    """Не хватает монет для покупки."""


class InvalidChoiceError(GameError):
    """Выбран несуществующий предмет (неверный номер)."""


class NoFoodError(GameError):
    """В сумке нет еды."""


class NoMedicineError(GameError):
    """В сумке нет лекарств."""


class MedicineEmptyError(GameError):
    """У лекарства закончились использования."""


class TooTiredError(GameError):
    """У питомца не хватает энергии на действие."""


class GameOverError(GameError):
    """Игра окончена: действия больше недоступны."""
