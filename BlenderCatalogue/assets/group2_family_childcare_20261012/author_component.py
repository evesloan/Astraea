"""Family Terrace source childcare component, trimmed around retained guard."""
import bpy,bmesh,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
site=json.loads((P/'evidence/TRIMMED_SITE_VERIFICATION.json').read_text());assert site['pass']
bpy.ops.wm.read_factory_settings(use_empty=True);objects=[];metrics=[];materials={}
for role,color in [('ivory',(.73,.72,.63,1)),('walnut',(.33,.20,.11,1)),('teal',(.13,.32,.33,1)),('soft',(.68,.62,.45,1)),('glass',(.65,.80,.79,.30)),('metal',(.56,.49,.33,1)),('lens',(1,.89,.64,1))]:
 m=bpy.data.materials.new('G2F_'+role);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=color
 if role=='glass':bs.inputs['Alpha'].default_value=.3;m.surface_render_method='DITHERED'
 if role=='lens':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m
def box(name,x0,x1,h0,h1,z0,z1,role):
 points=[(x,-z,97.5+h)for h in [h0,h1]for z in [z0,z1]for x in [x0,x1]]
 d=bpy.data.meshes.new('G2F_'+name);d.from_pydata(points,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>1e-7;bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);d.materials.append(materials[role]);objects.append(o);metrics.append({'name':o.name,'closed_manifold':True,'positive_volume_m3':vol});return o
# Internal enclosure entirely above the existing floor, no new floor export.
box('ForeAcousticWall',81.3,90.6,0,3.55,354.5,354.65,'ivory')
for side,x in [('West',81.3),('East',90.45)]:
 box(side+'Plinth',x,x+.15,0,.65,354.65,360.55,'ivory')
 box(side+'SightlineGlass',x+.045,x+.095,.65,2.85,354.65,360.55,'glass')
 box(side+'HighAcoustic',x,x+.15,2.85,3.55,354.65,360.55,'ivory')
# Exact wide retained guest-door casing needs5.16m, giving2.4m clear travel.
for label,x0,x1 in [('Left',81.3,83.40),('Right',88.60,90.6)]:
 box('Arrival'+label+'Plinth',x0,x1,0,.65,360.55,360.7,'ivory')
 box('Arrival'+label+'Glass',x0,x1,.65,2.65,360.60,360.65,'glass')
 box('Arrival'+label+'Header',x0,x1,2.65,3.55,360.55,360.7,'ivory')
box('DoorHeader',83.40,88.60,2.68,3.55,360.55,360.7,'ivory')
box('AcousticCeiling',81.3,90.6,3.55,3.70,354.5,360.7,'soft')
# Four daytime rest fittings, not adopted beds or guest capacity.
for j,(x,z)in enumerate([(82.1,355.25),(84.0,355.25),(85.9,355.25),(87.8,355.25)]):
 for n,(dx,dz)in enumerate([(0,0),(1.35,0),(0,1.8),(1.35,1.8)]):box('Rest'+str(j)+'Foot'+str(n),x+dx,x+dx+.07,0,.30,z+dz,z+dz+.07,'walnut')
 box('Rest'+str(j)+'Platform',x,x+1.42,.27,.35,z,z+1.87,'walnut')
 box('Rest'+str(j)+'DayPad',x+.07,x+1.35,.35,.48,z+.07,z+1.80,'teal')
 for n,(a,b)in enumerate([(x,x+.07),(x+1.35,x+1.42)]):box('Rest'+str(j)+'Side'+str(n),a,b,.35,.72,z,z+1.87,'ivory')
 box('Rest'+str(j)+'Back',x,x+1.42,.35,.88,z,z+.07,'ivory')
 box('Rest'+str(j)+'LowerEnd',x,x+1.42,.35,.57,z+1.8,z+1.87,'ivory')
