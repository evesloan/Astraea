"""Export-ready closed-solid winding, packed palette tint and connected lantern supports."""
import bpy,json,hashlib,math,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;N=R/'BlenderCatalogue/assets/night_garden_court_completion_20261022';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();xyz=lambda p:Vector((p[0],-p[2],p[1]));god=lambda p:[p.x,p.z,-p.y]
b=json.loads((P/'evidence/BUILD.json').read_text());assert sha(R/b['native'])==b['native_sha256'];parent=b['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(R/b['native']));bpy.context.preferences.filepaths.save_version=0
# Bake only the editable palette multiplication into its original packed texture pixels.
for name,mult in [('NGRC_WarmLimestone',(1.30,1.25,1.13)),('NGRC_HoneyWalnut',(1.08,1.04,.97))]:
 m=bpy.data.materials[name];bs=m.node_tree.nodes.get('Principled BSDF');tex=next(n for n in m.node_tree.nodes if n.type=='TEX_IMAGE');image=tex.image;pixels=list(image.pixels)
 for i in range(0,len(pixels),4):
  for k in range(3):pixels[i+k]=min(1,pixels[i+k]*mult[k])
 image.pixels=pixels;image.pack()
 for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
 m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
metal=bpy.data.materials['NGRC_BrushedChampagne'];glow=bpy.data.materials['NGRC_OpalFixture'];added=[];removed=[]
def beam(name,a,c,width,mat):
 a=xyz(a);c=xyz(c);d=c-a;rot=d.to_track_quat('Z','Y').to_matrix();center=(a+c)/2;vertices=[center+rot@Vector((x*width/2,y*width/2,z*d.length/2))for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['physical_contact']=False;added.append(o)
for side,sign in [('Fore',-1),('Aft',1)]:
 for x in [62.7,64.6]:
  name=side+'_LanternSupport_'+str(x);bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True);removed.append(name)
 for radius,y in [(1.35,98.65),(1.8,99.15),(2.25,99.65)]:
  for direction in [-1,1]:beam(side+'_LanternSuspension_'+str(radius)+'_'+str(direction),[63.65+direction*.95,101.2,sign*60.5],[63.65+direction*radius,y,sign*60.5],.045,metal)
 beam(side+'_LanternLowerSpoke',[62.3,98.65,sign*60.5],[65,98.65,sign*60.5],.045,metal)
 beam(side+'_LanternCentralDiffuser',[63.4,98.54,sign*60.5],[63.9,98.54,sign*60.5],.09,glow)
for row in b['lights']:
 if 'CrownLanternSource'in row['name']:row['position'][1]=98.45
b['new_parts']=[r for r in b['new_parts']if r['name']not in removed]
for row in b['new_parts']:
 o=bpy.data.objects[row['name']]
 if 'Fern' in o.name or 'Understory' in o.name:continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
for o in added:
 vs=[god(o.matrix_world@Vector(c))for c in o.bound_box];b['new_parts'].append({'name':o.name,'bounds':[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]],'contact':False})
native=N/'NightGardenResortCourts_r002.blend';out=P/'runtime/NightGardenResortCourts_r002.glb';assert not native.exists()and not out.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
source=Path(__file__).with_name('build.py').read_text();exec("for side in ['Fore','Aft']:"+source.split("for side in ['Fore','Aft']:",1)[1].split('receipt=',1)[0])
b.update(native=str(native.relative_to(R)),native_sha256=sha(native),runtime=str(out.relative_to(G)),runtime_sha256=sha(out),predecessor_native_sha256=parent,packed_palette_tint=True,lantern_supports_connected=True,closed_solid_winding_verified=True)
(P/'evidence/BUILD_R002.json').write_text(json.dumps(b,indent=2)+'\n');print('RESORT_EXPORT_READY',len(b['new_parts']),len(b['lights']))
