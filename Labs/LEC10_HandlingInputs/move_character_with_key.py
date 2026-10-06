from pico2d import *


TUK_WIDTH, TUK_HEIGHT = 1280, 1024
CHARACTER_SIZE = 100
MOVE_SPEED = 5
RIGHT_FACING_MIN_X = 18
RIGHT_FACING_MAX_X = 79
LEFT_FACING_MIN_X = 22
LEFT_FACING_MAX_X = 83
RUN_MIN_Y = 13
RUN_MAX_Y = 82
IDLE_MIN_Y = 14
IDLE_MAX_Y = 93

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
animation_count = 0
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

    if facing == 1:
        visible_min_x = RIGHT_FACING_MIN_X
        visible_max_x = RIGHT_FACING_MAX_X
    else:
        visible_min_x = LEFT_FACING_MIN_X
        visible_max_x = LEFT_FACING_MAX_X

    half_size = CHARACTER_SIZE // 2
    min_x = half_size - visible_min_x
    max_x = TUK_WIDTH - (visible_max_x - half_size)
    if is_moving:
        visible_min_y = RUN_MIN_Y
        visible_max_y = RUN_MAX_Y
    else:
        visible_min_y = IDLE_MIN_Y
        visible_max_y = IDLE_MAX_Y

    min_y = half_size - visible_min_y
    max_y = TUK_HEIGHT - (visible_max_y - half_size)
    x = max(min_x, min(max_x, x + dx * MOVE_SPEED))
    y = max(min_y, min(max_y, y + dy * MOVE_SPEED))

    if is_moving:
        sprite_y = 100 if facing == 1 else 0
        frame_interval = 1
    else:
        sprite_y = 300 if facing == 1 else 200
        frame_interval = 4

    animation_count += 1
    if animation_count >= frame_interval:
        frame = (frame + 1) % 8
        animation_count = 0

    clear_canvas()
    ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
    character.clip_draw(frame * 100, sprite_y, 100, 100, x, y)
    update_canvas()
    delay(0.05)

close_canvas()

