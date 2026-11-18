"""Line up Boing's pose pictures and pack them for the game.

Put one picture per pose in art/boing/poses/ named after the pose:
  rise.png apex.png fall.png land.png slam.png dead.png win.png
Transparent PNGs are best. A flat background (white, grey, green) is keyed out
from the corner colour if there is no transparency.

Needs:  pip install pillow numpy scipy
Run:  python3 tools/pack_sprites.py
It scales every pose so his silhouette covers the same area (squash and
stretch keep volume), and centres the middle of his body (the biggest circle
that fits inside his silhouette). The landing pose is anchored by its feet. Output:
  art/boing/game/<pose>.png      512x512 aligned poses (for checking in Photoshop)
  art/boing/game/sheet.png       all poses side by side, 256px cells
  art/boing/game/sprites.json    anchor data the game uses
Then run with --embed to write them into index.html (as small WebP data).
"""
import sys, json, io, base64, re, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'art/boing/poses', ROOT / 'art/boing/game'
POSES = ['rise', 'apex', 'fall', 'land', 'slam', 'dead', 'win']
CANVAS, BODY_R, GAME = 512, 0.24, 256  # body circle radius as a fraction of the canvas

def load_alpha(path):
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    if a[..., 3].min() == 255:  # no transparency: key out the corner colour
        rgb = a[..., :3].astype(int)
        bg = np.median(np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[-8:, -8:].reshape(-1, 3)]), 0)
        d = np.abs(rgb - bg).sum(-1)
        a[..., 3] = np.clip((d - 20) * 6, 0, 255).astype(np.uint8)
        im = Image.fromarray(a)
    return im, a[..., 3] > 128

def body_circle(mask):
    # keep the biggest blob (drops stray stars, sweat drops, etc.)
    lab, n = ndimage.label(mask)
    if n > 1:
        sz = ndimage.sum(mask, lab, range(1, n + 1))
        mask = lab == (np.argmax(sz) + 1)
    mask = ndimage.binary_fill_holes(mask)
    dist = ndimage.distance_transform_edt(mask)
    cy, cx = np.unravel_index(np.argmax(dist), dist.shape)
    return cx, cy, dist[cy, cx]

GROUNDED = {'land'}  # poses drawn with their feet on the ground instead of centred on the body
SQRT_AREA = 0.5     # every pose gets the same silhouette area (squash and stretch keep volume)

def align(path, pose):
    im, mask = load_alpha(path)
    lab, n = ndimage.label(mask)
    if n > 1:
        sz = ndimage.sum(mask, lab, range(1, n + 1))
        mask = lab == (np.argmax(sz) + 1)
    mask = ndimage.binary_fill_holes(mask)
    cx, cy, _ = body_circle(mask)
    k = SQRT_AREA * CANVAS / mask.sum() ** 0.5
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    out = Image.new('RGBA', (CANVAS, CANVAS))
    ox, oy = round(CANVAS / 2 - cx * k), round(CANVAS / 2 - cy * k)
    out.paste(im, (ox, oy), im)
    ay = 0.5
    if pose in GROUNDED:  # put the lowest point of the body one body-radius below the anchor
        ys = np.nonzero(mask)[0]
        ay = (oy + ys.max() * k - BODY_R * CANVAS) / CANVAS
    return out, ay

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    found = [p for p in POSES if (SRC / f'{p}.png').exists()]
    if not found:
        sys.exit(f'No poses found in {SRC}')
    sheet = Image.new('RGBA', (GAME * len(found), GAME))
    meta = {}
    for i, p in enumerate(found):
        a, ay = align(SRC / f'{p}.png', p)
        a.save(OUT / f'{p}.png')
        sheet.paste(a.resize((GAME, GAME), Image.LANCZOS), (i * GAME, 0))
        meta[p] = {'w': GAME, 'h': GAME, 'cx': 0.5, 'cy': round(ay, 4), 'r': BODY_R}
        print(f'{p}: aligned')
    sheet.save(OUT / 'sheet.png')
    (OUT / 'sprites.json').write_text(json.dumps(meta, indent=1))
    if '--embed' in sys.argv:
        embed(found, meta)

def embed(found, meta):
    html = (ROOT / 'index.html').read_text()
    sprd = json.loads(re.search(r'SPRD=(\{.*?\});\n', html).group(1))
    for p in found:
        buf = io.BytesIO()
        Image.open(OUT / f'{p}.png').resize((GAME, GAME), Image.LANCZOS).save(buf, 'WEBP', quality=90)
        sprd[p] = dict(meta[p], uri='data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())
    html = re.sub(r'SPRD=\{.*?\};\n', lambda m: 'SPRD=' + json.dumps(sprd) + ';\n', html, count=1)
    (ROOT / 'index.html').write_text(html)
    print('Embedded into index.html:', ', '.join(found))

if __name__ == '__main__':
    main()
