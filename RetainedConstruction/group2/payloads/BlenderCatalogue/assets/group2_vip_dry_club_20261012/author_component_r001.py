"""Source-fitted Star Atlas bar and bookable dining, preserving existing commons."""
import bpy,bmesh,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
survey=json.loads((P/'evidence/SITE_SURVEY001.json').read_text())
assert all(not r['occupied_source_surface_hits'] and abs(r['actual_floor_covered_m2']-r['area_m2'])<1e-6 for r in survey['regions'])
bpy.ops.wm.read_factory_settings(use_empty=True);objects=[];metrics=[];materials={}
for role,color in [('ivory',(.73,.72,.63,1)),('walnut',(.33,.20,.11,1)),('teal',(.13,.32,.33,1)),('glass',(.65,.80,.79,.30)),('metal',(.56,.49,.33,1)),('lens',(1,.89,.64,1))]:
 m=bpy.data.materials.new('G2D_'+role);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=color
 if role=='glass':bs.inputs['Alpha'].default_value=.3;m.surface_render_method='DITHERED'
 if role=='lens':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m
def box(name,x0,x1,h0,h1,z0,z1,role):
 vertices=[(x,-z,102+h)for h in [h0,h1]for z in [z0,z1]for x in [x0,x1]]
 d=bpy.data.meshes.new('G2D_'+name);d.from_pydata(vertices,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>1e-7;bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);d.materials.append(materials[role]);objects.append(o);metrics.append({'name':o.name,'closed_manifold':True,'positive_volume_m3':volume});return o
def chair(name,x,z,back):
 for j,(dx,dz)in enumerate([(-.3,-.3),(.3,-.3),(-.3,.3),(.3,.3)]):box(name+'Leg'+str(j),x+dx-.04,x+dx+.04,0,.42,z+dz-.04,z+dz+.04,'metal')
 box(name+'Pad',x-.42,x+.42,.39,.52,z-.39,z+.39,'teal')
 bz=z+back*.34;box(name+'Back',x-.42,x+.42,.48,1.12,bz-.055,bz+.055,'walnut')
# Dining enclosure within the verified source-clear41.36m² bay. Public bypasses remain outside.
for name,x in [('West',-93.1),('East',-88.85)]:
 box(name+'Plinth',x,x+.15,0,.65,2.4,11.8,'ivory');box(name+'Glass',x+.045,x+.095,.65,2.7,2.4,11.8,'glass');box(name+'Header',x,x+.15,2.7,3.35,2.4,11.8,'ivory')
box('RearWall',-93.1,-88.7,0,3.35,11.65,11.8,'ivory')
for name,x0,x1 in [('Left',-93.1,-92.66),('Right',-89.14,-88.7)]:box('Front'+name,x0,x1,0,3.35,2.4,2.55,'ivory')
box('EntryHeader',-92.66,-89.14,2.68,3.35,2.4,2.55,'ivory');box('Ceiling',-93.1,-88.7,3.35,3.50,2.4,11.8,'ivory')
# Four two-place tables; construction places are uncredited until Group8 dining-ledger transfer.
for j,(x,z)in enumerate([(-91.95,5.4),(-89.85,5.4),(-91.95,9.4),(-89.85,9.4)]):
 box('Table'+str(j)+'Foot',x-.22,x+.22,0,.72,z-.3,z+.3,'walnut');box('Table'+str(j)+'Top',x-.52,x+.52,.72,.80,z-.48,z+.48,'ivory')
 chair('Dining'+str(j)+'A',x,z-.98,-1);chair('Dining'+str(j)+'B',x,z+.98,1)
box('DiningCleanStock',-92.8,-91.8,0,1.2,10.85,11.55,'walnut');box('DiningUsedReturn',-90.0,-89.0,0,.95,10.85,11.55,'walnut')
# Bar outside the retained reading alcove, keeping cross-arrivalZ-1.2..1.2 clear.
box('BarBase',-92.85,-89.2,0,.95,-4.55,-3.8,'walnut');box('BarTop',-92.95,-89.1,.95,1.04,-4.65,-3.7,'ivory')
box('CleanGlassStock',-92.7,-91.7,1.04,1.55,-4.45,-4.05,'ivory');box('PreparationTray',-91.4,-90.5,1.04,1.08,-4.40,-3.95,'teal')
box('BeverageCasing',-90.3,-89.6,1.04,1.50,-4.40,-4.05,'metal')
for j in range(3):
 x=-92.2+j*1.15;box('BarStool'+str(j)+'Foot',x-.22,x+.22,0,.68,-2.8,-2.36,'metal');box('BarStool'+str(j)+'Pad',x-.35,x+.35,.65,.77,-2.95,-2.25,'teal')
lights=[]
for j,(x,z,h)in enumerate([(-92,5.4,3.1),(-90,9.4,3.1),(-91,-3.8,3.3)]):
 box('Light'+str(j)+'Mount',x-.04,x+.04,h,h+.18,z-.04,z+.04,'metal');box('Light'+str(j)+'Body',x-.4,x+.4,h-.1,h,z-.1,z+.1,'metal');box('Light'+str(j)+'Lens',x-.35,x+.35,h-.12,h-.1,z-.07,z+.07,'lens')
 lights.append({'source_mesh':'G2D_Light'+str(j)+'Lens','world_xyz':[x,102+h-.13,z],'range':5,'energy':.8})
src=ROOT/'Game/assets/models/AST-DOR-002.glb';before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(src));door_objects=set(bpy.data.objects)-before
for o in door_objects:
 if o.parent not in door_objects:o.location.x-=90.9;o.location.y-=2.47;o.location.z+=102
for o in door_objects:o.name='G2D_ReviewDoor_'+o.name
native=P/'source/VIP_DRY_CLUB_r001.blend';native.parent.mkdir(exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
path=ROOT/'Game/assets/group2_vip_dry_club/VIP_DRY_CLUB_r001.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
data={'schema':'astraea.group2_vip_dry_source.v1','parent_checkpoint':'c9ac7403706803b4356baf58c84d24d868c655c5','candidate_parent':'D17_directory_03','ame_ids':['AME-118','AME-119'],'source_receiver_sha256':survey['sha256'],'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'floor_y':102,'no_floor_exported':True,'source_dining_fittings':8,'credited_dining_places':0,'canonical_dining_total_unchanged':2200,'new_rooms_or_beds':0,'protected_bypasses':[{'id':'west_gallery','x':[-96.2,-93.8],'z':[-12,12]},{'id':'cross_arrival','x':[-96,-63],'z':[-1.2,1.2]}],'door':{'world_xyz':[-90.9,102,2.47],'file':'AST-DOR-002.glb','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'persistent_id':'group2-dry-source:bookable-dining-entry'},'lights':lights,'service_proposal':{'reservation':'port_service_riser_3','clean_delivery_port':[-92.3,103.1,11.3],'contained_dirty_return_port':[-89.5,102.9,11.3],'connection_implemented':False,'wet_cleaning_not_food_route':True},'admission_proposal':'All-luxury membership proposed for dedicated bookable dining; inclusive commons and bypass remain unrestricted; privacy/booking/inside egress coordination required','admission_implemented':False,'source_original_roof_floor_ring_stairs_reading_alcove_modified':False,'production_adoption':False,'food_staff_capacity_membership_gameplay_final_art_accepted':False}
out=ROOT/'Game/data/group2_vip_dry_club/COMPONENT_r001.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n');(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'original_sources_modified':False},indent=2)+'\n')
print('PASS source-fitted dining/bar; no original source or dining ledger changes')
