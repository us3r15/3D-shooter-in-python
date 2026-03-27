###This game uses arrow keeys to move/ look around###
###Esc button quits game###
###You will need to download and replace the files below (font, bg music)###

import pygame
import math
import random
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load and play moosic
sound = pygame.mixer.Sound(r"C:\Users\Owner\Downloads\DOOM.mp3")
sound.play(loops = -1)

# Screen setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOOM")

# Tile size and raycasting setup
tileSize = 64
FOV = math.pi / 3
numRays = 120
maxDepth = 800
deltaAngle = FOV / numRays
enemyHealth = 100
shotgunDamage = 50
shotgunFired = False
bulletSpeed = 5

# Load Press Start 2P font for HUD
font_path = r"C:\Users\Owner\Downloads\press_start_2p\PressStart2P.ttf"
pygame.font.init()
try:
    ui_font = pygame.font.Font(font_path, 24)
except FileNotFoundError:
    print("Custom font not found, using default.")
    ui_font = pygame.font.SysFont("Arial", 24)

# Player health
player_health = 100

# Enemy setup (spawns at tile 6,3)
enemy_x = 6 * tileSize + tileSize // 2
enemy_y = 3 * tileSize + tileSize // 2
enemy_speed = 1
bulletSpeed = 5
bullet_timer = 0
enemyBulletCooldown = 60
bullets = []

# Random wall generation
wallone = random.randint(0, 1)
walltwo = random.randint(0, 1)
wallthree = random.randint(0, 1)
wallfour = random.randint(0, 1)
wallfive = random.randint(0, 1)
wallsix = random.randint(0, 1)
wallseven = random.randint(0, 1)
walleight = random.randint(0, 1)

