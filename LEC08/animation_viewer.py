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
IDLE = [(x, 0, 95, 110) for x in (0, 100, 200, 300, 400, 500)]
MOVE = [(x, 120, 95, 100) for x in (0, 100, 200, 300, 400, 500)]
HIT = [(0, 230, 100, 100)]
TELEPORT = [
    (0, 345, 95, 100), (100, 345, 95, 100),
    (250, 270, 175, 165), (445, 270, 175, 165), (635, 270, 175, 165),
    (835, 270, 175, 165), (1020, 345, 100, 100), (1130, 345, 100, 100),
    (1240, 345, 100, 100),
]
ATTACK = [(x, 500, 95, 105) for x in (0, 100, 200, 300, 400, 500, 600)]
ATTACK_EFFECT = [(0, 620, 125, 100), (130, 620, 125, 100)]
DEATH = [(x, 760, 95, 110) for x in (0, 100, 200, 300, 400, 500)]

# 모든 동작은 대기 모션으로 다시 시작하게 한다.
PLAY_ORDER = (
    ("대기", IDLE, False),
    ("이동", MOVE, False),
    ("대기", IDLE, False),
    ("피격", HIT, False),
    ("대기", IDLE, False),
    ("순간이동", TELEPORT, False),
    ("대기", IDLE, False),
    ("공격", ATTACK, True),
    ("대기", IDLE, False),
    ("사망", DEATH, False),
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


def draw_current_motion(sprite_sheet, frames, frame_index, has_attack_effect):
    if has_attack_effect:
        # 공격 중에는 캐릭터를 왼쪽, 이펙트를 오른쪽에 표시한다.
        draw_clip(sprite_sheet, frames[frame_index], 235, 300, 280, 320)
        effect_index = frame_index % len(ATTACK_EFFECT)
        draw_clip(sprite_sheet, ATTACK_EFFECT[effect_index], 590, 300, 260, 240)
    else:
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
        _, frames, has_attack_effect = PLAY_ORDER[motion_index]

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
        draw_current_motion(sprite_sheet, frames, frame_index, has_attack_effect)
        update_canvas()

    close_canvas()


if __name__ == "__main__":
    main()
