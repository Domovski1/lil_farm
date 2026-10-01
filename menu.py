# menu.py
import pygame
import sys
from settings import WIDTH, HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY

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
