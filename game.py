import pygame
import math
import random
import sys
import json
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()
pygame.display.set_caption("Space Hunt")

# Game constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
PLAYER_SIZE = 40
TREASURE_SIZE = 30
PLAYER_SPEED = 4
INDICATOR_SIZE = (80, 80)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
TRANSPARENT_BG = (0, 0, 0, 128)
GREY = (128, 128, 128)

BG_IMAGE = pygame.image.load('background.jpg')  # Add your image file
BG_IMAGE = pygame.transform.scale(BG_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))

class Player:
    def __init__(self, x, y, controls, image_path, compass_pos):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.controls = controls
        self.angle = 0
        self.compass_img = pygame.image.load('arrow.png').convert_alpha()
        self.compass_img = pygame.transform.scale(self.compass_img, (60, 60))
        self.compass_pos = compass_pos

    def move(self, keys_pressed, indicator_angle):
        dx, dy = 0, 0
        
    # Original controls
        if indicator_angle == 0:  # Normal
            if keys_pressed[self.controls['up']]: dy -= 1
            if keys_pressed[self.controls['down']]: dy += 1
            if keys_pressed[self.controls['left']]: dx -= 1
            if keys_pressed[self.controls['right']]: dx += 1
        elif indicator_angle == 180:  # Reversed
            if keys_pressed[self.controls['up']]: dy += 1
            if keys_pressed[self.controls['down']]: dy -= 1
            if keys_pressed[self.controls['left']]: dx += 1
            if keys_pressed[self.controls['right']]: dx -= 1
        elif indicator_angle == 90:  # Rotated left
            if keys_pressed[self.controls['up']]: dx -= 1
            if keys_pressed[self.controls['down']]: dx += 1
            if keys_pressed[self.controls['left']]: dy += 1
            if keys_pressed[self.controls['right']]: dy -= 1
        elif indicator_angle == 270:  # Rotated right
            if keys_pressed[self.controls['up']]: dx += 1
            if keys_pressed[self.controls['down']]: dx -= 1
            if keys_pressed[self.controls['left']]: dy -= 1
            if keys_pressed[self.controls['right']]: dy += 1

        if dx != 0 or dy != 0:
            self.angle = math.degrees(math.atan2(-dy, dx)) % 360
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            

        new_x = self.rect.centerx + dx * PLAYER_SPEED
        new_y = self.rect.centery + dy * PLAYER_SPEED
    
        if PLAYER_SIZE//2 < new_x < SCREEN_WIDTH - PLAYER_SIZE//2:
            self.rect.centerx = new_x
        if PLAYER_SIZE//2 < new_y < SCREEN_HEIGHT - PLAYER_SIZE//2:
            self.rect.centery = new_y

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def draw_compass(self, surface, treasure_pos, indicator_angle):
            dx = treasure_pos[0] - self.rect.centerx
            dy = treasure_pos[1] - self.rect.centery
            true_angle = math.degrees(math.atan2(-dy, dx))
            adjusted_angle = true_angle % 360
            rotated_arrow = pygame.transform.rotate(self.compass_img, adjusted_angle)
            arrow_rect = rotated_arrow.get_rect(center=self.compass_pos)
            surface.blit(rotated_arrow, arrow_rect)

class Treasure:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(50, SCREEN_WIDTH-50),
            random.randint(50, SCREEN_HEIGHT-50),
            TREASURE_SIZE, TREASURE_SIZE
        )
    
    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)
        inner_rect = self.rect.inflate(-8, -8)
        pygame.draw.rect(surface, NEON_PINK, inner_rect, 2)
        pygame.draw.line(surface, NEON_PINK, 
                        (self.rect.left + 5, self.rect.centery),
                        (self.rect.right - 5, self.rect.centery), 2)
        pygame.draw.line(surface, NEON_PINK,
                        (self.rect.centerx, self.rect.top + 5),
                        (self.rect.centerx, self.rect.bottom - 5), 2)

def draw_score(surface, scores):
    font = get_retro_font(46)

# Render each part of the text in its respective color
    text_p1 = font.render(f"P1: {scores[0]}", True, NEON_BLUE)
    text_p2 = font.render(f"P2: {scores[1]}", True, NEON_PINK)

# Create a background rectangle big enough for both parts
    score_width = text_p1.get_width() + text_p2.get_width() + 20  # Add spacing between P1 and P2
    score_height = text_p1.get_height()
    bg_rect = pygame.Rect(190, 10, score_width + 20, score_height + 20)  # Add padding

# Draw the background and border
    pygame.draw.rect(surface, BLACK, bg_rect)
    pygame.draw.rect(surface, NEON_BLUE, bg_rect, 2)

