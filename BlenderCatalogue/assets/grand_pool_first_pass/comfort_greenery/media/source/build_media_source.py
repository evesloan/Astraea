"""SOURCE ONLY. Launch only in the parent-issued Blender two-thread slot.
blender --background --threads 2 --python-exit-code 1 --python source/build_media_source.py -- --allow-source-build
No export/render/import of a candidate into itself; no original-source/export or Game writes.
"""
from pathlib import Path
import sys,json,hashlib
import bpy,bmesh
from mathutils import Matrix
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from blender_media_common import root_matrix,metric_uv,evaluated_geometry,material_state,sha
from media_paths import CAT,resolve_pin,new_catalogue_writes
ARGS=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
assert '--allow-source-build'in ARGS,'Parent-issued source slot must be explicit'
assert bpy.app.background,'Use an isolated background source process'
OUT=ROOT/'source/AST-LIB-010_pool_leisure_displays.blend'
assert not OUT.exists(),'Refusing to overwrite a surviving source candidate; retain it and choose a new revision first'
C=json.loads((ROOT/'source_contract.json').read_text());PINS=json.loads((ROOT/'dependency_pins.json').read_text());ART=json.loads((ROOT/'content_manifest.json').read_text())
for p,h in PINS.items():assert sha(resolve_pin(p))==h,('changed retained dependency',p)
assert C['export_status']=='PROHIBITED_PENDING_SOURCE_QA_AND_INDEPENDENT_RETENTION'
for a in ART['material_roles'].values():
 assert sha(ROOT/a['file'])==a['sha256'];assert sha(ROOT/a['svg_source'])==a['svg_sha256']
SRC=CAT/'assets/library_use/source/AST-LIB-010.blend'
assert OUT.resolve()!=SRC.resolve()
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2
# Load actual named source parts to derive material and component provenance.
# Link and update before matrix_world or evaluated-mesh inspection.
refs=bpy.data.collections.new('READ_ONLY_LIB010_PROTOTYPES');scene.collection.children.link(refs)
lineages=sorted({p['lineage_object']for c in C['candidates']for p in c['parts']if p['kind']!='art'})
with bpy.data.libraries.load(str(SRC),link=False)as(src,dst):
 assert set(lineages)<=set(src.objects),('missing lineage objects',set(lineages)-set(src.objects));dst.objects=lineages
for ob in dst.objects:refs.objects.link(ob)
bpy.context.view_layer.update();M={};provenance=[]
for ob in dst.objects:
 for mat in ob.data.materials:
  role=mat.get('astraea_material_role') or ob.get('semantic_role')
  if role in ['ivory_enamel','warm_walnut','dark_rubber','champagne_metal','display_glass']:M[role]=mat
 coords=[list(ob.matrix_world@v.co)for v in ob.data.vertices]
 provenance.append({'source_object':ob.name,'source_file_relative_catalogue':str(SRC.relative_to(CAT)),'source_sha256':sha(SRC),'actual_source_world_matrix':[list(row)for row in ob.matrix_world],'source_vertex_count':len(coords),'source_face_count':len(ob.data.polygons),'source_coordinate_sha256':hashlib.sha256(json.dumps(coords,separators=(',',':')).encode()).hexdigest(),'material_roles':[m.get('astraea_material_role')for m in ob.data.materials],'interpretation':'Retained named construction prototype; dimensions re-authored as editable profiles, never complete-terminal scaling'})
