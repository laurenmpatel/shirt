"""Build the patriotic cowgirl-riding-eagle HTV design as 3 welded color layers.

Artboard: 100 units = 1 inch.  viewBox 0 0 1050 1260  ->  10.5in x 12.6in.
Colors:  WHITE #ffffff, NAVY #10214a, RED #d21f28  (on baby-blue #bfe0f5 shirt).
Press order (bottom->top): WHITE, NAVY, RED. Layers are made disjoint by
subtracting upper layers, so no two colors overlap.
"""
import math
from geom import (blob, poly, circle, ellipse, band, star, burst, spark_lines,
                  union, diff, clean, to_path_d)
from shapely.ops import unary_union
from shapely import affinity
from shapely.geometry import Polygon

W, H = 1050, 1260
WHITE = "#ffffff"
NAVY = "#10214a"
RED = "#d21f28"
BABY = "#bfe0f5"

white_parts = []
navy_parts = []
red_parts = []
punch_parts = []   # white shapes that must show THROUGH navy (punch holes in navy)


def add(color, *geoms):
    tgt = {"w": white_parts, "n": navy_parts, "r": red_parts}[color]
    for g in geoms:
        if g is not None and not g.is_empty:
            tgt.append(g)


def add_white_over_navy(*geoms):
    """White detail that sits on top of a navy fill: keep in white AND punch navy."""
    for g in geoms:
        if g is not None and not g.is_empty:
            white_parts.append(g)
            punch_parts.append(g)


navy_top_parts = []   # navy detail that must sit ON TOP of a punched-white area


def add_navy_over_white(*geoms):
    """Navy detail (eye, heel...) drawn on top of a white area that itself
    punches navy (eagle head, boots). Re-applied after the punch step."""
    for g in geoms:
        if g is not None and not g.is_empty:
            navy_top_parts.append(g)


# ----------------------------------------------------------------------------
# EAGLE  (flying, facing left; cowgirl sits on its back)
# ----------------------------------------------------------------------------

# --- Eagle body (navy torso, tucked under the cowgirl) ---
body = blob([
    (470, 600), (575, 640), (620, 740), (600, 850),
    (500, 900), (398, 862), (368, 750), (392, 660),
])
add("n", body)

def feather(tip, base_c, w, samples=10):
    """Elongated leaf-shaped flight feather from base center toward tip."""
    tx, ty = tip
    bx, by = base_c
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L, dx / L          # perpendicular
    mx, my = bx + dx * 0.45, by + dy * 0.45
    return blob([
        (tx, ty),
        (mx + px * w, my + py * w),
        (bx + px * w * 0.55, by + py * w * 0.55),
        (bx - px * w * 0.55, by - py * w * 0.55),
        (mx - px * w, my - py * w),
    ], samples=samples)


# --- LEFT wing (viewer left): clean sweep up and to the left ---
wing_l = blob([
    (448, 660), (360, 610), (250, 572), (140, 516), (106, 466),
    (162, 482), (150, 520), (228, 560), (312, 602), (392, 648),
    (438, 706),
], samples=22)
add("n", wing_l)
# white primary feathers along the left wingtip (bold, separated)
add_white_over_navy(
    feather((110, 470), (218, 520), 19),
    feather((150, 520), (250, 562), 19),
    feather((222, 566), (322, 604), 18),
    )

# --- RIGHT wing (viewer right): clean sweep up and to the right ---
wing_r = blob([
    (552, 660), (640, 610), (750, 572), (860, 516), (894, 466),
    (838, 482), (850, 520), (772, 560), (688, 602), (608, 648),
    (562, 706),
], samples=22)
add("n", wing_r)
add_white_over_navy(
    feather((890, 470), (782, 520), 19),
    feather((850, 520), (750, 562), 19),
    feather((778, 566), (678, 604), 18),
    )

# --- Eagle head (white) poking out to the lower-left, facing left ---
head = blob([
    (300, 668), (348, 676), (366, 730), (346, 786),
    (288, 812), (230, 792), (212, 736), (250, 690),
])
add_white_over_navy(head)
# navy neck wedge tying head up to the body
add("n", poly([(330, 690), (420, 664), (452, 730), (356, 772)]))
# beak (navy hooked), pointing left-down.  Head details sit ON the white head,
# so they go in the navy-on-top set (re-applied after the head punches navy).
beak = poly([(226, 742), (138, 752), (118, 776), (158, 790),
             (176, 778), (226, 782)])
