from pathlib import Path
import bpy,json,hashlib,struct
O=Path(__file__).resolve().parent;P=O/'Group4_Foremid_Tram_Source.blend'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.open_mainfile(filepath=str(P))
def geom():
 h=hashlib.sha256()
 for ob in sorted(bpy.data.objects,key=lambda a:a.name):
  if ob.type!='MESH':continue
  h.update(ob.name.encode());h.update(struct.pack('<I',len(ob.data.vertices)))
  for v in ob.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in ob.data.polygons:
   h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
before=geom();bpy.ops.file.make_paths_relative();packed=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack();packed.append(im.name)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);bpy.ops.wm.open_mainfile(filepath=str(P));after=geom();assert before==after
assert all(im.packed_file is not None for im in bpy.data.images if im.source=='FILE' and im.size[0]>0)
(O/'NATIVE_PORTABILITY.json').write_text(json.dumps({'geometry_before_sha256':before,'geometry_after_sha256':after,'geometry_unchanged':True,'native_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'original_shared_images_packed':packed,'external_credentials_or_sources':False,'scope':'Only owned native repacked for portability; existing material source pins stay unchanged'},indent=2)+'\n')
print('NATIVE_PORTABILITY_PASS',before,'images',len(packed))
