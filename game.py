# game.py
import pygame
from settings import WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT, GREEN, DARK_GREEN, WHITE

class GameWorld:
    def __init__(self, screen):
        self.screen = screen
        # Смещение мира, чтобы ферма была по центру экрана
        self.origin_x = WIDTH // 2
        self.origin_y = HEIGHT // 3

    def cartesian_to_isometric(self, x, y):
        """Перевод координат сетки в экранные изометрические."""
        iso_x = (x - y) * (TILE_WIDTH // 2) + self.origin_x
        iso_y = (x + y) * (TILE_HEIGHT // 2) + self.origin_y
        return iso_x, iso_y

    def draw_farm(self):
        self.screen.fill((30, 30, 40)) # Цвет фона за пределами фермы

        # Рисуем изометрическую сетку земли
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                # Точки для отрисовки ромба (плитки)
                points = [
                    (iso_x, iso_y),                          # Верхняя точка
                    (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2),  # Правая точка
                    (iso_x, iso_y + TILE_HEIGHT),            # Нижня точка
                    (iso_x - TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2)   # Левая точка
                ]
                
                # Чередуем цвета для эффекта шахматной доски
                color = GREEN if (x + y) % 2 == 0 else DARK_GREEN
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (50, 50, 50), points, 1) # Граница плитки

    def update(self):
        # Здесь будет логика роста урожая, перемещения персонажа и т.д.
        pass
