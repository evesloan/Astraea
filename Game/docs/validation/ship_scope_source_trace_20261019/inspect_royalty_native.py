import bpy,json,hashlib,pathlib
root=pathlib.Path('/workspace/Astraea')
src=root/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 # Native z-up to Godot y-up.
 pts=[[float(v.x),float(v.z),float(-v.y)] for v in vs]
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if 'RoyaltyLowerRoof' in o.name or (lo[0]<104 and hi[0]>94.5 and lo[2]<49.5 and hi[2]>40 and lo[1]<107 and hi[1]>105.5):
  o.data.calc_loop_triangles()
  rows.append({'name':o.name,'bounds_world':[lo,hi],'vertices':len(vs),'triangles':len(o.data.loop_triangles),'materials':[m.name for m in o.data.materials if m], 'props':{k:str(o[k]) for k in o.keys()},'world_vertices':pts if 'RoyaltyLowerRoof' in o.name else None})
out={'native_path':str(src.relative_to(root)),'native_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'read_only':True,'coordinate_conversion':'x,z,-y','parts_intersecting_circulation_height_bbox':rows}
pathlib.Path('/workspace/ship-scope-reconciliation-20261019/ROYALTY790_NATIVE_INSPECTION.json').write_text(json.dumps(out,indent=2)+'\n')
print('NATIVE_INSPECTION',out['native_sha256'],'candidate_parts',len(rows))
