"""Independent stdlib proof. Never imports builder; independently derives prism geometry.
Without --reopened: pure proposal screen only. With --reopened: check actual reopened
Blender vertices/winding/margin/metadata, then issue SOURCE_REOPEN_QA. No engines here.
"""
from pathlib import Path
import argparse,json,hashlib,math,collections
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sub=lambda a,b:[x-y for x,y in zip(a,b)]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def near(a,b,tol):return max(abs(x-y)for x,y in zip(a,b))<=tol
def manifold(vertices,faces):
    assert len(vertices)==8 and len(faces)==12 and len({tuple(v)for v in vertices})==8
    center=[sum(v[i]for v in vertices)/8 for i in range(3)];edges=collections.Counter();volume=0
    for f in faces:
        assert len(f)==3 and len(set(f))==3 and all(isinstance(i,int)and 0<=i<8 for i in f)
        a,b,c=[vertices[i]for i in f];n=cross(sub(b,a),sub(c,a));assert dot(n,sub(a,center))>1e-8,'Inward/degenerate face'
        assert all(dot(n,sub(p,a))<=1e-4 for p in vertices),'Nonconvex face'
        volume+=dot(a,cross(b,c))/6
        for x,y in zip(f,f[1:]+f[:1]):edges[(x,y)]+=1
    assert len(edges)==36 and all(n==1 and edges[(b,a)]==1 for (a,b),n in edges.items()),'Open/nonmanifold winding'
    assert volume>0
    return volume

def clipped_area(poly,rect):
    for axis,bound,sign in [(0,rect[0],1),(0,rect[2],-1),(1,rect[1],1),(1,rect[3],-1)]:
        q=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            da=sign*(a[axis]-bound);db=sign*(b[axis]-bound)
            if da>=0:q.append(a)
            if (da>=0)!=(db>=0):q.append([a[i]+(b[i]-a[i])*da/(da-db)for i in range(2)])
        poly=q
        if len(poly)<3:return 0
    return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1])))/2

def coverage(obj,y,rect):
    area=0
    for f in obj['faces']:
        pts=[obj['vertices_world'][i]for i in f]
        if all(abs(p[1]-y)<1e-7 for p in pts):area+=clipped_area([[p[0],p[2]]for p in pts],rect)
    return area

