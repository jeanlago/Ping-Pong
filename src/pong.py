import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_AUDIODRIVER"] = "dummy"

from PPlay.window import *
from PPlay.sprite import *

screen = Window(1280, 720)
screen.set_title("Ping Pong")

ball = Sprite("assets/images/ball.png", 1)
ball.x = (screen.width  / 2) - (ball.width  / 2)
ball.y = (screen.height / 2) - (ball.height / 2)

ball_speed = 300.0
dir_x = 1
dir_y = 1

speed_increase_factor = 1.05
speed_max = 900.0

pad_margin = 40
pad_left = Sprite("assets/images/padE.png", 1)
pad_left.x = pad_margin
pad_left.y = (screen.height / 2) - (pad_left.height / 2)

pad_right = Sprite("assets/images/padD.png", 1)
pad_right.x = screen.width - pad_margin - pad_right.width
pad_right.y = (screen.height / 2) - (pad_right.height / 2)

while True:
    dt = screen.delta_time()
    screen.set_background_color((85, 100, 85))

    ball.x += dir_x * ball_speed * dt
    ball.y += dir_y * ball_speed * dt

    if ball.x <= 0:
        ball.x = 0
        dir_x *= -1
        ball_speed = min(ball_speed * speed_increase_factor, speed_max)

    if ball.x + ball.width >= screen.width:
        ball.x = screen.width - ball.width
        dir_x *= -1
        ball_speed = min(ball_speed * speed_increase_factor, speed_max)

    if ball.y <= 0:
        ball.y = 0
        dir_y *= -1

    if ball.y + ball.height >= screen.height:
        ball.y = screen.height - ball.height
        dir_y *= -1

    pad_left.draw()
    pad_right.draw()
    ball.draw()

    screen.update()
