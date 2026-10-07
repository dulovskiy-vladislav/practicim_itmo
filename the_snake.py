"""Игра «Змейка» на Pygame.

Змейка ползёт по полю 32x24 ячейки, поедает яблоки и растёт.
Через границы поля змейка проходит насквозь. При столкновении
с собой игра начинается заново.
"""
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (кадров в секунду):
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Задаёт позицию и цвет объекта.

        По умолчанию объект находится в центре экрана.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None, border=True):
        """Отрисовывает одну ячейку сетки.

        Если цвет не передан, используется цвет объекта.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color or self.body_color, rect)
        if border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект. Переопределяется в дочерних классах."""
        pass


class Apple(GameObject):
    """Яблоко, которое поедает змейка."""

    def __init__(self, occupied=()):
        """Создаёт яблоко в случайной ячейке, не занятой `occupied`."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=()):
        """Выбирает случайную свободную ячейку поля для яблока."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, управляемая игроком."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color=SNAKE_COLOR)
        self.next_direction = None
        self.reset()

    def update_direction(self):
        """Применяет направление, выбранное игроком."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну ячейку в текущем направлении.

        Через границы поля змейка проходит насквозь. Если длина не
        выросла, последний сегмент удаляется (и запоминается в `last`,
        чтобы потом стереть его с экрана).
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку и стирает след от хвоста."""
        for position in self.positions:
            self.draw_cell(position)
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна.

    Змейка не может развернуться на 180 градусов.
    """
    opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
    keys_map = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT,
    }
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            new_direction = keys_map.get(event.key)
            if new_direction and new_direction != opposite[
                game_object.direction
            ]:
                game_object.next_direction = new_direction


def main():
    """Запускает основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
