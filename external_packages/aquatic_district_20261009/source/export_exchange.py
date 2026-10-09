"""Re-export saved editable native without rebuilding or changing source geometry."""
import bpy,json,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'source/aquatic_district.blend'))
s=importlib.util.spec_from_file_location('builder',P/'source/build_aquatic.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=json.loads((P/'qa/source_geometry.json').read_text())
for name in names:
 o=bpy.data.objects[name]
 (m.F if o.get('kind')=='compiler_floor_proposal' else m.A).append(o)
m.A.extend(o for o in bpy.context.scene.objects if o.type=='EMPTY' and o.name.startswith('DATUM_'))
m.export_exchange()
