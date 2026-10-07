"""Actual-GLB finite perimeter ray screen, with the unsealed source as control."""
from pathlib import Path
import json, runpy, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BATCH=ROOT.parent
decode=runpy.run_path(str(BATCH/'qa/independent_review/geometry_decode.py'))['decode']
points=[];labels=[]
def add(xs,ys,label):
    for x in xs:
        for y in ys:points.append((x,y,-12.78));labels.append(label)
add(np.arange(-3.49,3.491,.01),[.470,.475,.480,.4825,.485,.4875,.49,.495,.500],'sill')
add(np.arange(-3.49,3.491,.01),[3.570,3.580,3.585,3.590,3.5925,3.595,3.5975,3.60,3.605,3.61],'header')
add([-.070,-.065,-.060,-.055,-.050,-.045,0,.045,.050,.055,.060,.065,.070],np.arange(.49,3.591,.01),'central_mullion')
for sign in [-1,1]:add(sign*np.array([3.37,3.38,3.39,3.40,3.405,3.41,3.42,3.44,3.46,3.48,3.50]),np.arange(.49,3.591,.01),'outer_jamb')
P=np.array(points);labels=np.array(labels);directions=[(0,0,1),(4,0,1),(-4,0,1),(10,0,1),(-10,0,1),(0,1.5,1),(0,-1.5,1)]
def coverage(tri,d):
    # Only the actual source triangles whose depth bounds can touch the window
    # segment. Glass counts as opaque exterior geometry for this shape screen.
    tri=tri[(tri[:,:,2].min(1)<-12.70)&(tri[:,:,2].max(1)>-12.91)]
    d=np.array(d,dtype=float);ray=d*.49;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
    h=np.cross(np.broadcast_to(ray,e2.shape),e2);det=np.sum(e1*h,1);ok=np.abs(det)>1e-12;inv=np.where(ok,1/np.where(ok,det,1),0)
    hit=[]
    for i in range(0,len(P),300):
        start=P[i:i+300]-d*.41;s=start[:,None,:]-tri[None,:,0];u=np.sum(s*h,2)*inv
        q=np.cross(s,e1);v=np.sum(ray*q,2)*inv;t=np.sum(e2*q,2)*inv
        hit.extend(np.any(ok&(u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)&(t>=0)&(t<=1),axis=1))
    return np.array(hit)
rows=[];done={}
for revision in ['court_domestic_r009','court_domestic_r010']:
    for path in sorted((BATCH/'outputs'/revision).glob('*/shell.glb')):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in done:
            _,tri,_,_=decode(path);tests=[]
            for direction in directions:
                hit=coverage(tri,direction);tests.append({'direction_toward_room':direction,'tested_points':len(P),'unblocked':int((~hit).sum()),'unblocked_by_joint':{str(label):int(((labels==label)&~hit).sum())for label in np.unique(labels)},'first_unblocked_points':P[~hit][:5].tolist()})
            done[digest]=tests
        rows.append({'revision':revision,'unit':path.parent.name,'shell_sha256':digest,'tests':done[digest]})
old=[r for r in rows if r['revision'].endswith('r009')];new=[r for r in rows if r['revision'].endswith('r010')]
assert all(any(t['unblocked']>0 for t in r['tests'])for r in old),'Unsealed-source positive control missing'
assert all(t['unblocked']==0 for r in new for t in r['tests']),'Corrected source still has a perimeter gap'
report={'status':'PASS_FULL_SOURCE_PERIMETER_SCREEN','points_per_direction':len(P),'directions':len(directions),'unique_shell_hashes_tested':len(done),'old_horizontal_seams_detected':True,'corrected_perimeter_rays_unblocked':0,'rows':rows,'scope':'Actual GLB double-sided opaque geometric coverage of sill, header, both outer jambs and center mullion at normal, steep horizontal and vertical-oblique directions. Includes unsealed r009 source positive control. Does not replace native shader/pixel checks.'}
(ROOT/'qa/R010_FULL_PERIMETER_GLB_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],len(P)*len(directions),'rays per shell')
