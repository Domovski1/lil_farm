# main.py
import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import Menu
from game import GameWorld

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Мой Фермер (Изометрия)")
    clock = pygame.time.Clock()

    # Состояния игры
    state = "MENU" # Возможные: MENU, GAME, SETTINGS
    
    menu = Menu(screen)
    world = GameWorld(screen)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "MENU":
                action = menu.handle_event(event)
                if action == "играть":
                    state = "GAME"
                elif action == "настройки":
                    state = "SETTINGS"
                elif action == "выход":
                    pygame.quit()
                    sys.exit()
            
            elif state == "GAME":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "MENU" # Возврат в меню по кнопке ESC

            elif state == "SETTINGS":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "MENU"

        # Отрисовка и обновление в зависимости от состояния
        if state == "MENU":
            menu.draw()
        elif state == "GAME":
            world.update()
            world.draw_farm()
        elif state == "SETTINGS":
            # Заглушка для экрана настроек
            screen.fill((40, 40, 60))
            font = pygame.font.SysFont("Arial", 30)
            text = font.render("Экран настроек (Нажмите ESC для выхода)", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
