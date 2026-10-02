# game.py
import pygame
from settings import WIDTH, HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT, GREEN, DARK_GREEN

class GameWorld:
    def __init__(self, screen):
        self.screen = screen
        
        # Позиция камеры (смещение относительно центра экрана)
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
        self.has_moved_enough = False  # Флаг, чтобы отличать клик от перетаскивания

        # Координаты клетки под курсором
        self.hovered_tile = (-1, -1)

    def cartesian_to_isometric(self, x, y):
        """Перевод координат сетки в экранные изометрические с учетом зума и камеры."""
        iso_x = (x - y) * (TILE_WIDTH // 2)
        iso_y = (x + y) * (TILE_HEIGHT // 2)
        
        screen_x = int(iso_x * self.zoom + self.camera_x)
        screen_y = int(iso_y * self.zoom + self.camera_y)
        return screen_x, screen_y

    def isometric_to_cartesian(self, mouse_x, mouse_y):
        """Перевод экранных координат мыши в индексы сетки (x, y) с учетом зума и камеры."""
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

        # --- ЗУМ (Колесико мыши) ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Прокрутка вверх
                self.zoom = min(self.max_zoom, self.zoom + 0.1)
            elif event.button == 5:  # Прокрутка вниз
                self.zoom = max(self.min_zoom, self.zoom - 0.1)

            # --- НАЧАЛО ЗАЖАТИЯ (ЛКМ - кнопка 1) ---
            elif event.button == 1:
                self.is_dragging = True
                self.has_moved_enough = False
                self.drag_start_mouse = mouse_pos
                self.drag_start_camera = (self.camera_x, self.camera_y)

        # --- ОТПУСКАНИЕ КНОПКИ МЫШИ ---
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                # Если мышь во время зажатия почти не двигалась, то это обычный одиночный клик!
                if not self.has_moved_enough:
                    self.handle_tile_click()

        # --- ДВИЖЕНИЕ МЫШИ (Перетаскивание) ---
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # ИСПРАВЛЕНИЕ: Вычитаем координаты раздельно, а не кортежами
                delta_x = mouse_pos[0] - self.drag_start_mouse[0]
                delta_y = mouse_pos[1] - self.drag_start_mouse[1]
                
                # Порог в 5 пикселей, чтобы мелкое дрожание руки не считалось перетаскиванием
                if abs(delta_x) > 5 or abs(delta_y) > 5:
                    self.has_moved_enough = True

                if self.has_moved_enough:
                    # Прибавляем разницу к стартовой позиции камеры
                    self.camera_x = self.drag_start_camera[0] + delta_x
                    self.camera_y = self.drag_start_camera[1] + delta_y



    def handle_tile_click(self):
        """Метод, который будет срабатывать при одиночном клике ЛКМ на клетку."""
        hx, hy = self.hovered_tile
        if hx != -1 and hy != -1:
            print(f"Вы кликнули на клетку фермы: ({hx}, {hy})")
            # Сюда мы добавим логику вспахивания земли или посадки

    def update(self):
        """Обновление логики игры."""
        mouse_pos = pygame.mouse.get_pos()
        # Распаковываем кортеж mouse_pos на отдельные переменные x и y
        mx, my = mouse_pos
        # Теперь передаем правильные одиночные координаты
        self.hovered_tile = self.isometric_to_cartesian(mx, my)

    def draw_farm(self):
        self.screen.fill((30, 30, 40))

        cur_w = TILE_WIDTH * self.zoom
        cur_h = TILE_HEIGHT * self.zoom

        # 1. Рисуем сетку земли
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = self.cartesian_to_isometric(x, y)
                
                points = [
                    (iso_x, iso_y),
                    (iso_x + cur_w // 2, iso_y + cur_h // 2),
                    (iso_x, iso_y + cur_h),
                    (iso_x - cur_w // 2, iso_y + cur_h // 2)
                ]
                
                color = GREEN if (x + y) % 2 == 0 else DARK_GREEN
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (50, 50, 50), points, 1)

        # 2. Рисуем подсветку клетки
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
