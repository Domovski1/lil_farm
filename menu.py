# menu.py
import pygame
import sys
from settings import WIDTH, HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY, GREEN

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
        
        # Состояния настроек (подгружаем базовые)
        self.volume = 0.5
        self.fullscreen = False
        
        # Разметка для слайдера громкости
        self.slider_rect = pygame.Rect(WIDTH // 2 - 100, 300, 200, 10)
        self.slider_thumb_radius = 12
        self.is_dragging_slider = False
        
        # Разметка для чекбокса полноэкранного режима
        self.checkbox_rect = pygame.Rect(WIDTH // 2 + 50, 400, 30, 30)
        
        # Кнопка Назад
        self.back_rect = pygame.Rect(WIDTH // 2 - 100, 550, 200, 50)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Заголовок
        title_surface = self.title_font.render("НАСТРОЙКИ", True, WHITE)
        self.screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 100))
        
        # 1. Отрисовка слайдера громкости
        vol_label = self.font.render(f"Громкость звука: {int(self.volume * 100)}%", True, WHITE)
        self.screen.blit(vol_label, (WIDTH // 2 - 100, 250))
        
        pygame.draw.rect(self.screen, GRAY, self.slider_rect, border_radius=5)
        # Вычисляем положение ползунка на основе текущей громкости
        thumb_x = self.slider_rect.x + int(self.volume * self.slider_rect.width)
        thumb_y = self.slider_rect.centery
        pygame.draw.circle(self.screen, LIGHT_GRAY, (thumb_x, thumb_y), self.slider_thumb_radius)
        
        # 2. Отрисовка чекбокса Полноэкранный режим
        fs_label = self.font.render("Полноэкранный режим:", True, WHITE)
        self.screen.blit(fs_label, (WIDTH // 2 - 200, 400))
        
        pygame.draw.rect(self.screen, GRAY, self.checkbox_rect, border_radius=5)
        if self.fullscreen:
            # Рисуем внутренний зеленый квадрат, если включено
            inner_rect = self.checkbox_rect.inflate(-10, -10)
            pygame.draw.rect(self.screen, GREEN, inner_rect, border_radius=3)
            
        # 3. Кнопка "Назад"
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_rect.collidepoint(mouse_pos)
        button_color = LIGHT_GRAY if is_hovered else GRAY
        pygame.draw.rect(self.screen, button_color, self.back_rect, border_radius=5)
        
        back_label = self.font.render("Назад", True, BLACK if is_hovered else WHITE)
        self.screen.blit(back_label, (self.back_rect.centerx - back_label.get_width() // 2, 
                                      self.back_rect.centery - back_label.get_height() // 2))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Нажатие на кнопку Назад
            if self.back_rect.collidepoint(mouse_pos):
                return "back"
                
            # Проверка клика по чекбоксу
            if self.checkbox_rect.collidepoint(mouse_pos):
                self.fullscreen = not self.fullscreen
                return "toggle_fullscreen"
                
            # Проверка клика по слайдеру громкости
            # Расширим зону клика вокруг ползунка для удобства
            thumb_x = self.slider_rect.x + int(self.volume * self.slider_rect.width)
            thumb_y = self.slider_rect.centery
            distance = ((mouse_pos[0] - thumb_x)**2 + (mouse_pos[1] - thumb_y)**2)**0.5
            if distance <= self.slider_thumb_radius or self.slider_rect.collidepoint(mouse_pos):
                self.is_dragging_slider = True
                self.update_slider_volume(mouse_pos[0])
                return "volume_changed"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging_slider = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_slider:
                self.update_slider_volume(mouse_pos[0])
                return "volume_changed"
                
        return None

    def update_slider_volume(self, mouse_x):
        # Ограничиваем движение мыши рамками слайдера
        relative_x = max(0, min(mouse_x - self.slider_rect.x, self.slider_rect.width))
        self.volume = relative_x / self.slider_rect.width


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)
        self.options = ["Играть", "Настройки", "Выход"]
        self.selected_index = 0

    def draw(self):
        self.screen.fill(BLACK)
        
        # Название игры
        title_font = pygame.font.SysFont("Arial", 60, bold=True)
        title_surface = title_font.render("МОЙ ФЕРМЕР", True, WHITE)
        self.screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 150))

        # Отрисовка пунктов меню
        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(self.options):
            # Проверяем наведение мыши для подсветки
            rect = pygame.Rect(WIDTH // 2 - 150, 320 + i * 80, 300, 50)
            is_hovered = rect.collidepoint(mouse_pos)
            
            color = LIGHT_GRAY if is_hovered else GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            text_surface = self.font.render(option, True, BLACK if is_hovered else WHITE)
            self.screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                rect = pygame.Rect(WIDTH // 2 - 150, 320 + i * 80, 300, 50)
                if rect.collidepoint(mouse_pos):
                    return option.lower()
        return None


