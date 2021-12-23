import numpy as np
from image_maps import ImageMaps
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from signal import pause

sense = SenseHat()
sense.low_light = True
event = sense.stick.wait_for_event()

class Joystick(object):
    def __init__(self):
        self.controller()

    def controller(self):
        sense.stick.direction_up = self.up
        sense.stick.direction_down = self.down
        sense.stick.direction_right = self.right
        sense.stick.direction_left = self.left
        sense.stick.direction_any = self.refresh
        self.refresh()
        pause()

    def up(self, event):
        img = ImageMaps['arrow'][0]    
        print(f'{event.action} {event.direction}')
        sense.set_pixels(img)

    def right(self, event):
        img = ImageMaps['arrow'][1]
        print(f'{event.action} {event.direction}')
        sense.set_pixels(img)
    
    def down(self, event):
        img = ImageMaps['arrow'][2]
        print(f'{event.action} {event.direction}')
        sense.set_pixels(img)

    def left(self, event):
        img = ImageMaps['arrow'][3]
        print(f'{event.action} {event.direction}')
        sense.set_pixels(img)

    def refresh(self):
        sense.clear()



if __name__=='__main__':
    Joystick()
