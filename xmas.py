from collections import deque
import signal
import sys
from functools import partial
import time

from pixels import pixels
from colors import (
    XMAS_COLORS,
    GREEN,
    RED,
    WHITE,
    BLANK,
    AQUA,
    BLUE
)
from iterators import get_patterns, get_colors

tail_length = 20
gap = 5

default_delay = 0.1

LEFT_SIDE = (0, 90)
TOP = (90, 143)
RIGHT_SIDE = (143, 233)
BOTTOM = (233, 283)


def calculate_percentage(line_length, color_value):
    rise = 0 - color_value
    run = line_length - 1
    slope = rise / run
    return slope / color_value

def reduce_brightness(color, index, percentage):
    g, r, b = color
    percentage = max(1 + (index * percentage), 0)
    return list(map(int, [g * percentage, r * percentage, b * percentage]))

def half_brightness(color, n):
    if color == BLANK:
        return color
    g, r, b = color
    percentage = (3/4) ** n
    return list(map(int, [g * percentage, r * percentage, b * percentage]))

def fade_pixels(start, tail_length, pixels, index=0):
    if pixels[index] == BLANK:
        return pixels
    # percentage = calculate_percentage(tail_length, 255)
    # pixels[index] = reduce_brightness(pixels[index], start, percentage)
    pixels[index] = half_brightness(pixels[index], start)
    return pixels

def fade_pixel_list(deck=None, reverse=False, colors=XMAS_COLORS):
    if deck is None:
        pixel_list = deque([BLANK for _ in range(pixels.num_pixels)], maxlen=pixels.num_pixels)
    else:
        pixel_list = deck.copy()

    color_gen = get_colors(colors)
    color_index, color = next(color_gen)
    i = 0
    while True:
        if i < tail_length:
            pixel_list.appendleft(color)
            pixel_list = fade_pixels(i % tail_length, tail_length, pixel_list)
            i += 1
        elif i >= tail_length and i <= tail_length + gap:
            pixel_list.appendleft(BLANK)
            i += 1
        else:
            color_index, color = next(color_gen)
            pixel_list.appendleft(color)
            pixel_list = fade_pixels(0, tail_length, pixel_list)
            i = 0
        yield pixel_list

def fade_single(deck=None, max_run=pixels.num_pixels, colors=XMAS_COLORS):
    if deck is None:
        pixel_list = deque([BLANK for _ in range(pixels.num_pixels)], maxlen=pixels.num_pixels)
    else:
        pixel_list = deck.copy()
    color_gen = get_colors(colors)
    color_index, color = next(color_gen)
    while True:
        for i in range(max_run + tail_length):
            if i < tail_length:
                pixel_list.appendleft(color)
                pixel_list = fade_pixels(i % tail_length, tail_length, pixel_list)
            else:
                pixel_list.appendleft(BLANK)
            yield pixel_list

def alternate_colors():
    count = 0
    colors = (RED, GREEN)

    while True:
        count = count ^ 1
        pixels.fill(colors[count ^ 1])
        yield 1, pixels

def every_other_pixel():
    count = 0
    colors = (RED, GREEN)
    chunk = 20

    while True:
        for i in range(0, pixels.num_pixels, chunk):
            count = count ^ 1
            pixels[i: i + chunk] = [colors[count ^ 1] for _ in range(chunk)]
        yield 1, pixels

def tail_chase(deck=None, colors=XMAS_COLORS, reverse=False):
    if deck is None:
        pixel_list = deque([BLANK for _ in range(pixels.num_pixels)], maxlen=pixels.num_pixels)
    else:
        pixel_list = deck.copy()

    color_gen = get_colors(colors)
    color_index, color = next(color_gen)
    i = 0
    while True:
        if i < tail_length:
            pixel_list.appendleft(color)
            pixel_list = fade_pixels(i % tail_length, tail_length, pixel_list)
            i += 1
        elif i >= tail_length and i <= tail_length + gap:
            pixel_list.appendleft(BLANK)
            i += 1
        else:
            color_index, color = next(color_gen)
            pixel_list.appendleft(color)
            pixel_list = fade_pixels(0, tail_length, pixel_list)
            i = 0
        pixels.update_from_list(pixel_list, reverse=reverse)
        yield default_delay, pixels


def falling_lights():
    pixels.fill(0)
    pixels.show()
    left_len = LEFT_SIDE[1] - LEFT_SIDE[0]
    left_side = deque([BLANK for _ in range(left_len)], maxlen=left_len)

    for pixel_list in fade_pixel_list(left_side, colors=[WHITE, AQUA, BLUE]):
        for index, i in enumerate(range(LEFT_SIDE[1], LEFT_SIDE[0], -1)):
            pixels[i] = pixel_list[index]

        for index, i in enumerate(range(RIGHT_SIDE[0], RIGHT_SIDE[1])):
            pixels[i] = pixel_list[index]
        
        yield default_delay, pixels

def run_around():
    pixels.fill(0)
    pixels.show()
    left_len = LEFT_SIDE[1] - LEFT_SIDE[0]
    left_side = deque([BLANK for _ in range(left_len)], maxlen=left_len)

    top_len = TOP[1] - TOP[0]
    top_side = deque([BLANK for _ in range(top_len)], maxlen=top_len)

    side_pixels_iter = fade_single(left_side, left_len, colors=[GREEN])
    top_pixels_iter = fade_single(top_side, left_len, colors=[RED])

    for side_pixels, top_pixels in zip(side_pixels_iter, top_pixels_iter):
        for index, i in enumerate(range(LEFT_SIDE[0], LEFT_SIDE[1])):
            pixels[i] = side_pixels[index]

        for index, i in enumerate(range(RIGHT_SIDE[0], RIGHT_SIDE[1])):
            pixels[i] = side_pixels[index]

        for index, i in enumerate(range(TOP[0], TOP[1])):
            pixels[i] = top_pixels[index]

        for index, i in enumerate(range(BOTTOM[0], BOTTOM[1])):
            pixels[i] = top_pixels[index]
        
        yield default_delay, pixels

def run_all_patterns(all_patterns):
    run_time, pattern = next(all_patterns)
    
    start = time.time()
    for delay, pixels in pattern():
        if time.time() - start < run_time:
            pixels.show()
            time.sleep(delay)
        else:
            return run_all_patterns(all_patterns)

def signal_term_handler(signal, frame):
    pixels.fill((0, 0, 0))
    pixels.show()
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)

if __name__ == '__main__':
    try:
        all_patterns = get_patterns([
            (180, falling_lights),
            (60, run_around),
            (15, every_other_pixel),
            (60, partial(tail_chase, colors=[GREEN, RED, WHITE])),
            (60, partial(tail_chase, colors=[GREEN, RED, WHITE], reverse=True)),
        ])
        run_all_patterns(all_patterns)

    # This part will shut off the pixels when you hit control-c
    except KeyboardInterrupt:
        print("shutting off pixels...")
        pixels.deinit()
