#!/usr/bin/env python3
"""Bounded selected-owner/source geometry proof, no engine or admission.

Use exact triangles, including visual foliage. The vehicle test uses a complete
closed-door box envelope, swept with conservative pose-interval padding. It is
distinct from the retained four-metre protected-space test.
"""
from pathlib import Path
import hashlib, json, math, struct, sys
sys.dont_write_bytecode=True
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'recovery/tram_section_successor_20261023'))
import triangle_gate as tg
from validate_source import owners
G=ROOT/'Game';OUT=G/'tram_section_successor_20261024';checks=0

def require(value,label):
    global checks
    assert value,label
    checks+=1

def read(path):return json.loads(tg.raw(path))

def header_bounds(path):
    # The installed Group7 sources have identity scene transforms. Refuse any
    # newly transformed source rather than guessing accessor bounds are world.
    with path.open('rb') as f:
        head=f.read(20);size=struct.unpack_from('<I',head,12)[0];d=json.loads(f.read(size))
    positions=[]
    for n in d['nodes']:
        require(n.get('translation',[0,0,0])==[0,0,0] and n.get('rotation',[0,0,0,1])==[0,0,0,1] and n.get('scale',[1,1,1])==[1,1,1] and 'matrix'not in n,'Group7 identity transform')
        if 'mesh'in n:
            for p in d['meshes'][n['mesh']]['primitives']:
                a=d['accessors'][p['attributes']['POSITION']];positions += [a['min'],a['max']]
    q=np.array(positions);return q.min(axis=0),q.max(axis=0)

def rot(yaw):return np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])

def corners(lo,hi):return np.array([[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]])

def intersects_box(tri,half):
    """Vectorized triangle/axis-aligned box SAT; touching counts as collision."""
    keep=np.all(tri.max(axis=1)>=-half,axis=1)&np.all(tri.min(axis=1)<=half,axis=1)
    t=tri[keep]
    if not len(t):return False
    edges=np.stack([t[:,1]-t[:,0],t[:,2]-t[:,1],t[:,0]-t[:,2]],axis=1)
    axes=[np.cross(edges[:,0],edges[:,1])]
    for e in range(3):
        for a in np.eye(3):axes.append(np.cross(edges[:,e],a))
    ok=np.ones(len(t),bool)
    for axis in axes:
        projection=np.einsum('nij,nj->ni',t,axis);radius=np.abs(axis)@half
        ok&=(projection.min(axis=1)<=radius+1e-9)&(projection.max(axis=1)>=-radius-1e-9)
    return bool(ok.any())

