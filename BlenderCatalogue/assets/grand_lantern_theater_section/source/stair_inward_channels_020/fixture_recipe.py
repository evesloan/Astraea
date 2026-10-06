"""Pure, bounded inward stair channel recipe. No Blender/Godot execution on import."""
from pathlib import Path
import json, hashlib, math, sys
import numpy as np
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent
T = R.parent
P = Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section')
G = Path('/workspace/shared/astraea-godot-production-20261003')
SOURCE = P/'source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend'
SOURCE_SHA = 'dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
STATIC = P/'source/firstpass_003/exports_run005/AST-CUL-005_static_003.glb'
GEOMETRY = G/'data/architecture/packages/theater/SOURCE_GEOMETRY_003.json'
PROPOSAL = T/'stair_inward_lighting_plan018/INWARD_MOUNT_RECEIVER_PROPOSAL.json'
WALK_SOURCE = P/'source/stair_walking_contacts_011/AST-CUL-005_stair_walking_contacts_011.blend'
MATERIALS = {
 'champagne_metal': {'datablock':'ASTRAEA_champagne_metal','manifest':str(P.parents[1]/'materials/material_manifest.json'),'meters_per_tile_uv':[.6,.6],'texture_sha256':'0a2f8d50861d6d0ff22f50112384635c06191c2be6b1c46be151400443fa1cb4'},
 'staff_opal': {'datablock':'FP_PRACTICAL_AST-CUL-004_staff_opal','manifest':str(P.parents[1]/'materials/staff/manifest.json'),'meters_per_tile_uv':[.75,.75],'texture_sha256':'d1884536391beb3bbffbf8d5d9ecb40c678b810cf841c13b53f891594c5d086b'}
}
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write_new(path, obj):
 with Path(path).open('x') as f: json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def cross2(a,b): return a[0]*b[1]-a[1]*b[0]
def earclip(poly):
 p=np.array(poly); ids=list(range(len(poly))); out=[]
 assert sum(cross2(p[i],p[(i+1)%len(p)])for i in range(len(p)))>0
 while len(ids)>3:
  found=False
  for j in range(len(ids)):
   a,b,c=ids[j-1],ids[j],ids[(j+1)%len(ids)]
   if cross2(p[b]-p[a],p[c]-p[b])<=1e-12:continue
   def inside(i):
    return min(cross2(p[b]-p[a],p[i]-p[a]),cross2(p[c]-p[b],p[i]-p[b]),cross2(p[a]-p[c],p[i]-p[c]))>=-1e-12
   if any(inside(i) for i in ids if i not in [a,b,c]):continue
   out.append([a,b,c]);ids.pop(j);found=True;break
  assert found,('Cannot triangulate cross section',poly,ids)
 out.append(ids);return out

def triangles(row):
 vs=np.array(row['vertices_world']);return np.array([[vs[f[0]],vs[f[j]],vs[f[j+1]]]for f in row['faces']for j in range(1,len(f)-1)])
def extrude(name, polygon, a, b, role, flight, part):
 a,b=np.array(a),np.array(b); vs=[(o+[-d,h,0]).tolist()for o in [a,b]for d,h in polygon];n=len(polygon)
 fs=[]
 for tri in earclip(polygon):fs.extend([list(reversed(tri)),[i+n for i in tri]])
 for i in range(n):j=(i+1)%n;fs.append([i,j,j+n,i+n])
 row={'name':name,'vertices_world':vs,'faces':fs,'material_family':role,'flight':flight,'part':part,'catalogue_family':'AST-CUL-005','role':'source_only_fitted_inward_channel'}
 tr=triangles(row);base=tr[0,0];volume=np.einsum('ij,ij->i',tr[:,0]-base,np.cross(tr[:,1]-base,tr[:,2]-base)).sum()/6
 if volume<0:row['faces']=[list(reversed(f))for f in fs]
 return row

