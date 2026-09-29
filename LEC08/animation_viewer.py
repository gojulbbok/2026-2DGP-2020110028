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
MOVE_FRAME_SECONDS = 0.18 / 0.7 / 0.7
IDLE_REPEAT_COUNT = 2
ACTION_REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
CHARACTER_SCALE = 380 / 90
ATTACK_SCALE = CHARACTER_SCALE * 0.95
IDLE_SCALE = 3.8 * 1.05
SECONDARY_ACTION_SIZE_SCALE = 1.05

# (x, y, width, height): y는 이미지 파일의 위쪽을 기준으로 적는다.
# 행마다 프레임 수와 크기가 달라도 이 목록에 실제 영역을 따로 적으면 된다.
# 대기 행은 각 캐릭터의 실제 중심에 맞춰 자른다.
# 모든 프레임을 75 x 100으로 맞춰 옆 프레임이 섞이거나 좌우로 흔들리지 않게 한다.
IDLE = [(x, 10, 75, 100) for x in (0, 83, 166, 248, 326, 409)]
# 이동 행은 모든 프레임을 같은 96 x 90 영역으로 자른다.
# 실제 캐릭터 중심에 맞춘 x 좌표와 공통 y 범위를 사용해 수평 이동 중 흔들림을 줄인다.
MOVE = [(x, 115, 96, 90) for x in (0, 97, 203, 307, 404, 508)]
# 같은 이동 프레임을 사용하지만 공격 전후의 위치 계산을 구분하기 위한 목록이다.
ATTACK_APPROACH = MOVE.copy()
ATTACK_RETURN = MOVE.copy()
HIT = [(0, 215, 100, 100)]
TELEPORT = [
    (0, 345, 95, 100), (100, 345, 95, 100),
    (250, 270, 175, 165), (445, 270, 175, 165), (635, 270, 175, 165),
    (835, 270, 175, 165), (1020, 345, 100, 100), (1130, 345, 100, 100),
    (1240, 345, 100, 100),
]
# 공격 행은 앞쪽 7프레임보다 뒤쪽 5프레임의 폭이 더 넓다.
# 실제 프레임 경계대로 5번째 줄 전체 12프레임을 사용한다.
ATTACK = [
    (0, 485, 101, 115),
    (101, 485, 110, 115),
    (211, 485, 106, 115),
    (317, 485, 110, 115),
    (427, 485, 105, 115),
    (532, 485, 107, 115),
    (639, 485, 105, 115),
    (744, 485, 137, 115),
    (881, 485, 133, 115),
    (1014, 485, 138, 115),
    (1152, 485, 134, 115),
    (1286, 485, 139, 115),
]
# 6번째 줄의 공격 이펙트 두 프레임이다.
ATTACK_EFFECT = [(0, 600, 130, 125), (130, 600, 130, 125)]
ATTACK_EFFECT_START_FRAME = 7
DEATH = [(x, 760, 95, 110) for x in (0, 100, 200, 300, 400, 500)]

# 모든 동작은 대기 모션으로 다시 시작하게 한다.
HIT_SEQUENCE = (("대기", IDLE), ("피격", HIT)) * 5

