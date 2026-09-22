from pico2d import *

open_canvas(800,600)
character = load_image('character.png')
x= 100
y = 100

while 1:
    clear_canvas()
    if  100 <= x < 700 and y == 100:
        character.draw(x, y)
        x+= 2
    elif x == 700 and 100 <= y < 500 :
        character.draw(x, y)
        y += 2
    elif 100 <x <= 700 and y == 500:
        character.draw(x, y)
        x -= 2
    else :
        character.draw(x, y)
        y -= 2
    update_canvas()
    delay(0.01)
close_canvas()