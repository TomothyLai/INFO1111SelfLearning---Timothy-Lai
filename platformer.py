import pygame
import os
import random
from classes import Bullet
from classes import Enemy
pygame.init()
WIDTH, HEIGHT = 1280, 720
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fortnight Battle Royale")
FLOOR_POSITION = 400
MAX_BULLETS = 10
WHITE = (255, 255, 255)
FLOOR_COLOUR = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
RED = (255, 0, 0)
FPS = 60
VELOCITY = 5
JUMP_VELOCITY = 15
GRAVITY = 10
CHARACTER_WIDTH, CHARACTER_HEIGHT = 100, 200
ENEMY_DEAD = pygame.USEREVENT + 1

#getting images
MAIN_CHARACTER_IMAGE = pygame.image.load(os.path.join("assets", "character.png"))
MAIN_CHARACTER = pygame.transform.scale(MAIN_CHARACTER_IMAGE, (CHARACTER_WIDTH, CHARACTER_HEIGHT))
ENEMY_IMAGE = pygame.image.load(os.path.join("assets", "enemy.png"))
ENEMY = pygame.transform.scale(ENEMY_IMAGE, (CHARACTER_WIDTH, CHARACTER_HEIGHT))
font = pygame.font.SysFont(None, 24)
WIN_NOTIFICATION = font.render("ENEMY HAS DIED!!!", True, RED)
PLAYER_TAG = font.render("Player", True, WHITE)
JUMP_SOUND = pygame.mixer.Sound(os.path.join("assets", "jump_sound.mp3"))
GUN_SOUND = pygame.mixer.Sound(os.path.join("assets", "gunshot.mp3"))
HIT_MARKER = pygame.mixer.Sound(os.path.join("assets", "hitmarker.mp3"))
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.jpg")), (WIDTH, HEIGHT))


def draw_window(player, alive_enemies, player_bullets):
    WINDOW.blit(BACKGROUND, (0, 0))
    WINDOW.blit(MAIN_CHARACTER, (player.x, player.y))
    WINDOW.blit(PLAYER_TAG, (player.x, player.y))
    for enemy in alive_enemies:
        WINDOW.blit(ENEMY, (enemy.x, enemy.y))
        enemy_health_bar = pygame.Rect(enemy.x, enemy.y - 10, enemy.get_health(), 10)
        pygame.draw.rect(WINDOW, RED, enemy_health_bar)
    pygame.draw.rect(WINDOW, FLOOR_COLOUR, (0, FLOOR_POSITION + CHARACTER_HEIGHT, WIDTH, HEIGHT - FLOOR_POSITION))
    for bullet in player_bullets:
        pygame.draw.rect(WINDOW, RED, bullet)
    if check_for_win(alive_enemies):
        WINDOW.blit(WIN_NOTIFICATION, (50, 50))
    pygame.display.update()

def player_movement(keys_pressed, player, cooldown, time_after_air):
    if keys_pressed[pygame.K_d] and player.x < WIDTH - player.width:
        player.x += VELOCITY
    if keys_pressed[pygame.K_a] and player.x > 0:
        player.x -= VELOCITY
    if keys_pressed[pygame.K_w] and not cooldown:
        return True
    if keys_pressed[pygame.K_s] and player.y < FLOOR_POSITION:
        player.y += VELOCITY
    if player.y < FLOOR_POSITION:
        player.y += GRAVITY * time_after_air
    return False
def enemy_movement(keys_pressed, alive_enemies, cooldown, time_after_air):
    for enemy in alive_enemies:
        if keys_pressed[pygame.K_LEFT] and enemy.x > 0:
            enemy.x -= VELOCITY
        if keys_pressed[pygame.K_RIGHT] and enemy.x < WIDTH - enemy.width:
            enemy.x += VELOCITY
        if keys_pressed[pygame.K_UP] and not cooldown:
            return True
        if keys_pressed[pygame.K_DOWN] and enemy.y < FLOOR_POSITION:
            enemy.y += VELOCITY
        if enemy.y < FLOOR_POSITION:
            enemy.y += GRAVITY * time_after_air
    return False

def handle_bullet_collisions(player_bullets, alive_enemies):
    for bullet in player_bullets:
        for enemy in alive_enemies:
            if enemy.colliderect(bullet):
                player_bullets.remove(bullet)
                enemy.got_hit()
                HIT_MARKER.play()
        if bullet.x < 0 or bullet.x > WIDTH:
            player_bullets.remove(bullet)
        if bullet.direction == "LEFT":
            bullet.x -= bullet.VELOCITY
        else:
            bullet.x += bullet.VELOCITY

