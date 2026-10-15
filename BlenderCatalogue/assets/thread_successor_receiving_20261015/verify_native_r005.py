from pathlib import Path
import bpy,json,hashlib,struct
D=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((D/'NATIVE_SUCCESSOR_r005.json').read_text())
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices));h.update(struct.pack('<I',f.material_index))
  for uv in o.data.uv_layers:
   h.update(uv.name.encode())
   for v in uv.data:h.update(struct.pack('<2f',*v.uv))
  rows[o.name]={'mesh':h.hexdigest(),'pose':[list(row)for row in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials]}
 images={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest()for im in bpy.data.images if im.packed_file};return rows,images
old,oi=read(D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/source/thread_stock/thread_stock_repair_r004.blend');new,ni=read(D/'native/thread_stock_repair_r005.blend');assert old.keys()==new.keys();assert oi==ni;unmodified=0;rigid=0
for name,a in old.items():
 b=new[name];assert a['materials']==b['materials']
 if name=='Group5VisualFinish_ThreadCeiling':continue
 assert a['mesh']==b['mesh'],name
 if name.startswith(('East_CeilingCove_','East_CoveReveal_','East_Skirting_')):
  expected=[row[:]for row in a['pose']];expected[0][3]-=.08;assert max(abs(expected[i][j]-b['pose'][i][j])for i in range(4)for j in range(4))<.0001;rigid+=1
 else:assert a['pose']==b['pose'];unmodified+=1
report={'status':'PASS_INDEPENDENT_NATIVE_GEOMETRY_UV_MATERIAL_LINKS_PACKED_IMAGES_AND_RIGID_POSES','unchanged_meshes':unmodified,'rigid_trim_meshes':rigid,'ceiling_meshes_scoped_to_separate_surface_proof':1,'exact_packed_images':len(oi),'old_native_sha256':sha(D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/source/thread_stock/thread_stock_repair_r004.blend'),'new_native_sha256':sha(D/'native/thread_stock_repair_r005.blend')};assert report['new_native_sha256']==r['native_sha256'];(D/'NATIVE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],unmodified,rigid,len(oi))
