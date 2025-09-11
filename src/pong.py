import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_AUDIODRIVER"] = "dummy" #meu pc buga e nao abre o arquivo pq ta com saida de audio queimada

from PPlay.window import *
from PPlay.sprite import *
from PPlay.keyboard import Keyboard

screen = Window(1280, 720)
screen.set_title("Ping Pong")
keyboard = Keyboard()

ball = Sprite("assets/images/ball.png", 1)
ball.x = (screen.width  / 2) - (ball.width  / 2)
ball.y = (screen.height / 2) - (ball.height / 2)

ball_speed = 360.0
dir_x = 1
dir_y = 1

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

pad_speed = 400.0

score_left = 0
score_right = 0

# --- no topo, já existe ---
waiting_restart = False
deadzone = 12  # pixels de tolerância para a IA

while True:
    dt = screen.delta_time()
    screen.set_background_color((10, 50, 80))

    # bola só anda se não estiver esperando restart
    if not waiting_restart:
        ball.x += dir_x * ball_speed * dt
        ball.y += dir_y * ball_speed * dt

    # movimento do jogador
    if keyboard.key_pressed("UP"):
        pad_left.y -= pad_speed * dt
    if keyboard.key_pressed("DOWN"):
        pad_left.y += pad_speed * dt
    pad_left.y = max(0, min(screen.height - pad_left.height, pad_left.y))

    # ---- IA (com deadzone e congelada durante restart) ----
    if not waiting_restart:
        target_y = ball.y
    else:
        # durante a pausa, mantenha a IA estável (ou siga lentamente para o centro, se preferir)
        target_y = pad_right.y + pad_right.height/2  # fica onde está (não mexe)

    center_right = pad_right.y + pad_right.height/2
    diff = target_y - center_right

    if abs(diff) > deadzone:
        # move na direção do alvo sem oscilar quando a diferença é pequena
        pad_right.y += (pad_speed if diff > 0 else -pad_speed) * dt

    # limita a raquete da IA na tela
    pad_right.y = max(0, min(screen.height - pad_right.height, pad_right.y))
    # -------------------------------------------------------

    # colisões raquetes
    if ball.collided(pad_left):
        dir_x = 1
        ball.x = pad_left.x + pad_left.width
        ball_speed = min(ball_speed * paddle_boost, speed_max)

    if ball.collided(pad_right):
        dir_x = -1
        ball.x = pad_right.x - ball.width
        ball_speed = min(ball_speed * paddle_boost, speed_max)

    # colisões paredes
    if ball.y <= 0:
        ball.y = 0
        dir_y *= -1
        ball_speed = min(ball_speed * wall_boost_h, speed_max)

    if ball.y + ball.height >= screen.height:
        ball.y = screen.height - ball.height
        dir_y *= -1
        ball_speed = min(ball_speed * wall_boost_h, speed_max)

    # pontuação (ativa pausa)
    if ball.x <= 0:
        score_right += 1
        waiting_restart = True
        ball.x = (screen.width / 2) - (ball.width / 2)
        ball.y = (screen.height / 2) - (ball.height / 2)
        dir_x, dir_y = 1, 1
        ball_speed = 360.0

    if ball.x + ball.width >= screen.width:
        score_left += 1
        waiting_restart = True
        ball.x = (screen.width / 2) - (ball.width / 2)
        ball.y = (screen.height / 2) - (ball.height / 2)
        dir_x, dir_y = -1, -1
        ball_speed = 360.0

    # mensagem de pausa
    if waiting_restart:
        screen.draw_text("Pressione SPACE para continuar",
                         screen.width/2 - 250, screen.height/2 + 100,
                         size=32, color=(255,255,255))
        if keyboard.key_pressed("SPACE"):
            waiting_restart = False

    # desenho da linha central
    step = 32
    xmid = screen.width // 2
    y = 0
    while y < screen.height:
        screen.draw_text("|", xmid - 8, y, size=28, color=(255, 255, 255))
        y += step

    pad_left.draw()
    pad_right.draw()
    ball.draw()

    # placar
    sx = screen.width/2 - 90
    sy = 28
    screen.draw_text(f"{score_left}", sx, sy, size=72, color=(0, 0, 0))
    screen.draw_text(f"{score_right}", sx+140, sy, size=72, color=(0, 0, 0))
    screen.draw_text(f"{score_left}", sx-2, sy-2, size=72, color=(255, 255, 255))
    screen.draw_text(f"{score_right}", sx+138, sy-2, size=72, color=(255, 255, 255))

    screen.update()
