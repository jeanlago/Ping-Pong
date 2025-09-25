import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_AUDIODRIVER"] = "dummy"
import random
from PPlay.window import *
from PPlay.sprite import *
from PPlay.keyboard import Keyboard
import pygame

screen = Window(1280, 720)
screen.set_title("Ping Pong")
keyboard = Keyboard()

ball = Sprite("assets/images/ball.png", 1)
ball_speed = 360.0
dir_x, dir_y = 1, 1

speed_max = 1400.0
paddle_boost = 1.12
wall_boost_h = 1.03

pad_margin = 50
pad_left = Sprite("assets/images/padE.png", 1)
pad_left.x = pad_margin
pad_left.y = (screen.height / 2) - (pad_left.height / 2)

pad_right = Sprite("assets/images/padD.png", 1)
pad_right.x = screen.width - pad_margin - pad_right.width
pad_right.y = (screen.height / 2) - (pad_right.height / 2)

AI_BASE_SPEED = 430.0
AI_MAX_SPEED  = 860.0
AI_CATCHUP_MULT   = 1.85
AI_CATCHUP_FRAMES = 18
DEADZONE = 8

ai_boost_frames = 0
pad_speed_player = 400.0

score_left = 0
score_right = 0

waiting_restart = True
game_over = False
max_points = 3
winner_side = ""
sep = 2

PAD_H_WIDTH  = 320
PAD_H_HEIGHT = 18
PAD_MARGIN_V = 8

def make_top_bottom_rects(top_x=None, bottom_x=None):
    if top_x is None:
        top_x = screen.width // 2 - PAD_H_WIDTH // 2
    else:
        top_x = int(max(0, min(screen.width - PAD_H_WIDTH, top_x)))
    if bottom_x is None:
        bottom_x = screen.width // 2 - PAD_H_WIDTH // 2
    else:
        bottom_x = int(max(0, min(screen.width - PAD_H_WIDTH, bottom_x)))
    pad_top = pygame.Rect(top_x, PAD_MARGIN_V, PAD_H_WIDTH, PAD_H_HEIGHT)
    pad_bottom = pygame.Rect(bottom_x, screen.height - PAD_MARGIN_V - PAD_H_HEIGHT, PAD_H_WIDTH, PAD_H_HEIGHT)
    return pad_top, pad_bottom

def randomize_pad_x():
    return random.randint(10, screen.width - PAD_H_WIDTH - 10)

pad_top_rect, pad_bottom_rect = make_top_bottom_rects()

IGNORE_FRAMES_AFTER_WRAP = 10
ignore_top_frames = 0
ignore_bottom_frames = 0

def center_ball():
    ball.x = (screen.width / 2) - (ball.width / 2) - 4.6
    ball.y = (screen.height / 2) - (ball.height / 2)

def random_dirs():
    dx = random.choice([-1, 1])
    dy = random.choice([-1, 1])
    return dx, dy

def start_round_random():
    global dir_x, dir_y, ball_speed, ignore_top_frames, ignore_bottom_frames, ai_boost_frames, waiting_restart, game_over
    center_ball()
    dir_x, dir_y = random_dirs()
    ball_speed = 360.0
    ignore_top_frames = 0
    ignore_bottom_frames = 0
    ai_boost_frames = 0
    waiting_restart = False
    game_over = False

def reset_match():
    global score_left, score_right, winner_side
    score_left = 0
    score_right = 0
    winner_side = ""

def reposition_top_bottom_random():
    global pad_top_rect, pad_bottom_rect
    top_x = randomize_pad_x()
    bottom_x = randomize_pad_x()
    pad_top_rect, pad_bottom_rect = make_top_bottom_rects(top_x=top_x, bottom_x=bottom_x)

def make_net_surface():
    surf = pygame.Surface((12, screen.height), pygame.SRCALPHA)
    step = 32
    y = 0
    font = pygame.font.SysFont(None, 28, bold=False)
    txt = font.render("|", True, (255, 255, 255))
    while y < screen.height:
        surf.blit(txt, (2, y))
        y += step
    return surf

net_surf = make_net_surface()
net_x = screen.width // 2 - net_surf.get_width() // 2

center_ball()
reposition_top_bottom_random()

prev_r = False
prev_space = False