PLAY_ORDER = (
    ("대기", IDLE),
    ("이동", MOVE),
    *HIT_SEQUENCE,
    ("대기", IDLE),
    ("순간이동", TELEPORT),
    ("대기", IDLE),
    ("공격 위치로 이동", ATTACK_APPROACH),
    ("공격", ATTACK),
    ("중앙으로 복귀", ATTACK_RETURN),
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


def draw_current_motion(sprite_sheet, frames, frame_index, motion_progress, cycle_progress):
    if frames is IDLE:
        # 원본 비율을 유지하며 기존 크기보다 5% 크게 화면 중앙에 그린다.
        frame = frames[frame_index]
        draw_clip(
            sprite_sheet,
            frame,
            400,
            300,
            frame[2] * IDLE_SCALE,
            frame[3] * IDLE_SCALE,
        )
    elif frames is MOVE or frames is ATTACK_APPROACH:
        # 전반부: 중앙에서 왼쪽 바깥으로 이동한다.
        # 후반부: 오른쪽 바깥에서 다시 나타나 목표 위치로 이동한다.
        target_x = 600 if frames is ATTACK_APPROACH else 400
        # 일반 이동은 한 프레임 주기마다 한 바퀴, 공격 전 이동은 전체 시간 동안 한 바퀴 돈다.
        path_progress = cycle_progress if frames is MOVE else motion_progress
        move_draw_width = MOVE[0][2] * CHARACTER_SCALE
        half_width = move_draw_width / 2
        if path_progress < 0.5:
            section_progress = path_progress * 2
            center_x = 400 + (-half_width - 400) * section_progress
        else:
            section_progress = (path_progress - 0.5) * 2
            center_x = (800 + half_width) + (target_x - (800 + half_width)) * section_progress
        move_draw_height = MOVE[0][3] * CHARACTER_SCALE
        draw_clip(sprite_sheet, frames[frame_index], center_x, 300, move_draw_width, move_draw_height)
    elif frames is ATTACK:
        # 이동 모션과 비슷한 크기를 유지하되 시각적으로 맞도록 5%만 줄인다.
        frame = frames[frame_index]
        draw_width = frame[2] * ATTACK_SCALE
        draw_height = frame[3] * ATTACK_SCALE
        draw_clip(sprite_sheet, frame, 600, 300, draw_width, draw_height)

        # 방패·마법진이 나타나는 후반 프레임에만 중심선 대칭 위치에 이펙트를 그린다.
        if frame_index >= ATTACK_EFFECT_START_FRAME:
            effect_index = (frame_index - ATTACK_EFFECT_START_FRAME) % len(ATTACK_EFFECT)
            draw_clip(sprite_sheet, ATTACK_EFFECT[effect_index], 200, 300, 260, 250)
    elif frames is ATTACK_RETURN:
        # 공격이 끝나면 이동 모션으로 x=600에서 중앙까지 돌아온다.
        center_x = 600 + (400 - 600) * motion_progress
        draw_width = MOVE[0][2] * CHARACTER_SCALE
        draw_height = MOVE[0][3] * CHARACTER_SCALE
        draw_clip(sprite_sheet, frames[frame_index], center_x, 300, draw_width, draw_height)
    elif frames is HIT or frames is TELEPORT:
        # 피격과 순간이동은 기존 출력 크기에서 5% 키운다.
        draw_clip(
            sprite_sheet,
            frames[frame_index],
            400,
            300,
            330 * SECONDARY_ACTION_SIZE_SCALE,
            380 * SECONDARY_ACTION_SIZE_SCALE,
        )
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
        motion_progress = 1.0 if paused else 0.0
        cycle_progress = 1.0 if paused else 0.0

        if paused:
            frame_index = 0
            if now - phase_started_at >= PAUSE_SECONDS:
                motion_index = (motion_index + 1) % len(PLAY_ORDER)
                completed_repeats = 0
                phase_started_at = now
                paused = False
        else:
            elapsed = now - phase_started_at
            frame_seconds = MOVE_FRAME_SECONDS if frames is MOVE else FRAME_SECONDS
            frame_index = int(elapsed / frame_seconds) % len(frames)
            cycle_duration = frame_seconds * len(frames)
            completed_repeats = int(elapsed / cycle_duration)
            if frames is IDLE:
                repeat_count = IDLE_REPEAT_COUNT
            elif frames is HIT:
                repeat_count = 1
            else:
                repeat_count = ACTION_REPEAT_COUNT
            motion_duration = cycle_duration * repeat_count
            motion_progress = min(elapsed / motion_duration, 1.0)
            cycle_progress = (elapsed % cycle_duration) / cycle_duration

            # 대기, 공격 위치로 이동, 공격은 다음 동작과 바로 연결한다.
            # 그 밖의 동작은 완료 후 1초 동안 멈춘다.
            if completed_repeats >= repeat_count:
                frame_index = 0
                completed_repeats = repeat_count
                cycle_progress = 1.0
                phase_started_at = now
                if frames is IDLE or frames is ATTACK_APPROACH or frames is ATTACK:
                    motion_index = (motion_index + 1) % len(PLAY_ORDER)
                    completed_repeats = 0
                else:
                    paused = True

        clear_canvas()
        # 투명 스프라이트가 보일 흰색 배경을 매 프레임 먼저 채운다.
        draw_rectangle(0, 0, 799, 599, 255, 255, 255, 255, filled=True)
        draw_current_motion(sprite_sheet, frames, frame_index, motion_progress, cycle_progress)
        update_canvas()

    close_canvas()


if __name__ == "__main__":
    main()
