import pygame
import random
import sys
import subprocess

pygame.init()

# --- Ablak ---
WIDTH, HEIGHT = 800, 600    # Ablak méretei (szélesség, magasság) pixelben
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Ablak megrajzolása
pygame.display.set_caption("Matematikai Quiz")  # Ablak neve

FONT_BIG = pygame.font.SysFont(None, 60)
FONT_MED = pygame.font.SysFont(None, 40)
CLOCK = pygame.time.Clock()

NUM_QUESTIONS = 10  # Kérdések száma
OPERATORS = ['+', '-', '*', '/']    # Használható műveletek

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
btn_new = Button(30, HEIGHT-80, 200, 50, "Új játék", (50,150,50), (70,200,70))          # Gombok elhejezkedése, szövege, színe
btn_exit = Button(WIDTH -230, HEIGHT-80, 200, 50, "Kilépés", (200,50,50), (255,70,70))
btn_return = Button(300, HEIGHT-80, 200, 50, "Vissza", (255,140,0), (255,180,50))


# --- Quiz függvények ---
def generate_question():
    op = random.choice(OPERATORS)   # Random művelet sorsolása
    a, b = random.randint(1, 12), random.randint(1, 12) # Random számok sorsolása 1-12-ig
    if op == '/':
        a = a * b  # biztosan osztható
    answer = eval(f"{a}{op}{b}")
    if op == '/':
        answer = int(answer)
    question = f"{a} {op} {b} = ?"
    return question, answer

def draw_question(q_text, user_input, score, question_num, time_left):
    bg_img = pygame.image.load('math.jpg')
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    WIN.blit(bg_img, (0, 0))
    pygame.draw.rect(WIN, (50,50,50), (0, 0, WIDTH, 40))

    # --- Hátralévő idő kirajzolása ---
    time_surface = FONT_MED.render(f"Hátralévő idő: {time_left:.1f} mp", True, (255, 80, 80))
    WIN.blit(time_surface, (WIDTH//2 - time_surface.get_width()//2, 10))

    # Kérdés
    question_surface = FONT_BIG.render(q_text, True, (255,255,255))
    WIN.blit(question_surface, (WIDTH//2 - question_surface.get_width()//2, HEIGHT//2.5))

    # Input
    input_surface = FONT_BIG.render(user_input, True, (255,255,255))
    WIN.blit(input_surface, (WIDTH//2 - input_surface.get_width()//2, HEIGHT//2))

    # Pontszám
    score_surface = FONT_MED.render(f"Pontszám: {score}", True, (255,255,0))
    WIN.blit(score_surface, (10, 10))

    # Számláló
    counter_surface = FONT_MED.render(f"Kérdés: {question_num}/{NUM_QUESTIONS}", True, (255,255,0))
    WIN.blit(counter_surface, (WIDTH - counter_surface.get_width() - 10, 10))

    # Gombok
    btn_new.draw(WIN)
    btn_exit.draw(WIN)
    btn_return.draw(WIN)

    pygame.display.update()

    
# --- Fő játék függvény ---
def play_quiz():
    score = 0
    question_count = 0
    user_input = ''
    question, answer = generate_question()
    run = True

    time_limit = 5        # másodperc / kérdés
    question_start = pygame.time.get_ticks()
    total_start = pygame.time.get_ticks()

    while run:
        CLOCK.tick(30)

        # --- idő számítása ---
        elapsed = (pygame.time.get_ticks() - question_start) / 1000
        time_left = max(0, time_limit - elapsed)

        # --- kérdés kirajzolása ---
        draw_question(question, user_input, score, question_count + 1, time_left)

        # --- idő lejárta ---
        if time_left <= 0:
            question_count += 1
            # ha elfogytak a kérdések → vége
            if question_count >= NUM_QUESTIONS:
                run = False
                break

            # új kérdés
            question, answer = generate_question()
            user_input = ''
            question_start = pygame.time.get_ticks()
            continue

        # --- események ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif btn_exit.is_clicked(event):
                pygame.quit()
                sys.exit()
            elif btn_return.is_clicked(event):
                pygame.quit()
                subprocess.run([sys.executable, "main_menu.py"])
                sys.exit()
            elif btn_new.is_clicked(event):
                return True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # ENTER → válasz leadása
                    if user_input.strip() != '' and int(user_input) == answer:
                        score += 1

                    question_count += 1
                    if question_count >= NUM_QUESTIONS:
                        run = False
                        break

                    question, answer = generate_question()
                    user_input = ''
                    question_start = pygame.time.get_ticks()

                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isdigit() or (event.unicode == '-' and user_input == ''):
                    user_input += event.unicode

    # --- Játék vége ---
    WIN.fill((0,0,0))

    # Pontszám
    end_text = FONT_BIG.render(f"Játék vége! Pontszám: {score}/{NUM_QUESTIONS}", True, (255,255,255))
    WIN.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//3 - end_text.get_height()//2))

    # Összes eltelt idő
    total_time_sec = (pygame.time.get_ticks() - total_start) / 1000
    total_surface = FONT_MED.render(f"Összes idő: {total_time_sec:.1f} mp", True, (255,255,255))
    WIN.blit(total_surface, (WIDTH//2 - total_surface.get_width()//2, HEIGHT//3 + end_text.get_height()))

    # Gombok
    btn_new.draw(WIN)
    btn_exit.draw(WIN)
    btn_return.draw(WIN)

    pygame.display.update()


    # --- gombnyomás várása ---
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif btn_exit.is_clicked(event):
                pygame.quit()
                sys.exit()
            elif btn_return.is_clicked(event):
                pygame.quit()
                subprocess.run([sys.executable, "main_menu.py"])
                sys.exit()
            elif btn_new.is_clicked(event):
                return True
        CLOCK.tick(30)

    return False


# --- Main loop ---
while True:
    new_game = play_quiz()
    if not new_game:
        break

pygame.quit()

sys.exit()
