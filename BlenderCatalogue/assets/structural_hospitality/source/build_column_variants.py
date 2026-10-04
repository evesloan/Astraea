"""Fit shaft height while retaining the authored base/capital proportions."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parent
original=(root/'build_garden_column.py').read_text()
for suffix,height in [('H826',8.26),('H576',5.76),('H426',4.26)]:
 prefix,tail=original.split('scene=bpy.context.scene',1)
 prefix=re.sub(r'\b\d+\.\d+\b',lambda m:str(round(float(m[0])+height-8.13,6)) if float(m[0])>=6.4 else m[0],prefix)
 text=prefix+'scene=bpy.context.scene'+tail
 text=text.replace("source/AST-STR-001.blend",f"source/AST-STR-001-{suffix}.blend").replace("exports/AST-STR-001.glb",f"exports/AST-STR-001-{suffix}.glb").replace("'AST-STR-001.manifest.json'",f"'AST-STR-001-{suffix}.manifest.json'").replace("'height_m':8.13",f"'height_m':{height}").replace("'fits_deck_pitch_m':8.5",f"'fits_deck_pitch_m':{height+.24}")
 exec(compile(text,str(root/'build_garden_column.py'),'exec'),{'__file__':str(root/'build_garden_column.py'),'__name__':'__main__'})
