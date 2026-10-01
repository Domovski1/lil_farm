# main.py
import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import Menu, SettingsMenu  # Импортируем новый класс
from game import GameWorld

def main():
    pygame.init()
    
    # Флаги дисплея по умолчанию
    flags = pygame.DOUBLEBUF
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Мой Фермер (Изометрия)")
    clock = pygame.time.Clock()

    state = "MENU"
    
    menu = Menu(screen)
    settings_menu = SettingsMenu(screen) # Инициализируем настройки
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
                # Передаем события мыши в игровой мир для зума и перетаскивания карты
                world.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "MENU"

            elif state == "SETTINGS":
                # Передаем события в меню настроек
                settings_action = settings_menu.handle_event(event)
                
                if settings_action == "back" or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    state = "MENU"
                    
                elif settings_action == "toggle_fullscreen":
                    # Переключаем режим экрана Pygame на лету
                    if settings_menu.fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags | pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                        
                elif settings_action == "volume_changed":
                    # Тут в будущем будет управление громкостью микшера:
                    # pygame.mixer.music.set_volume(settings_menu.volume)
                    pass

        # Отрисовка
        if state == "MENU":
            menu.draw()
        elif state == "GAME":
            world.update()
            world.draw_farm()
        elif state == "SETTINGS":
            settings_menu.draw() # Рисуем наше проработанное меню

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
