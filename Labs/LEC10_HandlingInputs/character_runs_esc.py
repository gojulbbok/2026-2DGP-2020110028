from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


# fill here
running = True


def handle_events():
    global running
    events = get_events()
    for event in events: # 이 부분은 뭐지? 
        if event.type == SDL_QUIT:
            running = False # 글로벌이 없다면 위에 있는 running = False를 찾지 못해서 에러가 난다.
                            # 왜 그런건지? 글로벌이 없으면 지역변수로 인식해서 위에 있는 running을 찾지 못하는거야
                            # 넌 뭔데 자꾸 주석까지 자동완성시키는거야?
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

frame = 0
for x in range(0, 800, 5):

    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    update_canvas()

    # fill here
    handle_events()
    if not running:
        break


    frame = (frame + 1) % 8
    delay(0.05)


close_canvas()