assert set(M)=={'ivory_enamel','warm_walnut','dark_rubber','champagne_metal','display_glass'}
BASELINE={k:material_state(v)for k,v in M.items()}
for ob in list(refs.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(refs)
for role,a in ART['material_roles'].items():
 m=bpy.data.materials.new('ASTRAEA_POOL_LEISURE_'+role);m.use_nodes=True;m['astraea_material_role']=role;m['source_content_file']=a['file'];m['source_content_sha256']=a['sha256'];m['uv_mapping']='single original artwork, UV0..1';m['static_noninteractive']=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.34;bs.inputs['Metallic'].default_value=0.;bs.inputs['Alpha'].default_value=1.
 im=bpy.data.images.load(str(ROOT/a['file']),check_existing=False);im.name='POOL_ORIGINAL_'+role;im.pack();im['original_content_sha256']=a['sha256']
 tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.name='Original packed resort artwork';tx.image=im;tx.interpolation='Linear';tx.extension='EXTEND';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 emission=bs.inputs.get('Emission Color') or bs.inputs.get('Emission');assert emission is not None;m.node_tree.links.new(tx.outputs['Color'],emission);bs.inputs['Emission Strength'].default_value=.18
 M[role]=m
records=[]
for idx,c in enumerate(C['candidates']):
 col=bpy.data.collections.new('POOL_DISPLAY_'+c['name']);scene.collection.children.link(col)
 root=bpy.data.objects.new('AST-LIB-010_POOL_'+c['name'],None);col.objects.link(root);root.matrix_world=root_matrix(c);root['candidate_name']=c['name'];root['parent_design_id']='AST-LIB-010';root['family']='library_use';root['support_owner']='AST-AQU-016';root['source_candidate_only']=True;root['source_contract_sha256']=sha(ROOT/'source_contract.json')
 for p in c['parts']:
  name=('WET'if idx==3 else'M'+str(idx))+'__'+p['name'];me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(p['vertices_local_uvn_m'],[],p['faces']);me.update()
  if p['kind']!='art':
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
  ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4);me.materials.append(M[p['material_role']])
  ob['candidate_name']=c['name'];ob['part_spec_name']=p['name'];ob['parent_design_id']='AST-LIB-010';ob['family']='library_use';ob['lineage_source_object']=p['lineage_object'];ob['semantic_role']=p['material_role'];ob['kind']=p['kind'];ob['grain_axis']=p['grain_axis'];ob['joins_json']=json.dumps(p['joins']);ob['source_blend_sha256']=sha(SRC)
  if 'contact'in p:ob['contact_json']=json.dumps(p['contact']);ob['physical_interface_owner']='AST-AQU-016'
  if p['kind']=='art':
   uv=me.uv_layers.new(name='UV_Original_Artwork');uv.active_render=True
   for li in me.polygons[0].loop_indices:uv.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][me.loops[li].vertex_index]
  else:
   metric_uv(me,M[p['material_role']],p['grain_axis'])
   bevel=ob.modifiers.new('Editable source-family edge easing','BEVEL');bevel.width=.0005 if p['material_role']in ['dark_rubber','display_glass','champagne_metal']else .001;bevel.segments=1
   normal=ob.modifiers.new('Editable source-family weighted normals','WEIGHTED_NORMAL');normal.keep_sharp=True
 bpy.context.view_layer.update()
 meshes=[o for o in col.objects if o.type=='MESH'];geo={o['part_spec_name']:evaluated_geometry(o)for o in meshes}
 vs=[v for z in geo.values()for v in z['vertices_world']];tol=C['metres_tolerance']
 assert all(c['bounds'][0][j]-tol<=v[j]<=c['bounds'][1][j]+tol for v in vs for j in range(3)),(c['name'],'evaluated envelope fail')
 assert all(z['matrix_positive']for z in geo.values())
 assert all(z['closed_manifold']for k,z in geo.items()if k!='original_pool_leisure_image'),(c['name'],'evaluated nonmanifold')
 records.append({'candidate':c['name'],'source_mesh_objects':len(meshes),'actual_evaluated_triangles':sum(z['triangle_count']for z in geo.values()),'bounds_world_xyz':[list(map(min,zip(*vs))),list(map(max,zip(*vs)))],'part_stats':{k:{a:b for a,b in z.items()if a not in ['vertices_world','triangles_world']}for k,z in geo.items()}})
assert not any(o.type in ['LIGHT','CAMERA']for o in scene.objects)
assert {k:material_state(M[k])for k in BASELINE}==BASELINE,'Retained material graph unexpectedly changed'
for p,h in PINS.items():assert sha(resolve_pin(p))==h,('changed input after build',p)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report={'status':'SOURCE_BUILT_AWAITING_INDEPENDENT_REOPEN_AND_VISUAL_REVIEW','source_file':str(OUT.relative_to(ROOT)),'source_sha256':sha(OUT),'source_contract_sha256':sha(ROOT/'source_contract.json'),'content_manifest_sha256':sha(ROOT/'content_manifest.json'),'generator_sha256':sha(__file__),'blender_version':bpy.app.version_string,'original_source_file':str(SRC.relative_to(CAT)),'original_source_sha256':sha(SRC),'actual_prototype_provenance':provenance,'retained_material_baseline':BASELINE,'candidates':records,'lights':0,'cameras':0,'exports':[],'new_derivative_catalogue_writes':new_catalogue_writes([OUT,ROOT/'qa/SOURCE_BUILD_REPORT.json']),'retained_original_source_or_export_writes':[],'game_writes':[],'scene_visual_acceptance':False}
(ROOT/'qa/SOURCE_BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_BUILT_NO_EXPORT',OUT,report['source_sha256'])
