"""Scoped D03 receiving precincts against exact retained geometry; no registry edits."""
from pathlib import Path
import copy, hashlib, json, math, sys
sys.dont_write_bytecode = True
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from native_glb_subset import GLB

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[4]
CAT = ROOT / 'BlenderCatalogue'
FIRST = HERE.parent.parent
PREP = CAT / 'assets/crew_batch_receiving_preparation_20261008'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n')
BASE = 'affc5c807087ff87da29f3642c2d6e418241b896'

catalogue = json.loads((CAT/'catalogue_manifest.json').read_text())
for aid in range(22, 28):
    assert not any(q['catalogue_id'] == f'AST-STF-G3-{aid:03d}' for q in catalogue['assets']), aid
frozen = {}
for p in [FIRST] + sorted(FIRST.joinpath('extensions').iterdir()):
    manifest = p/'SHA256SUMS.txt'
    if not manifest.exists(): continue
    for line in manifest.read_text().splitlines():
        h, n = line.split('  ', 1)
        assert sha(p/n) == h, str(p/n)
    frozen[str(manifest.relative_to(ROOT))] = sha(manifest)
manifest = json.loads((ROOT/'Game/data/architecture/crew_batch/runtime_manifest.json').read_text())
streets = json.loads((FIRST/'source/CREW_STREETS.json').read_text())
native_street = GLB(FIRST/'exports/AST-STF-G3-001.glb')
original_fixtures = json.loads((CAT/'assets/crew_service_platform/source/geometry_parts.json').read_text())
housing = next(q for q in original_fixtures if q['name'] == 'CRW_Task_8_0_Housing')
oldx = sum(housing['world_aabb'][:2])/2
oldz = sum(housing['world_aabb'][4:])/2
pinfiles = ['Game/AGENTS.md', 'Game/docs/FULL_SHIP_SCOPE_INDEX.md',
 'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json', 'Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json',
 'Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',
 'Game/data/architecture/crew_batch/runtime_manifest.json', 'Game/data/generated/structural_meshes.json',
 'Game/data/generated/received_structural_meshes.json', 'Game/data/whole_ship_layout.json',
 'Game/data/spatial_layout.json', 'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json',
 'Game/scripts/ship.gd', 'Game/scripts/service_door.gd', 'Game/scripts/static_contact_cache.gd',
 'Game/scripts/player.gd', 'Game/assets/models/AST-STF-008.glb',
 'BlenderCatalogue/catalogue_manifest.json', 'BlenderCatalogue/materials/staff/manifest.json',
 'BlenderCatalogue/assets/crew_service_platform/source/geometry_parts.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-STF-G3-001.glb']
for key in ['D03_directory_05', 'D03_directory_06', 'D03_directory_10']:
    row = next(q for q in manifest['sections'] if q['programme'] == key)
    pinfiles += [str((PREP/'incoming'/f'{key}.{ext}').relative_to(ROOT)) for ext in ['glb', 'blend']]
    pinfiles += ['Game/assets/models/'+row['model_file'], f'Game/data/architecture/crew_batch/{key}_NODE_NAME_MAP.json']
pinfiles.append('Game/assets/models/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r002.glb')
pins = {f: sha(ROOT/f) for f in pinfiles}
protected_model=GLB(ROOT/'Game/assets/models/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r002.glb')
protected_columns=[]
for name,node in protected_model.by_name.items():
    if'mesh'not in node or not name.startswith('PCW_Column'):continue
    b=protected_model.bounds(name)
    if b[0]<-101 and b[1]>-106 and b[4]<44 and b[5]>-44 and b[2]<12 and b[3]>15.34:protected_columns.append(dict(name=name,bounds=b))
column_footprints=unary_union([box(q['bounds'][0],q['bounds'][4],q['bounds'][1],q['bounds'][5])for q in protected_columns])
base = dict(schema=1, family='group3_crew_service_20261009', material_contract='retained_lower_staff_network',
 coordinate_system='Godot world metres; floor Y12; identity transform', source_pins=pins,
 original_rooms_unchanged=True, automatic_runtime_adoption=False, new_registered_berths=0)