def verify(reopened=None):
    proposal=json.loads((R/'WALK_RAMP_PROPOSAL.json').read_text());stairs=json.loads((R/'stair_source_contract.json').read_text())
    assert sha(R/'WALK_RAMP_PROPOSAL.json')=='1057f62b7c2b9762c377a245e92c62f479eac22e826c923dfc7de512e3d4ce57'
    assert sha(R/'stair_source_contract.json')==proposal['input_sha256']['source_stair_contract']
    pins=json.loads((R/'SOURCE_PINS.json').read_text())
    for path,pin in pins.items():assert sha(path)==pin,path
    gp=next(Path(p)for p in pins if p.endswith('SOURCE_GEOMETRY_003.json'));objects={o['name']:o for o in json.loads(gp.read_text())['objects']}
    runtime=json.loads((R.parent/'game/data/architecture/THEATER_STAIR_WALK_CONTACTS_011.json').read_text());assert runtime['contacts']==proposal['rows']
    rows={r['id']:r for r in proposal['rows']};assert len(rows)==len(stairs['flights'])==8
    actual=None
    if reopened:
        e=json.loads(reopened.read_text());assert e['status']=='REOPENED_ACTUAL_MESH_EXPORT_QA_PENDING';actual={o['id']:o for o in e['objects']};assert set(actual)==set(rows)
    evidence=[];count=0;max_error=0
    for f in stairs['flights']:
        r=rows[f['id']+'_WALK_CONTACT'];assert r['source_flight']==f
        sign=1 if f['end_z']>f['start_z']else -1;x0,x1=f['clear_x'];z0=f['start_z']-sign*f['tread'];z1=f['end_z'];y0,y1=f['bottom_y'],f['top_y']
        top=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z1],[x0,y1,z1]];expected=top+[[x,y-.04,z]for x,y,z in top]
        assert r['vertices_world']==expected and r['top_quad_world']==top
        assert abs(x1-x0-3.2)<1e-8 and abs(f['tread']-.32)<1e-8 and r['shape_margin_m']==.001 and r['thickness_m']==.04
        volume=manifold(expected,r['faces']);assert abs(volume-(x1-x0)*abs(z1-z0)*.04)<1e-7
        lower=[x0,min(z0,f['start_z']),x1,max(z0,f['start_z'])]
        lower_area=sum(coverage(objects[n],y0,lower)for n in r['lower_landing_receivers']);assert abs(lower_area-1.024)<1e-7,'Lower extension must be covered by actual retained top faces'
        uz=z1+sign*.001;upper=[x0,min(z1,uz),x1,max(z1,uz)]
        upper_area=sum(coverage(objects[n],y1,upper)for n in r['upper_landing_receivers']);assert abs(upper_area-.0032)<1e-7,'Upper seam must abut actual landing top faces'
        def h(z):return y0+(z-z0)*(y1-y0)/(z1-z0)
        tread_evidence=[]
        for n,o in objects.items():
            if not n.startswith(f['id']+'_tread_'):continue
            v=o['vertices_world'];lo=[min(p[i]for p in v)for i in range(3)];hi=[max(p[i]for p in v)for i in range(3)]
            assert abs(lo[0]-x0)<1e-7 and abs(hi[0]-x1)<1e-7
            gaps=[h(z)-hi[1]for z in [lo[2],hi[2]]];assert min(gaps)>=-1e-7 and max(gaps)<=f['riser']+1e-7
            embed=.04/((y1-y0)/abs(z1-z0));assert 0<embed<f['tread']
            tread_evidence.append({'owner':n,'max_contact_above_tread_m':max(gaps),'positive_contact_strip_run_m':embed});count+=1
        assert len(tread_evidence)==f['risers']-1
        if actual:
            a=actual[r['id']];assert a['hide_render'] and a['faces']==r['faces'];props=a['properties']
            assert props['catalogue_family']=='AST-CUL-005' and props['source_flight_id']==f['id'] and props['proposal_sha256']==sha(R/'WALK_RAMP_PROPOSAL.json')
            assert props['walking_contact_approximation'] and props['collision_only'] and props['original_meshes_and_contacts_retained'] and not props['compiler_floor_credit'] and not props['load_certification']
            assert props['collision_margin_m']==.001 and props['vertical_thickness_m']==.04
            assert json.loads(props['source_lower_receiver_ids'])==r['lower_landing_receivers'] and json.loads(props['source_upper_receiver_ids'])==r['upper_landing_receivers']
            assert len(a['vertices_world'])==8
            for av,ev in zip(a['vertices_world'],expected):
                err=max(abs(x-y)for x,y in zip(av,ev));max_error=max(max_error,err);assert near(av,ev,.00002),'Actual reopened mesh drift exceeds 20 micrometres'
            manifold(a['vertices_world'],a['faces'])
        evidence.append({'id':r['id'],'bounds_xz':[x0,min(z0,z1),x1,max(z0,z1)],'lower_source_overlap_m2':lower_area,'upper_1mm_seam_strip_m2':upper_area,'volume_m3':volume,'treads':tread_evidence})
    assert count==90
    result={'status':'PASS_REOPENED_SOURCE_CONTACTS'if actual else'PASS_PURE_PROPOSAL_ONLY_REOPEN_PENDING','original_source_hashes_unchanged':True,'contacts':8,'literal_treads_preserved':count,'width_m':3.2,'vertical_thickness_m':.04,'margin_m':.001,'lower_landing_total_overlap_m2':8*1.024,'max_reopened_vertex_error_m':max_error if actual else None,'reopened_test_run':bool(actual),'load_certification':False,'evidence':evidence,'input_sha256':{'proposal':sha(R/'WALK_RAMP_PROPOSAL.json'),'stair_contract':sha(R/'stair_source_contract.json'),'source_geometry':sha(gp),'runtime_contract':sha(R.parent/'game/data/architecture/THEATER_STAIR_WALK_CONTACTS_011.json'),'verifier':sha(__file__)}}
    if actual:result.update({'blend_sha256':e['blend_sha256'],'reopened_export_sha256':sha(reopened),'reopen_exporter_sha256':e['reopen_exporter_sha256']})
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reopened',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert a.output.resolve().is_relative_to(Path('/workspace/scratch/375c2e438292')) and not a.output.exists()
    d=verify(a.reopened);a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'])
