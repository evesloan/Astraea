"""Independent actual-GLB continuous cabinet sweep by interval AABB separation.
No controller or physical interaction acceptance. Uses geometry, not author sweep.
"""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch03'
sys.path.insert(0,str(ROOT/'qa/batch02'))
from geometry_checks import GLB,triangles,triangles_intersect_box
PATH=ROOT/'assets/staff_workbay/AST-STF-007_supply_work_cabinet.glb'
MAN=json.loads(PATH.with_suffix('.manifest.json').read_text())
PIV=np.array(MAN['door']['pivot_blender_m']);START=0.;END=np.deg2rad(MAN['door']['open_degrees'])

def components():
 out=[]
 for row in triangles(PATH):
  t=row['triangles'];v,idx=np.unique(np.round(t.reshape(-1,3),7),axis=0,return_inverse=True);f=idx.reshape(-1,3)
  a=np.concatenate([f[:,0],f[:,1],f[:,2]]);b=np.concatenate([f[:,1],f[:,2],f[:,0]])
  _,label=connected_components(coo_matrix((np.ones(len(a)),(a,b)),shape=(len(v),len(v))),directed=False)
  for lab in np.unique(label):
   tr=t[label[f[:,0]]==lab];p=tr.reshape(-1,3);lo=p.min(0);hi=p.max(0)
   names=[x['name'] for x in MAN['parts'] if np.max(np.abs(np.array(x['bounds_min_m'])-lo))<3e-7 and np.max(np.abs(np.array(x['bounds_max_m'])-hi))<3e-7]
   out.append({'node':row['node'],'role':row['role'],'triangles':tr,'points':np.unique(p,axis=0),'min':lo,'max':hi,'name':'+'.join(names) or row['node']+'_component_'+str(lab),'moving':'door_' in row['node']})
 return out

# Exact extrema of each point's sinusoid over closed angle interval. Triangle
# interiors are convex combinations of vertices for every time, so vertex bounds
# conservatively enclose all triangle surfaces for the entire interval.
def sweep_bounds(points,a,b):
 p=points-PIV;loang,hiang=min(a,b),max(a,b)
 coord=[]
 for axis in [0,1]:
  A,B=(p[:,0],-p[:,1]) if axis==0 else (p[:,1],p[:,0])
  va=A*np.cos(a)+B*np.sin(a);vb=A*np.cos(b)+B*np.sin(b);mn=np.minimum(va,vb);mx=np.maximum(va,vb)
  phase=np.arctan2(B,A)
  for k in [-2,-1,0,1,2]:
   ang=phase+k*np.pi;valid=(ang>=loang)&(ang<=hiang);v=A*np.cos(ang)+B*np.sin(ang)
   mn=np.where(valid,np.minimum(mn,v),mn);mx=np.where(valid,np.maximum(mx,v),mx)
  coord.append((mn.min()+PIV[axis],mx.max()+PIV[axis]))
 return np.array([coord[0][0],coord[1][0],points[:,2].min()]),np.array([coord[0][1],coord[1][1],points[:,2].max()])

