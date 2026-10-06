"""Parent-coordinated standalone source adapter, NOT EXECUTED in preparation.

python -B build_court_A_source_DRAFT.py --inspect is safe pure JSON inspection.
Blender --python ... -- --build requires a separately supplied parent gate and
finished original artwork. This file never exports a GLB or touches Game.
"""
from pathlib import Path
import argparse,json,hashlib,sys
R=Path(__file__).resolve().parent
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
P=C/'assets/grand_lantern_theater_section'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def build():
 contract=read(R/'COURT_A_GEOMETRY_CONTRACT.json');screen=read(R/'COURT_A_PURE_SCREEN.json')
 assert screen['contract_sha256']==sha(R/'COURT_A_GEOMETRY_CONTRACT.json')
 assert not screen['failures'] and not screen['warnings']
 gate=read(R/'PARENT_SOURCE_BUILD_GATE.json')
 assert gate['parent_authorized_scratch_source_job'] is True
 assert gate['static_stage_checkpoint_verified'] is True
 assert gate['source_job_slot_granted'] is True
 assert gate['production_install_authorized'] is False
 assert sha(contract['base_source'])==contract['base_source_sha256']
 # Art must be prepared/reviewed as original work, not a fallback blank.
 art=Path(gate['original_programme_png']).resolve()
 assert art.is_relative_to(R) and sha(art)==gate['original_programme_png_sha256']
 outdir=R/'authored_preview001';outdir.mkdir(exist_ok=True)
 output=outdir/contract['standalone_source_proposal']
 report=outdir/'BUILD_REPORT.json'
 assert not output.exists() and not report.exists()
 import bpy
 sys.path.insert(0,str(P/'source/firstpass_001'))
 from firstpass_common import bvec,verify_new_geometry,mesh_record,digest
 import build_firstpass_assembly as source_tools
 bpy.ops.wm.read_factory_settings(use_empty=True)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 collection=bpy.data.collections.new('A4_COMPLETED_COURT');scene.collection.children.link(collection)
 root=bpy.data.objects.new('A4_SOURCE_ONLY',None);collection.objects.link(root)
 root['catalogue_id']='AST-CUL-005';root['derivative_id']='arrival_court_A_004'
 root['base_source_sha256']=contract['base_source_sha256'];root['standalone_addition']=True
 root['visual_acceptance']=False;root['runtime_installed']=False
 source_tools.ROOT=root;source_tools.BASE_MATS=[]
 definitions={};definition_records=[]
 measurements={r['asset']:{'source':str(Path(r['source']).relative_to(C)),'source_sha256':r['source_sha256'],'bounds_gltf':None}for r in contract['retained_instances']}
 a=R.parents[1];measured=read(a.parent/'RETAINED_MODULE_MEASUREMENTS.json');measured.update(read(a/'RETAINED_FOCAL_ASSET_BOUNDS.json'))
 for ident in sorted(measurements):
  definitions[ident]=source_tools.load_definition(ident,measured);definition_records.append(definitions[ident][2])
 # Append actual retained graphs, including packed images. No reconstructed
 # substitute graph and no edits to material datablocks in other source files.
 mat_sources=[C/'assets/furniture/AST-FUR-001_day_window_bench.blend',C/'assets/furniture/AST-FUR-002_day_reading_chair.blend',C/'assets/botanical_planter/AST-BOT-004.blend',C/'assets/botanical_understory/source/AST-BOT-002.blend']
 mats={};material_provenance={}
 def exact_material(role):
  if role in mats:return mats[role]
  for path in mat_sources:
   with bpy.data.libraries.load(str(path),link=False)as(src,dst):
    names=[n for n in src.materials if n in[role,'ASTRAEA_'+role]]
    dst.materials=names[:1]
   if names:
    mat=dst.materials[0];assert mat and mat.get('astraea_material_role',role)==role
    mats[role]=mat;material_provenance[role]={'source':str(path),'source_sha256':sha(path),'requested_datablock':names[0]};return mat
  raise AssertionError('Retained material graph missing: '+role)
 for role in contract['material_contracts']:exact_material(role)
 names=[]
 def mesh(name,vertices,faces,role,face_uv,properties):
  assert bpy.data.objects.get(name) is None
  me=bpy.data.meshes.new(name+'_editable');me.from_pydata([bvec(v)for v in vertices],[],faces);me.update()
  me.materials.append(exact_material(role));uv=me.uv_layers.new(name='MetricUV');uv.active_render=True
  assert len(me.polygons)==len(face_uv)
  for f,coords in zip(me.polygons,face_uv):
   assert len(f.loop_indices)==len(coords)
   for li,p in zip(f.loop_indices,coords):uv.data[li].uv=p
  ob=bpy.data.objects.new(name,me);collection.objects.link(ob);ob.parent=root
  for k,v in properties.items():ob[k]=v if isinstance(v,(str,int,float,bool))else json.dumps(v)
  names.append(name);return ob
 for row in contract['objects']:
  mesh(row['name'],row['vertices_world'],row['faces'],row['material_family'],row['face_uv'],{k:v for k,v in row.items()if k not in['vertices_world','faces','face_uv']})
 for row in contract['retained_instances']:
  ob=source_tools.instance(definitions[row['asset']][0],row['id'],row['position_world'],row['yaw_radians'])
  for col in list(ob.users_collection):col.objects.unlink(ob)
  collection.objects.link(ob);ob['source_sha256']=row['source_sha256'];ob['retained_family']=row['asset'];ob['whole_plant_or_furniture_scale_unchanged']=True
  if'root_receiver'in row:ob['root_receiver']=row['root_receiver'];ob['collides']=False
 # Optional fuller mass is a Court-A-specific new derivative, never a loaded
 # pool asset. Its own source reopen + material/soil test is still required.
 fuller=None
 if gate.get('include_fuller_rear_mass',False):
  fuller=read(R/'FULLER_REAR_MASS_CANDIDATE.json');asset=fuller['asset'];origin=asset['position_xyz']
  assert fuller['status']=='PASS_PURE_SOIL_FIT_ONLY_UNBUILT_UNRETAINED'
  for p in asset['parts']:
   verts=[[origin[0]+v[0],origin[1]+v[2],origin[2]-v[1]]for v in p['vertices']]
   coords=[];i=0
   for f in p['faces']:coords.append(p['loop_uvs'][i:i+len(f)]);i+=len(f)
   mesh(p['name'],verts,p['faces'],p['material_role'],coords,{'collides':False,'material_family':p['material_role'],'surface_kind':p['surface_kind'],'source_method':'Retained BOT-002 formula; Court A fitted derivative','root_receiver':asset['support'],'shape_controls':p['shape_controls']})
 # Original graphic face on the already modelled bearing/frame.
 im=bpy.data.images.load(str(art));im.pack();mat=bpy.data.materials.new('A4_original_programme');mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.84
 node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;node.extension='EXTEND';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 mats['court_A_original_programme']=mat
 lo,hi=contract['original_programme_art']['bounds_world']
 # A 5 mm printed plate; all six sides have explicit UVs, front is full art.
 vs=[[x,y,z]for z in[lo[2],hi[2]]for x,y in[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
 faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 mesh('A4_original_programme_face',vs,faces,'court_A_original_programme',[[[0,0],[1,0],[1,1],[0,1]]for f in faces],{'collides':False,'semantic_id':'D11.CourtA.Completion004.original_programme','original_art_sha256':sha(art)})
 # The parent may add two coherent low-cost programme stacks on the measured
 # tabletop/counter contacts; do not block the retained low writing wing.
 scene['court_A_status']='Source-only additive draft; composed visual/native gates pending'
 assert sha(contract['base_source'])==contract['base_source_sha256']
 assert not any(o.get('existing_family')=='AST-CUL-003'for o in scene.objects)
 # Verify closed architecture separately; botanical leaves are intentionally open.
 checks=verify_new_geometry(bpy,[r['name']for r in contract['objects']])
 signatures={o.name:digest(mesh_record(o.data))for o in collection.objects if o.type=='MESH'}
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
 result={'status':'STANDALONE_SOURCE_BUILT_REOPEN_VISUAL_NATIVE_UNACCEPTED','source':str(output),'sha256':sha(output),'protected_base_sha256':sha(contract['base_source']),'geometry_checks':checks,'mesh_uv_fingerprints':signatures,'retained_definitions':definition_records,'material_provenance':material_provenance,'original_art_sha256':sha(art),'fuller_mass_included':bool(fuller),'audience_chairs_rebuilt_or_exported':0,'runtime_exported':False}
 report.write_text(json.dumps(result,indent=2)+'\n')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--inspect',action='store_true');parser.add_argument('--build',action='store_true')
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:])
 if args.build:build()
 else:
  c=read(R/'COURT_A_GEOMETRY_CONTRACT.json');print(json.dumps({'mode':'UNRUN_BUILDER_DRAFT_INSPECTION','objects':len(c['objects']),'retained_instances':len(c['retained_instances']),'requires':'Parent-coordinated source slot, static checkpoint, original art PNG; scratch only','output':str(R/'authored_preview001'/c['standalone_source_proposal'])},indent=2))
if __name__=='__main__':main()
