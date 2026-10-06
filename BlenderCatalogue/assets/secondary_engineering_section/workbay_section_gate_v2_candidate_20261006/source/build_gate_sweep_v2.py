"""Bounded revision of immutable section: gate fixed sweep clearance and solid stair contact."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,resource
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R.parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays/sectional-proposal/gate-sweep-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=json.loads((R/'source/gate_sweep_correction_plan.json').read_text());assert json.loads((R/'qa/pure_correction_check.json').read_text())['passed'];original=B/'source/AST-ENG-008_workbay_section_final.blend';oldglb=B/'exports/AST-ENG-008_workbay_section.glb';assert sha(original)=='fb251d356c93c27a4b19bb3eb877e9a45866c2cf94a0412f9f90829931f9a600';assert sha(oldglb)=='887f0f68604091c3600203cba42c1a371aef090c2be1419b3bbc185c99e5a041'
registry=json.loads((C/'catalogue_manifest.json').read_text());ids=[a['catalogue_id'] for a in registry['assets']];assert len(ids)==len(set(ids));assert next(a for a in registry['assets'] if a['catalogue_id']=='AST-ENG-008')['family']=='secondary_engineering_section'
inputpins={str(original):sha(original),str(oldglb):sha(oldglb)};bpy.ops.wm.open_mainfile(filepath=str(original));sc=bpy.context.scene;cv=lambda p:Vector((p[0],-p[2],p[1]));changed=[]
def metric_uv(ob):
 me=ob.data;me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.active;tile=me.materials[0].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
for name in ['CellGateOutsideHousing','CellGateButtonOutside']:
 ob=bpy.data.objects[name]
 for v in ob.data.vertices:v.co.x-=.11
 ob.data.update();changed.append(name)
bpy.data.objects['TARGET_CELL_GATE_OUTSIDE'].location.x-=.11
for z in [-405.14,-403.86]:
 name='CellStairHandrail'+str(z);ob=bpy.data.objects[name];a=cv((21.9,6.95,z));b=cv((22.8,6.5,z))
 for v in ob.data.vertices:
  if (v.co-a).length<(v.co-b).length:v.co+=cv((.06,-.03,0))
 metric_uv(ob);changed.append(name)
ob=bpy.data.objects['CONTACT_CellStairFlight'];oldmesh=ob.data;me=bpy.data.meshes.new('SourceBoundSolidFlightV2');me.from_pydata([cv(p) for p in P['stair_contact_vertices_xyz']],[],P['stair_contact_faces']);me.update()
for m in oldmesh.materials:me.materials.append(m)
me.uv_layers.new(name='MetreScaled');ob.data=me;metric_uv(ob);ob['solid_flight_bottom_y']=5.55;ob['solid_flight_contract']='Exact inclined top; triangular solid wedge bearing on lower floor, sole compiler underside remains5.31';changed.append(ob.name)
marker=bpy.data.objects['DATUM_CELL_STAIR_FLIGHT'];marker['solid_bottom_y']=5.55;marker['contact_policy']='source_bound_solid_flight_on_lower_floor'
if 'thickness_m'in marker:del marker['thickness_m']
for part in P['new_supported_parts']:
 x,y,z,X,Y,Z=part['bounds_xyz'];me=bpy.data.meshes.new(part['name']);me.from_pydata([cv(p) for p in [(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();ob=bpy.data.objects.new(part['name'],me);sc.collection.objects.link(ob);me.materials.append(bpy.data.materials['ASTRAEA_'+part['role']]);me.uv_layers.new(name='MetreScaled');ob['section_proposal_only']=True;ob['bay']='WORKBAY';ob['kind']='fixed_gate_control_pedestal';ob['collision_contract']='static_surface';ob['bearing_owner']=part['bearing_owner'];ob['bearing_y']=part['bearing_y'];metric_uv(ob)
 # Source contact markers are explicit and can be checked on actual export triangles.
 pos=[(x+X)/2,y,(z+Z)/2];mark=bpy.data.objects.new('CONTACT_'+part['name'],None);sc.collection.objects.link(mark);mark.location=cv(pos);mark['kind']='bearing';mark['owner']=part['bearing_owner'];mark['part']=part['name'];mark['normal_xyz']=[0,-1,0]
sc['narrow_revision']='gate_sweep_v2';sc['previous_candidate_immutable']=True;sc['scope']='Same approved section, gate-only fixed-clearance correction plus faithful solid stair contact; no Game writes'
bpy.context.view_layer.update();bpy.ops.file.pack_all();dest=R/'source/AST-ENG-008_workbay_section_gate_v2.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
sys.path.insert(0,str(R/'source'));from export_section_package import export_package
report=export_package(R,dest,['WEST_DIAGNOSTIC_WALL','WEST_FILTER_SKID','WEST_TASK_PROPOSAL'])
for path,h in inputpins.items():assert sha(path)==h,path
record={'source_sha256':sha(dest),'export_sha256':report['export_sha256'],'immutable_input_hashes':inputpins,'changed_parts':changed,'changed_marker':'TARGET_CELL_GATE_OUTSIDE','added_parts':[p['name'] for p in P['new_supported_parts']],'aperture_travel_gate_and120control_IDs_unchanged':True,'source_collision_top_unchanged':True,'stair_bottom_y':5.55,'gate_field_range_unchanged_m':2.5,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/build_gate_sweep_v2.json').write_text(json.dumps(record,indent=2)+'\n');print('GATE_SWEEP_V2_SOURCE_EXPORTED',record)
