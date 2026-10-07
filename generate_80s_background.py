from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter


WIDTH = 1920
HEIGHT = 1080
OUTPUT = Path(__file__).resolve().parent / "assets" / "hot100_80s_montage.png"


def lerp(a, b, t):
    return int(a + (b - a) * t)


def gradient_background():
    top = (12, 13, 28)
    middle = (45, 17, 62)
    bottom = (8, 44, 55)
    img = Image.new("RGB", (WIDTH, HEIGHT), top)
    px = img.load()

    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        if t < 0.58:
            local = t / 0.58
            color = tuple(lerp(top[i], middle[i], local) for i in range(3))
        else:
            local = (t - 0.58) / 0.42
            color = tuple(lerp(middle[i], bottom[i], local) for i in range(3))

        for x in range(WIDTH):
            vignette = abs(x - WIDTH / 2) / (WIDTH / 2)
            shade = 1 - 0.25 * vignette
            px[x, y] = tuple(max(0, int(c * shade)) for c in color)

    return img


def glow(draw, xy, color, width):
    for spread, alpha in [(18, 36), (10, 54), (4, 110)]:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        layer_draw.line(xy, fill=(*color, alpha), width=width + spread)
        layer = layer.filter(ImageFilter.GaussianBlur(spread / 2))
        draw.alpha_composite(layer)
    ImageDraw.Draw(draw).line(xy, fill=(*color, 210), width=width)


def draw_stage_grid(img):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    horizon = 560
    vanishing = WIDTH // 2

    for i in range(23):
        x = int(i * WIDTH / 22)
        draw.line([(x, HEIGHT), (vanishing, horizon)], fill=(42, 221, 207, 58), width=2)

    for i in range(12):
        y = int(horizon + (i / 11) ** 1.75 * (HEIGHT - horizon))
        draw.line([(0, y), (WIDTH, y)], fill=(250, 65, 170, 55), width=2)

    img.alpha_composite(layer)


def draw_spotlight(layer, center, radius, color):
    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(light)
    x, y = center
    for step in range(12, 0, -1):
        r = int(radius * step / 12)
        alpha = int(10 * step)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha))
    layer.alpha_composite(light.filter(ImageFilter.GaussianBlur(18)))


def draw_singer(draw, cx, base, scale, accent, hair):
    skin_shadow = (22, 18, 24, 238)
    jacket = (12, 12, 18, 245)

    draw.ellipse(
        (cx - 42 * scale, base - 260 * scale, cx + 42 * scale, base - 176 * scale),
        fill=skin_shadow,
    )
    draw.ellipse(
        (cx - 70 * scale, base - 292 * scale, cx + 70 * scale, base - 202 * scale),
        fill=hair,
    )
    draw.rectangle(
        (cx - 24 * scale, base - 186 * scale, cx + 24 * scale, base - 142 * scale),
        fill=skin_shadow,
    )
    draw.polygon(
        [
            (cx - 120 * scale, base),
            (cx - 78 * scale, base - 145 * scale),
            (cx, base - 118 * scale),
            (cx + 78 * scale, base - 145 * scale),
            (cx + 120 * scale, base),
        ],
        fill=jacket,
    )
    draw.line(
        [(cx, base - 130 * scale), (cx, base - 18 * scale)],
        fill=accent,
        width=max(3, int(7 * scale)),
    )
    draw.line(
        [(cx + 48 * scale, base - 155 * scale), (cx + 114 * scale, base - 204 * scale)],
        fill=jacket,
        width=max(8, int(18 * scale)),
    )
    draw.line(
        [(cx + 114 * scale, base - 204 * scale), (cx + 152 * scale, base - 220 * scale)],
        fill=(220, 220, 210, 220),
        width=max(2, int(5 * scale)),
    )
    draw.ellipse(
        (
            cx + 143 * scale,
            base - 231 * scale,
            cx + 184 * scale,
            base - 205 * scale,
        ),
        fill=(24, 24, 30, 255),
        outline=accent,
        width=max(2, int(4 * scale)),
    )


def draw_guitarist(draw, cx, base, scale, accent, hair):
    dark = (11, 11, 18, 248)
    draw.ellipse(
        (cx - 58 * scale, base - 280 * scale, cx + 58 * scale, base - 196 * scale),
        fill=hair,
    )
    draw.ellipse(
        (cx - 36 * scale, base - 246 * scale, cx + 36 * scale, base - 174 * scale),
        fill=dark,
    )
    draw.polygon(
        [
            (cx - 95 * scale, base),
            (cx - 52 * scale, base - 142 * scale),
            (cx + 60 * scale, base - 136 * scale),
            (cx + 108 * scale, base),
        ],
        fill=dark,
    )
    draw.line(
        [(cx - 72 * scale, base - 128 * scale), (cx + 142 * scale, base - 256 * scale)],
        fill=(34, 22, 14, 255),
        width=max(5, int(13 * scale)),
    )
    draw.ellipse(
        (
            cx - 112 * scale,
            base - 116 * scale,
            cx + 28 * scale,
            base - 6 * scale,
        ),
        fill=accent,
        outline=(245, 232, 136, 215),
        width=max(2, int(4 * scale)),
    )
    for n in range(4):
        offset = (n - 1.5) * 5 * scale
        draw.line(
            [
                (cx - 86 * scale, base - 58 * scale + offset),
                (cx + 146 * scale, base - 246 * scale + offset),
            ],
            fill=(235, 236, 226, 150),
            width=max(1, int(2 * scale)),
        )


