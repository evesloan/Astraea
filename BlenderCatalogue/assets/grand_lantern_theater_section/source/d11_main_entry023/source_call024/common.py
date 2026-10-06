from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');C=P.parents[1]
SOURCE=P/'source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend';SOURCE_SHA='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
OUT=R/'run001';BLEND=OUT/'AST-CUL-005_D11_exterior_call_024.blend';GLB=OUT/'AST-CUL-005_D11_exterior_call_024.glb'
ORIGINAL_NAMES=('THEATER_D11_MAIN_call_plate','THEATER_D11_MAIN_call_lens')
NAMES=('D11_MAIN_EXTERIOR_CALL_PLATE','D11_MAIN_EXTERIOR_CALL_LENS')
ANCHOR=(-34.,71.1,-128.82);OLD_ANCHOR=(-34.75,70.71,-130.8)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,d):
 with Path(p).open('x')as f:json.dump(d,f,indent=2);f.write('\n')
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def b(v):return(v[0],-v[2],v[1])
def w(v):return(v[0],v[2],-v[1])
def pins():
 m=read(R/'INPUTS.json')
 for p,h in m['sha256'].items():assert sha(p)==h,('Input changed',p)
 assert sha(SOURCE)==SOURCE_SHA
 rows=read(C/'catalogue_manifest.json')['assets'];matches=[r for r in rows if r.get('catalogue_id')=='AST-CUL-005'];assert len(matches)==1 and matches[0]['family']=='grand_lantern_theater_section'
 return m

def snapshot(bpy):
 sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import material_record,image_nodes
 objects={};materials={};images={}
 for ob in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  row={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_world':[list(x)for x in ob.matrix_world],'matrix_local':[list(x)for x in ob.matrix_basis]}
  if ob.type=='MESH':
   me=ob.data;me.calc_loop_triangles();row.update(vertices=[list(v.co)for v in me.vertices],faces=[list(f.vertices)for f in me.polygons],uv=[list(x.uv)for x in me.uv_layers.active.data],materials=[m.name for m in me.materials],triangles=len(me.loop_triangles));assert not ob.modifiers
   for mat in me.materials:
    materials[mat.name]=material_record(mat)
    for node in image_nodes(mat.node_tree):
     assert node.image.packed_file;images[node.image.name]=hashlib.sha256(node.image.packed_file.data).hexdigest()
  objects[ob.name]=row
 return {'objects':objects,'materials':materials,'packed_images':images}
