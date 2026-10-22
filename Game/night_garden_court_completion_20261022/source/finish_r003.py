"""Exact-footprint D16 soffit cladding and editable finish UVs; no slab changes."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;N=R/'BlenderCatalogue/assets/night_garden_court_completion_20261022';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();xyz=lambda p:Vector((p[0],-p[2],p[1]));god=lambda p:[p.x,p.z,-p.y]
b=json.loads((P/'evidence/BUILD_R002.json').read_text());assert sha(R/b['native'])==b['native_sha256'];parent=b['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(R/b['native']));bpy.context.preferences.filepaths.save_version=0
plan=json.loads((P/'evidence/SOFFIT_PLAN.json').read_text());assert sha(G/'data/generated/structural_meshes.json')==plan['source_sha256']
cream=bpy.data.materials['NGRC_PorcelainStructure'];wood=bpy.data.materials['NGRC_HoneyWalnut'];metal=bpy.data.materials['NGRC_BrushedChampagne'];glow=bpy.data.materials['NGRC_OpalFixture'];added=[]
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,vs,fs,m,contact=True):
 data=bpy.data.meshes.new(name);data.from_pydata([xyz(v)for v in vs],[],fs);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(m);o['physical_contact']=contact;added.append(o);return o
def box(name,a,c,m,contact=True):
 x,y,z=a;X,Y,Z=c;return mesh(name,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],faces,m,contact)
for tile in plan['tiles']:
 vs=[];fs=[]
 for triangle in tile['triangles']:
  offset=len(vs);vs.extend([[x,96.90,z]for x,z in triangle]+[[x,96.94,z]for x,z in triangle]);fs.extend([tuple(offset+j for j in face)for face in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]])
 mesh(tile['name']+'_Inset',vs,fs,cream)
 if tile['whole_rectangle']:
  x,z,X,Z=tile['bounds']
  for i,(a,c)in enumerate([([x,96.78,z],[x+.08,96.94,Z]),([X-.08,96.78,z],[X,96.94,Z]),([x,96.78,z],[X,96.94,z+.08]),([x,96.78,Z-.08],[X,96.94,Z])]):box(tile['name']+'_Frame_'+str(i),a,c,wood)
for row in plan['lights']:
 side=row['side'];z=row['z'];box(side+'_SoffitWashHousing_'+str(z),[53.42,96.62,z-.24],[53.87,96.95,z+.24],metal)
 box(side+'_SoffitWashOpal_'+str(z),[53.40,96.65,z-.18],[53.425,96.76,z+.18],glow,False)
 b['lights'].append({'name':side+'_RetainedSoffitWash_'+str(z),'position':[53.38,96.69,z],'target':[51.05,96.76,z],'anchor':[51.05,96.76,z],'energy':2.6,'range':22,'angle':55})
# Authored planar UVs for every new textured architectural part, never the inherited meshes.
textured=0
for o in [bpy.data.objects[row['name']]for row in b['new_parts']]+added:
 if any(n.type=='TEX_IMAGE'for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes):
  layer=o.data.uv_layers.active or o.data.uv_layers.new(name='ResortFinishUV')
  for poly in o.data.polygons:
   skip=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3)if k!=skip]
   for li in poly.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=(co[axes[0]]*.35,co[axes[1]]*.35)
  textured+=1
for o in added:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
for o in added:
 vs=[god(o.matrix_world@Vector(c))for c in o.bound_box];b['new_parts'].append({'name':o.name,'bounds':[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]],'contact':bool(o.get('physical_contact',False))})
native=N/'NightGardenResortCourts_r003.blend';out=P/'runtime/NightGardenResortCourts_r003.glb';assert not native.exists()and not out.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
source=Path(__file__).with_name('build.py').read_text();exec("for side in ['Fore','Aft']:"+source.split("for side in ['Fore','Aft']:",1)[1].split('receipt=',1)[0])
b.update(native=str(native.relative_to(R)),native_sha256=sha(native),runtime=str(out.relative_to(G)),runtime_sha256=sha(out),predecessor_native_sha256=parent,textured_new_parts_with_editable_uv=textured,retained_slab_soffit_cladding_area_m2=plan['footprint_area_m2'],slab_geometry_unchanged=True)
(P/'evidence/BUILD_R003.json').write_text(json.dumps(b,indent=2)+'\n');print('PAIRED_COURT_COMPLETION',len(b['new_parts']),len(b['lights']),textured)
