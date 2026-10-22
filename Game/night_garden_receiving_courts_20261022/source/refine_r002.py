"""Preserve r001; close lower-gallery guard exposure and normalize solid face winding."""
from pathlib import Path
s=Path(__file__).with_name('build.py').read_text()
exec(s.split('pre=json.loads',1)[0].replace('bpy.context.view_layer.update();v=', 'v='))
import bmesh
if not (P/'evidence/BUILD.json').exists():
 # Recover metadata from the successfully saved native after r001 export batching failed.
 first=N/'NightGardenReceivingCourts_r001.blend';assert first.exists()
 bpy.ops.wm.open_mainfile(filepath=str(first));bpy.context.view_layer.update()
 objects=[{'name':o.name,'bounds':bounds(o),'contact':bool(o.get('physical_contact',False))}for o in bpy.context.scene.objects if o.type=='MESH']
 lights=[]
 for sign,side in [(-1,'Fore'),(1,'Aft')]:
  for z in [48,77]:
   for offset in [-2.5,2.5]:lights.append({'name':side+'_Grove_'+str(z)+'_'+str(offset),'position':[63.65,85.15,sign*(z+offset)],'target':[63.65,95,sign*z],'energy':2.4,'range':18,'angle':48})
  for z in [42,64,86]:lights.append({'name':side+'_Gallery_'+str(z),'position':[55.72,96,sign*z],'target':[57,93,sign*z],'energy':1.3,'range':9,'angle':65})
 pre=json.loads((P/'evidence/PREREQUISITES.json').read_text())
 original={'native':str(first.relative_to(R)),'native_sha256':sha(first),'objects':objects,'lights':lights,'source_pins':pre['source_pins'],'preserved_existing_base_area_m2':pre['existing_base_area_preserved_m2'],'new_ids':0,'capacity_change':0,'protected_slab_cuts':0,'main_integrated':False,'visual_accepted':False,'engineering_accessibility_acceptance':False,'r001_export_failed':'Removed object reference in second guard batch; native saved successfully; no runtime export produced.'}
 (P/'evidence/BUILD.json').write_text(json.dumps(original,indent=2)+'\n')
original=json.loads((P/'evidence/BUILD.json').read_text());assert sha(R/original['native'])==original['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/original['native']));bpy.context.preferences.filepaths.save_version=0
parts=[];metal=bpy.data.materials['NGRC_BrushedChampagne']
exec('def beam('+s.split('def beam(',1)[1].split('# Paired courts',1)[0])
# Direct mesh construction avoids thousands of global operator/dependency updates.
def beam(name,a,b,width,m,contact=True):
 aa,bb=xyz(a),xyz(b);direction=bb-aa;rotation=direction.to_track_quat('Z','Y').to_matrix();center=(aa+bb)/2
 vertices=[center+rotation@Vector((x*width/2,y*width/2,z*direction.length/2))for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(m);o['physical_contact']=contact;parts.append(o);return o
removed=[]
for o in list(bpy.context.scene.objects):
 if '_GardenLowerA_' in o.name:
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
original['objects']=[r for r in original['objects']if r['name']not in removed]
for sign,side in [(-1,'Fore'),(1,'Aft')]:
 rail(side+'_LowerGalleryProtectedEdge',[57.16,93,sign*50],[57.16,93,sign*79])
 rail(side+'_GardenLowerReceivingClear',[57.16,93,sign*36.9],[57.16,93,sign*48])
 rail(side+'_BridgeFarClosure',[57.2,93,sign*36.76],[59.2,93,sign*36.76])
 rail(side+'_RampLowerEnd',[57.2,93,sign*48.04],[59.16,93,sign*48.04])
 rail(side+'_RampUpperEnd',[57.2,97.5,sign*78.96],[59.16,97.5,sign*78.96])
 for y in [93,97.5]:rail(side+'_GalleryNearEnd_'+str(y),[55.04,y,sign*35.04],[57.16,y,sign*35.04])
for i,edge in enumerate(json.loads((P/'evidence/GROUND_GUARD_PLAN.json').read_text())):rail(edge['side']+'_GroundEdge_'+str(i),edge['a'],edge['b'])
bpy.context.view_layer.update()
newrecords=[{'name':o.name,'bounds':bounds(o),'contact':True}for o in parts]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
native=N/'NightGardenReceivingCourts_r002.blend';out=P/'runtime/NightGardenReceivingCourts_r002.glb';assert not native.exists() and not out.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
for side in ['Fore','Aft']:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(side) and '_Baluster_'in o.name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();group[0].name=side+'_GuardBalusters';group[0]['physical_contact']=True
# Four separate canopies retain local light/culling bounds; runtime groups by original material.
for side in ['Fore','Aft']:
 for z in [48,77]:
  prefix=side+'_Canopy_'+str(z)+'_'
  groups={}
  for o in list(bpy.context.scene.objects):
   if o.type=='MESH' and o.name.startswith(prefix):groups.setdefault(o.data.materials[0].name,[]).append(o)
  for i,group in enumerate(groups.values()):
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0]
   if len(group)>1:bpy.ops.object.join()
   group[0].name=prefix+'Material_'+str(i);group[0]['physical_contact']=False
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
original.update(native=str(native.relative_to(R)),native_sha256=sha(native),runtime=str(out.relative_to(G)),runtime_sha256=sha(out),predecessor_native_sha256=original['native_sha256'],solid_face_winding_normalized=True)
original['objects']+=newrecords
(P/'evidence/BUILD_R002.json').write_text(json.dumps(original,indent=2)+'\n')
print('RECEIVING_REFINED_R002',len(original['objects']))
