"""Independent source reopen of three new block-ins; no save/export/render/Game."""
import bpy,bmesh,json,hashlib,math,sys
from pathlib import Path
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');OUT=C/'assets/grand_pool_first_pass/architectural_composition/revisions/blockin002';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=json.loads((S/'BLOCKIN_PLAN_002.json').read_text());build=json.loads((OUT/'qa/BUILD_RECEIPT.json').read_text());assert build['plan_sha256']==sha(S/'BLOCKIN_PLAN_002.json');dest=OUT/'qa/INDEPENDENT_REOPEN.json';assert not dest.exists();actual={};results=[]
def canonical(v):
 if isinstance(v,(str,int,float,bool))or v is None:return v
 try:return[canonical(x)for x in v]
 except TypeError:return str(v)
def mat_state(mat):
 nodes=[]
 for n in mat.node_tree.nodes:
  row={'name':n.name,'type':n.type,'inputs':{x.name:canonical(x.default_value)for x in n.inputs if hasattr(x,'default_value')}}
  if n.type=='TEX_IMAGE':
   im=n.image;assert im and im.packed_file;row['image']={'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'extension':n.extension,'interpolation':n.interpolation}
  nodes.append(row)
 return{'role':mat.get('astraea_material_role'),'nodes':nodes,'links':sorted([l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in mat.node_tree.links),'metric_tile_m':canonical(mat.get('meters_per_tile_uv',[1,1])),'backface_culling':mat.use_backface_culling}
for source in build['sources']:
 p=Path(source['source']);assert sha(p)==source['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();expected={r['name']:r for r in plan['parts']if r['group']==source['group']};objects={o.name:o for o in bpy.context.scene.objects};assert set(objects)==set(expected);assert all(o.type=='MESH'for o in objects.values());group=[]
 for name,row in expected.items():
  o=objects[name];assert not o.modifiers and not o.constraints;assert o.location.length<1e-10 and o.rotation_euler.to_quaternion().angle<1e-8;assert all(abs(x-1)<1e-10 for x in o.scale);me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);bm.normal_update();assert all(e.is_manifold for e in bm.edges),(name,'not closed');volume=bm.calc_volume(signed=True);assert volume>1e-9,(name,volume);bm.free();assert len(me.materials)==1 and len(me.uv_layers)==1
  role=row['material_role'];assert o['material_role']==role and o['parent_design_id']=='AST-AQU-016'and not o['new_floor_owner'];assert mat_state(me.materials[0])==source['material_provenance'][role]['material_state'],('material drift',name)
  assert json.loads(o['support_json'])==row['support'];assert o.get('intentional_new_mechanical_joint')==row.get('intentional_new_mechanical_joint');vertices=[[float(v.co.x),float(v.co.z),float(-v.co.y)]for v in me.vertices];assert len(vertices)==len(row['vertices_xyz']);deviation=max(math.dist(a,b)for a,b in zip(vertices,row['vertices_xyz']));assert deviation<5e-5,(name,deviation)
  for tri in me.loop_triangles:
   a,b,c=[me.vertices[i].co for i in tri.vertices];assert(b-a).cross(c-a).length*.5>1e-10,(name,'collapsed triangle')
   uv=[me.uv_layers.active.data[i].uv for i in tri.loops];area=abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5;assert area>1e-12,(name,'collapsed UV')
  part=dict(row);part['vertices_xyz']=vertices;part['faces']=[list(f.vertices)for f in me.polygons];actual[name]=part;group.append(dict(name=name,triangles=len(me.loop_triangles),signed_volume_m3=volume,max_vertex_deviation_m=deviation,packed_material_role=role))
 assert sha(p)==source['source_sha256'];results.append(dict(source=str(p),source_sha256=sha(p),group=source['group'],parts=group))
for path,h in plan['input_sha256'].items():assert sha(path)==h
actual_plan=dict(plan);actual_plan['parts']=[actual[p['name']]for p in plan['parts']];actual_plan['status']='ACTUAL_REOPENED_SOURCE_VERTICES';actual_path=S/'BLOCKIN_ACTUAL_PLAN_002.json';assert not actual_path.exists();actual_path.write_text(json.dumps(actual_plan,indent=2)+'\n');dest.write_text(json.dumps(dict(status='PASS_INDEPENDENT_BLOCKIN_SOURCE_REOPEN',sources=results,source_count=3,mesh_parts=len(actual),original_inputs_unchanged=True,actual_snapshot_sha256=sha(actual_path),pending=['Recheck actual vertices against retained geometry/fixture/view/route protection','Complete exact source support/new-new joint review','Early source composition; asymmetric market thresholds and physically fitted new fixtures still pending','No export/runtime/final-art acceptance']),indent=2)+'\n');print('INDEPENDENT_BLOCKIN_REOPEN_PASS',len(actual),'parts, three unchanged saved sources.')
