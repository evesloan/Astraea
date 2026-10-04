"""Extract actual original INLET triangles, without regenerating their surface."""
import json,copy,hashlib
from pathlib import Path
import numpy as np
from glb_tools import read,accessor,primitives,worlds,Writer
BASE=Path(__file__).resolve().parents[1];source=BASE.parent/'exports/AST-ENG-004.glb';d,b=read(source);w=Writer(d,b);rows=[];count=0
for ni,p,v,ix,world,m in primitives(d,b):
 mask=np.all((world[ix,:,][...,0]>=-1e-7)&(world[ix,:,][...,0]<=.0950001),axis=1);mask &= ~np.all(np.abs(world[ix,:,][...,0]-.085)<1e-7,axis=1);subset=ix[mask]
 if not len(subset):continue
 used=np.unique(subset);remap=np.full(len(v),-1);remap[used]=np.arange(len(used));attrs={}
 for name,a in p['attributes'].items():attrs[name]=w.attr(accessor(d,b,a)[used],d['accessors'][a]['type'])
 prim={'attributes':attrs,'indices':w.attr(remap[subset].reshape(-1,1),'SCALAR',5125),'material':p['material']};mi=len(w.d['meshes']);w.d['meshes'].append({'name':'IMMUTABLE_NEAR_INLET_'+str(mi),'primitives':[prim]});node={'name':'IMMUTABLE_NEAR_INLET_'+str(mi),'mesh':mi,'matrix':m.T.reshape(-1).tolist(),'extras':{'comparison_source':str(source.relative_to(BASE.parents[2])),'original_node':d['nodes'][ni]['name'],'original_triangle_count':len(subset)}};w.d['scenes'][0]['nodes'].append(len(w.d['nodes']));w.d['nodes'].append(node);count+=len(subset)
 rows.append({'original_node':d['nodes'][ni]['name'],'triangles':len(subset),'world_triangle_position_sha256':hashlib.sha256(world[subset].astype('<f8').tobytes()).hexdigest()})
for i,n in enumerate(d['nodes']):
 if n.get('name')=='PORT_INLET':
  n=copy.deepcopy(n);n.pop('children',None);n.pop('translation',None);n.pop('rotation',None);n.pop('scale',None);n['matrix']=worlds(d)[i].T.reshape(-1).tolist();w.d['scenes'][0]['nodes'].append(len(w.d['nodes']));w.d['nodes'].append(n)
out=BASE/'exports/utility_flange_near_comparison.glb';w.write(out)
newd,newb=read(out);hashes=[hashlib.sha256(world[ix].astype('<f8').tobytes()).hexdigest()for _,p,v,ix,world,m in primitives(newd,newb)]
assert hashes==[r['world_triangle_position_sha256']for r in rows]
report={'source':str(source.relative_to(BASE.parents[2])),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'derivative_comparison':str(out.relative_to(BASE)),'comparison_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'criterion':'Triangles whose actual resolved GLB vertices all lie at source/native X in [0,.095] m; excludes shell spanning X .085..715, including its .085 planar annular cap and all outlet/identifier geometry','source_triangle_count':count,'actual_original_triangle_positions_exactly_preserved':True,'all_original_accessors_used_without_geometry_regeneration':True,'rows':rows}
(BASE/'qa/near_extraction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