def prisms(parts, name, geom, lo, hi, role, category, cell):
    for index, p in enumerate(shapely.get_parts(geom)):
        if p.geom_type != 'Polygon' or p.area < 1e-9: continue
        parts.append(dict(name=f'{name}_{index}', boundary=list(p.exterior.coords)[:-1],
         holes=[list(h.coords)[:-1] for h in p.interiors],
         triangles=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(p).geoms],
         y=[lo, hi], role=role, category=category, batch_cell=cell))

def fixture(parts, fixtures, name, x, z, cell):
    for suffix in ['Housing', 'Opal', 'Hanger0', 'Hanger1']:
        q = next(q for q in original_fixtures if q['name'] == 'CRW_Task_8_0_'+suffix)
        a,b,lo,hi,c,d = q['world_aabb']
        parts.append(dict(name=name+'_'+suffix, aabb=[a+x-oldx,b+x-oldx,lo,hi,c+z-oldz,d+z-oldz],
         role=q['role'], category='lighting_fixture', batch_cell=cell, original_rigid_fixture_profile=q['name']))
    fixtures.append(dict(name=name+'_Datum', position=[x,15.03,z], range_m=8, energy=.9, color=[.78,.88,1],
     native_extras=dict(datum_kind='supported_staff_task_light', source_housing=name+'_Housing',
      source_supports_json=json.dumps([name+'_Hanger0',name+'_Hanger1']))))

