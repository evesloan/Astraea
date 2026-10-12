from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[3];P=json.loads((W/'TERMINAL_PLAN.json').read_text())
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in P['source_pins'].items())
F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';family='group4_terminal_branch_edges_009'
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0].replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name",'OUT=W;FAMILY=family').replace("assert FAMILY=='group4_tram_connections_20261009'",'').replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=['AST-TRM-G4-027']").replace("['FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO']","['TERMINAL_BRANCH_EDGES','UNEXPORTED_REFERENCE_AND_STUDIO']")
exec(sc,globals());current=collections['TERMINAL_BRANCH_EDGES'];fixture_rows=[]
with bpy.data.libraries.load(str(R/P['source_lantern_native']),link=False)as(src,dst):dst.objects=src.objects
original=[o for o in dst.objects if o];source_meshes=[o for o in original if o.type=='MESH'];assert len(source_meshes)==8
exit_source=next(o for o in original if o.name=='DATUM_light_exit')
for q in P['terminals']:
 label=q['label'];z=q['center_z']
 for j,s in enumerate(q['new_floor_strips']):
  for i,t in enumerate(s['triangles_xz']):
   vs=[(x,y,zz) for y in [52.26,52.5] for x,zz in t]
   mesh(label+'_MissingOnlyEdge_'+str((j,i)),vs,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],stone,'additive outboard edge; retained4m floor untouched')
 for side in [-1,1]:
  zz=z+side*2.35
  box(label+'_EdgeLedger_'+str(side),(-6,52.32,z+side*2.125),(4,.08,.75),metal,'positive original floor-depth lap; no new lower programme column')
  for x in [-7.88,-6,-4.12]:
   box(label+'_GuardShoe_'+str((side,x)),(x,52.55,zz),(.16,.20,.20),ivory,'edge shoe embeds new ledger/floor')
   tube(label+'_GuardPost_'+str((side,x)),(x,52.5,zz),(x,53.65,zz),.045,metal,'guard outside exact4m route')
  box(label+'_GuardPanel_'+str(side),(-6,53.06,zz),(3.76,.90,.04),glass,'outboard infill,4m existing route remains clear')
  tube(label+'_GuardRail_'+str(side),(-7.88,53.65,zz),(-4.12,53.65,zz),.05,metal,'weighted continuous terminal handrail')
 for s in q['source_lanterns']:
  x,y,zz=s['origin'];box(s['name']+'_Foot',(x,52.55,zz),(.24,.20,.12),metal,'original/new terminal floor-edge lap receiver')
  box(s['name']+'_Pier',(x,53.85,zz-.025),(.12,2.70,.10),ivory,'fixture mast wholly outside4m route')
  box(s['name']+'_Mount',(x,y+.45,zz-.0125),(.46,.90,.035),metal,'full original backplate receiving;20mm overlap')
  T=Matrix.Translation(Vector(B(s['origin'])))@Matrix.Rotation(s['yaw'],4,'Z')
  for orig in source_meshes:
   ob=orig.copy();ob.data=orig.data.copy();ob.parent=None;ob.name=s['name']+'__'+orig.name;ob.matrix_world=T@orig.matrix_world;current.objects.link(ob)
   ob['collision_policy']='no_collision_detail';ob['source_fixture']='AST-LGT-001';parts.append(ob)
  emitter=G(T@exit_source.matrix_world.translation);marker(s['name']+'__LightExit',emitter,'exact original DATUM_light_exit; existing shadow budget')
  fixture_rows.append({'name':s['name'],'origin':s['origin'],'yaw':s['yaw'],'emitter':emitter,'range':6.0,'energy':.55,'color':[1,.90,.76]})
for ob in original:bpy.data.objects.remove(ob,do_unlink=True)
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0 and not im.packed_file:im.pack()
bpy.ops.object.select_all(action='DESELECT')
for o in current.objects:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(W/P['asset']),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
bpy.ops.wm.save_as_mainfile(filepath=str(W/P['native']),compress=True)
rows=[]
for ob in parts:
 ps=[G(ob.matrix_world@v.co) for v in ob.data.vertices];rows.append({'mesh':ob.name,'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)],'policy':ob['collision_policy']})
(W/'TERMINAL_INTERFACE.json').write_text(json.dumps({'asset':P['asset'],'native':P['native'],'fixture_instances':fixture_rows,'meshes':rows,'source_only':True,'terminals':P['terminals']},indent=2)+'\n');print('TERMINAL_BRANCH_SOURCE_BUILT',len(parts),'meshes;32 exact source fixture meshes,4 source exits')
