import pygame
import sys
import subprocess

pygame.init()

# --- Ablak és óra ---
WIDTH, HEIGHT = 900, 800
MENU_HEIGHT = 80
GAME_HEIGHT = HEIGHT - MENU_HEIGHT
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kocka Kaland")
CLOCK = pygame.time.Clock()

# --- Színek ---
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,50,50)
GREEN = (50,200,50)
BLUE = (50,150,255)
ORANGE = (255,170,60)
GRAY = (120,120,120)
DARK_BG = (30,30,30)

# --- Betűtípus ---
FONT = pygame.font.SysFont(None, 50)

# --- Gomb osztály ---
class Button:
    def __init__(self, x, y, w, h, text, color, hover):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover
    def draw(self, surf):
        mouse = pygame.mouse.get_pos()
        col = self.hover if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surf, col, self.rect)
        txt = FONT.render(self.text, True, WHITE)
        surf.blit(txt, (self.rect.x + (self.rect.width-txt.get_width())//2,
                        self.rect.y + (self.rect.height-txt.get_height())//2))
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- Gombok ---
btn_new = Button(20, GAME_HEIGHT + 15, 200, 50, "Új játék", (50,150,50), (70,200,70))
btn_back = Button(WIDTH//2 - 100, GAME_HEIGHT + 15, 200, 50, "Vissza", (255,140,0), (255,170,40))
btn_exit = Button(WIDTH - 220, GAME_HEIGHT + 15, 200, 50, "Kilépés", (200,50,50), (255,70,70))

# --- Parallax háttér ---
bg_layers = [
    {"color": (10,10,40), "speed": 0.2, "rects":[pygame.Rect(0,0,3000,600)]},
    {"color": (20,20,70), "speed": 0.5, "rects":[pygame.Rect(0,0,3000,400)]},
    {"color": (40,40,100), "speed": 0.8, "rects":[pygame.Rect(0,0,3000,200)]},
]

CAMERA_BASE_ZOOM = 1.0
CAMERA_MAX_ZOOM = 1.3
CAMERA_ZOOM_SPEED = 0.05
camera_zoom = CAMERA_BASE_ZOOM
camera_x = 0

# --- Szintek ---
LEVELS = [
    {
        "platforms": [pygame.Rect(0, 550, 900, 50), pygame.Rect(200,450,200,20), pygame.Rect(450,350,200,20), pygame.Rect(700,270,150,20)],
        "spikes": [pygame.Rect(350,530,50,20), pygame.Rect(400,530,50,20), pygame.Rect(450,530,50,20), pygame.Rect(500,530,50,20), pygame.Rect(550,530,50,20), pygame.Rect(600,530,50,20), pygame.Rect(650,530,50,20), pygame.Rect(700,530,50,20), pygame.Rect(750,530,50,20), pygame.Rect(800,530,50,20), pygame.Rect(850,530,50,20)],
        "enemy": pygame.Rect(500,310,40,40),
        "enemy_zone": (450,650),
        "goal": pygame.Rect(750,220,50,50),
        "player_start": (100,300),
    },
    {
        "platforms": [pygame.Rect(0,550,900,50), pygame.Rect(150,500,200,20), pygame.Rect(400,400,150,20), pygame.Rect(650,300,200,20), pygame.Rect(300,200,200,20)],
        "spikes": [pygame.Rect(350,530,50,20), pygame.Rect(400,530,50,20), pygame.Rect(450,530,50,20), pygame.Rect(500,530,50,20), pygame.Rect(550,530,50,20), pygame.Rect(600,530,50,20), pygame.Rect(650,530,50,20), pygame.Rect(700,530,50,20), pygame.Rect(750,530,50,20), pygame.Rect(800,530,50,20), pygame.Rect(850,530,50,20)],
        "enemy": pygame.Rect(650,260,40,40),
        "enemy_zone": (630,850),
        "goal": pygame.Rect(350,150,50,50),
        "player_start": (50,300),
    },
    {
        "platforms": [pygame.Rect(0,550,900,50), pygame.Rect(150,490,250,20), pygame.Rect(500,400,250,20), pygame.Rect(200,300,150,20), pygame.Rect(500,200,200,20)],
        "spikes": [pygame.Rect(350,530,50,20), pygame.Rect(400,530,50,20), pygame.Rect(450,530,50,20), pygame.Rect(500,530,50,20), pygame.Rect(550,530,50,20), pygame.Rect(600,530,50,20), pygame.Rect(650,530,50,20), pygame.Rect(700,530,50,20), pygame.Rect(750,530,50,20), pygame.Rect(800,530,50,20), pygame.Rect(850,530,50,20)],
        "enemy": pygame.Rect(200,260,40,40),
        "enemy_zone": (150,330),
        "goal": pygame.Rect(650,150,50,50),
        "player_start": (70,300),
    }
]

# --- Játékos ---
player = pygame.Rect(100,300,50,50)
player_vel_y = 0
GRAVITY = 0.6
PLAYER_SPEED = 5
on_ground = False

def draw(level):
    global camera_x, camera_zoom
    # Kamera követés
    camera_x = player.x - WIDTH//2
    camera_x = max(0, camera_x)

    WIN.fill(DARK_BG)

    # Parallax
    for layer in bg_layers:
        for rect in layer["rects"]:
            parallax_x = int(rect.x - camera_x*layer["speed"])
            scaled_rect = pygame.Rect(parallax_x, rect.y, int(rect.width*camera_zoom), int(rect.height*camera_zoom))
            pygame.draw.rect(WIN, layer["color"], scaled_rect)

    # Platformok
    for p in level["platforms"]:
        r = pygame.Rect((p.x - camera_x)*camera_zoom, p.y*camera_zoom, p.width*camera_zoom, p.height*camera_zoom)
        pygame.draw.rect(WIN, GRAY, r)

    # Tüskék
    for s in level["spikes"]:
        points = [(s.x - camera_x, s.bottom),(s.x + s.width//2 - camera_x, s.top),(s.right - camera_x, s.bottom)]
        points = [(x*camera_zoom, y*camera_zoom) for x,y in points]
        pygame.draw.polygon(WIN, RED, points)

    # Ellenség
    enemy_rect = pygame.Rect((level["enemy"].x - camera_x)*camera_zoom, level["enemy"].y*camera_zoom,
                             level["enemy"].width*camera_zoom, level["enemy"].height*camera_zoom)
    pygame.draw.rect(WIN, ORANGE, enemy_rect)

    # Cél
    goal_rect = pygame.Rect((level["goal"].x - camera_x)*camera_zoom, level["goal"].y*camera_zoom,
                             level["goal"].width*camera_zoom, level["goal"].height*camera_zoom)
    pygame.draw.rect(WIN, GREEN, goal_rect)

    # Játékos
    pygame.draw.rect(WIN, BLUE, pygame.Rect((player.x - camera_x)*camera_zoom, player.y*camera_zoom,
                                            player.width*camera_zoom, player.height*camera_zoom))

    # Menü
    pygame.draw.rect(WIN, (45,45,45), (0,GAME_HEIGHT,WIDTH,MENU_HEIGHT))
    btn_new.draw(WIN); btn_back.draw(WIN); btn_exit.draw(WIN)
    pygame.display.update()

def level_cleared(text):
    label = FONT.render(text, True, WHITE)
    WIN.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - 50))
    pygame.display.update()
    pygame.time.delay(1500)

def play_level(level_index):
    global player, player_vel_y, on_ground, camera_zoom
    level = LEVELS[level_index]
    player.x, player.y = level["player_start"]
    player_vel_y = 0
    on_ground = False

    enemy = level["enemy"]
    enemy_min, enemy_max = level["enemy_zone"]
    enemy_dir = 2

    run = True
    while run:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # --- Gombok ---
            if btn_new.is_clicked(event):
                main()
                return
            if btn_back.is_clicked(event):
                pygame.quit()
                subprocess.run([sys.executable, "main_menu.py"])
                sys.exit()
            if btn_exit.is_clicked(event):
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        # Mozgás
        if keys[pygame.K_LEFT]: player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]: player.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = -12
            on_ground = False

        # Gravitáció
        player_vel_y += GRAVITY
        player.y += player_vel_y

        # Platform ütközés
        on_ground = False
        for p in level["platforms"]:
            if player.colliderect(p) and player_vel_y >=0:
                player.bottom = p.top
                player_vel_y = 0
                on_ground = True

        # Tüskék
        for s in level["spikes"]:
            if player.colliderect(s):
                level_cleared("MEGHALTÁL!")
                main()

        # Ellenség mozgás
        enemy.x += enemy_dir
        if enemy.x < enemy_min or enemy.right > enemy_max: enemy_dir*=-1
        if player.colliderect(enemy):
            level_cleared("ELKAPTAK!")
            main()

        # Leesés
        if player.y > HEIGHT:
            level_cleared("LEESTÉL!")
            main()

        # Kijárat
        if player.colliderect(level["goal"]):
            return True

        # Kamera zoom
        speed = abs(PLAYER_SPEED)
        target_zoom = CAMERA_BASE_ZOOM + 0.2
        camera_zoom += (target_zoom - camera_zoom) * CAMERA_ZOOM_SPEED

        draw(level)

def main():
    for i in range(3):
        completed = play_level(i)
        if not completed:
            return main()
        else:
            level_cleared(f"{i+1}. SZINT KÉSZ!")
    main()


main()
