# game.py
import pygame
from settings import WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT, GREEN, DARK_GREEN, WHITE

class GameWorld:
    def __init__(self, screen):
        self.screen = screen
        # Смещение мира, чтобы ферма была по центру экрана
        self.origin_x = WIDTH // 2
        self.origin_y = HEIGHT // 4  # Немного приподняли, чтобы влезало больше сетки

        # Координаты клетки, на которую наведена мышь (-1, -1 означает, что мышь вне сетки)
        self.hovered_tile = (-1, -1)

    def cartesian_to_isometric(self, x, y):
        """Перевод координат сетки в экранные изометрические."""
        iso_x = (x - y) * (TILE_WIDTH // 2) + self.origin_x
        iso_y = (x + y) * (TILE_HEIGHT // 2) + self.origin_y
        return iso_x, iso_y

    def isometric_to_cartesian(self, mouse_x, mouse_y):
        """Перевод экранных координат мыши в индексы сетки (x, y)."""
        # Корректируем координаты относительно центра отрисовки
        dx = mouse_x - self.origin_x
        # Сдвигаем y на половину высоты плитки, так как точка отсчета ромба — его верхний угол
        dy = mouse_y - self.origin_y 

        # Вычисляем дробные координаты в изометрической проекции
        grid_x = int(((dx / (TILE_WIDTH / 2)) + (dy / (TILE_HEIGHT / 2))) / 2)
        grid_y = int(((dy / (TILE_HEIGHT / 2)) - (dx / (TILE_WIDTH / 2))) / 2)

        # Проверяем, находится ли полученный индекс внутри границ нашей фермы
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return grid_x, grid_y
        return -1, -1

    def update(self):
        """Обновление логики игры, включая позицию мыши."""
        mouse_pos = pygame.mouse.get_pos()
        # Рассчитываем, на какой плитке находится игрок
        self.hovered_tile = self.isometric_to_cartesian(mouse_pos[0], mouse_pos[1])

    def draw_farm(self):
        self.screen.fill((30, 30, 40)) # Цвет фона за пределами фермы

        # 1. Рисуем базовую изометрическую сетку земли
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                # Точки для отрисовки ромба (плитки)
                points = [
                    (iso_x, iso_y),                          # Верхняя точка
                    (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2),  # Правая точка
                    (iso_x, iso_y + TILE_HEIGHT),            # Нижняя точка
                    (iso_x - TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2)   # Левая точка
                ]
                
                # Чередуем цвета для эффекта шахматной доски
                color = GREEN if (x + y) % 2 == 0 else DARK_GREEN
                pygame.draw.polygon(self.screen, color, points)
                # Рисуем тонкую серую сетку
                pygame.draw.polygon(self.screen, (50, 50, 50), points, 1)

        # 2. Отрисовка подсветки поверх выбранной клетки
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            iso_x, iso_y = self.cartesian_to_isometric(hx, hy)
            hover_points = [
                (iso_x, iso_y),
                (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2),
                (iso_x, iso_y + TILE_HEIGHT),
                (iso_x - TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2)
            ]
            # Рисуем полупрозрачную белую заливку для выделения клетки
            # Так как pygame.draw.polygon не поддерживает альфа-канал напрямую,
            # мы делаем обводку ярким цветом, а саму клетку слегка подсвечиваем
            pygame.draw.polygon(self.screen, (255, 255, 100), hover_points, 3) # Желтый контур шириной 3 пикселя
