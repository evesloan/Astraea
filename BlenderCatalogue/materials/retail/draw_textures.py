"""Original small matte enamel role for recessed public retail construction."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parent
random_source = random.Random(1801)
image = Image.new('RGB', (256, 256))
pixels = image.load()
base = (184, 81, 39)
# Restrained coat variation; no sampled photographs, fake seams or cloth weave.
patches = [[random_source.choice((-2, -1, 0, 0, 1, 2)) for _ in range(32)] for _ in range(32)]
for y in range(256):
    for x in range(256):
        variation = patches[y // 8][x // 8] + random_source.choice((-1, 0, 0, 0, 1))
        pixels[x, y] = tuple(max(0, min(255, channel + variation)) for channel in base)
path = ROOT / 'retail_terracotta_enamel.png'
image.save(path)
manifest = {
    'revision': 'retail-original-01',
    'original_source': 'draw_textures.py',
    'provenance': 'Original deterministic painted enamel texture for the authorized catalogue; no reference pixels or external assets',
    'materials': {
        'retail_terracotta_enamel': {
            'file': path.name,
            'colour_srgb_8bit': list(base),
            'texture_pixels': [256, 256],
            'meters_per_tile_uv': [0.9, 0.9],
            'roughness': 0.68,
            'metallic': 0.0,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'intent': 'Warm recessed public-shop construction. Meaningful joins and profile depth belong to the mesh; subtle coat variation does not replace authored structure.',
        },
    },
}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
