import pygame
import random
import sys
import subprocess

pygame.init()

# --- Ablak ---
WIDTH, HEIGHT = 800, 900
BOARD_HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FONT_MED = pygame.font.SysFont(None, 40)
pygame.display.set_caption("Memóriajáték – 26 lapos francia pakli")

# --- Gomb osztály ---
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, self.hover_color if is_hover else self.color, self.rect)
        txt = FONT_MED.render(self.text, True, (255,255,255))
        surface.blit(txt, (self.rect.x + (self.rect.width-txt.get_width())//2,
                           self.rect.y + (self.rect.height-txt.get_height())//2))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- Gombok ---
btn_new = Button(30, BOARD_HEIGHT + 20, 200, 50, "Új játék", (50,150,50), (70,200,70))
btn_exit = Button(WIDTH - 230, BOARD_HEIGHT + 20, 200, 50, "Kilépés", (200,50,50), (255,70,70))
btn_return = Button(WIDTH//2 - 100, BOARD_HEIGHT + 20, 200, 50, "Vissza", (255,140,0), (255,180,50))

# --- Táblaméret ---
ROWS, COLS = 5, 6
CARD_WIDTH = WIDTH // COLS - 10
CARD_HEIGHT = BOARD_HEIGHT // ROWS - 10

# --- Új játék indítása ---
def reset_board():
    global board, hidden, card_images, cards_files

    cards_files = ['A.png','2.png','3.png','4.png','5.png','6.png','7.png','8.png',
                   '9.png','10.png','J.png','Q.png','K.png'] * 2
    random.shuffle(cards_files)

    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    hidden = [[True for _ in range(COLS)] for _ in range(ROWS)]

    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            if idx < len(cards_files):
                board[r][c] = cards_files[idx]
                idx += 1

    card_images = {}
    for f in cards_files:
        img = pygame.image.load(f)
        img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
        card_images[f] = img


# --- Tábla rajzolása ---
def draw_board():
    WIN.fill((0,0,0))

    # Kártyák
    for r in range(ROWS):
        for c in range(COLS):
            x = c*(CARD_WIDTH+10)
            y = r*(CARD_HEIGHT+10)
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

            if board[r][c] is None:
                continue

            if hidden[r][c]:
                pygame.draw.rect(WIN, (200,200,200), rect)
            else:
                WIN.blit(card_images[board[r][c]], (x, y))

    # Gombok sávja
    pygame.draw.rect(WIN, (50,50,50), (0, BOARD_HEIGHT, WIDTH, HEIGHT-BOARD_HEIGHT))

    btn_new.draw(WIN)
    btn_exit.draw(WIN)
    btn_return.draw(WIN)

    pygame.display.update()


# --- Flip animáció ---
def flip_card_anim(row, col):
    x = col*(CARD_WIDTH+10)
    y = row*(CARD_HEIGHT+10)

    for scale in range(CARD_WIDTH, 0, -10):
        draw_board()
        rect = pygame.Rect(x + (CARD_WIDTH-scale)//2, y, scale, CARD_HEIGHT)
        pygame.draw.rect(WIN, (200,200,200), rect)
        pygame.display.update()
        pygame.time.delay(20)

    for scale in range(0, CARD_WIDTH+1, 10):
        draw_board()
        img = pygame.transform.scale(card_images[board[row][col]], (scale, CARD_HEIGHT))
        WIN.blit(img, (x + (CARD_WIDTH-scale)//2, y))
        pygame.display.update()
        pygame.time.delay(20)

# --- Párok ellenőrzése ---
def all_matched():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] is not None and hidden[r][c]:
                return False
    return True


# --- Main loop ---
def main_game():
    reset_board()
    first_flip = None
    run = True

    while run:
        draw_board()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                # Új játék gomb
                if btn_new.is_clicked(event):
                    reset_board()
                    first_flip = None
                    continue

                # Kilépés
                if btn_exit.is_clicked(event):
                    pygame.quit()
                    sys.exit()

                # Vissza főmenübe
                if btn_return.is_clicked(event):
                    pygame.quit()
                    subprocess.run([sys.executable, "main_menu.py"])
                    sys.exit()

                # Kártya kattintás
                x, y = pygame.mouse.get_pos()
                if y > BOARD_HEIGHT:
                    continue

                row = y // (CARD_HEIGHT+10)
                col = x // (CARD_WIDTH+10)

                if row >= ROWS or col >= COLS:
                    continue

                if board[row][col] is None or not hidden[row][col]:
                    continue

                flip_card_anim(row, col)
                hidden[row][col] = False

                if first_flip is None:
                    first_flip = (row, col)
                else:
                    r1, c1 = first_flip
                    r2, c2 = row, col
                    pygame.time.delay(500)

                    if board[r1][c1] != board[r2][c2]:
                        hidden[r1][c1] = True
                        hidden[r2][c2] = True

                    first_flip = None

        if all_matched():
            print("Gratulálok! Minden pár megtalálva! 🏆")
            run = False


main_game()
pygame.quit()