def make_recipe(references=None):
 proposal=read(PROPOSAL);original=read(GEOMETRY);objects={o['name']:o for o in original['objects']};objects.update(references or {})
 fixtures=[];meshes=[];references_used={}
 # A closed simple C-profile body supplies a broad rear contact face and lower lip.
 # The separate upper protective cap finishes the top edge. Lens contacts rear and lips.
 sections={
  'CHANNEL':([(0,-.020),(.016,-.020),(.016,-.0125),(.008,-.0125),(.008,.0125),(.012,.0125),(.012,.020),(0,.020)],'champagne_metal'),
  'LENS':([(.008,-.0125),(.016,-.0125),(.016,.0125),(.008,.0125)],'staff_opal'),
  'CAP':([(.012,.0125),(.016,.0125),(.016,.020),(.012,.020)],'champagne_metal')
 }
 for p in proposal['rows']:
  flight=p['id'].replace('_INWARD_PRACTICAL_PROPOSAL','');guard=objects[p['existing_guard']];v=np.array(guard['vertices_world']);a,b=sorted([v[1],v[2]],key=lambda x:x[1]);unit=(b-a)/np.linalg.norm(b-a)
  start=a+unit*.020-[0,.160,0];end=b-unit*.020-[0,.160,0]
  origin=a*.25+b*.75-[.020,.160,0];lens=origin+[.004,0,0]
  names=[]
  for part,(section,material) in sections.items():
   name='INWARD_'+flight+'_'+part;meshes.append(extrude(name,section,start,end,material,flight,part));names.append(name)
  treadrows=sorted([o for o in objects.values()if o['name'].startswith(flight+'_tread_')],key=lambda o:o['name']);assert len(treadrows)==len(p['samples'])
  samples=[];corners=[]
  for o in treadrows:
   top=np.array(o['vertices_world'][:4]);target=top.mean(0)+[0,.05,0];samples.append({'tread':o['name'],'receiver_world':target.tolist()});corners.extend(top);references_used[o['name']]=o
  references_used[guard['name']]=guard
  fixtures.append({'flight':flight,'guard':guard['name'],'guard_reference_digest':digest(guard),'mesh_names':names,'attachment_empty':'INWARD_'+flight+'_SOURCE','attachment_world':origin.tolist(),'actual_lens_exit_world':lens.tolist(),'optical_exit_normal_world':[-1,0,0],'optical_source_offset_m':.004,'range_m_geometric_only':p['range_m_from_full_tread_corners_plus_035m'],'source_fraction_from_lower_guard_end':.75,'source_energy_unset':True,'runtime_light_created':False,'channel_end_inset_m':.020,'mount_plane_x':float(a[0]),'channel_centerline_endpoints':[start.tolist(),end.tolist()],'samples':samples})
 return {'schema':1,'status':'SOURCE_ONLY_ADDITIVE_RECIPE','coordinate_system':'world X/Y-up/Z; Blender X/-Z/Y conversion','scope':'Eight guard-fitted simple inward light channels, exactly three closed meshes per flight. Original outward strips, guards, treads, walking contacts and full sources retained unchanged. No runtime light or engine edits.','objects':meshes,'fixtures':fixtures,'actual_source_references':references_used,'materials':MATERIALS,'expected_meshes':24,'expected_attachment_empties':8,'expected_treads':90,'native_illumination_proven':False,'bounds_limits':{'new_depth_inward_m':.016,'original_route_width_m':3.2,'new_geometry_clearance_target_m':.014,'collision_margin_m':.001},'manufacturing_and_structural_certification':False}

def prepare():
 assert sha(SOURCE)==SOURCE_SHA
 proposal=read(PROPOSAL);assert sha(GEOMETRY)==proposal['source_geometry_sha256'];assert sha(STATIC)==proposal['retained_static_export_sha256']
 report=read(P/'source/firstpass_003/source_repair003/BUILD_REPORT.json')
 pins={str(p):sha(p)for p in [SOURCE,P/'source/AST-CUL-005.blend',WALK_SOURCE,STATIC,GEOMETRY,PROPOSAL,Path(__file__),P/'source/firstpass_001/firstpass_common.py',P/'source/firstpass_003/dependencies/geometry_review.py']+[Path(m['manifest'])for m in MATERIALS.values()]}
 recipe=make_recipe();recipe['input_pins']=pins
 for role,m in recipe['materials'].items():m['retained_material_record_sha256']=report['preserved_snapshot']['materials'][m['datablock']]
 write_new(R/'SOURCE_CONTRACT.json',recipe)
 print('Prepared',len(recipe['objects']),'meshes,',len(recipe['actual_source_references']),'pinned guard/tread parts. No Blender or Godot launched.')
if __name__=='__main__':prepare()