def check_for_win(alive_enemies):
    if len(alive_enemies) == 0:
        return True
    for enemy in alive_enemies:
        if enemy.get_health() <= 0:
            alive_enemies.remove(enemy)
            pygame.event.post(pygame.event.Event(ENEMY_DEAD))
            return True

def main():
    clock = pygame.time.Clock()
    run = True
    player = pygame.Rect(100, FLOOR_POSITION, CHARACTER_WIDTH, CHARACTER_HEIGHT)
    alive_enemies = []
    enemy = Enemy(WIDTH - 100, FLOOR_POSITION, CHARACTER_WIDTH, CHARACTER_HEIGHT)
    alive_enemies.append(enemy)
    player_jump_cooldown = False
    enemy_jump_cooldown = False
    count_player_time_in_air = False
    count_enemy_time_in_air = False
    count_player_time_after_air = False
    count_enemy_time_after_air = False
    respawn_timer_count = False
    respawn_timer = 0
    player_time_in_air = 0
    enemy_time_in_air = 0
    player_time_after_air = 0
    enemy_time_after_air = 0
    player_bullets = []
    last_player_direction = "RIGHT"
    pygame.mixer.music.load(os.path.join("assets", "background_music.mp3"))
    pygame.mixer.music.play(-1)

    while run:
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()
        jumped_player = player_movement(keys_pressed, player, player_jump_cooldown, player_time_after_air)
        jumped_enemy = enemy_movement(keys_pressed, alive_enemies, enemy_jump_cooldown, enemy_time_after_air)
        if jumped_player:
            JUMP_SOUND.play()
            player_jump_cooldown = True
            count_player_time_in_air = True
        if count_player_time_in_air:
            player_time_in_air += 3/FPS
            player.y -= JUMP_VELOCITY - GRAVITY * player_time_in_air
            if player_time_in_air > JUMP_VELOCITY/GRAVITY or keys_pressed[pygame.K_s]:
                count_player_time_in_air = False
                player_time_in_air = 0
                count_player_time_after_air = True
        if count_player_time_after_air:
            player_time_after_air += 3/FPS
            if player.y >= FLOOR_POSITION:
                player_jump_cooldown = False
                count_player_time_after_air = False
                player_time_after_air = 0
        for enemy in alive_enemies:
            if jumped_enemy:
                JUMP_SOUND.play()
                enemy_jump_cooldown = True
                count_enemy_time_in_air = True
            if count_enemy_time_in_air:
                enemy_time_in_air += 3/FPS
                enemy.y -= JUMP_VELOCITY - GRAVITY * enemy_time_in_air
                if enemy_time_in_air > JUMP_VELOCITY/GRAVITY or keys_pressed[pygame.K_DOWN]:
                    count_enemy_time_in_air = False
                    enemy_time_in_air = 0
                    count_enemy_time_after_air = True
            if count_enemy_time_after_air:
                enemy_time_after_air += 3/FPS
                if enemy.y >= FLOOR_POSITION:
                    enemy_jump_cooldown = False
                    count_enemy_time_after_air = False
                    enemy_time_after_air = 0
        handle_bullet_collisions(player_bullets, alive_enemies)
        draw_window(player, alive_enemies, player_bullets)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(player_bullets) < MAX_BULLETS:
                    player_bullet = Bullet(player.x + player.width//2, player.y + player.height//2 - 2, 10, 5, last_player_direction)
                    player_bullets.append(player_bullet)
                    GUN_SOUND.play()
                if event.key == pygame.K_d:
                    last_player_direction = "RIGHT"
                if event.key == pygame.K_a:
                    last_player_direction = "LEFT"
            if event.type == ENEMY_DEAD:
                respawn_timer_count = True
            if respawn_timer_count:
                respawn_timer += 3/FPS
                if respawn_timer >= 1:
                    respawn_timer_count = False
                    respawn_timer = 0
                    enemy = Enemy(WIDTH - 100, FLOOR_POSITION, CHARACTER_WIDTH, CHARACTER_HEIGHT)
                    alive_enemies.append(enemy)
    pygame.quit()
if __name__ == "__main__":
    main()