def main():
 start_hash=hashlib.sha256(PATH.read_bytes()).hexdigest()
 comps=components();moving=[c for c in comps if c['moving']];static=[c for c in comps if not c['moving']]
 assert moving and static and all(len(c['triangles'])>0 for c in comps), 'Empty exported geometry'
 raw=GLB(PATH);nodes=raw.doc['nodes'];pivot_index=next(i for i,n in enumerate(nodes) if n.get('name')=='AST-STF-007_door_hinge_pivot')
 pivot_node=nodes[pivot_index];gp=np.array(pivot_node['translation']);actual_pivot=np.array([gp[0],-gp[2],gp[1]])
 assert np.max(np.abs(actual_pivot-PIV))<1e-7,'Exported pivot differs from measured sweep pivot'
 child_names=[nodes[i]['name'] for i in pivot_node['children']]
 assert set(child_names)==set(c['node'] for c in moving),'Moving geometry is not exactly pivot descendants'
 assert not any(c['node'] in child_names for c in static),'Static cabinet is incorrectly parented'
 moving_rows=[{'node':c['node'],'role':c['role'],'triangles':c['triangles']} for c in moving]
 controls=[]
 for name,lo,hi in [('leaf_face',[-.51,-.32,.39],[-.49,-.28,.41]),('handle_grip',[-.16,-.37,.50],[-.12,-.33,.524])]:
  hits=triangles_intersect_box(moving_rows,lo,hi)
  assert hits,'Deliberately intersecting control did not detect '+name
  controls.append({'name':name,'box_min_m':lo,'box_max_m':hi,'intersections':hits,'passes':bool(hits)})
 angles=np.linspace(START,END,421);candidates=[];checks=0
 for c in moving:
  for i,(a,b) in enumerate(zip(angles,angles[1:])):
   lo,hi=sweep_bounds(c['points'],a,b)
   for s in static:
    checks+=1
    overlap=np.minimum(hi,s['max'])-np.maximum(lo,s['min'])
    if (overlap>1e-8).all():candidates.append((c,s,i,float(np.rad2deg(a)),float(np.rad2deg(b))))
 pairs={}
 for c,s,i,a,b in candidates:pairs.setdefault((c['name'],s['name']),[]).append(i)
 radial_proofs=[]
 byname={c['name']:c for c in comps}
 for names,intervals in pairs.items():
  c,s=[byname[n] for n in names]
  # Radial separation around the real Z hinge is invariant under rotation.
  # Min distance of every projected triangle to axis, including edge interiors.
  tri=c['triangles'][:,:,:2]-PIV[:2];mn=float('inf')
  for t in tri:
   a,b,d=t
   cross=lambda x,y:x[0]*y[1]-x[1]*y[0]
   area=cross(b-a,d-a)
   if abs(area)>1e-16:
    u=cross(-a,d-a)/area;v=cross(b-a,-a)/area
    if u>=0 and v>=0 and u+v<=1:mn=0;break
   for x,y in zip(t,np.roll(t,-1,axis=0)):
    delta=y-x;den=delta@delta;u=np.clip(-(x@delta)/den,0,1) if den>1e-24 else 0
    mn=min(mn,float(np.linalg.norm(x+u*delta)))
  mx=float(np.linalg.norm(s['points'][:,:2]-PIV[:2],axis=1).max())
  radial_proofs.append({'moving':names[0],'static':names[1],'moving_triangle_minimum_radius_m':mn,'static_maximum_radius_m':mx,'continuous_radial_separation_m':mn-mx,'passes':mn>mx+1e-7,'intervals_resolved':len(intervals)})
 whole_min=np.min([sweep_bounds(c['points'],START,END)[0] for c in moving],axis=0);whole_max=np.max([sweep_bounds(c['points'],START,END)[1] for c in moving],axis=0)
 summary={'export_sha256':hashlib.sha256(PATH.read_bytes()).hexdigest(),'pivot_blender_m':PIV.tolist(),'opening_degrees':[0,float(np.rad2deg(END))],'moving_connected_components':len(moving),'static_connected_components':len(static),'interval_count':420,'interval_degrees':.25,'interval_aabb_pair_checks':checks,'floor_minimum_z_m':float(whole_min[2]),'continuous_swept_bounds_m':{'min':whole_min.tolist(),'max':whole_max.tolist()},'unresolved_aabb_pairs':[{'moving':k[0],'static':k[1],'intervals':len(v),'first_interval':v[0],'last_interval':v[-1]} for k,v in pairs.items()],'components':[{'name':c['name'],'node':c['node'],'moving':c['moving'],'min_m':c['min'].tolist(),'max_m':c['max'].tolist(),'triangles':len(c['triangles'])} for c in comps],'scope':'Exact sinusoidal vertex extrema bound all triangles continuously per interval; disjoint AABBs prove separation. Overlapping pairs need further geometric proof. This is a visual component sweep, not engine collision/controller/actor acceptance.'}
 summary['export_stable_during_check']=start_hash==summary['export_sha256']
 summary['positive_intersection_controls']=controls
 summary['moving_triangle_count']=sum(len(c['triangles']) for c in moving)
 summary['static_triangle_count']=sum(len(c['triangles']) for c in static)
 summary['glb_pivot_and_hierarchy']={'actual_pivot_blender_m':actual_pivot.tolist(),'pivot_descendants':child_names,'matches_declared_pivot':True,'moving_and_static_separate':True,'source':'Actual glTF node matrices applied to accessor positions before sweep'}
 summary['radial_proofs']=radial_proofs
 summary['continuous_sweep_passes']=all(r['passes'] for r in radial_proofs) and summary['floor_minimum_z_m']>0 and summary['export_stable_during_check']
 summary['unresolved_aabb_pairs']=[p for p,r in zip(summary['unresolved_aabb_pairs'],radial_proofs) if not r['passes']]
 (OUT/'independent_cabinet_sweep.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k!='components'},indent=2))
if __name__=='__main__':main()
