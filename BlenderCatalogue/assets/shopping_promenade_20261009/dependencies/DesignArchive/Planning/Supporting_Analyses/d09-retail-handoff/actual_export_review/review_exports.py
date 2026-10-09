"""Read-only binary GLB review. Writes only beside this script. No Blender/render calls."""
from pathlib import Path
import json, struct, hashlib, math
from datetime import datetime, timezone
import numpy as np

OUT=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PLAN=CAT/'qa/batch18/assembly/plan.json'
PREFLIGHT=CAT/'qa/batch18/assembly/source_preflight_r06/preflight.json'
HANDOFF=OUT.parent/'D09_retail_programme_reference_handoff.json'
sha=lambda data:hashlib.sha256(data).hexdigest()
inputs={p:p.read_bytes() for p in [PLAN,PREFLIGHT,HANDOFF]}
plan=json.loads(inputs[PLAN]); preflight=json.loads(inputs[PREFLIGHT]); handoff=json.loads(inputs[HANDOFF])
assert sha(inputs[PLAN])==preflight['plan_sha256']
EPS=1e-6
pref={r['row_key']:r for r in preflight['items']}
ship_pref={r['part_state'].split('@')[0]:r for r in preflight['historical_allocation_checks']}
expected_regions={
 'arrival_band':([-6,0,-.001],[6,1.5,10]),
 'central_test_strip':([-1.2,1.5,-.001],[1.2,11.5,10]),
 'wall_browse_pad':([-4.4,1.8,-.001],[-2.9,5.2,10]),
 'island_browse_pad':([2.25,2,-.001],[4.15,3.5,10]),
 'public_parcel_pad':([2.1,7.05,-.001],[4.3,8.45,10]),
 'staff_work_pad':([2.1,9.35,-.001],[4.3,10.85,10])}
assert len(plan['proposed_empty_regions'])==6
for region in plan['proposed_empty_regions']:
    a,b=expected_regions[region['id']]
    assert np.allclose(region['min_source_m'],a,atol=1e-12,rtol=0)
    assert np.allclose(region['max_source_m'],b,atol=1e-12,rtol=0)
C=np.array([[1.,0,0],[0,0,-1],[0,1,0]]) # GLB (x,y,z) -> source (x,-z,y)
S=np.array([[0.,-1,0],[0,0,1],[-1,0,0]])
SHIP_OFFSET=np.array([78.,52.5,236.])

