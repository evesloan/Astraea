"""Specify isolated profiled receivers against exact source surface segments.

No production writes or capacity claims. Runtime contact and lower-room clearance
must pass before adoption.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import numpy as np

P = Path(__file__).resolve().parent
G = Path('/workspace/astraea-protected-integration-20261012/Game')
C = P.parent
regions = json.loads((P/'source_floor_regions/REGIONS.json').read_text())['regions']
homes = json.loads((C/'consolidated_all_eight_20261013/CONSOLIDATED_PLAN.json').read_text())['G2_homes']
district = {str(h['key']): h['reservation']['house'] for h in homes}
house_names = {'port_forward_upper_house': 'Tidal Garden',
               'starboard_forward_upper_house': 'Quiet Grove',
               'port_central_upper_house': 'Star Atlas',
               'starboard_central_upper_house': 'Night Garden',
               'port_aft_upper_house': 'Sunset',
               'starboard_aft_upper_house': 'Family Terrace'}
members = json.loads((P/'RETAINED_MEMBER_ANCHOR_CANDIDATES.json').read_text())['components']
surfaces = []
for model in sorted({r['source_model'] for r in members}):
    raw = (G/'assets/models'/model).read_bytes()
    n = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+n]); binary = raw[28+n:]
    def acc(i):
        a = doc['accessors'][i]; view = doc['bufferViews'][a['bufferView']]
        assert not view.get('byteStride')
        dt = {5126: '<f4', 5125: '<u4', 5123: '<u2'}[a['componentType']]
        w = {'VEC3': 3, 'SCALAR': 1}[a['type']]
        return np.frombuffer(binary, dtype=dt, count=a['count']*w,
                             offset=view.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],w)
    for node in doc['nodes']:
        name = node.get('name',''); category = node.get('extras',{}).get('category','')
        if 'mesh' not in node or not (category == 'pier' or 'column' in name.lower()):
            continue
        assert not any(k in node for k in ['matrix','translation','rotation','scale'])
        offset = np.array([63,84,0] if model == 'AST-COM-003.glb' else [0,0,0])
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            v = acc(primitive['attributes']['POSITION']) + offset
            ix = acc(primitive['indices']).ravel() if 'indices' in primitive else np.arange(len(v))
            for tri in v[ix].reshape(-1,3,3):
                for y in [101.66,106.16]:
                    points = []
                    for a,b in zip(tri,np.roll(tri,-1,axis=0)):
                        if abs(a[1]-y)<1e-7: points.append([float(a[0]),float(a[2])])
                        if (a[1]-y)*(b[1]-y)<0:
                            q = a+(b-a)*((y-a[1])/(b[1]-a[1]))
                            points.append([float(q[0]),float(q[2])])
                    if len(points)>=2:
                        surfaces.append({'model':model, 'node':name, 'y':y,
                                         'sha256':hashlib.sha256(raw).hexdigest(),
                                         'segment':points[:2], 'district': next(r['district'] for r in members if r['source_model']==model)})
for row in json.loads((P/'EXACT_HULL_FRAME_ATTACHMENT_SURFACES.json').read_text())['frame_nodes']:
    for y in [101.66,106.16]:
        for segment in row['surface_segments_xz_by_y'][str(y)]:
            surfaces.append({'model':row['model'],'node':row['node'],'y':y,
                             'sha256':row['model_sha256'],'segment':segment,'district':None})

def nearest(q, segment):
    a,b = segment; dx,dz = b[0]-a[0], b[1]-a[1]
    ll = dx*dx+dz*dz
    margin=min(.25,max(.05,.08/math.sqrt(ll))) if ll>1e-12 else 0
    t = max(margin,min(1-margin,((q[0]-a[0])*dx+(q[1]-a[1])*dz)/ll)) if ll>1e-12 else 0
    point = [a[0]+t*dx,a[1]+t*dz]
    return point, math.dist(point,q)

def spans(rings,z):
    hits=[]
    for ring in rings:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            if (a[1]<=z<b[1]) or (b[1]<=z<a[1]):
                hits.append(a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1]))
    hits.sort(); assert len(hits)%2==0
    return [(hits[i],hits[i+1]) for i in range(0,len(hits),2) if hits[i+1]-hits[i]>1e-5]

def offset_ring(ring, clearance=.20):
    # Source exterior rings are clockwise and void rings counterclockwise.
    # Offset to the right of every oriented edge: into floor, away from voids.
    lines=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        assert length>1e-8
        shift=[clearance*dz/length,-clearance*dx/length]
        lines.append(([a[0]+shift[0],a[1]+shift[1]],[dx,dz]))
    result=[]
    for i,(point,direction) in enumerate(lines):
        other,od=lines[i-1];matrix=np.array([[direction[0],-od[0]],[direction[1],-od[1]]])
        if abs(np.linalg.det(matrix))<1e-9:
            result.append(point);continue
        t=np.linalg.solve(matrix,np.array(other)-np.array(point))[0]
        result.append([point[0]+direction[0]*t,point[1]+direction[1]*t])
    return result

def crosses_void(a,b,holes):
    # Segment/polygon clipping with inclusive boundaries, for the full member
    # envelope because the input voids already have .20m profile clearance.
    for hole in holes:
        for c,d in zip(hole,hole[1:]+hole[:1]):
            v=np.array(b)-np.array(a);w=np.array(d)-np.array(c)
            matrix=np.column_stack((v,-w));det=np.linalg.det(matrix)
            if abs(det)<1e-9:continue
            t,u=np.linalg.solve(matrix,np.array(c)-np.array(a))
            if 1e-7<t<1-1e-7 and -1e-7<=u<=1+1e-7:return True
    return False

def inside(point,ring):
    x,z=point;hit=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit

def receiving_start(point,girders,holes,y):
    candidates=[]
    for member in girders:
        if member['role'] not in ['boundary_receiver','slab_strongback']:continue
        a=[member['a'][0],member['a'][2]];b=[member['b'][0],member['b'][2]]
        start,distance=nearest(point,[a,b])
        if not crosses_void(start,point,holes):candidates.append((distance,start))
    if not candidates:return None
    _,start=min(candidates,key=lambda pair:pair[0])
    return [start[0],y,start[1]]

result=[]
for region in regions:
    owner = region['source_owner']; house = district.get(owner,owner)
    rings=[offset_ring(ring) for ring in region['rings']]
    lo=min(v[1] for v in rings[0]); hi=max(v[1] for v in rings[0]); y=region['floor_y']-.52
    girder=[]
    for ring_index,ring in enumerate(rings):
        for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
            if math.dist(a,b)>0.02:
                girder.append({'name':f'edge_{ring_index}_{i}','a':[a[0],y,a[1]],'b':[b[0],y,b[1]],'role':'boundary_receiver'})
    count=max(2,math.ceil((hi-lo)/3))
    stations=[lo+(hi-lo)*(i+.5)/count for i in range(count)]
    for i,z in enumerate(stations):
        for j,(x0,x1) in enumerate(spans(rings,z)):
            girder.append({'name':f'strongback_{i}_{j}','a':[x0,y,z],'b':[x1,y,z],'role':'slab_strongback'})
    anchors=[]
    for fraction in [.25,.75]:
        z=lo+(hi-lo)*fraction; ranges=spans(rings,z); assert ranges
        x0,x1=max(ranges,key=lambda x:x[1]-x[0]); q=[(x0+x1)/2,z]
        if region['floor_y']==106.5:
            # Upper floors belong to the same private home. Receive them on
            # explicit new columns joined to its new lower receiver, rather
            # than routing through its protected cabin/void to distant hull.
            lower=next(r for r in result if r['source_owner']==owner and r['floor_y']==102)
            candidates=[]
            for member in lower['members']:
                if member['role']=='primary_transfer':continue
                a,b=[member['a'][0],member['a'][2]],[member['b'][0],member['b'][2]]
                for t in [i/40 for i in range(41)]:
                    point=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]
                    if not inside(point,rings[0]) or any(inside(point,h) for h in rings[1:]):continue
                    if anchors and math.dist(point,anchors[0]['surface_point_xz'])<3:continue
                    start=receiving_start(point,girder,rings[1:],y)
                    if start is None:continue
                    candidates.append((math.dist(q,point),point,member,start))
            assert candidates,(region['id'],'no_same_unit_lower_frame_attachment')
            _,point,member,start=min(candidates,key=lambda x:x[0])
            anchors.append({'authored_lower_receiver_region':lower['region_id'],
                            'authored_lower_receiver_member':member['name'],
                            'surface_point_xz':point,'slab_attachment_xyz':start,
                            'transfer_length_m':math.dist(start,[point[0],y,point[1]]),
                            'actual_contact_and_clearance_verified':False,'capacity_verified':False})
            index=len(anchors)
            girder.append({'name':f'upper_transfer_{index}','a':start,'b':[point[0],y,point[1]],'role':'same_unit_upper_transfer'})
            girder.append({'name':f'same_unit_post_{index}','a':[point[0],member['a'][1],point[1]],
                           'b':[point[0],y,point[1]],'role':'same_unit_post'})
            continue
        candidates=[]
        for s in surfaces:
            if abs(s['y']-(region['floor_y']-.34))>1e-5:continue
            if s['district'] is not None and s['district']!=house_names[house]:continue
            if math.dist(*s['segment'])<.05:continue
            a,dist=nearest(q,s['segment'])
            if anchors and math.dist(a,anchors[0]['surface_point_xz'])<3:continue
            start=receiving_start(a,girder,rings[1:],y)
            if start is None:continue
            candidates.append((dist,a,s,start))
        assert candidates,region['id'];distance,point,s,start=min(candidates,key=lambda x:x[0])
        anchor={'source_model':s['model'],'source_sha256':s['sha256'],'source_node':s['node'],
                'source_slice_y':s['y'],'exact_source_surface_segment_xz':s['segment'],
                'surface_point_xz':point,'slab_attachment_xyz':start,
                'transfer_length_m':math.dist(start,[point[0],y,point[1]]),
                'actual_contact_and_clearance_verified':False,'capacity_verified':False}
        assert anchor['transfer_length_m']<35,(region['id'],'unbounded_primary_transfer',anchor['transfer_length_m'])
        anchors.append(anchor)
        if anchor['transfer_length_m']>.02:
            girder.append({'name':f'transfer_{len(anchors)}','a':start,'b':[point[0],y,point[1]],'role':'primary_transfer'})
    result.append({'region_id':region['id'],'source_owner':owner,'house':house,
                   'floor_y':region['floor_y'],'profile':{'width':.36,'depth':.60,'flange_thickness':.045,'web_thickness':.055},
                   'source_surface_anchors':anchors,'members':girder,
                   'engineering_sizing_or_admission_accepted':False})
out=P/'receiver_frame_candidate';out.mkdir(exist_ok=True)
data={'schema':'astraea.approved_receiver_members.r001','status':'ISOLATED_GEOMETRIC_CANDIDATE_REQUIRES_CONTACT_AND_CLEARANCE',
      'base_commit':'e15f9d83838f3fca372475c2dfd8d1a29bf685d2', 'slab_overlap_m':.02,
      'member_plan_clearance_from_source_floor_edges_and_private_voids_m':.02,
      'original_structures_changed':False,'production_adoption':False,'regions':result}
(out/'MEMBERS.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'regions':len(result),'members':sum(len(r['members'])for r in result),
                  'exact_source_surface_anchors':sum(len(r['source_surface_anchors'])for r in result),
                  'maximum_candidate_transfer_m':max(a['transfer_length_m']for r in result for a in r['source_surface_anchors']),
                  'production_changed':False,'verified_capacity_claims':0}))
