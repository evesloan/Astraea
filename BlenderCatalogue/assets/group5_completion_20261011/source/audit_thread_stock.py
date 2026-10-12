"""Independent literal export/floor/contact audit for additive staff fit-out."""
from pathlib import Path
import ast,json,hashlib,struct
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
parser=ast.parse((P/'source/build_large_venue_lighting.py').read_text())
exec(compile(ast.Module(body=[next(n for n in parser.body if isinstance(n,ast.FunctionDef) and n.name=='exported_bounds')],type_ignores=[]),'literal_glb_bounds','exec'),globals())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((ROOT/'Game/data/architecture/group5/THREAD_STOCK_REPAIR.json').read_text())
original=ROOT/j['original_model'].replace('res://','Game/');new=ROOT/j['model_path'].replace('res://','Game/')
assert sha(original)==j['original_model_sha256'] and sha(new)==j['model_sha256']
assert sha(ROOT/j['native'])==j['native_sha256'] and sha(ROOT/j['original_native'])==j['original_native_sha256']
old={k:(a+np.array(j['model_origin_world_xyz']),b+np.array(j['model_origin_world_xyz'])) for k,(a,b) in exported_bounds(original).items()}
items={k:(a+np.array(j['model_origin_world_xyz']),b+np.array(j['model_origin_world_xyz'])) for k,(a,b) in exported_bounds(new).items()}
floor_path=ROOT/'Game/data/generated/structural_meshes.json'
floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_thread_shell_floor')
polygon=unary_union([Polygon(t) for t in floor['triangles']]);assert floor['floor_y']==52.5
contacts=[];intentional=[];unsupported=[]
for name,(a,b) in items.items():
    if not polygon.buffer(.00004).covers(box(a[0],a[2],b[0],b[2])):unsupported.append(name)
    for old_name,(c,d) in old.items():
        overlap=np.minimum(b,d)-np.maximum(a,c)
        if not np.all(overlap>.0001):continue
        row={'new':name,'original':old_name,'overlap_xyz_m':overlap.tolist()}
        allowed=(name in j['wall_mount_names'] and old_name.startswith('TAIL_StaffOuter_')) or (name.endswith('_fixture_stem') and old_name.startswith('TAIL_ServiceCeiling_'))
        (intentional if allowed else contacts).append(row)
mounts=[]
for name in j['wall_mount_names']:
    match=[r for r in intentional if r['new']==name];assert match,(name,'no original bearing')
    mounts.append({'new':name,'positive_original_wall_contacts':match})
stem_contacts=[]
for fixture in j['fixtures']:
    match=[r for r in intentional if r['new']==fixture['mount']];assert match,fixture
    a,b=items[fixture['lens']];at=np.array(fixture['world_xyz'])
    gap=float(np.linalg.norm(at-np.minimum(b,np.maximum(a,at))))
    assert .015<gap<.05 and at[1]<a[1]
    stem_contacts.append({'fixture':fixture['name'],'ceiling_contacts':match,'source_lens_gap_m':gap})
supports=[]
for row in j['generic_support_contacts']:
    a,b=items[row['mesh']];c,d=items[row['support']]
    assert abs(a[1]-d[1])<.00004 and a[0]>c[0] and b[0]<d[0] and a[2]>c[2] and b[2]<d[2]
    supports.append({'mesh':row['mesh'],'support':row['support'],'vertical_gap_m':float(a[1]-d[1]),'footprint_within_support':True})
for foot in j['foundation_contacts_world_xyz']:
    assert polygon.covers(box(foot[0]-.02,foot[2]-.02,foot[0]+.02,foot[2]+.02)) and foot[1]==floor['floor_y']
assert len(items)==j['native_mesh_count']+j['editable_lettering_count'],('export lettering/mesh count',len(items))
result={'status':'PASS' if not contacts and not unsupported else 'HOLD','new_export_meshes':len(items),'original_source_meshes':len(old),'floor_owner':floor['id'],'floor_source_sha256':sha(floor_path),'literal_floor_area_m2':polygon.area,'new_footprints_outside_original_floor':unsupported,'unintended_original_contacts':contacts,'wall_bearings':mounts,'ceiling_bearings_and_lens_gaps':stem_contacts,'generic_stock_supports':supports,'floor_feet':len(j['foundation_contacts_world_xyz']),'original_native_and_export_unchanged':True,'bounds_world_xyz':{k:[a.tolist(),b.tolist()] for k,(a,b) in items.items()},'scope':'Literal immutable original export/floor unions,new source bounding boxes,stock supports and positive mounting contacts;not structural sizing,inventory,capacity,rendered Game/CRT or whole-group acceptance'}
(P/'qa/THREAD_STOCK_SOURCE_FIT.json').write_text(json.dumps(result,indent=2)+'\n')
print('THREAD_STOCK_SOURCE_FIT',result['status'],len(items),'unintended',len(contacts),'unsupported',len(unsupported))
assert not contacts and not unsupported
