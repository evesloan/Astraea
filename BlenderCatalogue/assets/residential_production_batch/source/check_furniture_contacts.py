"""Read-only evaluated source AABB overlap screen for separate furniture pieces."""
from pathlib import Path
import bpy,json,hashlib,os
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];rev=os.environ.get('ASTRAEA_PRODUCTION_REVISION','production_r004');rows=[]
for source in sorted((ROOT/'outputs'/rev).glob('*/assembly.blend')):
    before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get();groups={}
    for ob in bpy.context.scene.objects:
        key=ob.get('assembly_member','')
        if ob.type!='MESH' or not key or not any(key.startswith(p)for p in ['HistoricalBedAnchor','FamilyGatheringBench','SalonBench','SalonChair','SharedTable','WritingChair']):continue
        ev=ob.evaluated_get(deps);mesh=ev.to_mesh();groups.setdefault(key,[]).extend(tuple(ob.matrix_world@v.co)for v in mesh.vertices);ev.to_mesh_clear()
    bounds={k:([min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)])for k,pts in groups.items()};overlaps=[]
    keys=list(bounds)
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            alo,ahi=bounds[a];blo,bhi=bounds[b];overlap=[min(ahi[k],bhi[k])-max(alo[k],blo[k])for k in range(3)]
            if all(v>.002 for v in overlap):overlaps.append({'a':a,'b':b,'aabb_overlap_xyz':overlap})
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    rows.append({'prototype':source.parent.name,'furniture_groups':len(bounds),'pairwise_aabb_overlaps':overlaps,'source_sha256':before})
report={'status':'PASS_NO_SEPARATE_FURNITURE_AABB_OVERLAP' if all(not r['pairwise_aabb_overlaps']for r in rows)else 'FAIL_FURNITURE_OVERLAP_SCREEN','revision':rev,'prototypes':rows,
 'scope':'Conservative evaluated source bounding-box screen of independent beds, seats and tables. Not Game collision, door sweep, character/cart clearance or supported-body acceptance.'}
(ROOT/'qa/FURNITURE_CONTACT_SCREEN.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['status'].startswith('PASS')
