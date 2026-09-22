# 실습 과제 진행
from pico2d import *

# 맨처음 해야할 일은.
open_canvas(800,600)
character = load_image('character.png')


def move_circle():
    print ('circle')
    # 캐릭터 이미지 표시
    clear_canvas()
    character.draw(400,300)
    update_canvas()
    pass

def move_rectangle():
    print ('rectangle')
    pass

def move_triangle():
    print ('triangle')
    pass

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass


close_canvas()