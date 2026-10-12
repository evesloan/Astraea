"""Replace whole-mesh bounds guesses with actual clipped original source faces.

The original0.8m reservation remains explicit. Nominal-node neighbour screens
and exact variable-hull containment are different results, not interchangeable
pressure, capacity or source-owner acceptance.
"""
from pathlib import Path
import json,sys,hashlib,itertools,re,collections
import numpy as np
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
sys.path.insert(0,str(C.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read,acc,nodes
inputs=json.loads((P/'docs/WIDTH_RECONCILIATION_INPUT.json').read_text())
old=json.loads((C/'continuation_r005/qa/ACTUAL_OCCLUDERS.json').read_text())
new=json.loads((P/'qa/ACTUAL_OCCLUDERS.json').read_text())
assert old['status']==new['status']=='PASS'
wanted={s for q in inputs['original_width_hold_samples']for s in q['actual_witness_candidates']}
models={};actual={};pins={};correlation=[]
for survey,folder in [(old,C/'continuation_r005'),(new,P)]:
    for row in survey['meshes']:
        if row['path']not in wanted:continue
        file=folder/'qa/occluders'/row['filename'];tri=np.fromfile(file,dtype='<f4').astype(float).reshape(-1,3,3)
        assert len(tri)==row['triangles'] and np.isfinite(tri).all()
        actual[row['path']]=tri
        resource=row['mesh_resource_path'].split('::')[0]
        if resource not in models:
            source=R/'Game'/resource.removeprefix('res://');pins[source.relative_to(R).as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
            d,b=read(source);table={}
            for node,m in nodes(d):
                triangles=[]
                for prim in d['meshes'][node['mesh']]['primitives']:
                    a=acc(d,b,prim['attributes']['POSITION']);a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3];idx=acc(d,b,prim['indices']).ravel();triangles.append(a[idx].reshape(-1,3,3))
                table[re.sub(r'[.:@/"%]','_',node['name'])]=np.concatenate(triangles)
            models[resource]=table
        source=models[resource][row['path'].split('/')[-1]];assert len(source)==len(tri)
        vertices=np.unique(source.reshape(-1,3),axis=0);tol=float(np.max(np.ptp(vertices,axis=0))/65535+.0002);buckets=collections.defaultdict(list)
        for q in vertices:buckets[tuple(np.floor(q/tol).astype(int))].append(q)
        worst=0.
        for q in np.unique(tri.reshape(-1,3),axis=0):
            k=np.floor(q/tol).astype(int);near=[p for off in itertools.product([-1,0,1],repeat=3)for p in buckets.get(tuple(k+off),[])];assert near,row['path'];error=float(np.min(np.max(np.abs(np.array(near)-q),axis=1)));assert error<=tol,(row['path'],error,tol);worst=max(worst,error)
        correlation.append({'path':row['path'],'triangles':len(tri),'actual_capture_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'original_glb_correlated_with_measured_import_quantization':True,'actual_max_error_m':worst,'mesh_scale_quantization_allowance_m':tol})
assert wanted==actual.keys(),(len(wanted),len(actual))
floors=[]
for name in ['structural_meshes.json','received_structural_meshes.json']:
    file=R/'Game/data/generated'/name;pins[file.relative_to(R).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest();floors+=json.loads(file.read_text())['regions']
hfile=R/'Game/data/hull_envelope.json';pins[hfile.relative_to(R).as_posix()]=hashlib.sha256(hfile.read_bytes()).hexdigest();hull=Polygon(json.loads(hfile.read_text())['plan_xz_m'])
def clip(poly,axis,bound,greater):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=a[axis]>=bound-1e-9 if greater else a[axis]<=bound+1e-9
        inb=b[axis]>=bound-1e-9 if greater else b[axis]<=bound+1e-9
        if ina:out.append(a)
        if ina!=inb:
            t=(bound-a[axis])/(b[axis]-a[axis]);out.append(a+(b-a)*t)
    return out
results=[]
for sample in inputs['original_width_hold_samples']:
    ya,yb=sample['screen_y'];za,zb=sample['screen_z'];side=sample['side'];need=0.;outside=[];contributors=[];clipped_faces=0
    for path in sample['actual_witness_candidates']:
        tri=actual[path];lo=tri.min(1);hi=tri.max(1);mask=(hi[:,1]>=ya)&(lo[:,1]<=yb)&(hi[:,2]>=za)&(lo[:,2]<=zb);extent=0.;bad=0
        for face in tri[mask]:
            poly=list(face)
            for axis,bound,greater in [(1,ya,True),(1,yb,False),(2,za,True),(2,zb,False)]:
                if not poly:break
                poly=clip(poly,axis,bound,greater)
            if not poly:continue
            a=np.array(poly);extent=max(extent,float(np.max(a[:,0]*side)));clipped_faces+=1
            projection=MultiPoint(a[:,[0,2]]).convex_hull
            #5mm is a declared old-import positional measurement allowance,
            # never a replacement for the original0.8m construction reserve.
            if not hull.buffer(.005).covers(projection):bad+=1
        if extent>0:contributors.append({'source':path,'actual_local_outboard_extent':extent,'faces_outside_calibrated_plan_with_5mm_measurement_allowance':bad})
        need=max(need,extent)
        if bad:outside.append(path)
    slab_sources=[]
    strip=box(-120,za,120,zb)
    for floor in floors:
        if not ya-.3<=floor['floor_y']<=yb+.3:continue
        projected=unary_union([Polygon(t)for t in floor['triangles']]).intersection(strip)
        if projected.is_empty:continue
        extent=projected.bounds[2]if side==1 else -projected.bounds[0];need=max(need,extent);slab_sources.append({'source_floor_id':floor['id'],'floor_y':floor['floor_y'],'local_outboard_extent':extent})
        if not hull.buffer(.0001).covers(projected):outside.append(floor['id'])
    exact_required=need+.8
    clear=exact_required<=sample['maximum_hull_halfbeam']+.005
    results.append({**sample,'actual_required_outer_x_with_original_0_8m_reserve':exact_required,'exact_clipped_source_faces':clipped_faces,'actual_local_source_contributors':contributors,'exact_original_floor_contributors':slab_sources,'nominal_node_neighbour_reserve_status':'CLEAR'if clear else'RESERVATION_HELD','actual_sources_outside_variable_calibrated_hull':outside,'owner_capacity_pressure_or_complete_body_fit_accepted':False})
out={'status':'ACTUAL_ORIGINAL_SOURCE_WIDTH_SCREENS_RECONCILED','original_samples':len(results),'actual_witness_meshes':len(wanted),'actual_captured_triangles':sum(len(x)for x in actual.values()),'clear_original_neighbour_reserve_samples':sum(q['nominal_node_neighbour_reserve_status']=='CLEAR'for q in results),'held_original_neighbour_reserve_samples':sum(q['nominal_node_neighbour_reserve_status']!='CLEAR'for q in results),'samples_with_actual_variable_hull_outside_sources':sum(bool(q['actual_sources_outside_variable_calibrated_hull'])for q in results),'original_construction_reserve_m':.8,'old_import_positional_measurement_allowance_m':.005,'source_pins':pins,'actual_source_correlation':correlation,'samples':results,'criterion_or_source_geometry_changed':False,'whole_enclosure_or_capacity_accepted':False}
(P/'docs/ACTUAL_WIDTH_RECONCILIATION.json').write_text(json.dumps(out,indent=2)+'\n');print('G7_R008_ACTUAL_WIDTH_SCREENS',out['original_samples'],out['clear_original_neighbour_reserve_samples'],'clear',out['held_original_neighbour_reserve_samples'],'reserve held',out['samples_with_actual_variable_hull_outside_sources'],'actual hull outside')
