"""Two editable VIP wet construction kits; actual shared receiving interfaces held.

Local metres: floorY0 in glTF, corresponding proposed D17 datumY102. No source
commons geometry is imported, overwritten or removed. No new catalogue identity.
"""
import bpy, bmesh, hashlib, json, pathlib, math
from mathutils import Vector
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
materials = {}
for role, rgba in [('ivory',(.73,.72,.63,1)), ('stone',(.53,.54,.48,1)),
                   ('walnut',(.33,.20,.11,1)), ('teal',(.13,.32,.33,1)),
                   ('metal',(.56,.49,.33,1)), ('water',(.12,.47,.49,.65)),
                   ('glass',(.65,.80,.79,.28)), ('lens',(1,.89,.64,1)),
                   ('plant',(.18,.38,.20,1)), ('dark',(.11,.14,.15,1))]:
    m = bpy.data.materials.new('G2VIP_' + role)
    m.diffuse_color = rgba
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = rgba
    bs.inputs['Roughness'].default_value = .55
    if role in ['water','glass']:
        bs.inputs['Alpha'].default_value = rgba[3]
        m.surface_render_method = 'DITHERED'
    if role == 'lens':
        bs.inputs['Emission Color'].default_value = rgba
        bs.inputs['Emission Strength'].default_value = .7
    materials[role] = m
metrics = []; exports = []; lights = []; doors = []; pins = []
def shape(name, verts, faces, role):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x,-z,y) for x,y,z in verts], [], faces)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), name
    volume = bm.calc_volume(signed=True)
    assert volume > 1e-7, name
    bm.to_mesh(mesh); bm.free()
    o = bpy.data.objects.new(name, mesh); collection.objects.link(o)
    mesh.materials.append(materials[role]); o['construction_only'] = True
    metrics.append({'name':name,'closed_manifold':True,'positive_volume_m3':volume})
    return o
def box(name,x0,x1,y0,y1,z0,z1,role):
    assert x1>x0 and y1>y0 and z1>z0
    verts=[(x,y,z) for y in [y0,y1] for z in [z0,z1] for x in [x0,x1]]
    return shape(prefix+name,verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],role)
