from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002';source=F/'Group4_Port_Successor_002.blend';sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
assert sourcehash=='36132af8f8335da1abce721d907ec053d1239341ecef375a112b10a511107335'
CAT=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());assert all(a['catalogue_id']!='AST-TRM-G4-030' for a in CAT['assets'])
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
collection=bpy.data.collections['AFT_MIDSHIP_STATIC_SOURCE'];keep=set(collection.objects)
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c!=collection:bpy.data.collections.remove(c)
collection.name='AFTMID_UPPER_RECEIVING_SUCCESSOR';held=bpy.data.collections.new('IMMUTABLE_ORIGINAL_GUARD_VARIANTS');bpy.context.scene.collection.children.link(held)
B=lambda p:Vector((p[0],-p[2],p[1]));G=lambda p:Vector((p[0],p[2],-p[1]));family='group4_aftmid_upper_receiving_015';original_names={o.name for o in collection.objects if o.type=='MESH'}
targets=['Aftmid_V2__LiftApproach_-3.46_'+p for p in ['foot','infill','rail']]+['Aftmid_V2__Port_Edge_'+p for p in ['foot','infill','rail']];cuts=[]
for name in targets:
 original=bpy.data.objects[name];oldverts=[G(original.matrix_world@v.co) for v in original.data.vertices];lo=min(v.z for v in oldverts);hi=max(v.z for v in oldverts)
 assert (abs(lo-224.6)<2e-4 and abs(hi-228.6)<2e-4) if 'LiftApproach' in name else (abs(lo-204)<2e-4 and abs(hi-228)<2e-4),(name,lo,hi)
 intervals=[(227.8,hi)] if 'LiftApproach' in name else [(lo,223.85),(226.25,hi)]
 for index,(a,b) in enumerate(intervals):
  copy=original.copy();copy.data=original.data.copy();copy.name=name+'_bounded_end_'+str(index);collection.objects.link(copy);copy.parent=None;copy.matrix_world=original.matrix_world.copy()
  for v,p in zip(copy.data.vertices,oldverts):
   q=p.copy();q.z=a+(p.z-lo)*(b-a)/(hi-lo);v.co=copy.matrix_world.inverted()@B(q)
  olduv=original.data.uv_layers.active.data;newuv=copy.data.uv_layers.active.data
  for poly in original.data.polygons:
   loops=list(poly.loop_indices);zs=[oldverts[original.data.loops[i].vertex_index].z for i in loops]
   if max(zs)-min(zs)<1e-5:continue
   for li in loops:
    p=oldverts[original.data.loops[li].vertex_index];pair=next(j for j in loops if abs(oldverts[original.data.loops[j].vertex_index].z-p.z)>1 and (Vector(oldverts[original.data.loops[j].vertex_index][:2])-Vector(p[:2])).length<1e-4)
    pj=oldverts[original.data.loops[pair].vertex_index];ul,uh=(olduv[li].uv,olduv[pair].uv) if p.z<pj.z else (olduv[pair].uv,olduv[li].uv);newz=a+(p.z-lo)*(b-a)/(hi-lo);newuv[li].uv=ul.lerp(uh,(newz-lo)/(hi-lo))
  copy.data.update();copy['construction_family']=family;copy['replaced_original_part']=name;copy['portal_opening_z']=[224.6,227.8] if 'LiftApproach' in name else [223.85,226.25]
 collection.objects.unlink(original);held.objects.link(original);cuts.append({'source':name,'source_bounds_z':[lo,hi],'selected_retained_ends_z':intervals,'exact_original_held':True})
metal=next(o.data.materials[0] for o in collection.objects if o.type=='MESH' and 'LiftApproach_-3.46_rail_bounded' in o.name)
for z in [223.77,226.33]:
 # New receiving posts are fully outside the 2.4m opening, positively received in the retained upper floor.
 verts=[(1.93+x*.05,56.065+y*.04,z+zz*.05) for x,y,zz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new('UpperPortalFoot');me.from_pydata([B(p) for p in verts],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(metal);me.update();ob=bpy.data.objects.new('Aftmid_UpperPortal_Foot_'+str(z),me);collection.objects.link(ob);ob['construction_family']=family;ob['collision_policy']='static_trimesh_candidate';ob['role']='positive retained upper-floor post receiver'
 uv=me.uv_layers.new(name='Original_metre_UV')
 for poly in me.polygons:
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.7,v.z*.7)
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.035,depth=1.18,location=B((1.93,56.64,z)));post=bpy.context.object;post.name='Aftmid_UpperPortal_Post_'+str(z)
 for c in list(post.users_collection):c.objects.unlink(post)
 collection.objects.link(post);post.data.materials.append(metal);post['construction_family']=family;post['collision_policy']='static_trimesh_candidate';post['role']='bounded opening guard-rail terminal post'
