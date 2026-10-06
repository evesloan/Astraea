"""Source-only shared inspection helpers. No engine execution on import."""
import hashlib,json,math
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def bvec(v):return (v[0],-v[2],v[1])
def wvec(v):return (v[0],v[2],-v[1])
def image_nodes(tree,seen=None):
 seen=set() if seen is None else seen
 if not tree or tree.as_pointer() in seen:return []
 seen.add(tree.as_pointer());out=[]
 for n in tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:out.append(n)
  elif n.type=='GROUP' and n.node_tree:out.extend(image_nodes(n.node_tree,seen))
 return out

def material_record(mat):
 if not mat:return None
 nodes=[];links=[]
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   defaults={}
   for inp in n.inputs:
    if hasattr(inp,'default_value'):
     v=inp.default_value
     if isinstance(v,(int,float,str,bool)):defaults[inp.identifier]=v
     else:
      try:defaults[inp.identifier]=list(v)
      except TypeError:pass
   row={'name':n.name,'type':n.bl_idname,'inputs':defaults}
   if n.type=='TEX_IMAGE' and n.image:row['image']={'name':n.image.name,'packed_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else None,'size':list(n.image.size)}
   nodes.append(row)
  links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links)
 return {'name':mat.name,'diffuse':list(mat.diffuse_color),'nodes':sorted(nodes,key=lambda n:n['name']),'links':links}

def mesh_record(me,start=0,count=None,vstart=0,vcount=None):
 count=len(me.polygons)-start if count is None else count;vcount=len(me.vertices)-vstart if vcount is None else vcount
 polys=list(me.polygons)[start:start+count]
 return {'vertices':[list(v.co) for v in list(me.vertices)[vstart:vstart+vcount]],'faces':[[i-vstart for i in p.vertices] for p in polys],'materials':[m.name if m else None for m in me.materials],'face_materials':[p.material_index for p in polys],'smooth':[p.use_smooth for p in polys],'uvs':{uv.name:[[list(uv.data[li].uv) for li in p.loop_indices] for p in polys] for uv in me.uv_layers}}

def baseline_snapshot(bpy,remove_names=()):
 parts={};objects={};materials={};remove_names=set(remove_names)
 for ob in bpy.data.objects:
  if 'pure_part_ranges' in ob:
   for p in json.loads(ob['pure_part_ranges']):
    if p['name'] not in remove_names:parts[p['name']]=digest(mesh_record(ob.data,p['face_start'],p['face_count'],p['vertex_start'],p['vertex_count']))
   record={'matrix_basis':[list(r)for r in ob.matrix_basis],'parent':ob.parent.name if ob.parent else None}
  else:
   record={'type':ob.type,'matrix_basis':[list(r)for r in ob.matrix_basis],'parent':ob.parent.name if ob.parent else None,'instance_collection':ob.instance_collection.name if ob.instance_collection else None,'hide_render':ob.hide_render}
   if ob.type=='MESH':record['mesh']=mesh_record(ob.data)
  objects[ob.name]=digest(record)
 for mat in bpy.data.materials:materials[mat.name]=digest(material_record(mat))
 return {'parts':parts,'objects':objects,'materials':materials}

def compare_subset(expected,actual):
 errors=[]
 for kind,rows in expected.items():
  for name,value in rows.items():
   if actual.get(kind,{}).get(name)!=value:errors.append(kind+':'+name)
 return errors

def verify_new_geometry(bpy,names):
 rows=[]
 for name in names:
  ob=bpy.data.objects.get(name);assert ob and ob.type=='MESH',name
  me=ob.data;me.calc_loop_triangles()
  assert all(math.isfinite(float(x)) for v in me.vertices for x in v.co),name
  bad=[]
  for i,t in enumerate(me.loop_triangles):
   a,b,c=[me.vertices[j].co for j in t.vertices]
   if (b-a).cross(c-a).length<1e-12:bad.append(i)
  assert not bad,('Degenerate new triangles',name,bad[:20])
  assert me.uv_layers and all(math.isfinite(float(x))for layer in me.uv_layers for u in layer.data for x in u.uv),('UV',name)
  rows.append({'name':name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'uv_layers':len(me.uv_layers)})
 return rows