# Map layout with randomized walls
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, wallone, walltwo, wallthree, wallfour, 0, 1],
    [1, 0, wallfive, wallsix, wallseven, walleight, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

tileSize = 64
FOV = math.pi / 3
numRays = 120
maxDepth = 800
deltaAngle= FOV / numRays

# Player setup
player_x, player_y = 100, 100
player_angle = 0
player_speed = 2

# Raycasting function
def cast_rays():
    start_angle = player_angle - FOV / 2
    ray_width = WIDTH / numRays
    step_size = 0.5

    for ray in range(numRays):
        angle = start_angle + ray * deltaAngle
        depth = 0

        while depth < maxDepth:
            target_x = player_x + depth * math.cos(angle)
            target_y = player_y + depth * math.sin(angle)

            i, j = int(target_x / tileSize), int(target_y / tileSize)

            if 0 <= j < len(game_map) and 0 <= i < len(game_map[0]):
                if game_map[j][i] == 1:
                    wall_height = min(HEIGHT, 10500 / (depth + 0.0001))
                    color = 255 / (1 + depth * depth * 0.0001)
                    wall_top = HEIGHT // 2 - wall_height // 2
                    x_pos = ray * ray_width
                    wall_rect = pygame.Rect(round(x_pos), round(wall_top), round(ray_width), round(wall_height))
                    pygame.draw.rect(screen, (color, color, color), wall_rect)
                    break

            depth += step_size

# Render enemy in 3D space
def render_enemy():
    dx = enemy_x - player_x
    dy = enemy_y - player_y
    distance = math.hypot(dx, dy)
    angle_to_enemy = math.atan2(dy, dx) - player_angle

    while angle_to_enemy < -math.pi:
        angle_to_enemy += 2 * math.pi
    while angle_to_enemy > math.pi:
        angle_to_enemy -= 2 * math.pi

    if abs(angle_to_enemy) < FOV / 2:
        screen_x = WIDTH // 2 + (angle_to_enemy / (FOV / 2)) * (WIDTH // 2)
        size = min(HEIGHT, 8000 / (distance + 0.0001))
        top = HEIGHT // 2 - size // 2
        enemy_rect = pygame.Rect(round(screen_x - size // 8), round(top), round(size // 4), round(size))
        pygame.draw.rect(screen, (255, 0, 0), enemy_rect)

# Render bullets in 3D space
def render_bullets():
    for bullet in bullets[:]:
        dx = bullet["x"] - player_x
        dy = bullet["y"] - player_y
        distance = math.hypot(dx, dy)
        angle_to_bullet = math.atan2(dy, dx) - player_angle

        while angle_to_bullet < -math.pi:
            angle_to_bullet += 2 * math.pi
        while angle_to_bullet > math.pi:
            angle_to_bullet -= 2 * math.pi

        if abs(angle_to_bullet) < FOV / 2:
            screen_x = WIDTH // 2 + (angle_to_bullet / (FOV / 2)) * (WIDTH // 2)
            size = min(HEIGHT, 6000 / (distance + 0.0001))  # Larger size for visibility
            top = HEIGHT // 2 - size // 2
            bullet_rect = pygame.Rect(round(screen_x - size // 8), round(top), round(size // 4), round(size))

            # Color based on bullet type
            if bullet.get("type") == "shotgun":
                color = (255, 255, 0)  # Bright yellow
            else:
                color = (255, 165, 0)  # Orange for enemy bullets

            pygame.draw.rect(screen, color, bullet_rect)

# Player movement
def move_player():
    global player_x, player_y, player_angle
    keys = pygame.key.get_pressed()

    dx = dy = 0
    if keys[pygame.K_a]:
        player_angle -= 0.03
    if keys[pygame.K_d]:
        player_angle += 0.03
    if keys[pygame.K_w]:
        dx = player_speed * math.cos(player_angle)
        dy = player_speed * math.sin(player_angle)
    if keys[pygame.K_s]:
        dx = -player_speed * math.cos(player_angle)
        dy = -player_speed * math.sin(player_angle)

    new_x = player_x + dx
    new_y = player_y + dy

    i = int(new_x / tileSize)
    j = int(new_y / tileSize)

    if 0 <= j < len(game_map) and 0 <= i < len(game_map[0]):
        if game_map[j][i] == 0:
            player_x = new_x
            player_y = new_y

# Main loop
running = True
clock = pygame.time.Clock()
hud_height = 100 #defined before use

while running:
    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (139, 69, 19), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    move_player()
    cast_rays()

    # Draw extended shotgun (silver box + barrel)
    shotgun_width = 100
    shotgun_height = 60
    shotgun_color = (192, 192, 192)

    # Base
    shotgun_rect = pygame.Rect(WIDTH // 2 - shotgun_width // 2, HEIGHT - hud_height - shotgun_height, shotgun_width,
                               shotgun_height)
    pygame.draw.rect(screen, shotgun_color, shotgun_rect)

    # Enemy movement
    dx = player_x - enemy_x
    dy = player_y - enemy_y
    dist = math.hypot(dx, dy)
    if dist > 1:
        next_x = enemy_x + enemy_speed * dx / dist
        next_y = enemy_y + enemy_speed * dy / dist
        i = int(next_x / tileSize)
        j = int(next_y / tileSize)
        if 0 <= j < len(game_map) and 0 <= i < len(game_map[0]):
            if game_map[j][i] == 0:
                enemy_x = next_x
                enemy_y = next_y

    # Enemy shooting
    bullet_timer += 1
    if bullet_timer >= enemyBulletCooldown:
        bullet_timer = 0
        angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
        bullets.append({
            "x": enemy_x,
            "y": enemy_y,
            "dx": bulletSpeed * math.cos(angle),
            "dy": bulletSpeed * math.sin(angle),
            "type": "enemy"
        })

    # Bullet movement and collision
    for bullet in bullets[:]:
        next_x = bullet["x"] + bullet["dx"]
        next_y = bullet["y"] + bullet["dy"]
        i = int(next_x / tileSize)
        j = int(next_y / tileSize)

        # Stop bullet if it hits a wall
        if 0 <= j < len(game_map) and 0 <= i < len(game_map[0]):
            if game_map[j][i] == 1:
                bullets.remove(bullet)
                continue

        bullet["x"] = next_x
        bullet["y"] = next_y

        # Check collision with player
        if bullet.get("type") == "enemy":
            if math.hypot(bullet["x"] - player_x, bullet["y"] - player_y) < 15:
                bullets.remove(bullet)
                player_health = max(0, player_health - 10)

    render_bullets()
    render_enemy()

    # HUD
    hud_height = 100
    hud_color = (80, 80, 80)
    pygame.draw.rect(screen, hud_color, (0, HEIGHT - hud_height, WIDTH, hud_height))

    label_text = ui_font.render("HEALTH", True, (200, 0, 0))
    label_rect = label_text.get_rect(center=(WIDTH // 2, HEIGHT - hud_height + 20))
    screen.blit(label_text, label_rect)

    health_text = ui_font.render(f"{player_health}", True, (200, 0, 0))
    health_rect = health_text.get_rect(center=(WIDTH // 2, HEIGHT - hud_height + 60))
    screen.blit(health_text, health_rect)

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.key == pygame.K_SPACE:
                shotgunFired = True

    # Shotgun firing logic
    if shotgunFired:
        num_pellets = 6
        spread_angle = math.radians(30)
        base_angle = player_angle  # Use player's facing direction

        for i in range(num_pellets):
            offset = spread_angle * (i - num_pellets // 2) / num_pellets
            pellet_angle = base_angle + offset
            bullets.append({
                "x": player_x,
                "y": player_y,
                "dx": bulletSpeed * math.cos(pellet_angle),
                "dy": bulletSpeed * math.sin(pellet_angle),
                "type": "shotgun"
            })

        # Damage enemy if within range and angle
        dx = enemy_x - player_x
        dy = enemy_y - player_y
        distance = math.hypot(dx, dy)
        angle_to_enemy = math.atan2(dy, dx) - player_angle

        while angle_to_enemy < -math.pi:
            angle_to_enemy += 2 * math.pi
        while angle_to_enemy > math.pi:
            angle_to_enemy -= 2 * math.pi

        if abs(angle_to_enemy) < FOV / 2 and distance < 200:
            enemyHealth -= shotgunDamage
            if enemyHealth <= 0:
                enemy_x = -1000
                enemy_y = -1000

        shotgunFired = False

    # Always update display and tick clock
    pygame.display.flip()
    clock.tick(60)

while True:
    if pygame.MOUSEBUTTONDOWN:
                shotgunFired = True

    if enemyHealth == 0:
        messagebox.showinfo("Game Over", "YOU WIN!")
        pygame.quit()