add_navy_over_white(beak)
add_navy_over_white(circle(288, 736, 12))             # eye
add_navy_over_white(band([(250, 710), (318, 704)], 9))  # brow

# --- Tail feathers: clean white fan pointing down, navy separators ---
tail = blob([
    (452, 870), (556, 870), (592, 1000), (556, 1092),
    (500, 1122), (448, 1090), (416, 998),
])
add("w", tail)
# 4 navy separators fanning out from a common origin -> reads as feathers
for ang in (-24, -8, 8, 24):
    a = math.radians(ang)
    x0, y0 = 504, 880
    x1 = x0 + 210 * math.sin(a)
    y1 = y0 + 210 * math.cos(a)
    add("n", band([(x0, y0), (x1, y1)], 8))

# --- Talons: two short navy legs + bold claws ---
leg1 = band([(452, 870), (438, 918), (430, 952)], 24)
leg2 = band([(552, 872), (566, 918), (574, 952)], 24)
add("n", leg1, leg2)
foot1 = blob([(408, 946), (452, 946), (456, 972), (430, 990), (404, 972)])
foot2 = blob([(552, 948), (596, 948), (600, 972), (574, 990), (548, 972)])
add("n", foot1, foot2)
for cx, cy, d in [(408, 972, -1), (430, 984, 0), (452, 972, 1),
                  (552, 972, -1), (574, 984, 0), (596, 972, 1)]:
    add("n", blob([(cx, cy), (cx + 9, cy + 4), (cx + 4 + 6 * d, cy + 26),
                   (cx - 6, cy + 18)], samples=8))


# ----------------------------------------------------------------------------
# COWGIRL  (sits upright on the eagle's back, facing slightly right)
# ----------------------------------------------------------------------------

# --- Pants / legs (navy) straddling the eagle, knees bent outward ---
leg_left = blob([
    (432, 470), (476, 472), (466, 540), (430, 588),
    (372, 612), (338, 590), (378, 548), (410, 512),
])
leg_right = blob([
    (498, 472), (542, 472), (566, 540), (604, 588),
    (632, 612), (600, 636), (556, 592), (508, 540),
])
add_white_over_navy(leg_left, leg_right)

# --- Boots (white) hanging at the sides, toes out; punch through navy ---
boot_l = blob([(378, 566), (416, 590), (402, 664), (356, 690),
               (300, 676), (312, 632), (348, 600)])
boot_r = blob([(566, 566), (610, 604), (656, 626), (668, 668),
               (612, 690), (566, 662), (556, 600)])
add_white_over_navy(boot_l, boot_r)
# red star on each boot shaft (red is top layer, shows over white)
add("r", star(360, 624, 14, 6), star(600, 636, 14, 6))
# navy soles/heels sit ON the white boots
add_navy_over_white(
    poly([(300, 672), (360, 686), (356, 708), (300, 694)]),
    poly([(612, 686), (668, 664), (676, 686), (620, 708)]),
)

# --- Torso / shirt (white) ---
torso = blob([
    (415, 300), (505, 292), (560, 340), (560, 430),
    (520, 480), (450, 486), (398, 452), (388, 372),
])
add("w", torso)
# red collar / scarf
collar = union(
    poly([(430, 300), (486, 296), (470, 340), (452, 352), (430, 340)]),
    poly([(486, 296), (534, 306), (536, 348), (500, 344), (476, 330)]),
)
add("r", collar)
# red belt
belt = poly([(398, 448), (556, 442), (558, 478), (400, 484)])
add("r", belt)
# navy belt buckle
add("n", poly([(462, 448), (498, 446), (500, 478), (464, 480)]))
# red shirt star decorations
add("r", star(432, 400, 13, 5.5), star(500, 392, 13, 5.5),
    star(468, 440, 11, 4.5))

# --- Head / face (white skin) ---
face = blob([
    (438, 196), (492, 198), (512, 236), (508, 280),
    (476, 306), (430, 302), (406, 262), (410, 220),
])
add("w", face)
# red cheeks
add("r", circle(424, 270, 13), circle(496, 270, 13))
# eyes (navy)
add("n", circle(444, 244, 8.5), circle(482, 244, 8.5))
# smile (red band)
add("r", band([(446, 284), (462, 292), (480, 284)], 8))

