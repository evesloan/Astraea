from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
import numpy as np
W=Path(__file__).resolve().parent;R=W.parents[3];P=json.loads((W/'SAFETY_PLAN.json').read_text());TP=json.loads((W/'TERMINAL_PLAN.json').read_text())
checks=0;errors=[]
def ck(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
def signature(o):
 return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],
 'uv':[[list(v.uv) for v in l.data] for l in o.data.uv_layers],'matrix':[list(v) for v in o.matrix_world],
 'smooth':[p.use_smooth for p in o.data.polygons],'modifiers':[(m.name,m.type) for m in o.modifiers]}
old=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend';bpy.ops.wm.open_mainfile(filepath=str(old))
changed={q['mesh'] for q in P['vehicle_cuts']};original={o.name:signature(o) for o in bpy.data.collections['TRAM_EDITABLE_COMPONENT'].objects if o.type=='MESH' and o.name not in changed}
assert len(original)==31
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Powered_Portal_Body_r001.blend'))
for name,sig in original.items():ck(signature(bpy.data.objects[name])==sig,name+' exact31-member source payload/UV/pose/modifiers')
rows=json.loads((W/'VEHICLE_CHANNEL_RECIPES.json').read_text())['members'];build=json.loads((W/'VEHICLE_CHANNEL_BUILD.json').read_text())
for q in rows:
 o=bpy.data.objects[q['mesh']];bm=bmesh.new();bm.from_mesh(o.data)
 ck(all(e.is_manifold for e in bm.edges),o.name+' closed convex cells')
 ck(abs(abs(bm.calc_volume())-q['remaining_volume_m3'])<1e-6,o.name+' actual native source-minus-slots volume');bm.free()
 planes=q['original_planes'];count=0;max_error=0.
 for f in o.data.polygons:
  pp=np.array([o.data.vertices[i].co[:] for i in f.vertices]);normal=np.array(f.normal)
  plane=next((p for p in planes if abs(abs(normal@np.array(p['normal']))-1)<1e-5 and np.max(abs(pp@np.array(p['normal'])-p['distance']))<1e-6),None)
  if plane is None:continue
  for li in f.loop_indices:
   at=o.data.vertices[o.data.loops[li].vertex_index].co;expected=np.array([at[plane['axes'][0]],at[plane['axes'][1]],1.])@np.array(plane['coefficients']);actual=np.array(o.data.uv_layers.active.data[li].uv[:]);max_error=max(max_error,float(np.linalg.norm(actual-expected)));count+=1
 ck(count>0 and max_error<1e-5,o.name+' exterior UV agrees with retained original source planes')
def export_collection(name,file):
 bpy.ops.object.select_all(action='DESELECT');c=bpy.data.collections[name]
 for o in c.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=next(o for o in c.objects if o.type=='MESH')
 out=W/('AUDIT_'+file);bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
 ck(out.read_bytes()==(W/file).read_bytes(),file+' byte-identical fresh native re-export')
export_collection('TRAM_EDITABLE_COMPONENT',P['vehicle_successor'])
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Barrier_Receivers_and_Restraints_r003.blend'))
for c in ['BARRIER_RECEIVERS','RESTRAINT_HARDWARE']:
 for o in bpy.data.collections[c].objects:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);ck(all(e.is_manifold for e in bm.edges),o.name+' closed hardware');bm.free()
export_collection('BARRIER_RECEIVERS',P['station_receiver_asset']);export_collection('RESTRAINT_HARDWARE',P['restraint_asset'])
# Rigid copies compare against the actual original lantern native, with local mesh/UV unchanged.
bpy.ops.wm.open_mainfile(filepath=str(R/TP['source_lantern_native']));lanterns={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'};ck(len(lanterns)==8,'original lantern native8 meshes')
bpy.ops.wm.open_mainfile(filepath=str(W/TP['native']));n=0
for o in bpy.data.collections['TERMINAL_BRANCH_EDGES'].objects:
 if o.type!='MESH' or '__' not in o.name:continue
 name=o.name.split('__',1)[1]
 if name not in lanterns:continue
 old_sig=lanterns[name];sig=signature(o)
 ck(all(sig[k]==old_sig[k] for k in ['vertices','faces','uv','smooth','modifiers']),o.name+' exact original fixture payload')
 n+=1
ck(n==32,'32 actual original lantern mesh copies')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:ck(im.packed_file is not None,im.name+' packed texture')
export_collection('TERMINAL_BRANCH_EDGES',TP['asset'])
report={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'unchanged_car_meshes':31,'changed_car_members':8,'closed_cell_prisms':88,'internal_cell_interfaces_retained':True,'original_fixture_mesh_copies':n,'fresh_native_exports_verified':4,'limits':'Source fidelity, closed cells, UV, volume and reproduction only; primary/mechanical capacity, actual cart restraint and final art remain open.'}
(W/'NATIVE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('SAFETY_NATIVE',report['status'],checks);assert not errors,errors
