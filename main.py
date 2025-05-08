import pygame
import sys
import random

pygame.init()

# --- Fenster & Clock ---
WIDTH, HEIGHT = 2560, 1440
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room 2D")
clock = pygame.time.Clock()

# --- Farben ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Fonts ---
font = pygame.font.Font(None, 36)

# --- Assets ---
room_background = pygame.image.load("assets/backgrounds/room1.png")

# --- Player ---
player_img = pygame.image.load("assets/characters/player.png")
player_img = pygame.transform.scale(player_img, (150, 120))
player_rect = player_img.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT - 100)

# --- Kabel Farben und Bilder ---
COLORS = ["purple", "ping", "green", "blue", "yellow", "red"]
COLOR_RGB = {
    "purple": (128, 0, 128),
    "ping": (255, 105, 180),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "red": (255, 0, 0)
}
IMAGE_FILES = {
    "purple": "wirep1.png",
    "ping": "wirep2.png",
    "green": "wireg.png",
    "blue": "wireb.png",
    "yellow": "wirey.png",
    "red": "wirer.png"
}

wire_images = {}
for color in COLORS:
    img = pygame.image.load(f"assets/backgrounds/{IMAGE_FILES[color]}")
    wire_images[color] = pygame.transform.scale(img, (175, 175))

# --- Kabelpositionen dynamisch vorbereiten ---
def generate_wire_positions():
    left = []
    right = []

    left_colors = COLORS.copy()
    right_colors = COLORS.copy()
    random.shuffle(left_colors)
    random.shuffle(right_colors)

    gap = HEIGHT // (len(COLORS) + 1)

    for idx, color in enumerate(left_colors):
        y = gap * (idx + 1)
        left.append({"color": color, "pos": (150, y)})

    for idx, color in enumerate(right_colors):
        y = gap * (idx + 1)
        right.append({"color": color, "pos": (WIDTH - 150, y)})

    return left, right

left_positions, right_positions = generate_wire_positions()

# --- Verbindungen ---
connections = []
selected_left = None
completed_pairs = []

# --- Game State ---
in_menu = True
in_room = False
minigame_active = False
minigame_won = False

def reset_minigame():
    global left_positions, right_positions, completed_pairs, selected_left, minigame_won
    left_positions, right_positions = generate_wire_positions()
    complete_pairs = []
    selected_left = None
    minigame_won = False

# --- Funktionen ---

def draw_text(text, x, y, center=False):
    t = font.render(text, True, WHITE)
    rect = t.get_rect(center=(x, y)) if center else t.get_rect(topleft=(x, y))
    screen.blit(t, rect)

def main_menu():
    screen.fill(BLACK)
    draw_text("ESCAPE ROOM 2D", WIDTH // 2, 100, center=True)
    draw_text("1 - Spiel starten", WIDTH // 2, 200, center=True)
    draw_text("2 - Beenden", WIDTH // 2, 250, center=True)
    pygame.display.flip()

def room_logic():
    screen.blit(room_background, (0, 0))
    screen.blit(player_img, player_rect)
    draw_text("Drücke E um das Kabel-Minispiel zu starten.", WIDTH // 2, 50, center=True)

def minigame_wires():
    screen.fill(BLACK)
    draw_text("Verbinde die Kabel!", WIDTH // 2, 50, center=True)

    # Kabelenden zeichnen
    for left in left_positions:
        color = left["color"]
        pos = left["pos"]
        screen.blit(wire_images[color], (pos[0] - 20, pos[1] - 20))

    for right in right_positions:
        color = right["color"]
        pos = right["pos"]
        screen.blit(wire_images[color], (pos[0] - 20, pos[1] - 20))

    # Verbindungen zeichnen
    for pair in completed_pairs:
        pos_left, pos_right, color = pair
        pygame.draw.line(screen, COLOR_RGB[color], pos_left, pos_right, 5)

    # Aktuelle Auswahl
    if selected_left:
        pygame.draw.circle(screen, (0, 255, 0), selected_left["pos"], 25, 3)

def get_clicked_cable(mouse_pos, side):
    positions = left_positions if side == "left" else right_positions
    for item in positions:
        pos = item["pos"]
        rect = pygame.Rect(pos[0] - 20, pos[1] - 20, 40, 40)
        if rect.collidepoint(mouse_pos):
            return item
    return None

def check_completion():
    return len(completed_pairs) == len(COLORS)

# --- Hauptloop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if in_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    in_menu = False
                    in_room = True
                elif event.key == pygame.K_2:
                    pygame.quit()
                    sys.exit()

        elif in_room:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    in_room = False
                    minigame_active = True
                elif event.key == pygame.K_ESCAPE:
                    in_room = False
                    in_menu = True
                    player_rect.center = (WIDTH // 2, HEIGHT // - 100)
                    reset_minigame()


        elif minigame_active and not minigame_won:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    minigame_active = False

                    in_menu = True

                    player_rect.center = (WIDTH // 2, HEIGHT - 100)

                    reset_minigame()


            elif event.type == pygame.MOUSEBUTTONDOWN:

                if not selected_left:

                    clicked = get_clicked_cable(event.pos, "left")

                    if clicked and clicked["pos"] not in [pair[0] for pair in completed_pairs]:
                        selected_left = clicked

                else:

                    clicked = get_clicked_cable(event.pos, "right")

                    if clicked and clicked["pos"] not in [pair[1] for pair in completed_pairs]:

                        if clicked["color"] == selected_left["color"]:

                            completed_pairs.append((selected_left["pos"], clicked["pos"], clicked["color"]))

                            if check_completion():
                                minigame_won = True

                        selected_left = None


        # Neustarten mit R im Minigame wenn gewonnen
        elif minigame_won:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    left_positions, right_positions = generate_wire_positions()
                    completed_pairs = []
                    selected_left = None
                    minigame_won = False
                elif event.key == pygame.K_ESCAPE:
                    minigame_active = False
                    in_menu = True
                    player_rect.center = (WIDTH // 2, HEIGHT - 100)
                    reset_minigame()

    # --- Zeichnen ---
    if in_menu:
        main_menu()

    elif in_room:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_rect.y -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_rect.y += 5

        room_logic()

    elif minigame_active and not minigame_won:
        minigame_wires()

    elif minigame_won:
        screen.fill(BLACK)
        draw_text("Alle Kabel verbunden! Du bist frei!", WIDTH // 2, HEIGHT // 2, center=True)
        draw_text("Drücke R zum Neustart.", WIDTH // 2, HEIGHT // 2 + 50, center=True)

    pygame.display.flip()
    clock.tick(60)