# Caregiver rest and direct sightlines through the low-glazed enclosure.
for j,x in enumerate([82.0,88.6]):
 box('Caregiver'+str(j)+'Foot',x,x+1.25,0,.40,359.15,360.0,'walnut')
 box('Caregiver'+str(j)+'Pad',x,x+1.25,.40,.51,359.15,360.0,'teal')
 box('Caregiver'+str(j)+'Back',x,x+1.25,.50,1.15,359.90,360.0,'walnut')
# Learning/project table and contained manipulative stock, with2m main aisle.
box('LearningPedestal',81.9,82.55,0,.58,357.4,358.9,'walnut')
box('LearningTop',81.65,82.85,.58,.66,357.15,359.05,'ivory')
for j in range(5):box('ProjectBlock'+str(j),81.80+j*.17,81.93+j*.17,.66,.77,357.35,357.52,'teal'if j%2 else 'walnut')
box('PersonalStock',89.3,90.3,0,1.15,357.1,358.65,'walnut')
for j in range(4):box('StockDrawer'+str(j),89.28,89.30,.10+j*.25,.32+j*.25,357.20,358.55,'ivory')
# Staff care/preparation point; no plumbing or caregiver operation invented.
box('CareCounter',87.8,90.25,0,.80,354.75,355.15,'walnut')
box('CareTop',87.8,90.25,.80,.87,354.75,355.15,'ivory')
box('PreparationMat',88.0,89.1,.87,.91,354.80,355.12,'teal')
box('CleanStock',89.30,90.10,.87,1.18,354.80,355.12,'ivory')
lights=[]
for j,(x,z)in enumerate([(83,356),(88.5,356),(83,359),(88.5,359)]):
 box('Light'+str(j)+'Mount',x-.04,x+.04,3.35,3.55,z-.04,z+.04,'metal')
 box('Light'+str(j)+'Body',x-.45,x+.45,3.25,3.35,z-.11,z+.11,'metal')
 box('Light'+str(j)+'Lens',x-.40,x+.40,3.23,3.25,z-.08,z+.08,'lens')
 lights.append({'source_mesh':'G2F_Light'+str(j)+'Lens','world_xyz':[x,100.72,z],'range':5,'energy':.8})
# Native review retains the exact standard wide-door geometry at its future fit.
src=ROOT/'Game/assets/models/AST-DOR-002_wide.glb';before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(src));door_objects=set(bpy.data.objects)-before
for o in door_objects:
 if o.parent not in door_objects:o.location.x+=86;o.location.y-=360.63;o.location.z+=97.5
for o in door_objects:o.name='G2F_ReviewDoor_'+o.name
native=P/'source/FAMILY_CHILDCARE_r001.blend';native.parent.mkdir(exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
path=ROOT/'Game/assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
data={'schema':'astraea.group2_family_childcare_source.v1','parent_checkpoint':'f31a45d21a73f490dc23e0b7df3634a6445ecdd8','candidate_parent_programme':'D16_directory_06','ame_ids':['AME-173','AME-174'],'site_xz':site['site_xz'],'area_m2':site['area_m2'],'floor_y':97.5,'no_floor_exported':True,'source_receiver_sha256':site['source_runtime_sha256'],'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'door':{'file':'AST-DOR-002_wide.glb','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'world_xyz':[86,97.5,360.63],'clear_width_nominal_m':2.4,'persistent_id':'group2-family-source:childcare-entry','construction_controller_only':True},'lights':lights,'proposed_day_rest_fittings':4,'new_registered_beds_or_rooms':0,'admission_implemented':False,'receiving_owner':'Group1; Group8 child-destination coordination','service_owner':'Group3','source_original_roof_floor_guard_and_props_modified':False,'production_adoption':False,'child_body_supervision_capacity_gameplay_final_art_accepted':False}
out=ROOT/'Game/data/group2_family_childcare/COMPONENT_r001.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n')
(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'originals_modified':False},indent=2)+'\n')
print('PASS57.66m² editable family childcare source component; actual programme adoption held')
