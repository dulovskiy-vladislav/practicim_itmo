import os

from game.clicker import AbstractClicker, SimpleRandomClicker
from game.exceptions import GameError
from game.game import AbstractGame, SimpleGame
from game.models import Food, Medicine
from game.tamagochi import AbstractTamagochi, SimpleTamagochi


def choose_index(title: str, items: list) -> int:
    """Показывает нумерованный список и запрашивает выбор.

    Args:
        title: заголовок списка.
        items: предметы на выбор.

    Returns:
        Индекс выбранного предмета (с нуля); -1, если ввод неверный.
    """
    print(title)
    for number, item in enumerate(items, start=1):
        print(f'{number}. {item!r}')
    try:
        return int(input('Введите номер: ')) - 1
    except ValueError:
        return -1


def handle_action(game: AbstractGame, choice: str) -> str:
    """Выполняет выбранное действие и возвращает сообщение для игрока.

    Args:
        game: игра (работаем только через интерфейс).
        choice: введённый пункт меню.

    Returns:
        Текст результата действия.

    Raises:
        GameError: если действие невозможно.
    """
    match choice:
        case '1':
            income = game.work()
            game.tamagochi.update()
            return f'Вы заработали {income} монет'
        case '2':
            game.buy_food(choose_index('Магазин еды:', game.shop_food))
            return 'Еда куплена'
        case '3':
            game.buy_medicine(
                choose_index('Аптека:', game.shop_medicine)
            )
            return 'Лекарство куплено'
        case '4':
            game.feed_tamagochi(choose_index('Сумка с едой:', game.food))
            return 'Питомец поел'
        case '5':
            game.heal_tamagochi(
                choose_index('Сумка с лекарствами:', game.medicine)
            )
            return 'Питомец вылечен'
        case '6':
            game.play_with_tamagochi()
            return 'Вы поиграли с питомцем'
        case '7':
            game.rest_tamagochi()
            return 'Питомец отдохнул'
        case _:
            return 'Неверная команда'


def main():
    all_food = [
        Food(name='Бургер', satiety=20, price=40),
        Food(name='Салат', satiety=10, price=20),
        Food(name='Яблоко', satiety=10, price=15)
    ]

    all_medicine = [
        Medicine(name='Ибупрофен', price=30, heal_hp=20, number_of_uses=2)
    ]

    tamagochi: AbstractTamagochi = SimpleTamagochi()
    clicker: AbstractClicker = SimpleRandomClicker(10, 20)
    game: AbstractGame = SimpleGame(
        tamagochi, clicker, all_food=all_food, all_medicine=all_medicine
    )

    print("Добро пожаловать в тамагочи-кликер!")
    output = ''

    while True:
        print(output)

        print(f"Сумка с едой: {game.food}")
        print(f"Сумка с лекарствами: {game.medicine}")

        status = game.get_status()
        print(
            f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
            f"энергия {status['energy']}, монет {status['coins']}\n"
        )
        if game.is_over():
            print("Питомец погиб. Игра окончена!")
            break
        if game.tamagochi.is_sick():
            print("=======Тамагочи болеет======")
            print("=======Отдых действует менее эффективно=======")
        print("1. Пойти на работу")
        print("2. Купить еду")
        print("3. Купить лекарство")
        print("4. Покормить")
        print("5. Вылечить")
        print("6. Играть")
        print("7. Отдых")
        print("0. Выход")

        choice = input("Выберите действие: ")
        if choice == "0":
            break
        try:
            output = handle_action(game, choice)
        except GameError as error:
            output = str(error)

        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()