while True:
    dt = screen.delta_time()
    screen.set_background_color((10, 50, 80))

    r_now = keyboard.key_pressed("R") or keyboard.key_pressed("r")
    space_now = keyboard.key_pressed("SPACE")

    if r_now and not prev_r:
        reset_match()
        reposition_top_bottom_random()
        start_round_random()

    if not waiting_restart:
        ball.x += dir_x * ball_speed * dt
        ball.y += dir_y * ball_speed * dt

    if keyboard.key_pressed("UP") or keyboard.key_pressed("w"):
        pad_left.y -= pad_speed_player * dt
    if keyboard.key_pressed("DOWN") or keyboard.key_pressed("s"):
        pad_left.y += pad_speed_player * dt
    pad_left.y = max(0, min(screen.height - pad_left.height, pad_left.y))

    if not waiting_restart:
        target_y = ball.y + ball.height / 2
    else:
        target_y = pad_right.y + pad_right.height / 2

    center_right = pad_right.y + pad_right.height / 2
    diff = target_y - center_right

    ai_speed = AI_BASE_SPEED + 0.38 * ball_speed
    if ai_speed > AI_MAX_SPEED:
        ai_speed = AI_MAX_SPEED
    if ai_boost_frames > 0:
        ai_speed *= AI_CATCHUP_MULT
        ai_boost_frames -= 1

    if abs(diff) > DEADZONE:
        pad_right.y += (ai_speed if diff > 0 else -ai_speed) * dt
    pad_right.y = max(0, min(screen.height - pad_right.height, pad_right.y))

    if ball.collided(pad_left) and dir_x < 0:
        dir_x = 1
        ball.x = pad_left.x + pad_left.width + sep
        ball_speed = min(ball_speed * paddle_boost, speed_max)

    if ball.collided(pad_right) and dir_x > 0:
        dir_x = -1
        ball.x = pad_right.x - ball.width - sep
        ball_speed = min(ball_speed * paddle_boost, speed_max)

    if ignore_top_frames > 0:
        ignore_top_frames -= 1
    if ignore_bottom_frames > 0:
        ignore_bottom_frames -= 1

    ball_rect = pygame.Rect(int(ball.x), int(ball.y), int(ball.width), int(ball.height))

    if dir_y < 0 and ignore_top_frames == 0 and ball_rect.colliderect(pad_top_rect):
        dir_y = 1
        ball.y = pad_top_rect.bottom + sep
        ball_speed = min(ball_speed * wall_boost_h, speed_max)

    if dir_y > 0 and ignore_bottom_frames == 0 and ball_rect.colliderect(pad_bottom_rect):
        dir_y = -1
        ball.y = pad_bottom_rect.top - ball.height - sep
        ball_speed = min(ball_speed * wall_boost_h, speed_max)

    if (ball.y + ball.height) < 0:
        ball.y = screen.height - ball.height - sep
        ignore_bottom_frames = IGNORE_FRAMES_AFTER_WRAP
        ai_boost_frames = AI_CATCHUP_FRAMES

    if ball.y > screen.height:
        ball.y = sep
        ignore_top_frames = IGNORE_FRAMES_AFTER_WRAP
        ai_boost_frames = AI_CATCHUP_FRAMES

    if ball.x <= 0:
        score_right += 1
        waiting_restart = True
        center_ball()
        dir_x, dir_y = 0, 0
        ball_speed = 360.0
        ignore_top_frames = ignore_bottom_frames = 0
        ai_boost_frames = 0
        if score_right >= max_points:
            game_over = True
            winner_side = "Direito"

    if (ball.x + ball.width) >= screen.width:
        score_left += 1
        waiting_restart = True
        center_ball()
        dir_x, dir_y = 0, 0
        ball_speed = 360.0
        ignore_top_frames = ignore_bottom_frames = 0
        ai_boost_frames = 0
        if score_left >= max_points:
            game_over = True
            winner_side = "Esquerdo"

    pygame.display.get_surface().blit(net_surf, (net_x, 0))

    pad_left.draw()
    pad_right.draw()
    ball.draw()

    surf = pygame.display.get_surface()
    pygame.draw.rect(surf, (255, 255, 255), pad_top_rect)
    pygame.draw.rect(surf, (255, 255, 255), pad_bottom_rect)

    sx = screen.width/2 - 90
    sy = 28
    screen.draw_text(f"{score_left}", sx, sy, size=72, color=(0, 0, 0))
    screen.draw_text(f"{score_right}", sx+140, sy, size=72, color=(0, 0, 0))
    screen.draw_text(f"{score_left}", sx-2, sy-2, size=72, color=(255, 255, 255))
    screen.draw_text(f"{score_right}", sx+138, sy-2, size=72, color=(255, 255, 255))

    if waiting_restart:
        if game_over:
            rw = int(screen.width * 0.6)
            rh = int(screen.height * 0.6)
            rx = (screen.width - rw) // 2
            ry = (screen.height - rh) // 2
            overlay = pygame.Surface((rw, rh), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 170), overlay.get_rect(), border_radius=28)
            pygame.draw.rect(overlay, (255, 255, 255, 40), overlay.get_rect(), width=2, border_radius=28)
            surf.blit(overlay, (rx, ry))
            screen.draw_text("GAME OVER", screen.width/2 - 179, ry + 26, size=56, color=(255,255,255))
            screen.draw_text(f"Lado {winner_side} venceu!", screen.width/2 - 165, ry + 100, size=32, color=(255,255,255))
        screen.draw_text("SPACE", screen.width/2 - 55, screen.height/2 + 100, size=32, color=(255,255,255))
        if space_now and not prev_space:
            if game_over:
                reset_match()
            reposition_top_bottom_random()
            start_round_random()

    prev_r = r_now
    prev_space = space_now

    screen.update()
