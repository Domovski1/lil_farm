# game.py
import pygame
import random
import os
from settings import WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT

# ==============================================================================
# 🎨 НАСТРОЙКА ВАШЕЙ ГРАФИКИ (Редактируйте эти словари при добавлении новых картинок)
# ==============================================================================

# Какие картинки соответствуют типам земли (0, 1, 2...)
# Формат: ID_ТИПА: "имя_файла.png"
GROUND_CONFIG = {
    0: "grass.png",
    1: "road.png",   # Когда нарисуете дорогу, просто положите road.png в assets
    # 2: "field.png", # <- Сюда в будущем добавите грядку!
}

# Какие картинки соответствуют объектам (1, 2, 3...)
# Формат: ID_ОБЪЕКТА: {"file": "имя.png", "offset_y": смещение_вверх_в_пикселях}
OBJECTS_CONFIG = {
    1: {"file": "stone.png",  "offset_y": 10}, # Камень невысокий, приподнимем чуть-чуть
    2: {"file": "tree.png",   "offset_y": 45}, # Дерево высокое, его нужно поднять выше, чтобы корни были на плитке
    # 3: {"file": "house.png", "offset_y": 60}, # <- Сюда в будущем добавите дом!
}

# ==============================================================================

class GameWorld:
    def __init__(self, screen):
        self.screen = screen
        
        # Позиция камеры и зум
        self.camera_x = WIDTH // 2
        self.camera_y = HEIGHT // 4
        self.zoom = 1.0
        self.min_zoom = 0.4
        self.max_zoom = 2.5

        # Логика перемещения
        self.is_dragging = False
        self.drag_start_mouse = (0, 0)
        self.drag_start_camera = (0, 0)
        self.has_moved_enough = False
        self.hovered_tile = (-1, -1)

        # Матрицы игрового мира
        self.ground_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.objects_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_obstacles()

        # Автоматическая загрузка графики
        self.ground_sprites = {}
        self.object_sprites = {}
        self.load_game_assets()

    def load_game_assets(self):
        """Автоматически загружает все картинки на основе конфигов выше."""
        # 1. Загрузка плиток земли
        for tile_id, file_name in GROUND_CONFIG.items():
            path = os.path.join("assets", file_name)
            if os.path.exists(path):
                self.ground_sprites[tile_id] = pygame.image.load(path).convert_alpha()
            else:
                # Если файла нет, делаем цветную заглушку, чтобы игра не падала
                print(f"Файл {path} не найден! Создана заглушка.")
                surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
                color = (34, 139, 34) if tile_id == 0 else (140, 120, 100)
                pygame.draw.polygon(surf, color, [(TILE_WIDTH//2, 0), (TILE_WIDTH, TILE_HEIGHT//2), (TILE_WIDTH//2, TILE_HEIGHT), (0, TILE_HEIGHT//2)])
                self.ground_sprites[tile_id] = surf

        # 2. Загрузка объектов (деревья, камни)
        for obj_id, config in OBJECTS_CONFIG.items():
            path = os.path.join("assets", config["file"])
            if os.path.exists(path):
                self.object_sprites[obj_id] = pygame.image.load(path).convert_alpha()
            else:
                print(f"Файл {path} не найден! Создана заглушка.")
                # Делаем простой цветной квадратик вместо спрайта
                surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                color = (130, 130, 130) if obj_id == 1 else (101, 67, 33)
                surf.fill(color)
                self.object_sprites[obj_id] = surf

    def generate_obstacles(self):
        """Генерация препятствий."""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if 3 <= x <= 6 and 3 <= y <= 6:
                    continue
                rand = random.random()
                if rand < 0.10:
                    self.objects_grid[x][y] = 1 # Камень
                elif rand < 0.25:
                    self.objects_grid[x][y] = 2 # Дерево

    def cartesian_to_isometric(self, x, y):
        """Перевод координат в изометрию."""
        iso_x = (x - y) * (TILE_WIDTH // 2)
        iso_y = (x + y) * (TILE_HEIGHT // 2)
        screen_x = int(iso_x * self.zoom + self.camera_x)
        screen_y = int(iso_y * self.zoom + self.camera_y)
        return screen_x, screen_y

    def isometric_to_cartesian(self, mouse_x, mouse_y):
        """Перевод мыши в сетку."""
        dx = (mouse_x - self.camera_x) / self.zoom
        dy = (mouse_y - self.camera_y) / self.zoom
        grid_x = int(((dx / (TILE_WIDTH / 2)) + (dy / (TILE_HEIGHT / 2))) / 2)
        grid_y = int(((dy / (TILE_HEIGHT / 2)) - (dx / (TILE_WIDTH / 2))) / 2)
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return grid_x, grid_y
        return -1, -1

    def handle_event(self, event):
        """Управление мышкой (зум, драг)."""
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
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
            if not self.has_moved_enough:
                self.handle_tile_click()
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            delta_x = mouse_pos[0] - self.drag_start_mouse[0]
            delta_y = mouse_pos[1] - self.drag_start_mouse[1]
            if abs(delta_x) > 5 or abs(delta_y) > 5:
                self.has_moved_enough = True
            if self.has_moved_enough:
                self.camera_x = self.drag_start_camera[0] + delta_x
                self.camera_y = self.drag_start_camera[1] + delta_y

    def handle_tile_click(self):
        """Клик по плитке."""
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            obj_type = self.objects_grid[hx][hy]
            if obj_type == 0:
                # Переключаем траву и дорогу
                self.ground_grid[hx][hy] = 1 if self.ground_grid[hx][hy] == 0 else 0

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_tile = self.isometric_to_cartesian(mouse_pos[0], mouse_pos[1])

    def draw_farm(self):
        self.screen.fill((30, 30, 40))
        cur_w = int(TILE_WIDTH * self.zoom)
        cur_h = int(TILE_HEIGHT * self.zoom)

        # Универсальный рендер
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                # 1. Авто-отрисовка ЗЕМЛИ
                tile_type = self.ground_grid[x][y]
                original_tile_img = self.ground_sprites[tile_type]
                scaled_tile = pygame.transform.scale(original_tile_img, (cur_w, cur_h))
                self.screen.blit(scaled_tile, (iso_x - cur_w // 2, iso_y))

                # 2. Авто-отрисовка ОБЪЕКТОВ
                obj_type = self.objects_grid[x][y]
                if obj_type != 0:
                    original_obj_img = self.object_sprites[obj_type]
                    
                    # Получаем пропорциональные размеры объекта под зумом
                    obj_w = int(original_obj_img.get_width() * self.zoom)
                    obj_h = int(original_obj_img.get_height() * self.zoom)
                    scaled_obj = pygame.transform.scale(original_obj_img, (obj_w, obj_h))
                    
                    # Считаем смещение объекта вверх (offset) с учетом зума
                    offset_y = int(OBJECTS_CONFIG[obj_type]["offset_y"] * self.zoom)
                    
                    # Точка отрисовки: центр плитки по X, и основание плитки минус смещение по Y
                    render_x = iso_x - obj_w // 2
                    render_y = (iso_y + cur_h // 2) - obj_h + offset_y
                    
                    self.screen.blit(scaled_obj, (render_x, render_y))

        # 3. Подсветка плитки
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            iso_x, iso_y = self.cartesian_to_isometric(hx, hy)
            hover_points = [(iso_x, iso_y), (iso_x + cur_w // 2, iso_y + cur_h // 2), (iso_x, iso_y + cur_h), (iso_x - cur_w // 2, iso_y + cur_h // 2)]
            pygame.draw.polygon(self.screen, (255, 255, 100), hover_points, max(2, int(3 * self.zoom)))
