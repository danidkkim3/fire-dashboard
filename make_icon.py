"""Generate a fire icon and convert to .icns for macOS."""
import os, math
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024

def draw_fire(size=SIZE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = size // 2
    # ── dark background circle ─────────────────────────────────────────
    pad = int(size * 0.04)
    draw.ellipse([pad, pad, size - pad, size - pad], fill=(20, 14, 40, 255))

    # ── helper: filled polygon with alpha ──────────────────────────────
    def flame(pts, color):
        overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).polygon(pts, fill=color)
        blurred = overlay.filter(ImageFilter.GaussianBlur(size * 0.018))
        img.alpha_composite(blurred)

    S = size / 1024  # scale factor

    # ── outer flame (deep orange) ──────────────────────────────────────
    flame([
        (cx,           int(80  * S)),
        (int(720 * S), int(420 * S)),
        (int(760 * S), int(620 * S)),
        (int(700 * S), int(820 * S)),
        (int(560 * S), int(940 * S)),
        (int(440 * S), int(960 * S)),
        (int(300 * S), int(930 * S)),
        (int(240 * S), int(820 * S)),
        (int(220 * S), int(640 * S)),
        (int(280 * S), int(420 * S)),
    ], (255, 90, 10, 230))

    # ── mid flame (bright orange) ──────────────────────────────────────
    flame([
        (cx,           int(200 * S)),
        (int(660 * S), int(450 * S)),
        (int(680 * S), int(620 * S)),
        (int(630 * S), int(800 * S)),
        (int(540 * S), int(900 * S)),
        (int(440 * S), int(930 * S)),
        (int(350 * S), int(900 * S)),
        (int(300 * S), int(800 * S)),
        (int(320 * S), int(620 * S)),
        (int(360 * S), int(450 * S)),
    ], (255, 160, 20, 220))

    # ── inner flame (yellow-white) ─────────────────────────────────────
    flame([
        (cx,           int(380 * S)),
        (int(590 * S), int(530 * S)),
        (int(610 * S), int(660 * S)),
        (int(570 * S), int(800 * S)),
        (int(500 * S), int(880 * S)),
        (int(430 * S), int(900 * S)),
        (int(360 * S), int(870 * S)),
        (int(320 * S), int(790 * S)),
        (int(340 * S), int(660 * S)),
        (int(420 * S), int(530 * S)),
    ], (255, 220, 60, 210))

    # ── core (near-white hot center) ──────────────────────────────────
    flame([
        (cx,           int(540 * S)),
        (int(555 * S), int(620 * S)),
        (int(550 * S), int(720 * S)),
        (int(510 * S), int(840 * S)),
        (int(460 * S), int(880 * S)),
        (int(400 * S), int(875 * S)),
        (int(360 * S), int(830 * S)),
        (int(355 * S), int(720 * S)),
        (int(400 * S), int(620 * S)),
        (int(460 * S), int(540 * S)),
    ], (255, 255, 180, 200))

    # ── soft glow around flame ─────────────────────────────────────────
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [int(280*S), int(400*S), int(740*S), int(940*S)],
        fill=(255, 120, 0, 60)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.06))
    img.alpha_composite(glow)

    return img

# ── build iconset ──────────────────────────────────────────────────────
iconset_dir = "/Users/dannykim/finance-tracker/AppIcon.iconset"
os.makedirs(iconset_dir, exist_ok=True)

sizes = [16, 32, 64, 128, 256, 512, 1024]
for s in sizes:
    icon = draw_fire(s)
    icon.save(f"{iconset_dir}/icon_{s}x{s}.png")
    if s <= 512:
        icon2x = draw_fire(s * 2)
        icon2x.save(f"{iconset_dir}/icon_{s}x{s}@2x.png")

print("Iconset created.")