def main():
    plan=read(OUT/'section_plan_r002.json');parts=read(HERE/'geometry_r002/MESHES.json');poses=np.array(read(OUT/'POSE_KNOTS_r002.json'))
    require(not plan['active']and not any(plan[k]for k in ['integration_motion_admitted','integration_boarding_admitted','integration_joint_admitted']),'all admission off')
    old=read(ROOT/'recovery/tram_section_successor_20261023/candidate_r002/CANDIDATE.json')
    require(plan['central']==old['central'],'exact curved CENTRAL body/bridge preserved')
    require(tg.raw(OUT/'bridge.glb')==tg.raw(ROOT/'recovery/tram_section_successor_20261023/runtime_r002/AST-TRM-BRIDGE-20261023-r002.glb'),'exact previously connected bridge')
    require(plan['guideway']['running_width_m']==4 and plan['guideway']['running_clearance_top_y']-plan['guideway']['boarding_y']==4,'four metre width/height unchanged')
    require(not plan['unresolved_receivers'],'all receiver bindings resolved')
    layout=read(G/'data/generated/structural_meshes.json');pads=[]
    for part in parts:
        t=tg.part_triangles(part);require(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()>0,'outward volume '+part['name'])
        if 'Bearing_'not in part['name']and'SouthPad_'not in part['name']:continue
        points=np.array(part['vertices']);lo,hi=points.min(axis=0),points.max(axis=0);c=(lo+hi)/2
        floor=52.5 if 'SouthPad_'in part['name']else 61.
        matches=owners(c[0],c[2],hi[0]-lo[0],hi[2]-lo[2],[r for r in layout['regions']if r['floor_y']==floor]);area=(hi[0]-lo[0])*(hi[2]-lo[2])
        require(len(matches)==1 and abs(matches[0][1]-area)<1e-6,'complete pad bearing '+part['name']);pads.append({'name':part['name'],'owner':matches[0][0],'area_m2':area})
    route=np.array(plan['route_points_xz']);length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(route,axis=0),axis=1))]
    begin,end=plan['central_interval_m'];route=route[(length>=begin-1e-6)&(length<=end+1e-6)]
    oldroute=np.array(old['route_points_xz']);ll=np.r_[0,np.cumsum(np.linalg.norm(np.diff(oldroute,axis=0),axis=1))];oldroute=oldroute[(ll>=old['central_interval_m'][0]-1e-6)&(ll<=old['central_interval_m'][1]+1e-6)]
    source=[]
    def add(label,path,origin=(0,0,0),yaw=0):source.append((label,G/path,origin,yaw))
    core=read(G/'data/architecture/PRIMARY_ATRIUM_CORE.json')
    add('primary_core','assets/models/AST-CIR-005.glb',core['origin']);add('atrium','assets/models/AST-ATR-001.glb')
    add('nursery','assets/models/AST-ATR-001_botanical_nursery_open001.glb')
    for x,z in [(-31,-18),(-31,18),(31,-18),(31,18),(-18,-46),(18,-46),(-18,46),(18,46)]:
        yaw=(0 if x>0 else math.pi)if abs(x)>abs(z)else(math.pi/2 if z<0 else -math.pi/2)
        for filename in ['AST-STR-001-H826.glb','AST-STR-002-H826.glb']:add(filename+f'@{x},{z}','assets/models/'+filename,(x,52.5,z),yaw)
    screened=[]
    for manifest in ['data/architecture/GROUP7_COMPLETION.json','data/consolidated_all_eight_20261013/G7_ADDITIONAL.json']:
        for row in read(G/manifest)['models']:
            path=G/'assets/models'/row['file'];lo,hi=header_bounds(path)
            overlap=hi[1]>=55.55 and lo[1]<=60.1 and hi[0]>=route[:,0].min()-3 and lo[0]<=route[:,0].max()+3 and hi[2]>=route[:,1].min()-3 and lo[2]<=route[:,1].max()+3
            screened.append({'file':row['file'],'source_sha256':row['sha256'],'header_aabb':[lo.tolist(),hi.tolist()],'selected_for_triangles':bool(overlap)})
            if overlap:
                require(hashlib.sha256(tg.raw(path)).hexdigest()==row['sha256'],'selected installed G7 pin');add(row['cell'],'assets/models/'+row['file'])
    for row in read(G/'data/architecture/ATRIUM_GALLERY_RECEIVING.json')['rooms']:
        if row['deck']in ['D09','D10']:add(row['id'],'assets/models/'+row['model_file'],row['origin_world_xyz'])
    for file,origin,yaw in [('AST-SAL-007.glb',(64,52.5,-15),0),('AST-SAL-008.glb',(68,52.5,-12),0),('AST-SAL-001.glb',(52,52.5,0),math.pi/2)]:add('retail/'+file,'assets/models/'+file,origin,yaw)
    for code in ['014_central_source','017_receiving_module','018_central_stair_receiving']:add(code,f'source_derivatives/group4_completion_20261011/AST-TRM-G4-{code}.glb')
    removed_prefix=('M003_Site_','M003_UnderwebGirder_','M003_SouthFoot_');removed_exact={'V2_Central_NorthEnd_infill','V2_Central_NorthEnd_rail','V2__CENTRAL__Boarding_Post_-73.2','V2__CENTRAL__Boarding_Post_-70.8','V2__CENTRAL__Boarding_Header'}
    triangles=[];labels=[];hits=[];old_g7=[];sources=[]
    for label,path,origin,yaw in source:
        sources.append({'label':label,'path':'res://'+str(path.relative_to(G)),'origin':origin,'yaw':yaw})
        for obj in tg.glb(path,origin,yaw):
            if obj['name'].startswith(removed_prefix)or obj['name']in removed_exact:continue
            t=obj['triangles'];triangles.append(t);labels.extend([label+'/'+obj['name']]*len(t))
            n,w,_=tg.swept_hits(t,route,[55.55,60.1])
            if n:hits.append({'kind':'new_four_metre_route','owner':label+'/'+obj['name'],'triangles':n,'witnesses':w})
            if 'ComposedEdge'in label:
                n,w,_=tg.swept_hits(t,oldroute,[55.55,60.1])
                if n:old_g7.append({'owner':label+'/'+obj['name'],'triangles':n,'witnesses':w})
    for part in parts:
        t=tg.part_triangles(part)
        for name,path,band in [('protected_lower',np.array(plan['protected_route_xz']),[52.55,56.55]),('upper',route,[56.1,60.1])]:
            n,w,_=tg.swept_hits(t,path,band)
            if n:hits.append({'kind':name,'owner':part['name'],'triangles':n,'witnesses':w})
        # Rolling rail/web intentionally contacts wheels, all other architecture stays.
        if part['name']not in ['TSC23_ContinuousWeb','TSC23_RailPort','TSC23_RailStarboard']:
            triangles.append(t);labels.extend(['candidate/'+part['name']]*len(t))
    # Complete closed moving assembly, not the cylinder surrogate. Keep all visible
    # meshes including visual-only details, clamps through their full stroke, the
    # retained operating console, closed portals and articulated bogie extrema.
    boarding=read(G/'data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json');travel=read(G/'data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json');controls=read(G/'data/architecture/GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE.json')
    clouds=[];vehicle_sources=[];component_boxes=[]
    def vehicle(path,origin=(0,0,0),yaw=0,scale=(1,1,1),extra_x=0.):
        obj=list(tg.glb(path))
        for item in obj:
            q=item['points']*np.array(scale)@rot(yaw).T+origin;lo,hi=q.min(axis=0),q.max(axis=0);lo[0]-=extra_x;hi[0]+=extra_x
            component_boxes.append((str(path.name)+'/'+item['name'],lo,hi))
        p=np.concatenate([x['points']for x in obj]);p=p*np.array(scale)@rot(yaw).T+origin
        lo,hi=p.min(axis=0),p.max(axis=0);lo[0]-=extra_x;hi[0]+=extra_x;clouds.append(corners(lo,hi));vehicle_sources.append({'path':str(path.relative_to(ROOT)),'bounds':[lo.tolist(),hi.tolist()]})
    for row in boarding['models']:
        if row['role']in ['vehicle','restraint']:vehicle(G/boarding['model_root'].removeprefix('res://')/row['file'],extra_x=.139 if row['role']=='restraint'else 0.)
    for gate in boarding['vehicle_gate_placements']:vehicle(G/'assets/models/AST-DOR-003.glb',gate['origin'],gate['yaw'],gate['scale'])
    vehicle(G/controls['model_root'].removeprefix('res://')/controls['exports'][0]['file'])
    bogie=next(x for x in travel['models']if '028_'in x['file']);objects=list(tg.glb(G/travel['model_root'].removeprefix('res://')/bogie['file']))
    # Original source wheels are reparented to the same steering trucks. Bound
    # each articulated component over its actual complete allowable yaw range,
    # including the gaps between sample angles, without filling the whole car.
    vehicle_item=next(x for x in boarding['models']if x['role']=='vehicle')
    wheels=[x for x in tg.glb(G/boarding['model_root'].removeprefix('res://')/vehicle_item['file'])if 'Tram_Wheel'in x['name']]
    for item in objects+wheels:
        p=item['points'];moving=any('BOGIE_MOVING_ROOT'in x for x in item['ancestors'])or 'Tram_Wheel'in item['name']
        if moving:
            sign=-1 if p[:,2].mean()<0 else 1;local=p-np.array([0,-.2,1.5*sign]);bb=corners(local.min(axis=0),local.max(axis=0))
            angles=np.linspace(-float(travel['maximum_relative_bogie_yaw_rad']),float(travel['maximum_relative_bogie_yaw_rad']),65)
            q=np.concatenate([bb@rot(angle).T+np.array([0,-.2,1.5*sign])for angle in angles])
            padding=2*np.linalg.norm(np.max(abs(bb[:,[0,2]]),axis=0))*math.sin((angles[1]-angles[0])/2)+float(travel['cross_slide_limit_m'])
            lo,hi=q.min(axis=0)-np.array([padding,0,padding]),q.max(axis=0)+np.array([padding,0,padding])
        else:lo,hi=p.min(axis=0),p.max(axis=0)
        clouds.append(corners(lo,hi));component_boxes.append(('steering/'+item['name'],lo,hi))
    p=np.concatenate(clouds);vlo,vhi=p.min(axis=0),p.max(axis=0);center=(vlo+vhi)/2;half=(vhi-vlo)/2
    selected=poses[(poses[:,0]>=begin)&(poses[:,0]<=end)];tri=np.concatenate(triangles);lo=tri.min(axis=1);hi=tri.max(axis=1)
    sweep_hits=[];max_padding=0.;queries=0
    for i in range(len(selected)-1):
        a,b=selected[i:i+2];yaw_delta=abs(math.atan2(math.sin(b[3]-a[3]),math.cos(b[3]-a[3])))
        basis=rot(a[3]);translation=np.array([b[1]-a[1],0.,b[2]-a[2]])@basis
        angular=2*np.linalg.norm(np.maximum(abs(vlo[[0,2]]),abs(vhi[[0,2]])))*math.sin(yaw_delta/2)
        padding=np.abs(translation)+np.array([angular+.002,0.,angular+.002])
        max_padding=max(max_padding,float(padding.max()));origin=np.array([a[1],56.1,a[2]]);wc=center@basis.T+origin;extent=np.abs(basis)@(half+padding)
        sel=np.flatnonzero(np.all(hi>=wc-extent,axis=1)&np.all(lo<=wc+extent,axis=1));queries+=1
        if len(sel)and intersects_box((tri[sel]-wc)@basis,half+padding):
            owners_hit=[]
            for label in sorted(set(labels[j]for j in sel)):
                ss=[j for j in sel if labels[j]==label]
                if intersects_box((tri[ss]-wc)@basis,half+padding):owners_hit.append(label)
            # Refine only conservative full-car-box hits against complete source
            # component boxes. Each receives the same conservative interval pad.
            actual=[]
            for name,clo,chi in component_boxes:
                cc=(clo+chi)/2;hh=(chi-clo)/2+padding
                wc2=cc@basis.T+origin;extent2=np.abs(basis)@hh
                ss=sel[np.all(hi[sel]>=wc2-extent2,axis=1)&np.all(lo[sel]<=wc2+extent2,axis=1)]
                if len(ss)and intersects_box((tri[ss]-wc2)@basis,hh):
                    actual.append({'vehicle_component':name,'neighbor_owners':sorted(set(labels[j]for j in ss))})
            if actual:sweep_hits.append({'cursor_m':float(a[0]),'components':actual,'padding_xyz_m':padding.tolist()})
            if len(sweep_hits)>=12:break
    report={'status':'PASS_BOUNDED_SOURCE'if not hits and not sweep_hits else'FAIL_BOUNDED_SOURCE','checks':checks,'parts':len(parts),'pads':pads,'selected_installed_sources':sources,'group7_header_screen':screened,'four_metre_hits':hits,'old_alignment_G7_conflict':old_g7,'body_envelope':{'local_bounds':[vlo.tolist(),vhi.tolist()],'source_parts':vehicle_sources,'component_box_count':len(component_boxes),'queries':queries,'max_interval_padding_m':max_padding,'hits':sweep_hits,'scope':'Complete closed body/portal/restraint/console source component boxes and articulated bogie/wheel bounds; all CENTRAL pose intervals, conservative translation/rotation padding; only rail/web wheel-contact excluded; no runtime claim'},'source_pins':tg.PINS,'remaining':['Full selected SceneTree neighbor assertion at integration','Structural load capacity','Actual controller/gates/bridge occupancy fixture','Moving original passenger and caster/joint','Native/visual review and performance']}
    tg.raw(Path(__file__));out=HERE/'SOURCE_GATE_r004.json';require(not out.exists(),'immutable receipt output');out.write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'NEIGHBORS.json').write_text(json.dumps({'scope':'Bounded selected installed source fixture; not whole SceneTree','sources':sources},indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':checks,'pads':len(pads),'old_G7_hit_meshes':len(old_g7),'four_metre_hits':len(hits),'body':report['body_envelope']}))

if __name__=='__main__':main()