def accessor(doc,blob,index):
    a=doc['accessors'][index]
    assert 'sparse' not in a, 'Sparse accessor not implemented; do not silently skip'
    assert 'bufferView' in a
    v=doc['bufferViews'][a['bufferView']]
    assert v.get('buffer',0)==0
    dtypes={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
    counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
    dt=np.dtype(dtypes[a['componentType']]); components=counts[a['type']]
    stride=v.get('byteStride',dt.itemsize*components)
    offset=v.get('byteOffset',0)+a.get('byteOffset',0)
    assert offset+(a['count']-1)*stride+components*dt.itemsize<=len(blob)
    arr=np.ndarray(shape=(a['count'],components),dtype=dt,buffer=blob,offset=offset,strides=(stride,dt.itemsize)).copy()
    if a.get('normalized'):
        info=np.iinfo(dt); arr=np.maximum(arr.astype(float)/info.max,-1) if info.min<0 else arr.astype(float)/info.max
    return arr

def local_matrix(n):
    if 'matrix' in n:
        return np.array(n['matrix'],dtype=float).reshape(4,4,order='F')
    x,y,z,w=n.get('rotation',[0,0,0,1])
    assert abs(x*x+y*y+z*z+w*w-1)<1e-5
    r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
    return m

def decode(path):
    data=path.read_bytes();inputs[path]=data
    magic,version,total=struct.unpack_from('<4sII',data,0)
    assert magic==b'glTF' and version==2 and total==len(data)
    chunks=[];off=12
    while off<len(data):
        size,typ=struct.unpack_from('<II',data,off);off+=8;chunks.append((typ,data[off:off+size]));off+=size
    doc=json.loads(next(v for typ,v in chunks if typ==0x4e4f534a))
    blob=next(v for typ,v in chunks if typ==0x004e4942)
    assert not doc.get('extensionsRequired')
    assert len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
    triangles=[];node_rows=[];mesh_rows=[];seen_nodes=set();vertex_total=0
    def visit(i,parent,stack):
        nonlocal vertex_total
        assert i not in stack
        n=doc['nodes'][i];m=parent@local_matrix(n);seen_nodes.add(i)
        assert 'skin' not in n, 'Skinned geometry requires explicit evaluation'
        det=float(np.linalg.det(m[:3,:3])); assert det>0, 'Unexpected reflected or singular scene node'
        node_rows.append({'index':i,'name':n.get('name'),'determinant':det,'mesh':n.get('mesh')})
        if 'mesh' in n:
            mesh=doc['meshes'][n['mesh']]
            assert not n.get('weights') and not mesh.get('weights')
            for j,prim in enumerate(mesh['primitives']):
                assert prim.get('mode',4)==4 and not prim.get('targets') and not prim.get('extensions')
                p=accessor(doc,blob,prim['attributes']['POSITION']).astype(float)
                assert p.shape[1]==3 and np.isfinite(p).all()
                ids=accessor(doc,blob,prim['indices']).ravel().astype(int) if 'indices' in prim else np.arange(len(p))
                assert len(ids)%3==0 and ids.min()>=0 and ids.max()<len(p)
                v=(p@m[:3,:3].T)+m[:3,3]
                t=v[ids.reshape(-1,3)];triangles.append(t);vertex_total+=len(p)
                mesh_rows.append({'node':i,'mesh':n['mesh'],'primitive':j,'vertices':len(p),'triangles':len(t),
                                  'native_bounds_from_referenced_vertices':{'min':t.reshape(-1,3).min(0).tolist(),'max':t.reshape(-1,3).max(0).tolist()}})
        for child in n.get('children',[]):visit(child,m,stack+[i])
    scene=doc['scenes'][doc.get('scene',0)]
    for i in scene['nodes']:visit(i,np.eye(4),[])
    tri=np.concatenate(triangles); assert len(tri)>0
    return tri,{'file':str(path.relative_to(CAT)),'sha256':sha(data),'bytes':len(data),'active_scene':doc.get('scene',0),
                'scene_nodes':len(seen_nodes),'scene_mesh_primitive_instances':len(mesh_rows),'accessor_vertex_total':vertex_total,
                'referenced_triangle_count':len(tri),'all_scene_node_determinants_positive':True,'node_transforms':node_rows,'mesh_primitives':mesh_rows}

def triangle_intersects_box(tri,lo,hi):
    # Separating axis theorem: 3 box axes, triangle normal, and 9 edge x box-axis tests.
    c=(lo+hi)/2;half=(hi-lo)/2;v=tri-c;e=np.roll(v,-1,axis=0)-v
    axes=[*np.eye(3),np.cross(e[0],e[1])]
    axes += [np.cross(edge,axis) for edge in e for axis in np.eye(3)]
    for axis in axes:
        if np.dot(axis,axis)<1e-28:continue
        q=v@axis;r=half@np.abs(axis)
        if q.min()>r or q.max()<-r:return False
    return True

def checked_region(tri,lo,hi):
    # Contract each side by one micrometre so boundary contact is never advertised as positive clearance.
    innerlo=lo+EPS;innerhi=hi-EPS
    tlo=tri.min(1);thi=tri.max(1)
    candidates=np.flatnonzero(np.all(thi>=innerlo,axis=1)&np.all(tlo<=innerhi,axis=1))
    hits=[int(k) for k in candidates if triangle_intersects_box(tri[k],innerlo,innerhi)]
    vertices=tri.reshape(-1,3);a=vertices.min(0);b=vertices.max(0)
    separations=np.maximum(lo-b,a-hi);sep=float(separations.max());axis=int(separations.argmax())
    return {'strict_interior_triangle_hits':len(hits),'hit_triangle_indices':hits[:12],
            'aabb_candidates_after_numerical_inset':len(candidates),'triangles_checked_by_aabb':len(tri),
            'max_separating_axis_m_raw':sep,'separating_axis':'XYZ'[axis],
            'classification':'positive_arithmetic_separation' if sep>EPS else ('boundary_contact_within_numerical_tolerance' if sep>=-EPS else 'AABB_overlap_requires_triangle_result'),
            'passed':len(hits)==0}

unique={}
for item in plan['items']:
    p=CAT/item['variants']['closed']
    if p not in unique:unique[p]=decode(p)

instances=[];checks=[];all_tri={}
for item in plan['items']:
    key=item['key'];native,meta=unique[CAT/item['variants']['closed']]
    assert sha(inputs[CAT/item['variants']['closed']])==pref[key]['export_sha256']
    yaw=math.radians(item.get('source_z_rotation_deg',0));c,s=math.cos(yaw),math.sin(yaw)
    rot=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
    origin=np.array(item['source_origin_m'],dtype=float)
    source=(native@C.T)@rot.T+origin;all_tri[key]=source
    ship=source@S.T+SHIP_OFFSET
    v=source.reshape(-1,3);lo=v.min(0);hi=v.max(0);sv=ship.reshape(-1,3);slo=sv.min(0);shi=sv.max(0)
    pbound=pref[key]['actual_source_bounds_m'];sb=ship_pref[key]['actual_ship_bounds_m']
    source_delta=float(max(np.abs(lo-pbound['min']).max(),np.abs(hi-pbound['max']).max()))
    ship_delta=float(max(np.abs(slo-sb['min']).max(),np.abs(shi-sb['max']).max()))
    assert source_delta<=EPS and ship_delta<=1e-5
    assert len(source)==pref[key]['triangles']
    local_front=np.array([0.,-1,0]);placed_front=rot@local_front;front_ship=S@placed_front
    nominal=next((p.get('sample_source_bounds_xyz_m') for p in handoff['bounded_relative_plan_section_proposal']['components'] if p['catalogue_id']==item['asset_id']),None)
    margins={'source_X_negative':float(lo[0]+6),'source_X_positive':float(6-hi[0]),'source_Y_front':float(lo[1]),'source_Y_rear':float(12-hi[1])}
    contained=all(x>=-EPS for x in margins.values())
    instances.append({'key':key,'asset_id':item['asset_id'],'export_sha256':meta['sha256'],
       'source_origin_m':origin.tolist(),'source_z_rotation_deg':item.get('source_z_rotation_deg',0),
       'native_scene_bounds_m':{'min':native.reshape(-1,3).min(0).tolist(),'max':native.reshape(-1,3).max(0).tolist()},
       'independently_decoded_source_bounds_m':{'min':lo.tolist(),'max':hi.tolist()},
       'independently_decoded_ship_bounds_m':{'min':slo.tolist(),'max':shi.tolist()},
       'referenced_triangles':len(source),'source_preflight_bound_max_abs_difference_m':source_delta,
       'ship_preflight_bound_max_abs_difference_m':ship_delta,
       'source_preflight_source_transform_max_abs_difference':float(np.abs(rot-np.array(pref[key]['source_transform'])[:3,:3]).max()),
       'contained_in_historical_outer_plan':contained,'historical_outer_plan_margins_m':margins,
       'front_vector_source':placed_front.tolist(),'front_vector_ship':front_ship.tolist(),
       'native_to_source_det':float(np.linalg.det(C)),'placed_source_to_ship_det':float(np.linalg.det(S@rot)),
       'nominal_bounds_delta_m':None if nominal is None else {'min':[float(lo[k]-nominal[a][0]) for k,a in enumerate('xyz')],'max':[float(hi[k]-nominal[a][1]) for k,a in enumerate('xyz')]},
       'height_vs_deck_allowance_report_only':{'source_top_m':float(hi[2]),'below_recorded_8_25m_allowance_by_m':float(8.25-hi[2]),'actual_local_ceiling_fit':False}})
    for region in plan['proposed_empty_regions']:
        lo_r=np.array(region['min_source_m']);hi_r=np.array(region['max_source_m'])
        checks.append({'instance':key,'region':region['id'],**checked_region(source,lo_r,hi_r)})

# Positive controls use an actual nondegenerate triangle centroid, so the method must detect geometry.
controls=[]
for key,t in all_tri.items():
    a2=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)
    i=int(a2.argmax());center=t[i].mean(0)
    result=checked_region(t,center-.0001,center+.0001)
    assert result['strict_interior_triangle_hits']>0
    controls.append({'instance':key,'triangle_index':i,'control_center_source_m':center.tolist(),'control_box_half_extent_m':.0001,'real_geometry_intersection_detected':True})

