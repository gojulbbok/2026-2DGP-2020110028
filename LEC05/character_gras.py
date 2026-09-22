from pico2d import *

open_canvas(800,600)
grass = load_image('grass.png')
character = load_image('character.png')

x = 0
y = 90
while x < 800:
    clear_canvas()
    grass.draw(400, 30)
    if 300 <x <= 400:
        character.draw(x, y)
        y+= 10
    elif 400 <x < 500:
            character.draw(x, y)
            y-= 10
    else:
        character.draw(x, 90)
    update_canvas()
    x += 2
    delay(0.01)
close_canvas()