receivers=[]; cuts=[]; request=[]; doors=[]; checks=[]
for index, (label, key, side, streetx, z, doorx) in enumerate([
 ('Training','D03_directory_05','west',-101.06,0,-99.4),
 ('Administration','D03_directory_06','east',101.06,0,99.4),
 ('Uniforms','D03_directory_10','east',55.06,432,54.5)]):
    row=next(q for q in manifest['sections'] if q['programme']==key)
    source=GLB(PREP/'incoming'/f'{key}.glb'); runtime=GLB(ROOT/'Game/assets/models'/row['model_file'])
    assert sha(source.path)==row['source_sha256'] and sha(runtime.path)==row['runtime_sha256']
    assert source.bin==runtime.bin and row['placement']==[0,0,0]
    names=[f'E_outer_{side}_{s}'for s in ['openingpier0','openingpier1','openingheader','openingreveal0','openingreveal1']]+['E_ceiling']
    bounds={n:source.bounds(n)for n in names}
    # Round only the known 0.1mm source representation; native proof below records actual bounds.
    end=round(bounds[f'E_outer_{side}_openingpier0'][0 if side=='west' else 1],5)
    roofedge=round(bounds['E_ceiling'][0 if side=='west'else 1],5)
    zlo=round(bounds[f'E_outer_{side}_openingreveal0'][5],5)
    zhi=round(bounds[f'E_outer_{side}_openingreveal1'][4],5)
    clear=Polygon([[streetx,z-1.8],[end,zlo],[end,zhi],[streetx,z+1.8]])
    a,b=sorted([streetx,end]); parts=[]; fixtures=[]; cell=label.lower()+'_receiver'
    walls=clear.buffer(.14,join_style=2).difference(clear).intersection(box(a,z-4,b,z+4))
    prisms(parts,label+'WallLow',walls,12,13.03,'staff_bluegrey_paint','screen_wall',cell)
    prisms(parts,label+'WallHigh',walls,13.03,15.2,'staff_white_paint','screen_wall',cell)
    prisms(parts,label+'Roof',clear.union(walls),15.2,15.34,'staff_bluegrey_paint','overhead',cell)
    # Complete the original header-to-roof head without moving its frame or original rounded roof.
    header=bounds[f'E_outer_{side}_openingheader']
    htop=round(header[3],5)
    prisms(parts,label+'FrameHead',box(header[0],z-2.5,header[1],z+2.5),htop,15.2,'staff_white_paint','screen_wall',cell)
    # Match the actual rounded native roof edge by subtracting its convex XY profile.
    roofv=source.geometry('E_ceiling')[0]
    from shapely.geometry import MultiPoint
    profile=MultiPoint([(v[0],v[1])for v in roofv]).convex_hull
    xr0,xr1=sorted([roofedge,end]); target=box(xr0,15.2,xr1,15.34).difference(profile)
    for ni,p in enumerate(shapely.get_parts(target)):
        if p.geom_type!='Polygon'or p.area<1e-10:continue
        vs=[]; fs=[]
        for t in shapely.constrained_delaunay_triangles(p).geoms:
            tri=list(t.exterior.coords)[:3];k=len(vs)
            vs += [[x,y,z-2.5]for x,y in tri]+[[x,y,z+2.5]for x,y in tri]
            fs += [[k+2,k+1,k],[k+3,k+4,k+5]]
        for ring in [list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1]for h in p.interiors]:
            for u,v in zip(ring,ring[1:]+ring[:1]):
                k=len(vs);vs += [[u[0],u[1],z-2.5],[v[0],v[1],z-2.5],[v[0],v[1],z+2.5],[u[0],u[1],z+2.5]];fs.append([k,k+1,k+2,k+3])
        parts.append(dict(name=label+f'OriginalRoofProfileNib_{ni}',vertices_godot=vs,faces=fs,
         role='staff_bluegrey_paint',category='overhead',batch_cell=cell,original_roof_overlap_m2=p.intersection(profile).area))
    # Source door is rigid and unchanged. Fill the new collar beside its real 2.76 x 2.82m fitting.
    side_fit=clear.intersection(box(doorx-.18,z-4,doorx+.18,z+4)).difference(box(doorx-.19,z-1.38,doorx+.19,z+1.38))
    prisms(parts,label+'DoorSideFit',side_fit,12,15.2,'staff_white_paint','door_receiver',cell)
    prisms(parts,label+'DoorHead',box(doorx-.18,z-1.38,doorx+.18,z+1.38),14.82,15.2,'staff_white_paint','door_receiver',cell)
    # Visible fixture lies above the fitting, with exact source hangers meeting the new roof.
    fixture(parts,fixtures,label+'Task',doorx,z,cell)
    spec=dict(base,catalogue_id=f'AST-STF-G3-{index+22:03d}',parts=parts,fixtures=fixtures,
     existing_programme=key,original_source_native_bounds=bounds,clear_flare_boundary=list(clear.exterior.coords)[:-1],
     original_source_runtime_binary_identical=True,original_meshes=sum('mesh'in q for q in source.doc['nodes']))
    write(HERE/'source'/f'{label.upper()}_RECEIVER.json',spec);receivers.append(spec)
    cut=box(min(streetx,streetx+(-.14 if side=='west'else .14)),z-1.8,max(streetx,streetx+(-.14 if side=='west'else .14)),z+1.8)
    cuts.append(cut);request.append(clear.union(walls).union(box(xr0,z-2.5,xr1,z+2.5)))
    doors.append(dict(name=label+'ServiceGate',id=key+'_'+side+'_service_gate_g3_completion',position=[doorx,12,z],
     yaw=math.pi/2 if side=='west'else -math.pi/2,model='AST-STF-008.glb',original_door_not_scaled=True,
     fitting_width_height_m=[2.76,2.82],open_leaf_clearance_m=2.168,default_closed=True))
    checks.append(dict(programme=key,label=label,clear_length_m=abs(end-streetx),native_bounds=bounds,
     retained_source_runtime_binary_identical=True,original_meshes=spec['original_meshes'],original_roof_profile_overlap_m2=sum(q.get('original_roof_overlap_m2',0)for q in parts)))