bykey={r['key']:r for r in instances}
lo=lambda key:np.array(bykey[key]['independently_decoded_source_bounds_m']['min'])
hi=lambda key:np.array(bykey[key]['independently_decoded_source_bounds_m']['max'])
margins={'wall_to_arrival_band_m':float(lo('wall_bay')[1]-1.5),
         'wall_to_negative_allocation_edge_m':float(lo('wall_bay')[0]+6),
         'wall_to_central_strip_m':float(-1.2-hi('wall_bay')[0]),
         'island_to_central_strip_m':float(lo('island')[0]-1.2),
         'bench_to_central_strip_m':float(lo('workbench')[0]-1.2),
         'bench_rear_to_staff_pad_m':float(9.35-hi('workbench')[1]),
         'wall_bay_front_to_browse_pad_m_raw':float(-4.4-hi('wall_bay')[0]),
         'island_front_to_browse_pad_m_raw':float(lo('island')[1]-3.5),
         'bench_front_to_public_pad_m_raw':float(lo('workbench')[1]-8.45)}

assert all(r['contained_in_historical_outer_plan'] for r in instances)
assert all(c['passed'] for c in checks)
assert len(checks)==36 and len(instances)==6 and len(unique)==4
assert np.allclose(S,np.array(preflight['source_to_ship_matrix'])[:3,:3])
assert np.allclose(SHIP_OFFSET,np.array(preflight['source_to_ship_matrix'])[:3,3])
assert np.allclose(bykey['wall_bay']['front_vector_source'],[1,0,0])
assert np.allclose(bykey['workbench']['front_vector_ship'],[1,0,0])
assert np.linalg.det(C)==np.linalg.det(S)==1

