from pico2d import *


TUK_WIDTH, TUK_HEIGHT = 1280, 1024
CHARACTER_SIZE = 100
MOVE_SPEED = 5

open_canvas(TUK_WIDTH, TUK_HEIGHT)
ground = load_image('TUK_GROUND.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running
    global left_pressed, right_pressed, up_pressed, down_pressed

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                left_pressed = True
            elif event.key == SDLK_RIGHT:
                right_pressed = True
            elif event.key == SDLK_UP:
                up_pressed = True
            elif event.key == SDLK_DOWN:
                down_pressed = True
            elif event.key == SDLK_ESCAPE:
                running = False
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                left_pressed = False
            elif event.key == SDLK_RIGHT:
                right_pressed = False
            elif event.key == SDLK_UP:
                up_pressed = False
            elif event.key == SDLK_DOWN:
                down_pressed = False


running = True
x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
frame = 0
facing = 1

left_pressed = False
right_pressed = False
up_pressed = False
down_pressed = False

while running:
    handle_events()

    dx = int(right_pressed) - int(left_pressed)
    dy = int(up_pressed) - int(down_pressed)
    is_moving = dx != 0 or dy != 0

    if dx < 0:
        facing = -1
    elif dx > 0:
        facing = 1

    half_size = CHARACTER_SIZE // 2
    x = max(half_size, min(TUK_WIDTH - half_size, x + dx * MOVE_SPEED))
    y = max(half_size, min(TUK_HEIGHT - half_size, y + dy * MOVE_SPEED))

    if is_moving:
        sprite_y = 100 if facing == 1 else 0
        frame = (frame + 1) % 8
    else:
        sprite_y = 300 if facing == 1 else 200
        frame = (frame + 1) % 8

    clear_canvas()
    ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
    character.clip_draw(frame * 100, sprite_y, 100, 100, x, y)
    update_canvas()
    delay(0.05)

close_canvas()

