"""Independent non-Blender triangle contact and image-ray preflight.

This validates planned triangle coordinates, not evaluated saved source. The
saved-source verifier repeats these gates from Blender evaluated meshes.
"""
import json,math,hashlib,sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
def triangles(part):
    v=np.array(part['vertices'],float);return np.array([v[[f[0],f[i],f[i+1]]] for f in part['faces'] for i in range(1,len(f)-1)])
def surface(t,p):
    a=t[:,0];b=t[:,1];c=t[:,2];e=b-a;f=c-a;v=np.array(p)-a;n=np.cross(e,f);area=(n*n).sum(1);distance=np.abs((v*n).sum(1))/np.sqrt(area);ee=(e*e).sum(1);ef=(e*f).sum(1);ff=(f*f).sum(1);ve=(v*e).sum(1);vf=(v*f).sum(1);den=ee*ff-ef*ef;u=(ff*ve-ef*vf)/den;w=(ee*vf-ef*ve)/den;return bool(np.any((distance<2e-7)&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)))
def inside(t,p):
    if surface(t,p):return True
    a,b,c=(t[:,i]-p for i in range(3));la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1);num=np.sum(a*np.cross(b,c),axis=1);den=la*lb*lc+np.sum(a*b,axis=1)*lc+np.sum(b*c,axis=1)*la+np.sum(c*a,axis=1)*lb;return abs(np.sum(2*np.arctan2(num,den)))>2*math.pi
def hit(t,a,b):
    o=np.array(a);d=np.array(b)-o;e=t[:,1]-t[:,0];f=t[:,2]-t[:,0];h=np.cross(d,f);det=np.sum(e*h,axis=1);good=np.abs(det)>1e-10;inv=np.divide(1.,det,out=np.zeros_like(det),where=good);s=o-t[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e);v=inv*np.sum(d*q,axis=1);depth=inv*np.sum(f*q,axis=1);return np.any(good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(depth>1e-6)&(depth<1-1e-6))
def main():
    path=HERE/'greenery_contract.json';p=json.loads(path.read_text());alltri=[];errors=[];count=0;minimum_curve=1
    for a in p['assets']:
        parts={m['name']:m for m in a['parts']};geo={n:triangles(m) for n,m in parts.items()}
        for j in a['joints']:
            count+=1;probe=np.array(j['probe_local']);parent=geo[j['parent']];child=geo[j['child']]
            if not inside(parent,probe):errors.append(a['name']+'/'+j['child']+' parent contact')
            if not (inside(child,probe) if parts[j['child']]['surface_kind']=='closed_support' else surface(child,probe)):errors.append(a['name']+'/'+j['child']+' child contact')
        for n,m in parts.items():
            t=geo[n]
            if m['surface_kind']=='closed_support':
                vol=np.sum(t[:,0]*np.cross(t[:,1],t[:,2]))/6
                if vol<=1e-12:errors.append(a['name']+'/'+n+' nonpositive closed volume')
            else:
                v=np.array(m['vertices']);sv=np.linalg.svd(v-v.mean(axis=0),compute_uv=False);minimum_curve=min(minimum_curve,float(sv[2]/sv[0]))
                if sv[2]/sv[0]<=.009:errors.append(a['name']+'/'+n+' flat billboard')
            w=np.stack((t[:,:,0]+a['position_xyz'][0],t[:,:,2]+a['position_xyz'][1],a['position_xyz'][2]-t[:,:,1]),axis=2);alltri.extend(w)
    alltri=np.array(alltri);pins=json.loads((HERE/'INPUT_PINS.json').read_text());media=Path(next(q for q in pins['immutable_inputs'] if q.endswith('/MEDIA_FITTING_CANDIDATES.json')));media=media if media.is_absolute() else (HERE/media).resolve();probes=0
    for screen in json.loads(media.read_text())['candidates']:
        for ray in screen['sampled_current_triangle_sightlines']:
            probes+=1
            if hit(alltri,ray['eye_xyz'],ray['target_xyz']):errors.append(screen['name']+' planned foliage obstruction')
    report=dict(status='PASS_PLANNED_TRIANGLES' if not errors else 'FAIL',contract_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),physical_triangle_contact_probes=count,screen_probes=probes,minimum_leaf_nonplanarity_singular_ratio=minimum_curve,errors=errors,limitation='Not evaluated saved Blender source or rendered/runtime acceptance')
    (HERE/'PLANNED_CONTACT_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return not errors
if __name__=='__main__':sys.exit(0 if main() else 1)