frozen_before={str(p.relative_to(CAT)) if p.is_relative_to(CAT) else str(p):sha(data) for p,data in inputs.items()}
unchanged=all(p.read_bytes()==data for p,data in inputs.items())
assert unchanged
report={
 'schema':'astraea.d09_actual_export_bounded_review.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
 'status':'PASS for exact current snapshot; final production freeze not confirmed',
 'scope':'Independent binary decode of four unique closed native GLBs, placed as six instances using plan.json. Historical R070 outer containment, two new clear bands, four new approach pads, source/ship orientation and preflight-bound comparison only.',
 'input_hashes':frozen_before,'inputs_unchanged_during_review':unchanged,'final_freeze_confirmed':False,
 'historical_handoff_sha256_unchanged':sha(inputs[HANDOFF]),
 'coordinate_method':{'native_GLTF_to_source_formula':'source=(nativeX,-nativeZ,nativeY)',
    'native_GLTF_to_source_matrix':C.tolist(),'source_to_ship_formula':'ship=(78-sourceY,52.5+sourceZ,236-sourceX)',
    'source_to_ship_rotation':S.tolist(),'source_to_ship_translation':SHIP_OFFSET.tolist(),
    'node_processing':'Decode active scene hierarchy, each matrix or quaternion TRS, then actual POSITION and index accessors. Transform active referenced triangles in native GLB space, then native-to-source basis, then per-instance source Z rotation/translation, then proper source-to-ship basis. No source regeneration or render.',
    'normal_transport':'All node and basis determinants are positive. Direction/normal transport uses the corresponding proper basis; winding is never reversed or sourceX silently mirrored. This is orientation verification, not a new shading-normal craft audit.',
    'wall_front':'Local front -sourceY becomes +sourceX after +90 degrees, then -shipZ. Local left -X becomes -placedSourceY, toward the symbolic entrance datum.',
    'bench_faces':'Public local -sourceY becomes +shipX; staff local +sourceY becomes -shipX.',
    'door_side':'Placed source -Y faces +shipX, matching R070 historical +X entry edge.'},
 'decoder':{'uses_actual_binary_positions_and_indices':True,'uses_accessor_min_max_as_geometry':False,
    'supported': ['GLB2 binary buffers','strided numeric accessors','active scene matrix/quaternion TRS nodes','indexed triangle primitives'],
    'unsupported_inputs_fail_loudly':['sparse accessors','skins','morph targets','non-triangle primitive modes','primitive extensions or compression'],
    'required_unsupported_inputs_encountered':False},
 'decoded_unique_exports':[m for _,m in unique.values()],
 'instances':instances,
 'region_test_method':{'numerical_boundary_tolerance_m':EPS,'maximum_preflight_source_bound_tolerance_m':EPS,'maximum_preflight_ship_bound_tolerance_m':1e-5,
    'six_region_plan_bounds_match_prior_nominal_handoff_xy':True,
    'method':'Actual transformed triangle AABBs against each box contracted by 1 micrometre, with 13-axis triangle-box SAT for candidate overlaps. This rejects finite interior intrusion and separately reports boundary contact. The microscopic inset is numerical tolerance, not permitted construction clearance.',
    'region_scope':'Full sourceZ -0.001..10 vertical volumes as declared by the plan; all four proposed pads and both clear bands checked for all six instances.',
    'solid_scope':'Surface triangle screen and actual decoded bounds. Not a physics collision/occupancy/closed-volume proof; here all region pairs are separated in decoded AABB projection or only touch within numeric tolerance.'},
 'region_checks':checks,'positive_controls':controls,'measured_arithmetic_margins_m':margins,
 'summary':{'unique_designs':4,'placed_instances':6,'closed_container_instances':3,'empty_region_pair_checks':36,
    'empty_region_pair_checks_passed':sum(c['passed'] for c in checks),
    'outer_containment_instances_passed':sum(r['contained_in_historical_outer_plan'] for r in instances),
    'all_preflight_GLB_hashes_match':True,'plan_matches_preflight_hash':True,
    'maximum_source_bound_difference_from_preflight_m':max(r['source_preflight_bound_max_abs_difference_m'] for r in instances),
    'maximum_ship_bound_difference_from_preflight_m':max(r['ship_preflight_bound_max_abs_difference_m'] for r in instances),
    'proper_handedness_no_reflection':True,'no_new_registered_places':True},
 'material_findings':[
    'Wall, island and workbench nominal extents are met within numerical precision except the actual workbench is 0.020 m shallower at its rear than the nominal box.',
    'Wall-browse, island-browse and public parcel-pad boundaries have essentially zero geometric gap at the nominal fixture faces. These are boundary contacts, not positive safety clearance or actor-space guarantees.',
    'Workbench rear has approximately 0.020 m arithmetic separation from the proposed staff-pad front. This is not an ergonomic or moving-component reserve.',
    'All three closed containers remain in the outer allocation and clear of the six proposed empty regions. Support/contact validity and unsupported/handling states are left to the component reviewer.',
    'This snapshot can support the bounded arrangement review. Any changed GLB, plan, state, fixture movement or protrusion invalidates the affected hashes/checks until reviewed again.'
 ],
 'not_granted':['actual R070 finished room fit','door aperture/pocket/head or moving-door clearance','host floor/wall/ceiling support','facility slot transforms, exclusivity or ownership migration','six-species/cart/actor approach','contents compatibility or inventory','support/contact/load acceptance','body/collision proxy acceptance','final visual approval','render/camera acceptance','final production freeze'],
 'read_only_guarantee':'Only this actual_export_review directory was written. Historical handoff, catalogue, exports, plan, preflight, sources and runtime were not edited.'}
(OUT/'current_snapshot_actual_export_review.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'SHA256.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256.json'},indent=2)+'\n')
print(json.dumps({'status':report['status'],'summary':report['summary'],'margins':margins,
                 'report_sha256':sha((OUT/'current_snapshot_actual_export_review.json').read_bytes())},indent=2))
