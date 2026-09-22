from pico2d import *

open_canvas(800,600)
character = load_image('character.png')
x= 400
y = 300
rad = 0
r = 200

while 1:
    clear_canvas()
    character.draw(x+r*math.cos(rad), y+r*math.sin(rad))
    rad += 0.01
    update_canvas()
    delay(0.01)
close_canvas() 