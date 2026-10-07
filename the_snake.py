"""Игра «Змейка» (Изгиб Питона).

Классическая игра, где игрок управляет змейкой, собирающей яблоки
на игровом поле.
"""

import random
import sys

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Изгиб Питона')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Attributes:
        position: Позиция объекта на игровом поле (кортеж координат).
        body_color: Цвет объекта в формате RGB.
    """

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовый игровой объект.

        Args:
            position: Начальная позиция объекта. По умолчанию — центр экрана.
            body_color: Цвет объекта. По умолчанию None.
        """
        if position is None:
            position = (
                (SCREEN_WIDTH // 2),
                (SCREEN_HEIGHT // 2)
            )
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта.

        Должен быть переопределён в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле.

    Яблоко появляется в случайной позиции и может быть «съедено» змейкой.
    """

    def __init__(self, body_color=APPLE_COLOR):
        """Инициализирует яблоко со случайной позицией.

        Args:
            body_color: Цвет яблока. По умолчанию красный.
        """
        super().__init__(body_color=body_color)
        self.randomize_position()

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайную позицию яблока на игровом поле.

        Args:
            occupied_positions: Список занятых позиций, которые нужно избежать.
        """
        if occupied_positions is None:
            occupied_positions = []

        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение.

    Управляет движением, отрисовкой и обработкой событий змейки.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в начальном состоянии.

        Args:
            body_color: Цвет змейки. По умолчанию зелёный.
        """
        super().__init__(body_color=body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки.

        Применяет следующее направление, если оно задано и не противоположно
        текущему.
        """
        if self.next_direction:
            # Запрещаем движение в противоположном направлении
            opposite_directions = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT
            }
            if opposite_directions.get(self.direction) != self.next_direction:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки, перемещая её на одну клетку.

        Добавляет новую голову в начало списка и удаляет хвост,
        если длина не увеличилась.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учётом прохождения сквозь стены
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        # Сохраняем позицию последнего сегмента для стирания
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране и затирает след."""
        # Затираем след от последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        # Отрисовываем все сегменты змейки
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self):
        """Возвращает позицию головы змейки.

        Returns:
            Кортеж с координатами головы змейки.
        """
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние.

        Вызывается при столкновении змейки с собой.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None
        # Очищаем экран для новой игры
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        game_object: Объект змейки, у которого обновляется направление.

    Returns:
        False, если нажата клавиша выхода (ESC), иначе True.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_UP:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                game_object.next_direction = RIGHT
    return True


def main():
    """Основная функция игры, содержащая игровой цикл."""
    # Инициализация Pygame
    pygame.init()

    # Создаём объекты игры
    snake = Snake()
    apple = Apple()

    running = True

    while running:
        # Ограничиваем скорость игры
        clock.tick(SPEED)

        # Обрабатываем нажатия клавиш
        running = handle_keys(snake)

        # Обновляем направление движения
        snake.update_direction()

        # Двигаем змейку
        snake.move()

        # Проверяем, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            # Генерируем новое яблоко, избегая позиций змейки
            apple.randomize_position(snake.positions)

        # Проверяем столкновение змейки с собой
        # Голова не должна совпадать с другими сегментами тела
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            # Пересоздаём яблоко после сброса
            apple.randomize_position(snake.positions)

        # Отрисовываем объекты
        snake.draw()
        apple.draw()

        # Обновляем экран
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()