# Blit both parts onto the surface
    surface.blit(text_p1, (bg_rect.x + 10, bg_rect.y + 10))  # Position P1 with padding
    surface.blit(text_p2, (bg_rect.x + 10 + text_p1.get_width() + 20, bg_rect.y + 10))  # P2 after P1 with spacing


def get_retro_font(size):
    return pygame.font.Font("retro_font.ttf", size)

class Settings:
    def __init__(self):
        self.volume = 0.5
        self.random_direction = True
        self.load_settings()
        #self.hidden_treasure = False  


    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump({
                'volume': self.volume,
                'random_direction': self.random_direction,
                'hidden_treasure': self.hidden_treasure 
            }, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                data = json.load(f)
                self.volume = data.get('volume', 0.5)
                self.random_direction = data.get('random_direction', True)
                self.hidden_treasure = data.get('hidden_treasure', False) 
        except FileNotFoundError:
            self.save_settings()

class Button:
    def __init__(self, x, y, width, height, text, color=NEON_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = NEON_PINK
        self.is_hovered = False
        self.font = get_retro_font(50)
        self.original_color = color

    def draw(self, surface):
        border_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(surface, self.hover_color if self.is_hovered else self.color, 
                        self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, border_rect, 2, border_radius=8)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class RotatingIndicator:
    def __init__(self, settings):
        self.original_image = pygame.image.load('indicator.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, INDICATOR_SIZE)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.current_angle = 0
        self.settings = settings

    def random_rotate(self):
        if self.settings.random_direction:
            self.current_angle = random.choice([0, 90, 180, 270])
        else:
            self.current_angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.current_angle)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, 50))

