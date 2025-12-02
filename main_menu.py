import pygame
import sys
import subprocess

pygame.init()  

# --- Ablak ---
WIDTH, HEIGHT = 800, 600    # Ablak méretei(szélesség, hosszúság) pixelben
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Ablak megrajzolása méretek alapján
pygame.display.set_caption("Menu")  # Ablak neve

FONT_BIG = pygame.font.SysFont(None, 60)
FONT_MED = pygame.font.SysFont(None, 40)
CLOCK = pygame.time.Clock()

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
btn_quiz = Button(200, 150, 400, 70, "Matematikai Quiz", (50,150,50), (70,200,70))  # Gombok elhejezkedése, szövege, színe
btn_memory = Button(200, 250, 400, 70, "Memóriajáték", (50,50,200), (70,70,255))
btn_platform = Button(200, 350, 400, 70, "Platformer", (255,140,0), (255,180,50))
btn_exit = Button(200, 450, 400, 70, "Kilépés", (200,50,50), (255,70,70))

# --- Főmenü ---
def main_menu():
    while True:
        bg_img = pygame.image.load('hq720.jpg') # Háttérkép betöltése
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))    # Háttérkép igazítása az ablak méreteihez
        WIN.blit(bg_img, (0, 0))    # Háttérkép megrajzolása
        title = FONT_BIG.render("Válassz játékot", True, (255,255,255)) # Ablak felírata, színe
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        btn_quiz.draw(WIN)  # Gombok megrajzolása
        btn_memory.draw(WIN)
        btn_platform.draw(WIN)
        btn_exit.draw(WIN)
        pygame.display.update() # Ablak frissítése

        for event in pygame.event.get():    # Gombok figyelése (rákattintott e a felhasználó)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif btn_quiz.is_clicked(event):
                pygame.quit()  # bezárjuk a főmenü ablakot
                subprocess.run([sys.executable, "matek_quiz.py"])
                sys.exit()
            elif btn_memory.is_clicked(event):
                pygame.quit()  # bezárjuk a főmenü ablakot
                subprocess.run([sys.executable, "memoriajatek.py"])
                sys.exit()
            elif btn_platform.is_clicked(event):
                pygame.quit()  # bezárjuk a főmenü ablakot
                subprocess.run([sys.executable, "platformer.py"])
                sys.exit()
            elif btn_exit.is_clicked(event):
                pygame.quit()
                sys.exit()
        CLOCK.tick(30)

# --- Fő program ---
if __name__ == "__main__":
    main_menu()