def draw_keyboardist(draw, cx, base, scale, accent, hair):
    dark = (13, 13, 20, 248)
    draw.ellipse(
        (cx - 66 * scale, base - 270 * scale, cx + 66 * scale, base - 190 * scale),
        fill=hair,
    )
    draw.ellipse(
        (cx - 34 * scale, base - 238 * scale, cx + 34 * scale, base - 168 * scale),
        fill=dark,
    )
    draw.polygon(
        [
            (cx - 100 * scale, base - 24 * scale),
            (cx - 58 * scale, base - 150 * scale),
            (cx + 70 * scale, base - 150 * scale),
            (cx + 114 * scale, base - 24 * scale),
        ],
        fill=dark,
    )
    draw.rounded_rectangle(
        (
            cx - 180 * scale,
            base - 58 * scale,
            cx + 180 * scale,
            base,
        ),
        radius=int(10 * scale),
        fill=(234, 236, 223, 230),
        outline=accent,
        width=max(2, int(5 * scale)),
    )
    key_w = 18 * scale
    for i in range(16):
        x = cx - 168 * scale + i * key_w
        draw.line([(x, base - 56 * scale), (x, base)], fill=(22, 22, 28, 150), width=1)
    for i in [1, 2, 4, 6, 7, 9, 10, 12, 14]:
        x = cx - 168 * scale + i * key_w
        draw.rectangle((x, base - 58 * scale, x + 10 * scale, base - 22 * scale), fill=(20, 20, 24, 235))


def draw_performers(img):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    performers = [
        ("guitar", 260, 845, 1.14, (236, 64, 143, 255), (35, 19, 51, 255)),
        ("singer", 570, 835, 1.20, (61, 225, 211, 255), (26, 25, 35, 255)),
        ("keyboard", 970, 850, 1.10, (249, 198, 76, 255), (44, 20, 58, 255)),
        ("singer", 1330, 830, 1.16, (247, 84, 65, 255), (16, 18, 26, 255)),
        ("guitar", 1650, 850, 1.04, (67, 185, 244, 255), (48, 19, 42, 255)),
    ]

    for kind, cx, base, scale, accent, hair in performers:
        if kind == "singer":
            draw_singer(draw, cx, base, scale, accent, hair)
        elif kind == "guitar":
            draw_guitarist(draw, cx, base, scale, accent, hair)
        else:
            draw_keyboardist(draw, cx, base, scale, accent, hair)

    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.25)))


def draw_music_shapes(img):
    rng = Random(1984)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    colors = [
        (245, 67, 153, 75),
        (66, 220, 207, 70),
        (248, 198, 76, 64),
        (245, 86, 66, 58),
    ]

    for _ in range(72):
        x = rng.randint(40, WIDTH - 40)
        y = rng.randint(40, 610)
        size = rng.randint(16, 52)
        color = rng.choice(colors)
        if rng.random() < 0.45:
            draw.ellipse((x, y, x + size, y + size), outline=color, width=3)
        elif rng.random() < 0.75:
            draw.rectangle((x, y, x + size, y + size), outline=color, width=3)
        else:
            draw.polygon(
                [(x, y + size), (x + size / 2, y), (x + size, y + size)],
                outline=color,
            )

    for x, y, scale, color in [
        (146, 190, 1.2, (66, 220, 207, 125)),
        (1720, 240, 1.0, (245, 67, 153, 118)),
        (1075, 145, 0.9, (248, 198, 76, 112)),
    ]:
        draw.ellipse((x, y + 58 * scale, x + 34 * scale, y + 92 * scale), fill=color)
        draw.rectangle((x + 28 * scale, y, x + 38 * scale, y + 74 * scale), fill=color)
        draw.arc(
            (x + 26 * scale, y, x + 98 * scale, y + 58 * scale),
            185,
            330,
            fill=color,
            width=max(4, int(7 * scale)),
        )

    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.2)))


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img = gradient_background().convert("RGBA")

    lights = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    for center, radius, color in [
        ((330, 360), 360, (245, 67, 153)),
        ((940, 310), 390, (66, 220, 207)),
        ((1540, 370), 360, (248, 198, 76)),
    ]:
        draw_spotlight(lights, center, radius, color)
    img.alpha_composite(lights)

    draw_stage_grid(img)
    draw_music_shapes(img)
    draw_performers(img)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 58))
    img.alpha_composite(overlay)

    img = img.convert("RGB")
    img.save(OUTPUT, quality=92, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
