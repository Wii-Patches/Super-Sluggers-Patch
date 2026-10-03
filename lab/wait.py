"""Scene detection by comparing a screen region against a reference screenshot."""
import sys, time; sys.path.insert(0, '.')
from PIL import Image, ImageChops
SH = '/Volumes/SSD/larsen/Documents/Git/Super-Sluggers-Patch/lab/shots/'
SCENES = {            # name: (reference file, crop box in the 640x508 window)
    'title':    ('c1.png', (190, 140, 450, 300)),
    'files':    ('s1x.png', (130, 160, 510, 260)),
    'main':     ('s5.png', (200, 120, 440, 160)),
    'main_prac': ('s6x.png', (30, 395, 350, 418)),
    'practice': ('o1.png', (190, 195, 450, 235)),
    'lesson':   ('t4.png', (130, 305, 510, 335)),
    'tutorial': ('k5.png', (230, 135, 410, 175)),
    'pullup':   ('g1.png', (335, 295, 420, 315)),
    'throw':    ('g2.png', (335, 295, 420, 315)),
}
def crop(path, box):
    return Image.open(path).convert('L').crop(box).resize((32, 24))
def score(l, scene):
    ref, box = SCENES[scene]
    l.shot(SH + 'w_now.png')
    a, b = crop(SH + ref, box), crop(SH + 'w_now.png', box)
    d = ImageChops.difference(a, b)
    return sum(d.getdata()) / (32 * 24)
def is_scene(l, scene, thr=14): return score(l, scene) < thr
def wait_scene(l, scene, timeout=600, thr=14):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if is_scene(l, scene, thr): return True
        time.sleep(5)
    return False

THR = {'pullup': 7, 'throw': 7, 'main_prac': 6}
def hit(sc):
    for s in ['throw', 'pullup', 'tutorial', 'lesson', 'main_prac', 'main', 'practice', 'files', 'title']:
        if sc[s] < THR.get(s, 16): return s
