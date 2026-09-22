from pico2d import *


open_canvas()
grass = load_image('grass.png')
character = load_image('character.png')

grass.draw(400, 30)
character.draw(400, 90)
update_canvas()
delay(5)
close_canvas()

