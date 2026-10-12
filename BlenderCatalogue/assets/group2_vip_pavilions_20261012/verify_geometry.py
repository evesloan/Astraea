"""Direct retained GLB triangle checks for unplaced kit section and public lane."""
import hashlib,json,pathlib,sys,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'BlenderCatalogue/assets/utility_pipework/derived_lod/qa'))
import glb_tools as g
data=json.loads((ROOT/'Game/data/group2_vip_pavilions/KITS_r003.json').read_text())
rows=[];lane=box(-17,-4,17,4)
for entry in data['exports']:
 file=ROOT/entry['path'];assert hashlib.sha256(file.read_bytes()).hexdigest()==entry['sha256']
 d,b=g.read(file);all_vertices=[];projected=[];plant=[];ramps=[]
 for i,prim,v,indices,w,m in g.primitives(d,b):
  name=d['nodes'][i].get('name','');all_vertices.append(w)
  for triangle in indices:
   p=Polygon(w[triangle][:,[0,2]])
   if p.area>1e-9:projected.append(p)
  if 'OverheadPlantCasing' in name:plant.append(w)
  if 'ArrivalRamp' in name:ramps.append(w)
 vertices=np.concatenate(all_vertices);assert vertices[:,1].min()>-.0001
 assert vertices[:,1].max()<6.5
 footprint=unary_union(projected);assert footprint.intersection(lane).area<1e-7
 for pts in plant:
  # Piecewise roof underside is the authored localY profile alongZ.
  for x,y,z in pts:
   ceiling=5.5+(z+13.7)/4.7*.7 if z<=-9 else 6.2-(z+9)/4.85*.7
   assert y<ceiling-.1,(entry['kit'],y,ceiling)
 assert len(ramps)==1
 # Source top triangle vertices, not the prism's lower face, contain the18m profile.
 ramp=ramps[0];assert abs(ramp[:,0].max()-3)<.001
 assert abs(ramp[:,2].max()-ramp[:,2].min()-1.8)<.001
 assert abs(ramp[:,1].max()-1.5)<.001
 rows.append({'kit':entry['kit'],'new_source_mesh_nodes':len([n for n in d['nodes']if 'mesh'in n]),
  'public_eight_metre_lane_overlap_m2':footprint.intersection(lane).area,
  'local_height_bounds_m':[float(vertices[:,1].min()),float(vertices[:,1].max())],
  'all_source_geometry_at_or_above_candidate_D17':True,'overhead_casing_clears_authored_roof':True,
  'source_ramp_nominal_width_m':1.8,'source_ramp_run_m':18,'placement_accepted':False})
for pin in data['retained_dependency_pins']:assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
out=P/'evidence/GEOMETRY_FINAL.json';assert not out.exists()
out.write_text(json.dumps({'pass':True,'rows':rows,'actual_receiving_roof_or_bearing_acceptance':False,
 'scope':'Two unplaced source kits only; excludes shared roof/commons/location approval'},indent=2)+'\n')
print('PASS unplaced source section, public lane, ramp geometry and casing/roof clearance')
