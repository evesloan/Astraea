"""Validate actual exported r007 bathroom bytes; no analytic patch injection."""
from audit_bathroom import *
from check_sweep import triangle_box_hits
from itertools import product
import time
ROOT=OUT.parents[1]
REV=ROOT/'outputs/court_domestic_r007'


def rays():
    probes=[('front_corner_z_'+str(z),(-.78,-.2,z),(-.78,.5,z))for z in [.3,.6,1.,1.3,1.6,2.,2.3,2.55]]
    probes += [('door_head_z_'+str(z),(-.4,2.9,z),(-1.2,2.9,z))for z in [2.155,2.165,2.175]]
    enclosure=[]
    for z in [.3,.6,1.,1.3,1.6,2.,2.3,2.55]:
        for x in np.arange(-3.43,-.761,.01):enclosure.append(('front',(float(x),-.2,z),(float(x),.5,z)))
        for y in np.arange(.25,3.93,.01):
            enclosure.append(('inner',(-.4,float(y),z),(-1.2,float(y),z)))
            enclosure.append(('outer',(-3.8,float(y),z),(-3.2,float(y),z)))
        for x in np.arange(-3.43,-.77,.03):enclosure.append(('return',(float(x),4.3,z),(float(x),3.7,z)))
    for x,y in product(np.arange(-3.4,-.77,.1),np.arange(.25,3.91,.1)):enclosure.append(('ceiling',(float(x),float(y),2.90),(float(x),float(y),2.3)))
    head=[('head_chamfer_and_seam',(-.4,float(y),float(z)),(-1.2,float(y),float(z)))for y,z in product(np.arange(2.31,3.491,.005),np.arange(2.055,2.291,.005))]
    eyes=list(product([-.4,0.,.6,1.2],[.3,1.2,2.9,3.6,4.3,5.0],[.6,1.1,1.65,2.2]))+list(product([-1.2,-.78,0.],[-.6],[.6,1.1,1.65,2.2]))
    targets=list(product([-3.,-2.5,-2.,-1.2],[.5,1.1,2.,3.1,3.7],[.45,.9,1.4,1.9]))
    return {'targeted_defects':probes,'boundary':enclosure,'head_chamfers':head,'occupied_sightlines':[('eye_to_bath_occupied_volume',eye,target)for eye,target in product(eyes,targets)]}


def verify_solid(rows,name,lo,hi,role):
    expected=np.array(list(product(*zip(lo,hi))));all_tri=merge(rows)
    dist=np.linalg.norm(all_tri[:,:,:,None]-expected.T[None,None,:,:],axis=2)
    keep=np.all(dist.min(axis=2)<2e-6,axis=1)
    tri=all_tri[keep]
    result={'name':name,'expected_bounds':[lo,hi],'triangle_count':len(tri),'actual_bounds':[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],'faces':[]}
    assert len(tri)==12,(name,len(tri))
    for axis in range(3):
        area_expected=np.prod(np.delete(np.array(hi)-np.array(lo),axis))
        for side,plane in [('min',lo[axis]),('max',hi[axis])]:
            face=tri[np.all(np.abs(tri[:,:,axis]-plane)<2e-6,axis=1)]
            area=float(np.linalg.norm(np.cross(face[:,1]-face[:,0],face[:,2]-face[:,0]),axis=1).sum()/2)
            assert len(face)==2 and abs(area-area_expected)<2e-6,(name,axis,side,area)
            result['faces'].append({'axis':axis,'side':side,'triangles':len(face),'area_m2':area,'expected_area_m2':float(area_expected)})
    matching=[]
    for r in rows:
        t=r['triangles'];d=np.linalg.norm(t[:,:,:,None]-expected.T[None,None,:,:],axis=2)
        if np.any(np.all(d.min(axis=2)<2e-6,axis=1)):matching.append(r['material'])
    assert matching==[role],matching
    result['material']=matching[0];result['max_corner_error_m']=float(dist[keep].min(axis=2).max())
    return result


def component_path(c):
    if c.get('candidate_export'):return ROOT/c['candidate_export']
    p=CAT/c['catalogue_source']
    result=p.with_suffix('.glb')if p.parent.name!='source'else p.parent.parent/'exports'/p.with_suffix('.glb').name
    assert result.is_file(),result
    return result


