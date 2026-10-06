# game.py
import pygame
import random
import os
from settings import (WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT, 
                      STONE_COLOR, LEAVES_COLOR, TRUNK_COLOR, ROAD_COLOR)

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

        # --- ЗАГРУЗКА ГРАФИКИ ---
        # Загружаем вашу текстуру травы и сохраняем прозрачность (.convert_alpha())
        try:
            self.grass_img_original = pygame.image.load(os.path.join("assets", "grass.png")).convert_alpha()
        except pygame.error:
            # На случай, если файла нет, создаем временную зеленую заплатку, чтобы игра не вылетала
            print("Предупреждение: Файл assets/grass.png не найден! Использована заглушка.")
            self.grass_img_original = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(self.grass_img_original, (34, 139, 34), 
                                [(TILE_WIDTH//2, 0), (TILE_WIDTH, TILE_HEIGHT//2), (TILE_WIDTH//2, TILE_HEIGHT), (0, TILE_HEIGHT//2)])

        # --- СИСТЕМА ЗЕМЛИ И ДОРОГ ---
        self.ground_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # --- ГЕНЕРАЦИЯ ПРЕПЯТСТВИЙ ---
        self.objects_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_obstacles()

    def generate_obstacles(self):
        """Случайная генерация камней и деревьев."""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if 3 <= x <= 6 and 3 <= y <= 6:
                    continue
                rand = random.random()
                if rand < 0.10:
                    self.objects_grid[x][y] = 1
                elif rand < 0.25:
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
        """Обработка событий мыши."""
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
        """Клик ЛКМ."""
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            obj_type = self.objects_grid[hx][hy]
            if obj_type == 1:
                print(f"Тут камень на ({hx}, {hy}), дорогу не построить!")
            elif obj_type == 2:
                print(f"Тут дерево на ({hx}, {hy}), дорогу не построить!")
            else:
                if self.ground_grid[hx][hy] == 0:
                    self.ground_grid[hx][hy] = 1
                    print(f"Построена дорога на клетке ({hx}, {hy})")
                else:
                    self.ground_grid[hx][hy] = 0
                    print(f"Дорога убрана с клетки ({hx}, {hy})")

    def update(self):
        """Обновление логики игры."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_tile = self.isometric_to_cartesian(mouse_pos[0], mouse_pos[1])

    def draw_farm(self):
        self.screen.fill((30, 30, 40))

        # Вычисляем текущие размеры плитки с учетом зума
        cur_w = int(TILE_WIDTH * self.zoom)
        cur_h = int(TILE_HEIGHT * self.zoom)

        # Масштабируем текстуру травы под текущий зум
        # Используем pygame.transform.scale — он сохраняет пиксели "острыми", если разрешение кратное
        scaled_grass = pygame.transform.scale(self.grass_img_original, (cur_w, cur_h))

        # Отрисовка карты по рядам и колонкам
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                # Точки для ромба (нужны для дорог, подсветки и сеток)
                points = [
                    (iso_x, iso_y),
                    (iso_x + cur_w // 2, iso_y + cur_h // 2),
                    (iso_x, iso_y + cur_h),
                    (iso_x - cur_w // 2, iso_y + cur_h // 2)
                ]
                
                # 1. ОТРИСОВКА ПОВЕРХНОСТИ ЗЕМЛИ
                if self.ground_grid[x][y] == 1:
                    # Дорога пока остается цветным полигоном (пока вы её не нарисуете)
                    pygame.draw.polygon(self.screen, ROAD_COLOR, points)
                    pygame.draw.polygon(self.screen, (50, 50, 50), points, 1)
                else:
                    # РИСУЕМ ВАШУ ТЕКСТУРУ ТРАВЫ!
                    # Картинка рисуется от верхнего левого угла, поэтому смещаем её влево на половину ширины
                    self.screen.blit(scaled_grass, (iso_x - cur_w // 2, iso_y))

                # 2. Отрисовка объектов поверх плитки
                obj = self.objects_grid[x][y]
                if obj == 1:  # КАМЕНЬ
                    stone_w = int(16 * self.zoom)
                    stone_h = int(12 * self.zoom)
                    sx, sy = iso_x, iso_y + cur_h // 2
                    stone_points = [
                        (sx, sy - stone_h), (sx + stone_w, sy),
                        (sx, sy + stone_h // 2), (sx - stone_w, sy)
                    ]
                    pygame.draw.polygon(self.screen, STONE_COLOR, stone_points)
                    pygame.draw.polygon(self.screen, (80, 80, 80), stone_points, 1)

                elif obj == 2:  # ДЕРЕВО
                    trunk_w = max(2, int(6 * self.zoom))
                    trunk_h = int(24 * self.zoom)
                    leaves_r = int(16 * self.zoom)
                    base_x, base_y = iso_x, iso_y + cur_h // 2
                    
                    pygame.draw.rect(self.screen, TRUNK_COLOR, 
                                     (base_x - trunk_w // 2, base_y - trunk_h, trunk_w, trunk_h))
                    pygame.draw.circle(self.screen, LEAVES_COLOR, (base_x, base_y - trunk_h), leaves_r)
                    pygame.draw.circle(self.screen, (20, 70, 20), (base_x, base_y - trunk_h), leaves_r, 1)

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