class MainMenu:
    def __init__(self):
        self.start_button = Button(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-50, 300, 80, "START GAME")
        self.settings_button = Button(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2+80, 300, 80, "SETTINGS")
        self.title_font = get_retro_font(120)

    def draw(self, surface):
        surface.fill(BLACK)
        title = self.title_font.render("Space HUNT", True, NEON_BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        surface.blit(title, title_rect)
        pygame.draw.rect(surface, NEON_PINK, (0, 0, SCREEN_WIDTH, 10))
        pygame.draw.rect(surface, NEON_PINK, (0, SCREEN_HEIGHT-10, SCREEN_WIDTH, 10))
        self.start_button.draw(surface)
        self.settings_button.draw(surface)

class SettingsMenu:
    def __init__(self, settings):
        self.settings = settings
        self.back_button = Button(50, 50, 120, 60, "BACK")
        self.volume_slider = pygame.Rect(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-100, 300, 25)
        text_left_margin = SCREEN_WIDTH//2 - 200  # Starting position for text
        toggle_right_margin = SCREEN_WIDTH//2 + 200  # Position for toggles
        self.toggle_pos = (toggle_right_margin, SCREEN_HEIGHT//2-20)
        self.hidden_toggle_pos = (toggle_right_margin, SCREEN_HEIGHT//2+60)
        self.toggle_radius = 20
        self.text_pos = {
            'random': (text_left_margin, SCREEN_HEIGHT//2-20),
            'hidden': (text_left_margin, SCREEN_HEIGHT//2+60)
        }

    def draw(self, surface):
        surface.fill(BLACK)
        title = get_retro_font(70).render("SETTINGS", True, NEON_BLUE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        # Volume controls
        pygame.draw.rect(surface, WHITE, self.volume_slider, 2, border_radius=3)
        handle_x = self.volume_slider.x + (self.volume_slider.width * self.settings.volume)
        pygame.draw.circle(surface, NEON_PINK, (int(handle_x), self.volume_slider.centery), 15)
        volume_text = get_retro_font(50).render(f"VOLUME: {int(self.settings.volume*100)}%", True, WHITE)
        surface.blit(volume_text, (self.volume_slider.x, self.volume_slider.y-50))

        # Random rotation toggle and text
        toggle_color = NEON_PINK if self.settings.random_direction else GREY
        pygame.draw.circle(surface, toggle_color, self.toggle_pos, self.toggle_radius)
        pygame.draw.circle(surface, WHITE, self.toggle_pos, self.toggle_radius, 2)
        toggle_text = get_retro_font(46).render("RANDOM ROTATION   ", True, WHITE)
        text_rect = toggle_text.get_rect(midleft=self.text_pos['random'])
        surface.blit(toggle_text, text_rect)

        # Hidden treasure toggle and text
        toggle_color = NEON_PINK if self.settings.hidden_treasure else GREY
        pygame.draw.circle(surface, toggle_color, self.hidden_toggle_pos, self.toggle_radius)
        pygame.draw.circle(surface, WHITE, self.hidden_toggle_pos, self.toggle_radius, 2)
        toggle_text = get_retro_font(46).render("HIDDEN TREASURE   ", True, WHITE)
        text_rect = toggle_text.get_rect(midleft=self.text_pos['hidden'])
        surface.blit(toggle_text, text_rect)

        self.back_button.draw(surface)

    def handle_volume(self, pos):
        if self.volume_slider.collidepoint(pos):
            self.settings.volume = (pos[0] - self.volume_slider.x) / self.volume_slider.width
            self.settings.volume = max(0, min(1, self.settings.volume))
            mixer.music.set_volume(self.settings.volume)

    def handle_toggle(self, pos):
        distance = math.hypot(pos[0]-self.toggle_pos[0], pos[1]-self.toggle_pos[1])
        if distance <= self.toggle_radius:
            self.settings.random_direction = not self.settings.random_direction
            
        distance = math.hypot(pos[0]-self.hidden_toggle_pos[0], pos[1]-self.hidden_toggle_pos[1])
        if distance <= self.toggle_radius:
            self.settings.hidden_treasure = not self.settings.hidden_treasure

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        mixer.music.load('background_music.mp3')
        mixer.music.set_volume(self.settings.volume)
        mixer.music.play(-1)
        self.state = "MENU"
        self.main_menu = MainMenu()
        self.settings_menu = SettingsMenu(self.settings)
        self.reset_game()

    def reset_game(self):
        self.scores = [0, 0]
        self.indicator = RotatingIndicator(self.settings)
        self.players = [
            Player(100, 100, 
                  {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d},
                  'arrow_player1.png',
                  (100, 50)),
            Player(1500, 800,
                  {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT},
                  'arrow_player2.png',
                  (SCREEN_WIDTH-100, 50))
        ]
        self.treasure = Treasure()
        self.winner = None

    def new_round(self):
        self.indicator.random_rotate()
        self.treasure = Treasure()
        self.players[0].rect.center = (100, 100)
        self.players[1].rect.center = (1500, 800)

    def run(self):
        while True:
            if self.state == "MENU":
                self.handle_menu()
            elif self.state == "SETTINGS":
                self.handle_settings()
            elif self.state == "PLAYING":
                self.handle_gameplay()
            elif self.state == "END":
                self.handle_endgame()

    def handle_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if self.main_menu.start_button.handle_event(event):
                self.state = "PLAYING"
                self.new_round()
            if self.main_menu.settings_button.handle_event(event):
                self.state = "SETTINGS"
            self.main_menu.start_button.handle_event(event)
            self.main_menu.settings_button.handle_event(event)

        self.main_menu.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    def handle_settings(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.settings_menu.back_button.handle_event(event):
                    self.state = "MENU"
                else:
                    self.settings_menu.handle_toggle(event.pos)
                    self.settings_menu.handle_volume(event.pos)
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self.settings_menu.handle_volume(event.pos)
            self.settings_menu.back_button.handle_event(event)

        self.settings_menu.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    def handle_gameplay(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"  # Return to main menu
                    return  
        keys = pygame.key.get_pressed()
        self.screen.blit(BG_IMAGE, (0, 0)) 
        
        for player in self.players:
            player.move(keys, self.indicator.current_angle)
        
        for i, player in enumerate(self.players):
            if player.rect.colliderect(self.treasure.rect):
                self.winner = i + 1
                self.scores[i] += 1
                self.state = "END"
        
        # Only draw treasure if not hidden
        if not self.settings.hidden_treasure:
            self.treasure.draw(self.screen)
        
        self.screen.blit(self.indicator.image, self.indicator.rect)
        for player in self.players:
            player.draw(self.screen)
            player.draw_compass(self.screen, self.treasure.rect.center, self.indicator.current_angle)
        draw_score(self.screen, self.scores)
        pygame.display.flip()
        self.clock.tick(60)

    def handle_endgame(self):
        restart_btn = Button(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2+50, 300, 80, "PLAY AGAIN")
        menu_btn = Button(SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2+150, 300, 80, "MAIN MENU")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if restart_btn.handle_event(event):
                self.new_round()
                self.state = "PLAYING"
            if menu_btn.handle_event(event):
                self.state = "MENU"
            restart_btn.handle_event(event)
            menu_btn.handle_event(event)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(TRANSPARENT_BG)
        self.screen.blit(overlay, (0, 0))
        
        color = NEON_BLUE if self.winner == 1 else NEON_PINK
        win_text = get_retro_font(120).render(f"PLAYER {self.winner} WINS!", True, color)
        self.screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)))
        
        score_text = get_retro_font(60).render(f"SCORES: P1 - {self.scores[0]} / P2 - {self.scores[1]}", True, WHITE)
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        
        restart_btn.draw(self.screen)
        menu_btn.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    def quit_game(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()