def beam(name,a,b,width,role):
    # Cube cross-section along exact line, including roof ribs and handrails.
    av,bv=Vector(a),Vector(b);direction=(bv-av).normalized()
    side=direction.cross(Vector((0,1,0)))
    if side.length<.01:side=direction.cross(Vector((1,0,0)))
    side.normalize();up=direction.cross(side).normalized()
    v=[tuple(end+side*s*width/2+up*t*width/2) for end in [av,bv]for s,t in [(-1,-1),(-1,1),(1,1),(1,-1)]]
    return shape(prefix+name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
def ramp(name):
    # 18m run,1.5m rise,1.8m clear before handrail fittings. No public lane crossing.
    v=[(-15,.0,-5.95),(3,1.5,-5.95),(3,1.5,-4.15),(-15,0,-4.15),
       (-15,-.12,-5.95),(3,1.38,-5.95),(3,1.38,-4.15),(-15,-.12,-4.15)]
    # Keep everything at or above theD17 datum, including the low-end ramp soffit.
    v[4]=(-15,0,-5.95);v[7]=(-15,0,-4.15)
    # Truncated tip,10cm ground landing; exact physics plane remains continuous.
    v[0]=(-14.9,1.5*.1/18,-5.95);v[3]=(-14.9,1.5*.1/18,-4.15)
    return shape(prefix+name,v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'stone')
def fixture(name,x,y,z):
    box(name+'_Mount',x-.055,x+.055,y,y+.15,z-.055,z+.055,'metal')
    box(name+'_Body',x-.6,x+.6,y-.12,y,z-.14,z+.14,'metal')
    box(name+'_Lens',x-.53,x+.53,y-.14,y-.12,z-.105,z+.105,'lens')
    lights.append({'kit':kit,'source_mesh':prefix+name+'_Lens','local_xyz':[x,y-.15,z],
                   'energy':1,'range':6,'shadow_enabled_initially':False,'visible_initially':False})
def seat(name,x,z,y=1.5):
    for n,(sx,sz)in enumerate([(-.38,-.3),(.38,-.3),(-.38,.3),(.38,.3)]):
        box(name+'_Leg'+str(n),x+sx-.04,x+sx+.04,y,y+.40,z+sz-.04,z+sz+.04,'metal')
    box(name+'_Seat',x-.48,x+.48,y+.36,y+.50,z-.40,z+.40,'teal')
    box(name+'_Back',x-.48,x+.48,y+.45,y+1.15,z+.34,z+.42,'walnut')
    box(name+'_BackPad',x-.43,x+.43,y+.53,y+1.09,z+.30,z+.345,'teal')
def door_frame(name,x,z):
    # Existing unchanged AST-DOR-001 runtime instance completes this opening.
    # Native review imports its exact model at the declared transform.
    doors.append({'kit':kit,'name':name,'local_xyz':[x,0,z],'yaw':0,
                  'persistent_id':'group2-vip-construction:'+kit+':'+name,
                  'catalogue_id':'AST-DOR-001','production_access_policy':False})
    src=ROOT/'Game/assets/models/AST-DOR-001.glb'
    manifest=json.loads((ROOT/'BlenderCatalogue/catalogue_manifest.json').read_text())
    # Registered source identity is reused; nothing is registered or overwritten.
    assert 'AST-DOR-001' in json.dumps(manifest)
    pins.append({'path':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(src))
    new=set(bpy.data.objects)-before
    roots=[o for o in new if o.parent not in new]
    for root in roots:
        root.location+=Vector((x,-z,0))
    for o in new:
        o.name=prefix+name+'_'+o.name
        for c in list(o.users_collection):c.objects.unlink(o)
        collection.objects.link(o)
    for root in roots:root['review_only_retained_door']=True
for kit in ['TIDAL','QUIET']:
    prefix='G2VIP_'+kit+'_'
    collection=bpy.data.collections.new(prefix+'ConstructionKit');scene.collection.children.link(collection)
    # Fore wet court and aft ground changing/plant remain separated by8m public arrival.
    box('BearingPad',-15.8,15.8,0,.12,-13.7,-4.15,'dark')
    box('VesselFloor',-1.2,11.2,.12,.2,-12.4,-6.0,'stone')
    box('TankFore',-1.2,11.2,.2,1.5,-12.4,-12.2,'ivory')
    box('TankAft',-1.2,11.2,.2,1.5,-6.2,-6.0,'ivory')
    box('TankWest',-1.2,-1,.2,1.5,-12.2,-6.2,'ivory')
    box('TankEast',11,11.2,.2,1.5,-12.2,-6.2,'ivory')
    box('Water_Illustrative',-1,11,.2,1.4,-12.2,-6.2,'water')
    # Four fitted dry receiving bands without a duplicate floor beneath the basin.
    box('TerraceFore',-15.8,15.8,.12,1.5,-13.7,-12.4,'stone')
    box('TerraceWest',-15.8,-1.2,.12,1.5,-12.4,-6.0,'stone')
    box('TerraceEast',11.2,15.8,.12,1.5,-12.4,-4.15,'stone')
    box('TerraceAftWest',-15.8,-15,.12,1.5,-6.0,-4.15,'stone')
    box('TerraceAftMiddle',-15,3,.12,1.5,-6.0,-5.95,'stone')
    box('TerraceAftLanding',3,11.2,.12,1.5,-6.0,-4.15,'stone')
    ramp('ArrivalRamp')
    for edge in [-6.0,-4.10]:
        for j in range(10):
            x=-14.9+17.9*j/9;h=(x+15)/18*1.5
            beam('RampPost'+str(edge)+'_'+str(j),(x,h,edge),(x,h+1.05,edge),.055,'metal')
        beam('RampRail'+str(edge),(-14.9,.008333+1.05,edge),(3,2.55,edge),.06,'walnut')
    # Ground arrival to ramp first point is a fitted12cm horizontal toe, noD16 recess.
    box('GroundRampToe',-15.8,-14.9,0,.008333,-5.95,-4.15,'stone')
    # Acoustic enclosure and stepped rib roof. Local roof exception remains unadopted.
    for x in [-15.8,-8,0,8,15.8]:
        box('Column'+str(x),x-.12,x+.12,1.5,5.5,-13.65,-13.41,'walnut')
        beam('RoofRibA'+str(x),(x,5.5,-13.7),(x,6.2,-9.0),.16,'ivory')
        beam('RoofRibB'+str(x),(x,6.2,-9.0),(x,5.5,-4.15),.16,'ivory')
    box('ForePlinth',-15.8,15.8,1.5,2.4,-13.7,-13.55,'ivory')
    box('ForeClerestory',-15.8,15.8,2.4,5.5,-13.62,-13.58,'glass')
    box('OuterWall',15.65,15.8,1.5,5.5,-13.55,-4.15,'ivory')
    box('InnerWall',-15.8,-15.65,1.5,5.5,-13.55,-6.05,'ivory')
    # Roof panels are faceted planes with positive thickness, not a box volume.
    for n,(a,b,ha,hb)in enumerate([(-13.7,-9,5.5,6.2),(-9,-4.15,6.2,5.5)]):
        verts=[(x,h,z)for hshift in [0,.18]for x,z,h in [(-15.8,a,ha+hshift),(15.8,a,ha+hshift),(15.8,b,hb+hshift),(-15.8,b,hb+hshift)]]
        shape(prefix+'RoofPanel'+str(n),verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory')
    # Screened overhead environmental spine with maintenance clearance unaccepted.
    box('OverheadPlantCasing',-14.5,-9,5.5,6.25,-12.8,-7.5,'dark')
    for j in range(15):box('PlantScreen'+str(j),-14.6,-14.5,5.6,6.25,-12.8+j*.35,-12.75+j*.35,'walnut')
    for x,z in [(-6,-9),(4,-12.7),(13.6,-10),(6,-5.0)]:fixture('WetLight'+str(x),x,5.25,z)
    for j,(x,z)in enumerate([(-11.5,-11.5),(-8.5,-11.5),(-11.5,-8),(-8.5,-8),(13.5,-8),(13.5,-11)]):seat('Rest'+str(j),x,z)
    box('TowelStation',-5.0,-3,1.5,2.45,-9.1,-8.45,'walnut')
    for j in range(5):box('Towel'+str(j),-4.9,-3.1,2.45+j*.035,2.48+j*.035,-9.0,-8.55,'ivory')
    # Water entry construction: wide submerged stairs, rail and transfer seat.
    for j in range(5):
        box('WaterEntryStep'+str(j),-.8,1.2,.2,1.4-j*.24,-6.8-j*.32,-6.48-j*.32,'stone')
    beam('WaterEntryHandrail',(1.32,2.4,-6.5),(1.32,1.2,-8.1),.065,'metal')
    for z in [-6.5,-7.3,-8.1]:beam('WaterEntryPost'+str(z),(1.32,.2,z),(1.32,2.4-(abs(z+6.5)/1.6)*1.2,z),.06,'metal')
    seat('TransferSeat',-2.1,-6.95)
    # Aft service/changing module: total16x7.5=120m², keeps the entire public lane empty.
    # Ground module receives the existing adopted house floor; no duplicate slab.
    box('AftBack',-15.8,.2,0,3.4,12.55,12.7,'ivory')
    box('AftWest',-15.8,-15.65,0,3.4,5.2,12.55,'ivory')
    box('AftEast',.05,.2,0,3.4,5.2,12.55,'ivory')
    box('AftRoof',-15.8,.2,3.4,3.6,5.2,12.7,'walnut')
    # Open1.16m privacy door thresholds at ground datum; no membership gate.
    for j,x in enumerate([-14,-9.5]):
        for n,(a,b)in enumerate([(x-1.2,x-.04),(x+1.16,x+2.4)]):
            box('ChangingFront'+str(j)+'_'+str(n),a,b,0,3.4,7.5,7.65,'ivory')
        box('ChangingHeader'+str(j),x-.04,x+1.16,2.3,3.4,7.5,7.65,'ivory')
        box('ChangingSide'+str(j),x+2.25,x+2.4,0,3.4,7.65,12.55,'ivory')
        door_frame('Privacy'+str(j),x,7.55)
        seat('ChangingBench'+str(j),x+.5,11.6,0)
        for n in range(4):box('PersonalLocker'+str(j)+'_'+str(n),x-.9+n*.55,x-.4+n*.55,0,2.0,12.0,12.5,'walnut')
    box('PlantPartition',-5.0,-4.85,0,3.4,7.6,12.55,'ivory')
    for j in range(3):
        box('TreatmentCabinet'+str(j),-3.9,-2.6,0,2.5,8.5+j*1.15,9.35+j*1.15,'dark')
        box('ServicePanel'+str(j),-3.91,-3.90,.8,2.1,8.6+j*1.15,9.25+j*1.15,'metal')
    box('ServiceCounter',-1.8,-.3,0,.95,10.5,12.4,'walnut')
    for j in range(6):beam('TreatmentPipe'+str(j),(-2.4,2.6,8.5+j*.6),(-.3,2.6,8.5+j*.6),.08,'metal')
    for x in [-13,-8.5,-2]:fixture('DryLight'+str(x),x,3.35,9.7)
    # Palette and authored details distinguish the quieter planted counterpart.
    if kit=='QUIET':
        for j in range(12):box('AcousticBaffle'+str(j),-15.4+j*.28,-15.3+j*.28,2.5,4.8,-13.5,-13.35,'teal')
        for j in range(3):
            x=-7+j*2.3;box('Planter'+str(j),x,x+1.3,1.5,2.05,-13.25,-12.6,'walnut')
            for k in range(5):beam('Reed'+str(j)+'_'+str(k),(x+.15+k*.2,2.05,-12.95),(x+.2+k*.2,2.8+.1*(k%2),-12.9),.06,'plant')
    else:
        for j in range(8):box('GardenTile'+str(j),-14+j*1.0,-13.2+j*1.0,1.5,1.53,-12.4,-10.2,'teal')
    # A native scene retains both independently editable kit collections.
    for obj in collection.objects:
        if obj.type=='MESH':obj['local_unplaced_kit']=kit
    path=ROOT/'Game/assets/group2_vip_pavilions'/('VIP_'+kit+'_r001.glb');path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
    bpy.ops.object.select_all(action='DESELECT')
    # Retained door review meshes stay native; runtime creates original controllers.
    export_objs=[o for o in collection.objects if not any(o.name.startswith(prefix+d['name']+'_')for d in doors if d['kit']==kit)]
    for o in export_objs:o.select_set(True)
    bpy.context.view_layer.objects.active=export_objs[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
    exports.append({'kit':kit,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
native=P/'source/VIP_WET_KITS_r001.blend';native.parent.mkdir(exist_ok=True);assert not native.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(native))
data={'schema':'astraea.group2_vip_source_kits.v1','proposed_count':2,'proposed_membership':'all_four_luxury_tiers; unimplemented',
      'new_room_ids':0,'capacity_ledger_changes':0,'parent_checkpoint':'9067cf8dce5625f16d4109cbeca0855474b5fc68',
      'kit_coordinate_system':'localY0 is candidate D17Y102; nativeZup; glTFYup',
      'candidate_transforms':[{'kit':'TIDAL','world_xyz':[-80,102,-370],'adoption':False},
                              {'kit':'QUIET','world_xyz':[80,102,-370],'adoption':False}],
      'unresolved_shared_interfaces':['Installed receiving roofsY106.02..106.26','Tidal lift/stair openings and fixed approach','Quiet commons arrival/stair/guard composition','Group7 tank-bearing load path','Exact membership/count/capacity','Group3 separated wet-service connection'],
      'public_dry_lane_local_z':[-4,4],'source_kit_crosses_public_lane':False,
      'basin_internal_m':[12,6,1.2],'illustrative_water_m3_per_kit':86.4,'water_entry_accessibility_accepted':False,
      'terrace_y':1.5,'occupied_ceiling_y':5.5,'roof_max_y':6.38,'ramp_run_m':18,'ramp_clear_nominal_m':1.8,
      'exports':exports,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'doors':doors,'lights':lights,
      'retained_dependency_pins':list({pin['path']:pin for pin in pins}.values()),
      'production_adoption':False,'swimming_treatment_service_gameplay_final_art_accepted':False}
out=ROOT/'Game/data/group2_vip_pavilions/KITS_r001.json';out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_text(json.dumps(data,indent=2)+'\n')
(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'exports':exports,'original_sources_changed':False,'placement_accepted':False},indent=2)+'\n')
print('PASS two complete editable wet/changing/plant construction kits; shared placement held')