# Extend only the uniforms street beyond its original closed end. Remove its source cap in successor only.
uniform_extension=box(55.2,432,58.8,435.8)
uniform_outer=uniform_extension.buffer(.14,join_style=2)
cuts.append(box(54.9,431.9999,59.1,432.1401))
extension_parts=[]; extension_lights=[]
ew=uniform_outer.difference(uniform_extension).difference(box(54.9,431.8,59.1,432.14)).difference(cuts[2])
prisms(extension_parts,'UniformStreetExtensionLow',ew,12,13.02,'staff_bluegrey_paint','screen_wall','uniform_extension')
prisms(extension_parts,'UniformStreetExtensionHigh',ew,13.02,15.2,'staff_white_paint','screen_wall','uniform_extension')
prisms(extension_parts,'UniformStreetExtensionRoof',uniform_outer.intersection(box(54.9,432,59.1,436)),15.2,15.34,'staff_bluegrey_paint','overhead','uniform_extension')
fixture(extension_parts,extension_lights,'UniformStreetTask',57,434.8,'uniform_extension')
extension=dict(base,catalogue_id='AST-STF-G3-025',parts=extension_parts,fixtures=extension_lights)
write(HERE/'source/UNIFORM_STREET_EXTENSION.json',extension)

# Scoped precinct copy: exact original street polygons restricted to two central loops and aft street.
# It is a successor selection, never loaded concurrently with the same original meshes.
selected_area=unary_union([box(-105.7,-42.7,-53.4,42.7),box(53.4,-42.7,105.7,42.7),box(54.9,420,59.1,432.14)])
cut_union=unary_union(cuts);selected=[];original_selection=[];omissions=set()
for q in streets['parts']:
    if 'boundary'not in q:continue
    footprint=Polygon(q['boundary'],q['holes']);selection=footprint.intersection(selected_area)
    if selection.area<1e-9:continue
    original_selection.append(q['name'])
    if q['category']=='screen_wall': selection=selection.difference(cut_union)
    selection=selection.difference(column_footprints)
    prisms(selected,q['name']+'_Selected',selection,*q['y'],q['role'],q['category'],q['batch_cell'])
    omissions.add(q['category']+'_'+q['role']+'_'+q['batch_cell'])
fixtures=[]
for label,side in [('Port',-1),('Starboard',1)]:
    for z in [-30,-18,-6,6,18,30]:fixture(selected,fixtures,label+'OuterTask_'+str(z),(-102 if side==-1 else 103),z,label.lower()+'_outer')
    for z in [-40,40]:
        for x in [63,75,87,99]:fixture(selected,fixtures,label+'CrossTask_'+str(x)+'_'+str(z),side*x,z,label.lower()+'_cross')
fixture(selected,fixtures,'UniformApproachTask',57,424,'uniform_approach')
selection_spec=dict(base,catalogue_id='AST-STF-G3-026',parts=selected,fixtures=fixtures,
 selected_original_semantic_parts=original_selection,original_geometry_unchanged=True,protected_column_notches=protected_columns,
 explicit_portal_cuts=[list(g.exterior.coords)[:-1]for g in cuts],
 adoption='Use selected precinct only, or compose cuts into full original street source. Never load selected polygons over full street. No original source overwritten.')
write(HERE/'source/SELECTED_STREET_PRECINCTS.json',selection_spec)

clearstreet=unary_union([Polygon(q['boundary'],q['holes'])for q in streets['route_shape']+streets['porch_shapes']]).intersection(selected_area)
floor_request=clearstreet.buffer(.14,join_style=2).union(unary_union(request)).union(uniform_outer)
compiled=json.loads((ROOT/'Game/data/generated/structural_meshes.json').read_text());received=json.loads((ROOT/'Game/data/generated/received_structural_meshes.json').read_text())
assert received['source_checks']['baseline_structural_sha256']==sha(ROOT/'Game/data/generated/structural_meshes.json')
actual=unary_union([Polygon(t)for region in compiled['regions']+received['regions']if region['deck']=='D03'for t in region['triangles']])
missing=floor_request.difference(actual).difference(column_footprints)
floor_parts=[];prisms(floor_parts,'MissingOnlyD03Floor',missing,11.76,12,'staff_rubber','floor','missing_d03_floor')
floor_spec=dict(base,catalogue_id='AST-STF-G3-027',parts=floor_parts,fixtures=[],
 floor_patch_proposal_only=True,original_floor_overlap_m2=missing.intersection(actual).area,
 adoption='Group-local missing-only floor patch for staged tests. Integration owner recomputes against current compiler floor; no shared registry/root edits. Structural capacity unaccepted.')
