from colors import XMAS_COLORS

def get_colors(colors=XMAS_COLORS):
    while True:
        for index, color in enumerate(colors):
            yield index, color

def get_patterns(patterns):
    while True:
        for pattern in patterns:
            yield pattern