# --- Hair (navy) flowing behind & to the right ---
hair = blob([
    (416, 190), (500, 188), (540, 220), (556, 300),
    (588, 400), (556, 430), (520, 360), (512, 300),
    (508, 250), (470, 236), (430, 244), (410, 224),
], samples=18)
add("n", diff(hair, face))

# --- Cowgirl hat (red) with navy band + white stars ---
hat_brim = ellipse(462, 176, 118, 34)
hat_crown = blob([
    (410, 176), (420, 110), (470, 92), (516, 112), (520, 176),
])
add("r", union(hat_brim, hat_crown))
# navy hat band
add("n", poly([(414, 158), (516, 158), (514, 176), (416, 176)]))
# white stars on hat band -> punch through navy band
add_white_over_navy(star(440, 167, 8.5, 3.6), star(468, 167, 8.5, 3.6),
                    star(496, 167, 8.5, 3.6))


# ----------------------------------------------------------------------------
# ARMS + SPARKLER + FLAG
# ----------------------------------------------------------------------------

# --- Left arm raised to upper-left holding sparkler (white sleeve) ---
arm_l = band([(430, 336), (360, 300), (300, 240), (262, 190)], 34)
add("w", arm_l)
# red star cuff decorations on sleeve
add("r", star(392, 318, 10, 4.2), star(336, 274, 10, 4.2))
# hand (white)
add("w", circle(258, 184, 20))

# sparkler stick (navy) + burst (red)
add("n", band([(258, 184), (232, 150), (214, 128)], 10))
add("r", burst(206, 118, 74, 26, spikes=12, rot=8))
add("r", spark_lines(206, 118, 40, 96, n=12, width=7, rot=15))
# a few red spark specks (intentional)
add("r", circle(150, 96, 8), circle(268, 84, 8), circle(126, 150, 7))

# --- Right arm forward holding flag pole (white sleeve) ---
arm_r = band([(536, 350), (600, 320), (650, 292)], 34)
add("w", arm_r)
add("r", star(588, 326, 10, 4.2))
add("w", circle(654, 288, 20))

# --- Flag pole (navy) diagonal ---
pole = band([(648, 320), (700, 190), (724, 120)], 14)
add("n", pole)
# pole finial
add("n", circle(726, 116, 13))

# --- Flag (waving to the right) ---
# canton / blue field (navy)
canton = blob([
    (700, 176), (792, 168), (800, 176), (792, 236),
    (784, 246), (696, 252), (700, 214),
])
add("n", canton)
# white stars on canton (grid) -> punch through navy field
for i, sx in enumerate([718, 744, 770]):
    for j, sy in enumerate([196, 222]):
        off = 13 if j == 1 else 0
        add_white_over_navy(star(sx + off - 6, sy, 9, 3.9))

# stripes (alternating red / white wavy bands) to the right of canton
stripe_pts_base = [(792, 172), (860, 164), (920, 176), (966, 168)]
n_stripes = 7
for k in range(n_stripes):
    yoff = k * 14.5
    pts = [(x, y + yoff) for (x, y) in stripe_pts_base]
    b = band(pts, 12.5, samples=10)
    # clip stripes to a flag rectangle-ish waving region
    if k % 2 == 0:
        add("r", b)
    else:
        add("w", b)
# lower half stripes (full width incl. below canton)
stripe_pts_low = [(700, 260), (800, 252), (890, 264), (966, 256)]
for k in range(6):
    yoff = k * 14.5
    pts = [(x, y + yoff) for (x, y) in stripe_pts_low]
    b = band(pts, 12.5, samples=10)
    if k % 2 == 0:
        add("r", b)
    else:
        add("w", b)


# ----------------------------------------------------------------------------
# SCATTERED STARS around the design (navy + red)
# ----------------------------------------------------------------------------
navy_stars = [(70, 300, 20), (600, 108, 15), (940, 470, 16),
              (970, 790, 16), (120, 980, 18), (470, 1170, 16),
              (770, 1120, 16), (300, 905, 15)]
for x, y, r in navy_stars:
    add("n", star(x, y, r, r * 0.42))

red_stars = [(70, 480, 17), (700, 84, 14), (1000, 560, 16),
             (884, 980, 16), (215, 1085, 16), (615, 1150, 15),
             (60, 760, 16), (944, 640, 14)]
for x, y, r in red_stars:
    add("r", star(x, y, r, r * 0.42))


