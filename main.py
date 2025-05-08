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
backgrounds = {
    1: pygame.image.load("assets/backgrounds/room1.png"),
    2: pygame.image.load("assets/backgrounds/room2.png"),
    3: pygame.image.load("assets/backgrounds/room3.png")
}

# --- Player ---
player_img = pygame.image.load("assets/characters/player.png")
player_img = pygame.transform.scale(player_img, (150, 120))
player_rect = player_img.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT - 100)

# --- Kabel Farben und Bilder ---
COLORS = ["purple", "pink", "green", "blue", "yellow", "red"]
COLOR_RGB = {
    "purple": (128, 0, 128),
    "pink": (255, 105, 180),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "red": (255, 0, 0)
}
IMAGE_FILES = {
    "purple": "wirep1.png",
    "pink": "wirep2.png",
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
completed_pairs = []
selected_left = None

# --- Game State ---
in_menu = True
in_room = False
minigame_active = False
minigame_won = False
final_screen = False

room_number = 1
popup_active = False
input_code = ""
correct_code = "826"
code_entered = False

room1_completed = False
room2_completed = False
room3_completed = False

# --- Captcha Minigame Variablen ---
captcha_list = ["Xy12Ab", "pYth0n", "Mavis25", "M3talkill3r", "Raum3Go", "KackGam3"]
current_captcha = ""
captcha_input = ""
captcha_solved = 0
captcha_needed = 3

def reset_minigame():
    global left_positions, right_positions, completed_pairs, selected_left, minigame_won
    left_positions, right_positions = generate_wire_positions()
    completed_pairs = []
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
    draw_text("1 - Raum 1 starten", WIDTH // 2, 200, center=True)
    draw_text("2 - Raum 2 starten", WIDTH // 2, 250, center=True)
    draw_text("3 - Raum 3 starten", WIDTH // 2, 300, center=True)
    draw_text("ESC - Beenden", WIDTH // 2, 350, center=True)
    pygame.display.flip()

def room_logic():
    screen.blit(backgrounds[room_number], (0, 0))
    screen.blit(player_img, player_rect)
    draw_text("Drücke E für Aktion im Raum.", WIDTH // 2, 50, center=True)

def minigame_wires():
    screen.fill(BLACK)
    draw_text("Verbinde die Kabel!", WIDTH // 2, 50, center=True)
    for left in left_positions:
        color = left["color"]
        pos = left["pos"]
        screen.blit(wire_images[color], (pos[0] - 87, pos[1] - 87))
    for right in right_positions:
        color = right["color"]
        pos = right["pos"]
        screen.blit(wire_images[color], (pos[0] - 87, pos[1] - 87))
    for pair in completed_pairs:
        pos_left, pos_right, color = pair
        pygame.draw.line(screen, COLOR_RGB[color], pos_left, pos_right, 5)
    if selected_left:
        pygame.draw.circle(screen, (0, 255, 0), selected_left["pos"], 25, 3)

def get_clicked_cable(mouse_pos, side):
    positions = left_positions if side == "left" else right_positions
    for item in positions:
        pos = item["pos"]
        rect = pygame.Rect(pos[0] - 87, pos[1] - 87, 175, 175)
        if rect.collidepoint(mouse_pos):
            return item
    return None

def check_completion():
    return len(completed_pairs) == len(COLORS)

def draw_code_popup():
    pygame.draw.rect(screen, (30, 30, 30), (WIDTH // 2 - 250, HEIGHT // 2 - 120, 500, 240))
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 250, HEIGHT // 2 - 120, 500, 240), 2)
    draw_text("Zahlenrätsel – gib den 3-stelligen Code ein:", WIDTH // 2, HEIGHT // 2 - 60, center=True)
    draw_text(input_code, WIDTH // 2, HEIGHT // 2, center=True)

def draw_captcha_popup():
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH // 2 - 350, HEIGHT // 2 - 150, 700, 300))
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 350, HEIGHT // 2 - 150, 700, 300), 2)
    if captcha_solved < captcha_needed:
        draw_text(f"Captcha {captcha_solved + 1}/{captcha_needed}", WIDTH // 2, HEIGHT // 2 - 100, center=True)
        draw_text(f"Gib ein: {current_captcha}", WIDTH // 2, HEIGHT // 2 - 40, center=True)
        draw_text(f"Deine Eingabe: {captcha_input}", WIDTH // 2, HEIGHT // 2 + 20, center=True)
    else:
        draw_text("Captcha bestanden! Raum gelöst!", WIDTH // 2, HEIGHT // 2, center=True)

def check_all_completed():
    return room1_completed and room2_completed and room3_completed

# --- Hauptloop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if final_screen:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if in_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    in_menu = False
                    in_room = True
                    room_number = 1
                elif event.key == pygame.K_2:
                    in_menu = False
                    in_room = True
                    room_number = 2
                elif event.key == pygame.K_3:
                    in_menu = False
                    in_room = True
                    room_number = 3
                    if captcha_solved < captcha_needed:
                        popup_active = True
                        captcha_input = ""
                        current_captcha = random.choice(captcha_list)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        elif in_room:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if room_number == 1 and not room1_completed:
                        in_room = False
                        minigame_active = True
                    elif room_number == 2 and not room2_completed:
                        popup_active = True
                        input_code = ""
                    elif room_number == 3 and not room3_completed:
                        if captcha_solved < captcha_needed:
                            popup_active = True
                            captcha_input = ""
                            current_captcha = random.choice(captcha_list)
                elif event.key == pygame.K_ESCAPE:
                    in_room = False
                    in_menu = True
                    room_number = 1
                    player_rect.center = (WIDTH // 2, HEIGHT - 100)
                    reset_minigame()

        if popup_active and room_number == 2:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_code == correct_code:
                        popup_active = False
                        code_entered = True
                        room2_completed = True
                        if check_all_completed():
                            final_screen = True
                    elif event.key == pygame.K_BACKSPACE:
                        input_code = input_code[:-1]
                elif event.unicode.isdigit() and len(input_code) < 3:
                    input_code += event.unicode

        elif popup_active and room_number == 3:
            if captcha_solved >= captcha_needed:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    popup_active = False
                    room3_completed = True
                    if check_all_completed():
                        final_screen = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if captcha_input == current_captcha:
                            captcha_solved += 1
                            if captcha_solved < captcha_needed:
                                captcha_input = ""
                                current_captcha = random.choice(captcha_list)
                            else:
                                captcha_input = ""
                                room3_completed = True
                                popup_active = False
                                if check_all_completed():
                                    final_screen = True
                        else:
                            captcha_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        captcha_input = captcha_input[:-1]
                    elif len(event.unicode) > 0 and len(captcha_input) < 20:
                        captcha_input += event.unicode

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

        elif minigame_won:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    minigame_active = False
                    in_room = True
                    room1_completed = True
                    if check_all_completed():
                        final_screen = True
                elif event.key == pygame.K_r:
                    reset_minigame()
                elif event.key == pygame.K_ESCAPE:
                    minigame_active = False
                    in_menu = True
                    reset_minigame()

    # --- Zeichnen ---
    if final_screen:
        screen.fill(BLACK)
        draw_text("Du hast alle Räume erfolgreich bestanden!", WIDTH // 2, HEIGHT // 2 - 20, center=True)
        draw_text("Danke fürs Spielen!", WIDTH // 2, HEIGHT // 2 + 30, center=True)
        draw_text("Drücke ESC zum Beenden.", WIDTH // 2, HEIGHT // 2 + 80, center=True)

    elif in_menu:
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

        if room1_completed and room_number == 1:
            draw_text("Raum 1 geschafft!", WIDTH // 2, HEIGHT // 2 + 100, center=True)
        if room2_completed and room_number == 2:
            draw_text("Raum 2 geschafft!", WIDTH // 2, HEIGHT // 2 + 100, center=True)
        if room3_completed and room_number == 3:
            draw_text("Raum 3 geschafft!", WIDTH // 2, HEIGHT // 2 + 100, center=True)

        if popup_active:
            if room_number == 2:
                draw_code_popup()
            elif room_number == 3:
                draw_captcha_popup()

        if room_number == 2 and code_entered:
            draw_text("Code korrekt! Raum gelöst!", WIDTH // 2, HEIGHT // 2 + 140, center=True)

    elif minigame_active and not minigame_won:
        minigame_wires()

    elif minigame_won:
        screen.fill(BLACK)
        draw_text("Alle Kabel verbunden! Du bist frei!", WIDTH // 2, HEIGHT // 2 - 50, center=True)
        draw_text("Drücke ENTER um weiterzugehen.", WIDTH // 2, HEIGHT // 2 + 10, center=True)
        draw_text("Oder R für Neustart.", WIDTH // 2, HEIGHT // 2 + 50, center=True)

    pygame.display.flip()
    clock.tick(60)
