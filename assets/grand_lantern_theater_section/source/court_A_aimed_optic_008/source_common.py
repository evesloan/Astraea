from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent
P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section')
SOURCE=P/'source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend'
SOURCE_SHA='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
OUT=R/'AST-CUL-005_CourtA_aimed_optic_008.blend'
sys.path.insert(0,str(P/'source/firstpass_001'))
from firstpass_common import sha,digest,bvec,wvec,mesh_record,material_record,image_nodes
read=lambda p:json.loads(Path(p).read_text())
def write_new(p,d):
 with Path(p).open('x')as f:json.dump(d,f,indent=2);f.write('\n')
def inspect(bpy):
 records={}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   records[ob.name]={'mesh_sha256':digest(mesh_record(ob.data)),'matrix_world':[list(r)for r in ob.matrix_world],'vertices_world':[list(wvec(ob.matrix_world@v.co))for v in ob.data.vertices],'faces':[list(p.vertices)for p in ob.data.polygons],'materials':[m.name for m in ob.data.materials]}
 mats={m.name:material_record(m)for m in bpy.data.materials if m.users>0}
 images={im.name:hashlib.sha256(im.packed_file.data).hexdigest()for im in bpy.data.images if im.users>0 and im.packed_file}
 return {'meshes':records,'materials':mats,'packed_images':images}
