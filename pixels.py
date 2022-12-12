import board
import neopixel

pixel_pin = board.D18
num_pixels = 283

class NeoPixel(neopixel.NeoPixel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_pixels = num_pixels

    def update_from_list(self, new_list, reverse=False):
        values_for_update = new_list.copy()
        if reverse:
            values_for_update.reverse()
        for i, color in enumerate(values_for_update):
            self[i] = color

pixels = NeoPixel(
    pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=neopixel.RGB
)