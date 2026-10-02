# game.py
import pygame
import random
from settings import (WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT, 
                      GREEN, DARK_GREEN, STONE_COLOR, LEAVES_COLOR, TRUNK_COLOR)

class GameWorld:
    def __init__(self, screen):
        self.screen = screen
        
        # Позиция камеры
        self.camera_x = WIDTH // 2
        self.camera_y = HEIGHT // 4

        # Система масштабирования (зум)
        self.zoom = 1.0
        self.min_zoom = 0.4
        self.max_zoom = 2.5

        # Логика перемещения карты мышкой (ЛКМ)
        self.is_dragging = False
        self.drag_start_mouse = (0, 0)
        self.drag_start_camera = (0, 0)
        self.has_moved_enough = False

        # Координаты клетки под курсором
        self.hovered_tile = (-1, -1)

        # --- ГЕНЕРАЦИЯ ПРЕПЯТСТВИЙ ---
        # Матрица объектов: 0 - пусто, 1 - камень, 2 - дерево
        self.objects_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_obstacles()

    def generate_obstacles(self):
        """Случайная генерация камней и деревьев на карте."""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # Оставляем центр фермы (клетки от 3 до 6) пустым для старта игрока
                if 3 <= x <= 6 and 3 <= y <= 6:
                    continue
                
                rand = random.random()
                if rand < 0.10:    # 10% шанс на появление камня
                    self.objects_grid[x][y] = 1
                elif rand < 0.25:  # 15% шанс на появление дерева (0.10 + 0.15)
                    self.objects_grid[x][y] = 2

    def cartesian_to_isometric(self, x, y):
        """Перевод координат сетки в экранные изометрические с учетом зума и камеры."""
        iso_x = (x - y) * (TILE_WIDTH // 2)
        iso_y = (x + y) * (TILE_HEIGHT // 2)
        
        screen_x = int(iso_x * self.zoom + self.camera_x)
        screen_y = int(iso_y * self.zoom + self.camera_y)
        return screen_x, screen_y

    def isometric_to_cartesian(self, mouse_x, mouse_y):
        """Перевод экранных координат мыши в индексы сетки с учетом зума."""
        dx = (mouse_x - self.camera_x) / self.zoom
        dy = (mouse_y - self.camera_y) / self.zoom

        grid_x = int(((dx / (TILE_WIDTH / 2)) + (dy / (TILE_HEIGHT / 2))) / 2)
        grid_y = int(((dy / (TILE_HEIGHT / 2)) - (dx / (TILE_WIDTH / 2))) / 2)

        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return grid_x, grid_y
        return -1, -1

    def handle_event(self, event):
        """Обработка событий мыши (зум и ЛКМ) для игрового мира."""
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.zoom = min(self.max_zoom, self.zoom + 0.1)
            elif event.button == 5:
                self.zoom = max(self.min_zoom, self.zoom - 0.1)
            elif event.button == 1:
                self.is_dragging = True
                self.has_moved_enough = False
                self.drag_start_mouse = mouse_pos
                self.drag_start_camera = (self.camera_x, self.camera_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                if not self.has_moved_enough:
                    self.handle_tile_click()

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                delta_x = mouse_pos[0] - self.drag_start_mouse[0]
                delta_y = mouse_pos[1] - self.drag_start_mouse[1]
                
                if abs(delta_x) > 5 or abs(delta_y) > 5:
                    self.has_moved_enough = True

                if self.has_moved_enough:
                    self.camera_x = self.drag_start_camera[0] + delta_x
                    self.camera_y = self.drag_start_camera[1] + delta_y

    def handle_tile_click(self):
        """Одиночный клик ЛКМ на клетку (для будущих механик расчистки)."""
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            obj_type = self.objects_grid[hx][hy]
            if obj_type == 1:
                print(f"Клик по камню на клетке ({hx}, {hy}). Нужно разбить киркой!")
            elif obj_type == 2:
                print(f"Клик по дереву на клетке ({hx}, {hy}). Нужно срубить топором!")
            else:
                print(f"Клик по пустой траве на клетке ({hx}, {hy}).")

    def update(self):
        """Обновление логики игры."""
        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos
        self.hovered_tile = self.isometric_to_cartesian(mx, my)

    def draw_farm(self):
        self.screen.fill((30, 30, 40))

        cur_w = TILE_WIDTH * self.zoom
        cur_h = TILE_HEIGHT * self.zoom

        # Отрисовка карты по рядам и колонкам
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                # 1. Отрисовка плитки земли
                points = [
                    (iso_x, iso_y),
                    (iso_x + cur_w // 2, iso_y + cur_h // 2),
                    (iso_x, iso_y + cur_h),
                    (iso_x - cur_w // 2, iso_y + cur_h // 2)
                ]
                color = GREEN if (x + y) % 2 == 0 else DARK_GREEN
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (50, 50, 50), points, 1)

                # 2. Отрисовка объектов поверх плитки земли
                obj = self.objects_grid[x][y]
                
                if obj == 1:  # КАМЕНЬ (рисуем небольшой серый многоугольник)
                    stone_w = int(16 * self.zoom)
                    stone_h = int(12 * self.zoom)
                    # Центрируем камень на плитке и приподнимаем к её центру
                    sx = iso_x
                    sy = iso_y + cur_h // 2
                    
                    stone_points = [
                        (sx, sy - stone_h),
                        (sx + stone_w, sy),
                        (sx, sy + stone_h // 2),
                        (sx - stone_w, sy)
                    ]
                    pygame.draw.polygon(self.screen, STONE_COLOR, stone_points)
                    pygame.draw.polygon(self.screen, (80, 80, 80), stone_points, 1)

                elif obj == 2:  # ДЕРЕВО (ствол + крона)
                    trunk_w = max(2, int(6 * self.zoom))
                    trunk_h = int(24 * self.zoom)
                    leaves_r = int(16 * self.zoom)
                    
                    # Точка основания дерева
                    base_x = iso_x
                    base_y = iso_y + cur_h // 2
                    
                    # Ствол дерева
                    pygame.draw.rect(self.screen, TRUNK_COLOR, 
                                     (base_x - trunk_w // 2, base_y - trunk_h, trunk_w, trunk_h))
                    # Крона дерева (листва)
                    pygame.draw.circle(self.screen, LEAVES_COLOR, 
                                       (base_x, base_y - trunk_h), leaves_r)
                    pygame.draw.circle(self.screen, (20, 70, 20), 
                                       (base_x, base_y - trunk_h), leaves_r, 1)

        # 3. Рисуем подсветку выбранной клетки поверх всего
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            iso_x, iso_y = self.cartesian_to_isometric(hx, hy)
            hover_points = [
                (iso_x, iso_y),
                (iso_x + cur_w // 2, iso_y + cur_h // 2),
                (iso_x, iso_y + cur_h),
                (iso_x - cur_w // 2, iso_y + cur_h // 2)
            ]
            line_thickness = max(2, int(3 * self.zoom))
            pygame.draw.polygon(self.screen, (255, 255, 100), hover_points, line_thickness)
