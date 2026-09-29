from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    draw_rectangle,
    get_events,
    get_time,
    load_image,
    open_canvas,
    update_canvas,
)


SHEET_HEIGHT = 949
FRAME_SECONDS = 0.12
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0

# (x, y, width, height): y는 이미지 파일의 위쪽을 기준으로 적는다.
# 행마다 프레임 수와 크기가 달라도 이 목록에 실제 영역을 따로 적으면 된다.
# 대기 행은 각 캐릭터의 실제 중심에 맞춰 자른다.
# 모든 프레임을 75 x 100으로 맞춰 옆 프레임이 섞이거나 좌우로 흔들리지 않게 한다.
IDLE = [(x, 10, 75, 100) for x in (0, 83, 166, 248, 326, 409)]
MOVE = [(x, 120, 95, 100) for x in (0, 100, 200, 300, 400, 500)]
HIT = [(0, 230, 100, 100)]
TELEPORT = [
    (0, 345, 95, 100), (100, 345, 95, 100),
    (250, 270, 175, 165), (445, 270, 175, 165), (635, 270, 175, 165),
    (835, 270, 175, 165), (1020, 345, 100, 100), (1130, 345, 100, 100),
    (1240, 345, 100, 100),
]
# 공격 행은 앞쪽 7프레임보다 뒤쪽 5프레임의 폭이 더 넓다.
# 실제 프레임 경계대로 5번째 줄 전체 12프레임을 사용한다.
ATTACK = [
    (0, 500, 101, 115),
    (101, 500, 110, 115),
    (211, 500, 106, 115),
    (317, 500, 110, 115),
    (427, 500, 105, 115),
    (532, 500, 107, 115),
    (639, 500, 105, 115),
    (744, 500, 137, 115),
    (881, 500, 133, 115),
    (1014, 500, 138, 115),
    (1152, 500, 134, 115),
    (1286, 500, 139, 115),
]
DEATH = [(x, 760, 95, 110) for x in (0, 100, 200, 300, 400, 500)]

# 모든 동작은 대기 모션으로 다시 시작하게 한다.
PLAY_ORDER = (
    ("대기", IDLE),
    ("이동", MOVE),
    ("대기", IDLE),
    ("피격", HIT),
    ("대기", IDLE),
    ("순간이동", TELEPORT),
    ("대기", IDLE),
    ("공격", ATTACK),
    ("대기", IDLE),
    ("사망", DEATH),
)


def should_close():
    for event in get_events():
        if event.type == SDL_QUIT:
            return True
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return True
    return False


def draw_clip(sprite_sheet, frame, center_x, center_y, draw_width, draw_height):
    source_x, source_top, source_width, source_height = frame
    # pico2d clip_draw는 왼쪽 아래를 원점으로 사용한다.
    source_y = SHEET_HEIGHT - source_top - source_height
    sprite_sheet.clip_draw(
        source_x, source_y, source_width, source_height,
        center_x, center_y, draw_width, draw_height,
    )


def draw_current_motion(sprite_sheet, frames, frame_index):
    if frames is IDLE:
        # 75:100 원본 비율을 유지하면서 화면 중앙의 같은 위치에 그린다.
        draw_clip(sprite_sheet, frames[frame_index], 400, 300, 285, 380)
    elif frames is ATTACK:
        # 프레임 폭이 달라도 같은 배율과 중심을 사용해 흔들림을 막는다.
        frame = frames[frame_index]
        scale = 380 / frame[3]
        draw_width = frame[2] * scale
        draw_clip(sprite_sheet, frame, 400, 300, draw_width, 380)
    else:
        # 공격을 포함한 나머지 동작도 화면 중앙에서 재생한다.
        draw_clip(sprite_sheet, frames[frame_index], 400, 300, 330, 380)


def main():
    image_path = Path(__file__).with_name("provided_sprite_sheet.png")
    open_canvas(800, 600)
    sprite_sheet = load_image(str(image_path))

    motion_index = 0
    completed_repeats = 0
    phase_started_at = get_time()
    paused = False
    running = True

    while running:
        running = not should_close()
        now = get_time()
        _, frames = PLAY_ORDER[motion_index]

        if paused:
            frame_index = 0
            if now - phase_started_at >= PAUSE_SECONDS:
                motion_index = (motion_index + 1) % len(PLAY_ORDER)
                completed_repeats = 0
                phase_started_at = now
                paused = False
        else:
            elapsed = now - phase_started_at
            frame_index = int(elapsed / FRAME_SECONDS) % len(frames)
            completed_repeats = int(elapsed / (FRAME_SECONDS * len(frames)))

            # 현재 동작을 5회 반복한 다음 1초 동안 멈춘다.
            if completed_repeats >= REPEAT_COUNT:
                frame_index = 0
                completed_repeats = REPEAT_COUNT
                phase_started_at = now
                paused = True

        clear_canvas()
        # 투명 스프라이트가 보일 흰색 배경을 매 프레임 먼저 채운다.
        draw_rectangle(0, 0, 799, 599, 255, 255, 255, 255, filled=True)
        draw_current_motion(sprite_sheet, frames, frame_index)
        update_canvas()

    close_canvas()


if __name__ == "__main__":
    main()
