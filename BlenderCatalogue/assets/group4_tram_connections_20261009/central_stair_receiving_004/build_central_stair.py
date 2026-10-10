from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';P=json.loads((W/'RECEIVING_PLAN.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in P['retained_source_pins'].items())
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0]
sc=sc.replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name","OUT=W;FAMILY='group4_central_stair_receiving_004'").replace("assert FAMILY=='group4_tram_connections_20261009'",'')
sc=sc.replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=['AST-TRM-G4-018']")
sc=sc.replace("'FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'","'CENTRAL_STAIR_RECEIVING_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'")
sc=sc.replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)","bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor c in list(bpy.data.collections):bpy.data.collections.remove(c)")
exec(sc,globals());current=collections['CENTRAL_STAIR_RECEIVING_SOURCE']
for q in P['boxes']:
 ob=box(q['name'],q['center'],q['size'],ivory if q['name'].endswith('_Pier') else metal,q['role']);ob['target_source_mesh']=q['target_source_mesh'] or ''
for q in P['inclined_shoes']:
 top=q['upper_corners_xyz'];vs=[(x,y-q['thickness_m'],z) for x,y,z in top]+[tuple(p) for p in top];ob=mesh(q['name'],vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],metal,'closed source-plane-matched inclined receiving shoe');ob['target_source_mesh']=q['target_source_mesh']
for q in P['positive_floor_contacts']:marker(q['member']+'_EXACT_RECEIVER',q['center_xyz'],q['contacts'][0]['owner']+'; complete0.128m² positive footprint')
file='AST-TRM-G4-018_central_stair_receiving.glb';bpy.ops.object.select_all(action='DESELECT')
for ob in current.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=next(iter(current.objects));bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
rows=[]
for ob in parts:
 ps=[G(ob.matrix_world@v.co) for v in ob.data.vertices];rows.append({'mesh':ob.name,'role':ob['role'],'policy':ob['collision_policy'],'target_source_mesh':ob.get('target_source_mesh',''),'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)],'faces':len(ob.data.polygons)})
(W/'MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n')
meta={k:v for k,v in P.items() if k not in ['boxes','inclined_shoes']};meta.update(asset=file,native='Group4_Central_Stair_Receiving_004.blend',editable_member_count=len(parts),source_material_pins=texture_pins,operating_gate='NONE supplied; retain existing parent-owned cabin/controller/door/bridge bindings',structural_gate='Geometric source receivers only; existing slab/primary-hull capacity, deflection/vibration and actual-main receiving remain open')
(W/'MODULE_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(W/meta['native']),compress=True);print('CENTRAL_STAIR_RECEIVING_EXPORTED',len(parts),'members',len(P['positive_floor_contacts']),'retained-floor contacts')