# Retain the exact lower guard post as a variant; the expanded turn bay replaces its blocked boundary.
post=bpy.data.objects['Aftmid_V2__LiftApproach_-3.46_post_-204'];collection.objects.unlink(post);held.objects.link(post)
relocated=[]
for name in ['Aftmid_V2__Quiet_Perch_Base_-225.8','Aftmid_V2__Quiet_Perch_Cushion_-225.8']:
 original=bpy.data.objects[name];copy=original.copy();copy.data=original.data.copy();copy.name=name+'_same_station_relocated';collection.objects.link(copy);copy.parent=None;copy.matrix_world=original.matrix_world.copy();copy.location+=B((0,0,-4));collection.objects.unlink(original);held.objects.link(original);relocated.append({'source':name,'translation_xyz':[0,0,-4],'same_count_and_station':True})
# Missing-only return floor south of the existing landing; original slab footprint is not duplicated.
sc=(R/'BlenderCatalogue/assets/group4_tram_connections_20261009/build_source.py').read_text();parts=[];markers=[];FAMILY=family;current=collection;collections={'UNEXPORTED_REFERENCE_AND_STUDIO':held};B=lambda p:(p[0],-p[2],p[1]);exec(sc[sc.index('def mesh('):sc.index('def guard(')],globals())
stone=bpy.data.materials['warm_stone'];glass=bpy.data.materials['station_guard_preview']
box('Aftmid_MissingOnly_ReturnBayFloor',(3.8,55.975,224.225),(3.6,.25,.75),stone,'only missing2.7m2 floor; original landing/board island unchanged')
box('Aftmid_ReturnBay_FloorDepthLap',(3.8,55.955,224.6),(3.6,.14,.40),metal,'positive retained landing and new floor receiving, below floor surface')
box('Aftmid_ReturnBay_OuterGuardFoot',(3.8,56.21,223.93),(3.6,.22,.10),stone,'new exposed-edge guard base on new floor')
box('Aftmid_ReturnBay_OuterGuardInfill',(3.8,56.76,223.93),(3.6,.82,.06),glass,'new exposed-edge infill;2.4m cross-route behind')
tube('Aftmid_ReturnBay_OuterHandrail',(2.0,57.23,223.93),(5.6,57.23,223.93),.04,metal,'new exposed-edge handrail')
for x in [2.08,5.52]:tube('Aftmid_ReturnBay_OuterPost_'+str(x),(x,56.065,223.93),(x,57.23,223.93),.045,metal,'positive new floor/rail post receiver')
for o in collection.objects:
 if o.type=='MESH' and 'construction_family' not in o:o['construction_family']=family
bpy.ops.object.select_all(action='DESELECT')
for o in collection.objects:o.select_set(True)
file=W/'AST-TRM-G4-030_aftmid_upper_receiving_r002.glb';bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file:image.pack()
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(W/'Group4_Aftmid_Upper_Receiving_r002.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sourcehash
(W/'SUCCESSOR_INTERFACE.json').write_text(json.dumps({'active':False,'family':family,'reserved_unregistered_id':'AST-TRM-G4-030','original_native_sha256':sourcehash,'original_model':'AST-TRM-G4-012_aft_midship_source.glb','original_model_sha256':hashlib.sha256((F/'AST-TRM-G4-012_aft_midship_source.glb').read_bytes()).hexdigest(),'selected_model':file.name,'selected_model_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'native':'Group4_Aftmid_Upper_Receiving_r002.blend','original_mesh_count':len(original_names),'unchanged_mesh_count':len(original_names)-9,'modified_source_parts':cuts,'same_station_relocated_perch_parts':relocated,'protected_canopy_pier_moved':False,'new_floor_area_m2':2.7,'outer_clear_portal_z':[223.85,226.25],'inner_clear_portal_z':[224.6,227.8],'new_bay_floor_xz':[2,223.85,5.6,224.6],'original_lift_station_floor_berths_and_room_ids_unchanged':True,'actual_player_route_requires_retest':True,'whole_group_complete':False,'capacity_species_cart_or_final_art_accepted':False},indent=2)+'\n');print('AFTMID_UPPER_SUCCESSOR_R002_BUILT',len(original_names)-9,'unchanged source meshes;6 guard lines clipped, lower post archived, same perch relocated;missing-only2.7m2 receiving bay')