def screen_box(tri,center,rotation,size,margin=.002):
    half=np.array(size)/2+margin;lo=center-np.abs(rotation)@half;hi=center+np.abs(rotation)@half
    candidate=tri[np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1)]
    return triangle_box_hits(candidate,center,rotation,half)


def sweeps(static,bath_closed,entry_fixed,door_nodes,bath_component,entry_component):
    bath_fixed=static # Includes both new actual exported pieces and all fixed furnishings/kitchenette.
    specs=[('LeafContact',[.525,0,1.0875],[1.026,.05,2.125]),('InnerHandleContact',[.925,.060,1.1],[.17,.035,.23]),('OuterHandleContact',[.925,-.060,1.1],[.17,.035,.23])]
    failures=[];yaw=bath_component['source_yaw'];hinge=transform(door_nodes['HINGE_LEFT'],bath_component['source_xyz'],yaw)
    for step in range(301):
        angle=step*math.pi/2/300;rotation=rz(yaw+angle)
        for label,center,size in specs:
            p=np.array(center)@rotation.T+hinge;n=screen_box(bath_fixed,p,rotation,size)
            if n:failures.append({'angle_degrees':step*.3,'collider':label,'triangles':n})
    # Additional actual-entry sweep proves the new corner block does not obstruct the original sliding pair.
    entry_static=np.concatenate([static,bath_closed]);entryfail=[]
    for step in range(301):
        f=step/300
        for side in [-1,1]:
            center=np.array([side*(.40+.84*f),0,1.26]);rot=rz(entry_component['source_yaw']);center=center@rot.T+entry_component['source_xyz']
            n=screen_box(entry_static,center,rot,[.78,.06,2.45])
            if n:entryfail.append({'fraction':f,'collider':'EntryLeaf_'+str(side),'triangles':n})
        center=np.array([-.40-.84*f+.402,-.0375,1.26]);rot=rz(entry_component['source_yaw']);center=center@rot.T+entry_component['source_xyz']
        n=screen_box(entry_static,center,rot,[.04,.015,2.45])
        if n:entryfail.append({'fraction':f,'collider':'MeetingSealContact','triangles':n})
    return {'bathroom':{'angles':301,'contact_tests':903,'box_inflation_m':.002,'intersections':failures},'suite_entry':{'travel_samples':301,'contact_tests':903,'box_inflation_m':.002,'intersections':entryfail}}

