"""Aquatic native/export inspector. Reads retained sources, writes only this delivery's QA."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
items={
 'grand_pool':('BlenderCatalogue/assets/grand_pool_orchard_section/source/AST-AQU-016.blend',(0,0,0)),
 'gentle_arrival':('BlenderCatalogue/assets/aquatic_arrival/source/AST-AQU-014.blend',(8,44,210)),
 'receiver':('BlenderCatalogue/assets/vesper_watercourse/source/AST-AQU-015.blend',(21.5,61,207)),
 'thermal':('external_packages/sol_entry_successors_20261008/D/D08_directory_02/source/section.blend',(0,0,0)),
 'mineral':('external_packages/sol_entry_successors_20261008/D/D08_directory_03/source/section.blend',(0,0,0))}
out={}
for k,(n,origin) in items.items():
 bpy.ops.wm.open_mainfile(filepath=str(R/n));rows=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  worlds=[(v.x+origin[0],v.z+origin[1],-v.y+origin[2]) for v in vs]
  rows.append({'name':o.name,'world_min':[min(v[a] for v in worlds) for a in range(3)],'world_max':[max(v[a] for v in worlds) for a in range(3)],'vertices':len(o.data.vertices)})
 out[k]={'path':n,'placement':origin,'mesh_count':len(rows),'objects':rows}
(P/'qa/retained_native_inspection.json').write_text(json.dumps(out,indent=2))
print('Read five current native assemblies; did not save or change them.')
