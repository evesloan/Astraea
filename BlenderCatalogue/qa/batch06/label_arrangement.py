"""Add a provenance footer outside the unchanged component-render pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'qa/batch06/arrangement'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
rows = []
for name in ('overview_1280', 'standing_640', 'operator_controls_640'):
    path = OUT / (name + '.png')
    source = Image.open(path).convert('RGB')
    large = source.width > 1000
    height = 72 if large else 56
    image = Image.new('RGB', (source.width, source.height + height), '#18262c')
    image.paste(source, (0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 18 if large else 12)
    lines = [
        'ASTRAEA | Engineering utilities | Imported-component QA',
        'Blender render. Controls, flow and game integration remain unimplemented.',
    ] if large else [
        'ASTRAEA | Imported-component QA | ' + ('Standing view' if name == 'standing_640' else 'Control approach'),
        'Blender render. Controls, flow and game integration pending.',
    ]
    for i, text in enumerate(lines):
        draw.text((14 if large else 10, source.height + 11 + i * (25 if large else 18)), text, font=font, fill='#e2edf0')
    target = OUT / (name + '_labelled.png')
    image.save(target)
    assert image.crop((0, 0, source.width, source.height)).tobytes() == source.tobytes()
    rows.append({'source': str(path.relative_to(ROOT)), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'labelled': str(target.relative_to(ROOT)), 'labelled_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'render_pixels_unchanged': True})
(OUT / 'labelled_media.json').write_text(json.dumps(rows, indent=2) + '\n')
