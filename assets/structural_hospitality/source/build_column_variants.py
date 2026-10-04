"""Fit named shaft/capital elevations without rewriting arbitrary numeric tokens."""
from pathlib import Path
root=Path(__file__).resolve().parent
original=(root/'build_garden_column.py').read_text()
for suffix,height in [('H826',8.26),('H576',5.76),('H426',4.26),('H810',8.10)]:
 exec(compile(original,str(root/'build_garden_column.py'),'exec'),{'__file__':str(root/'build_garden_column.py'),'__name__':'__main__','TARGET_HEIGHT':height,'ASSET_SUFFIX':'-'+suffix})