write(HERE/'source/MISSING_ONLY_FLOOR_PATCH.json',floor_spec)
layout=json.loads((ROOT/'Game/data/whole_ship_layout.json').read_text())
programmes=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']=='D03'])
bank=json.loads((FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json').read_text())
bankshape=unary_union([box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])for q in bank['instances']])
inner=Polygon(next(q for q in json.loads((ROOT/'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json').read_text())['levels']if q['deck']=='D03')['inner_reservation_boundary'])
voids={q['id']:floor_request.intersection(Polygon(q['boundary'])).area for q in json.loads((ROOT/'Game/data/spatial_layout.json').read_text())['voids']if'D03'in q['decks']}
report=dict(status='PASS',receivers=checks,new_missing_floor_m2=missing.area,requested_floor_m2=floor_request.area,
 original_floor_overlap_m2=missing.intersection(actual).area,protected_programme_overlap_m2=floor_request.intersection(programmes).area,
 protected_bank_envelope_overlap_m2=floor_request.intersection(bankshape).area,protected_void_overlap_m2=voids,
 outside_hull_m2=floor_request.difference(inner).area,selected_street_parts=len(selected),mounted_new_fixture_count=sum(len(q['fixtures'])for q in receivers+[extension,selection_spec]),
 source_only=True,default_main_unchanged=True,capacity_or_identity_migration=False)
# Header nib joins extend a few centimetres within their own retained allocation and do not add floor there.
assert report['original_floor_overlap_m2']<1e-7 and report['protected_bank_envelope_overlap_m2']<1e-7
assert report['outside_hull_m2']<1e-7 and all(v<1e-7 for v in voids.values())
report['new_missing_floor_programme_overlap_m2']=missing.intersection(programmes).area
other_programmes=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']=='D03'and q['programme_key']not in ['D03_directory_05','D03_directory_06','D03_directory_10']])
report['other_programme_overlap_m2']=floor_request.intersection(other_programmes).area
write(HERE/'qa/PLAN_CHECKS.json',report)
assert report['new_missing_floor_programme_overlap_m2']<1e-7 and report['other_programme_overlap_m2']<1e-7
write(HERE/'qa/PLAN_CHECKS.json',report)
write(HERE/'source/PRECINCT_CONTRACT.json',dict(base,base_commit=BASE,receivers=[q['catalogue_id']for q in receivers],
 service_doors=doors,frozen_manifests=frozen,source_model_specs=[f'{q["catalogue_id"]}.glb'for q in receivers+[extension,selection_spec,floor_spec]],
 selected_street_programme_boundaries_preserved=True,new_floor_m2=missing.area,fixture_count=report['mounted_new_fixture_count'],
 crew_berths=dict(required=400,physical_bank_proposal=398,preserved_shared_home=2,authoritative_key_reconciliation='HELD',migration_applied=False),
 protected_routes=['D01 shared lower circuit unchanged','D04 neighborhood staff routes unchanged','Original fore-port lift stop identities and D04-D07 blank rule unchanged'],
 clean_used_flow='Uniform issue and used-return rooms retain their separate original fixtures; new receiver/street remains shared. Dedicated shipwide segregation and sealed-load dispatch unfinished.',
 retained_hold=['184 inferred crew addresses','C036 original berth/person/save keys','Seven other staff-riser reservations','Clinical interlock/dispatch','Primary engineering','Full-species and loaded-cart','Stock/refill/persistence','Final game/CRT/hardware visuals']))
print(json.dumps(report))
