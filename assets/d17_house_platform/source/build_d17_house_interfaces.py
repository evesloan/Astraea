"""Bounded editable interface stage. No walkable floors and no runtime systems."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-RES-005';FAMILY='d17_house_platform'
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
D=json.loads((R/'source/section_contract.json').read_text())
# Read the real retained hull mesh. Raycast every footprint corner and centre.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'))
o=bpy.data.objects['HUL_LowerBand_00'];tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());seats=[]
for spec in D['footing_specs']:
 cx,z=spec['centre_xz'];width,depth=spec['size_xz'];top=float(spec['top_y'])
 assert width==.8 and depth==1.2
 corners=[];witness=[]
 for x,zz in [(cx-width/2,z-depth/2),(cx+width/2,z-depth/2),(cx+width/2,z+depth/2),(cx-width/2,z+depth/2),(cx,z)]:
  hit,n,face,distance=tree.ray_cast(Vector((x,-zz,4)),Vector((0,0,-1)),12)
  assert hit is not None and n.z>.9,(x,zz)
  corners.append([x,hit.z,zz]);witness.append({'point_world':[x,hit.z,zz],'normal_world':[n.x,n.z,-n.y],'face_index':face})
 assert min(top-v[1] for v in corners)>.34
 seats.append({'x':cx,'z':z,'corners_world':corners[:4],'witnesses':witness,'top_y':top,'source_owner':'AST-HUL-001/HUL_LowerBand_00','hull_source_sha256':sha(C/'assets/lower_hull_body/source/AST-HUL-001.blend'),'method':'Actual editable hull BVH; positive wedge bottom seated on the upward-facing inner hull surface. Hull is never edited.'})
# Reuse the established material graphs and packed textures without creating flat substitutes.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/starboard_house_upper/source/AST-COM-003.blend'))
mats={name:bpy.data.materials[name] for name in ['ivory_enamel','warm_walnut','champagne_metal']}
for m in mats.values():m.use_fake_user=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[];records=[]
def xyz(p):x,y,z=p;return(x,-z,y)
def mesh(name,world,faces,role,seat):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(p)for p in world],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
 ob['catalogue_id']=AID;ob['assembly']=name;ob['support']=seat;parts.append(ob);records.append({'name':name,'material':role,'world_vertices':world,'support':seat});return ob
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,y0,y1,z0,z1,role,seat):return mesh(name,[[x,y,z]for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],faces,role,seat)
for i,s in enumerate(seats):
 q=s['corners_world'];mesh('D17_SeatedHullFooting_%s'%i,q+[[x,s['top_y'],z]for x,y,z in q],faces,'champagne_metal',s['source_owner'])
for spec in D.get('royalty_frame_candidate',{}).get('members',[]):
 box(spec['name'],*spec['bounds'],'champagne_metal',spec['support'])
if D.get('royalty_frame_candidate'):
 # Open, in-plane triangulated web within the actual cleared support strip.
 levels=[-.45,5.76,11.76,16.26,20.76,26.76,35.26,43.76,52.26,60.76,69.26,77.76,83.76,88.26,92.76,97.26,100.56]
 for i,high in enumerate(levels[1:]):
  low=levels[i]
  box('D17_RoyaltyWebRail_%02d'%i,107.7,108.3,high-.36,high,29.8,50.2,'champagne_metal','D17_RoyaltyPier_Fore and D17_RoyaltyPier_Aft')
  ya,yb=(low+.20,high-.20) if i%2==0 else (high-.20,low+.20)
  # World-YZ parallelogram, extruded across X; both ends embedded in chords.
  yz=[(ya-.16,29.9),(ya+.16,29.9),(yb+.16,50.1),(yb-.16,50.1)]
  world=[[x,y,z] for x in [107.8,108.2] for y,z in yz]
  mesh('D17_RoyaltyWebBrace_%02d'%i,world,faces,'champagne_metal','D17_RoyaltyPier_Fore and D17_RoyaltyPier_Aft')
 D['royalty_frame_candidate']['web_levels_y']=levels
 D['royalty_frame_candidate']['web_status']='Geometric in-plane bracing only; out-of-plane frame, connection/load capacity and transverse floor bearings unresolved'
for side in[-1,1]:
 z0,z1=sorted([side*12.75,side*13.65]);prefix='D17_CommonsPortal_%s'%('Fore'if side<0 else'Aft')
 for name,x0,x1 in [('Left',78.22,78.5),('Right',81.5,81.78)]:
  box(prefix+'_'+name+'Jamb',x0,x1,102,104.82,z0,z1,'ivory_enamel','D17_starboard_house_extension floor top Y102')
 box(prefix+'_Header',78.22,81.78,104.82,105.06,z0,z1,'ivory_enamel',prefix+' left and right jamb top Y104.82')
 # Restrained layered metal inner fillet; no reduced clear opening.
 for name,x0,x1 in [('Left',78.43,78.5),('Right',81.5,81.57)]:
  a,b=sorted([side*12.73,side*12.77]);box(prefix+'_'+name+'Fillet',x0,x1,102.04,104.84,a,b,'champagne_metal',prefix+' jamb contact')
 a,b=sorted([side*12.73,side*12.77]);box(prefix+'_HeaderFillet',78.43,81.57,104.82,104.89,a,b,'champagne_metal',prefix+' header contact')
 for name,pos in [('Entry',[80,102,side*12.1]),('ExitHeld',[80,102,side*15.5])]:
  ob=bpy.data.objects.new('DATUM_'+prefix+'_'+name,None);bpy.context.collection.objects.link(ob);ob.location=xyz(pos);ob['status']='Source interface only; onward floor not adopted'
D['seated_footings']=seats;D['source_stage_parts']=records;D['new_walkable_source_meshes']=0
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();src=R/'source'/f'{AID}.blend';out=R/'exports'/f'{AID}.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Portal groups and isolated footings form small spatial batches; editable source stays unjoined.
groups={}
for ob in parts:
 key=('Fore'if 'Fore' in ob.name else'Aft'if'Aft'in ob.name else ob.name,ob.data.materials[0].name);groups.setdefault(key,[]).append(ob)
for key,obs in sorted(groups.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name='D17_InterfaceBatch_'+'_'.join(key)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':FAMILY,'name':'D17 residential house portal interfaces and held Royalty support bay','source':f'source/{AID}.blend','export':f'exports/{AID}.glb','source_sha256':sha(src),'export_sha256':sha(out),'editable_part_count':len(records),'runtime_mesh_batches':len(groups),'status':'Partial source kit; full16-unit supported platform and routes held. Not adopted.','new_walkable_source_meshes':0}
M.update({'verification': ['qa/interface_verification.json', 'qa/seated_contact_verification.json', 'qa/floor_contract_verification.json', 'qa/source_join_ledger.json', 'qa/texture_byte_equality.json', 'qa/royalty_frame_verification.json', 'qa/allocation_footprint_regression.json'], 'integration_hold': 'No Godot adoption of this partial family or companion COM-003 open portals until supported onward floor, guard and route fit is ready'})
(R/f'{AID}.manifest.json').write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M))
