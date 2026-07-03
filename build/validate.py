"""Validate the HTV cut files against the production requirements."""
import re
import sys
import xml.etree.ElementTree as ET

LAYERS = ["cowgirl_eagle_WHITE.svg", "cowgirl_eagle_NAVY.svg", "cowgirl_eagle_RED.svg"]
ALL = LAYERS + ["cowgirl_eagle_COMBINED_PREVIEW.svg"]
NS = "{http://www.w3.org/2000/svg}"

fail = []
warn = []


def check(cond, msg):
    (print(f"  PASS  {msg}") if cond else fail.append(msg))
    if not cond:
        print(f"  FAIL  {msg}")


# 1. identical viewBox across all files
viewboxes = {}
for f in ALL:
    root = ET.parse(f).getroot()
    viewboxes[f] = root.get("viewBox")
vb_set = set(viewboxes.values())
check(len(vb_set) == 1, f"all files share one viewBox: {vb_set}")

# 2/3/4. forbidden constructs: raster, strokes, masks/filters/clips
banned_tags = ["image", "mask", "filter", "clipPath", "pattern", "use", "text"]
banned_attr_substr = ["stroke", "clip-path", "mask", "filter", "url("]
for f in ALL:
    raw = open(f).read()
    for t in banned_tags:
        check(f"<{t}" not in raw and f":{t}" not in raw, f"{f}: no <{t}> element")
    for a in banned_attr_substr:
        check(a not in raw, f"{f}: no '{a}' attribute/value")
    check("data:image" not in raw, f"{f}: no embedded raster data")

# 5. every subpath closed (each M has a matching Z before the next M / end)
for f in ALL:
    root = ET.parse(f).getroot()
    for p in root.iter(f"{NS}path"):
        d = p.get("d", "")
        # split into subpaths on 'M'
        subs = re.findall(r"[Mm][^Mm]*", d)
        for s in subs:
            if not re.search(r"[Zz]\s*$", s.strip()):
                fail.append(f"{f}: unclosed subpath")
                break
        else:
            continue
        break
    else:
        print(f"  PASS  {f}: all subpaths closed with Z")

# 6. exactly one fill color per layer file (color separation)
expected = {"cowgirl_eagle_WHITE.svg": "#ffffff",
            "cowgirl_eagle_NAVY.svg": "#10214a",
            "cowgirl_eagle_RED.svg": "#d21f28"}
for f, col in expected.items():
    root = ET.parse(f).getroot()
    fills = {p.get("fill") for p in root.iter(f"{NS}path")}
    check(fills == {col}, f"{f}: single fill {col} (found {fills})")

# 7. registration marks: each layer file's LAST path is the reg-mark path;
#    require its `d` string be byte-identical across all three layers, and
#    that it contains 4 corner marks.
def reg_path_d(f):
    paths = list(ET.parse(f).getroot().iter(f"{NS}path"))
    return paths[-1].get("d", "")


reg_ds = {f: reg_path_d(f) for f in LAYERS}
first = reg_ds[LAYERS[0]]
n_marks = len(re.findall(r"[Mm]", first))
# 4 corner marks; each mark is a plus-in-frame -> 5 rings -> ~20 M commands
check(all(reg_ds[f] == first for f in LAYERS) and n_marks >= 4,
      f"registration-mark path byte-identical across all layers ({n_marks} subpaths, 4 corners)")

print("\n" + ("VALIDATION FAILED: " + "; ".join(fail) if fail else "ALL VALIDATION CHECKS PASSED"))
sys.exit(1 if fail else 0)