if __name__=='__main__':
    started=time.time();sources={};ref=json.loads((OUT/'REFERENCE_INSPECTION_SHA256.json').read_text())
    assert all(sha(r['path'])==r['sha256']for r in ref),'Inspected reference changed; reread before verification'
    for p,h in json.loads((OUT/'AUDITED_SOURCE_SHA256.json').read_text()).items():assert sha(p)==h,('Retained source drift',p)
    groups=rays();units=[]
    for path in sorted(REV.glob('*/shell.glb')):
        print('VERIFY',path.parent.name,flush=True)
        receiptpath=path.parent/'SOURCE_RECEIPT.json';receipt=json.loads(receiptpath.read_text());sources[str(receiptpath)]=sha(receiptpath)
        for name,h in receipt['files'].items():assert sha(path.parent/name)==h,(path.parent.name,name);sources[str(path.parent/name)]=h
        shell,marks=decode(path);shelltri=merge(shell)
        solids=[verify_solid(shell,'SUI_BathEntryCornerClosure',[-.84,.12,0],[-.70,.24,2.60],'ivory_enamel'),verify_solid(shell,'SUI_BathDoorHeadStop',[-.755,2.36,2.10],[-.735,3.44,2.25],'warm_walnut')]
        assert np.linalg.norm(marks['DATUM_bath_door']-[-.7,2.9,0])<2e-6
        assert not any('HINGE_LEFT'in r['chain']or 'BATH_Leaf'in r['name']for r in shell),'Baked privacy leaf in shell'
        fixed=[shelltri];doortri=None;bathclosed=None;entryfixed=None;bathc=None;entryc=None;door_nodes=None;components=[]
        for c in receipt['placements']:
            p=component_path(c);sources[str(p)]=sha(p);rr,mm=decode(p);t=transform(merge(rr),c['source_xyz'],c['source_yaw'])
            components.append({'label':c['label'],'path':str(p),'sha256':sources[str(p)],'source_xyz':c['source_xyz'],'source_yaw':c['source_yaw']})
            if c['label']=='BathroomDoor':
                bathc=c;door_nodes=mm;doortri=t;bathclosed=transform(merge([r for r in rr if 'HINGE_LEFT'in r['chain']]),c['source_xyz'],c['source_yaw']);fixed.append(transform(merge([r for r in rr if 'HINGE_LEFT'not in r['chain']]),c['source_xyz'],c['source_yaw']))
                assert sha(p)==sha(GAME/'assets/models/AST-DOR-001.glb');assert np.linalg.norm(np.array(c['source_xyz'])-marks['DATUM_bath_door'])<2e-6
            elif c['label']=='EntryDoor':
                entryc=c;entryfixed=transform(merge([r for r in rr if not any(n.startswith('LEAF_')for n in r['chain'])]),c['source_xyz'],c['source_yaw']);fixed.append(entryfixed)
            else:fixed.append(t)
        assert bathc and entryc
        privacy=np.concatenate([shelltri,doortri])
        # Exact-triangle broad phase only; no analytic enclosure geometry added.
        privacy=privacy[np.all(privacy.max(axis=1)>=np.array([-4,-1,-.1]),axis=1)&np.all(privacy.min(axis=1)<=np.array([1.3,5.1,3.1]),axis=1)]
        results={name:sample_rays(privacy,rr)for name,rr in groups.items()}
        sweep=sweeps(np.concatenate(fixed),bathclosed,entryfixed,door_nodes,bathc,entryc)
        result={'unit':path.parent.name,'layout':receipt['layout'],'shell_sha256':sha(path),'actual_geometry':solids,'bathroom_markers':{k:v.tolist()for k,v in marks.items()if k.startswith('DATUM_bath')},'components':components,'privacy_rays':results,'sweeps':sweep,'receipt_has_bathroom_contract':'bathroom_enclosure_contract'in receipt}
        units.append(result)
        print(json.dumps({'unit':result['unit'],'ray_failures':sum(v['unblocked']for v in results.values()),'bath_contacts':len(sweep['bathroom']['intersections']),'entry_contacts':len(sweep['suite_entry']['intersections'])}),flush=True)
    unchanged=all(sha(p)==h for p,h in sources.items());assert unchanged
    report={'status':'PASS_ACTUAL_R007_EXPORTED_ENCLOSURE_PRIVACY_AND_OFFLINE_SWEEP'if all(all(not v['unblocked']for v in u['privacy_rays'].values())and all(not v['intersections']for v in u['sweeps'].values())for u in units)else 'FAIL_ACTUAL_R007_SCREEN','revision':str(REV),'geometry_tested':'Actual shell.glb triangles plus actual retained/candidate component GLBs positioned by r007 SOURCE_RECEIPT. No analytic fix triangles were added.','units':units,'sources':sources,'source_hashes_unchanged_after':unchanged,'inspection_evidence':'REFERENCE_INSPECTION.md and REFERENCE_INSPECTION_SHA256.json; every recorded reference hash reverified unchanged','reference_hashes_unchanged':True,'engine_jobs':0,'runtime_acceptance':False,'total_closed_privacy_rays':sum(v['tested']for u in units for v in u['privacy_rays'].values()),'total_sampled_contact_tests':sum(v['contact_tests']for u in units for v in u['sweeps'].values()),'elapsed_seconds':round(time.time()-started,3),'limitations':['Finite offline ray/SAT screens; not operation or Godot physics acceptance','Reference pixels are the explicitly recorded unchanged original observations, not new r007 in-engine capture','Actual .blend assembly evaluation not performed; component GLBs are placed by receipts','Existing controller grazing-handle occupied-query edge case remains runtime test requirement','25 mm door undercut retained intentionally; no airtight, water, lock, save or species-fit claim']}
    (OUT/'R007_ACTUAL_EXPORT_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['total_closed_privacy_rays'],report['total_sampled_contact_tests'],flush=True)