# ----------------------------------------------------------------------------
# REGISTRATION MARKS  (identical on every layer, outside the design area)
# ----------------------------------------------------------------------------
def reg_mark(cx, cy, size=24, thick=6, gap=7):
    """Crosshair-in-frame registration mark, all filled (no strokes)."""
    h = size / 2
    outer = Polygon([(cx - h, cy - h), (cx + h, cy - h),
                     (cx + h, cy + h), (cx - h, cy + h)])
    inner = Polygon([(cx - h + thick, cy - h + thick), (cx + h - thick, cy - h + thick),
                     (cx + h - thick, cy + h - thick), (cx - h + thick, cy + h - thick)])
    frame = outer.difference(inner)
    cross_v = Polygon([(cx - thick / 2, cy - h - gap), (cx + thick / 2, cy - h - gap),
                       (cx + thick / 2, cy + h + gap), (cx - thick / 2, cy + h + gap)])
    cross_h = Polygon([(cx - h - gap, cy - thick / 2), (cx + h + gap, cy - thick / 2),
                       (cx + h + gap, cy + thick / 2), (cx - h - gap, cy + thick / 2)])
    return unary_union([frame, cross_v, cross_h])


REG_POS = [(70, 70), (980, 70), (70, 1190), (980, 1190)]
reg_geom = unary_union([reg_mark(x, y) for x, y in REG_POS])


# ----------------------------------------------------------------------------
# ASSEMBLE, WELD, and enforce NON-OVERLAP (subtract upper layers)
# ----------------------------------------------------------------------------
raw_white = clean(union(*white_parts))
raw_navy = clean(union(*navy_parts))
raw_red = clean(union(*red_parts))
punch = union(*punch_parts) if punch_parts else Polygon()
navy_top = union(*navy_top_parts) if navy_top_parts else Polygon()

# Non-overlap rule: red is top. Navy beats white by default, EXCEPT designated
# white detail (`punch`) that shows through navy (eagle head, feather tips,
# flag/hat stars, boots). Then navy detail that sits ON those white areas
# (eye, brow, beak, boot soles) is re-applied on top.
final_red = raw_red
final_navy = clean(diff(diff(raw_navy, raw_red), punch))
final_navy = clean(union(final_navy, diff(navy_top, raw_red)))
final_white = clean(diff(raw_white, union(final_navy, raw_red)))

# Registration marks are emitted as a SEPARATE path with a byte-identical `d`
# string in every layer file -> provably identical position on all layers.
REG_D = to_path_d(reg_geom)

LAYERS = {
    "WHITE": (final_white, WHITE),
    "NAVY": (final_navy, NAVY),
    "RED": (final_red, RED),
}

VIEWBOX = f"0 0 {W} {H}"
WIDTH_IN = "10.5in"
HEIGHT_IN = "12.6in"


def svg_header():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{WIDTH_IN}" height="{HEIGHT_IN}" viewBox="{VIEWBOX}">')


def write_layer(path, geom, color):
    d = to_path_d(geom)
    with open(path, "w") as f:
        f.write(svg_header() + "\n")
        f.write(f'  <path d="{d}" fill="{color}" fill-rule="evenodd"/>\n')
        f.write(f'  <path d="{REG_D}" fill="{color}" fill-rule="evenodd"/>\n')
        f.write("</svg>\n")


def write_combined(path):
    with open(path, "w") as f:
        f.write(svg_header() + "\n")
        f.write(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{BABY}"/>\n')
        for name in ["WHITE", "NAVY", "RED"]:
            geom, color = LAYERS[name]
            d = to_path_d(geom)
            f.write(f'  <path d="{d}" fill="{color}" fill-rule="evenodd"/>\n')
        # registration marks drawn once (shared position across all layers)
        f.write(f'  <path d="{REG_D}" fill="{NAVY}" fill-rule="evenodd"/>\n')
        f.write("</svg>\n")


if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    write_layer(os.path.join(out, "cowgirl_eagle_WHITE.svg"), *LAYERS["WHITE"])
    write_layer(os.path.join(out, "cowgirl_eagle_NAVY.svg"), *LAYERS["NAVY"])
    write_layer(os.path.join(out, "cowgirl_eagle_RED.svg"), *LAYERS["RED"])
    write_combined(os.path.join(out, "cowgirl_eagle_COMBINED_PREVIEW.svg"))
    print("layers written")
    for n, (g, c) in LAYERS.items():
        print(f"  {n}: area={g.area:.0f} type={g.geom_type}")
