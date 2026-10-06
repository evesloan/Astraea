"""Pure preparation/checks only. No Blender, export, or renderer. Writes only this new derivative package."""
from pathlib import Path
import sys,json,hashlib,importlib.util,collections,copy
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from media_paths import CAT,AUDIT,PACKAGE,original_path,pin_name,resolve_pin,archived_reference
import media_geometry as mg
sp=importlib.util.spec_from_file_location('retained_geometry',CAT/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def tri_hits(o,d,ts,min_t=0,max_t=100):
 o=np.asarray(o);d=np.asarray(d);T=np.asarray(ts);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];h=np.cross(d,e2);det=(e1*h).sum(1);good=abs(det)>1e-11;iv=np.divide(1.,det,out=np.zeros_like(det),where=good);s=o-T[:,0];u=iv*(s*h).sum(1);q=np.cross(s,e1);v=iv*(d*q).sum(1);t=iv*(e2*q).sum(1);ids=np.where(good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=min_t)&(t<=max_t))[0];return [(float(t[i]),int(i),(o+d*t[i]).tolist())for i in sorted(ids,key=lambda i:t[i])]

def inside_box(b,p,tol=5e-5):return all(b[0][i]-tol<=p[i]<=b[1][i]+tol for i in range(3))
def segment_box(a,b,box):
 lo,hi=0.,1.
 for k in range(3):
  d=b[k]-a[k]
  if abs(d)<1e-12:
   if a[k]<box[0][k] or a[k]>box[1][k]:return False
  else:
   x=(box[0][k]-a[k])/d;y=(box[1][k]-a[k])/d;lo=max(lo,min(x,y));hi=min(hi,max(x,y))
   if lo>hi:return False
 return hi>.0001 and lo<.9999

def main():
 pins={str(original_path(p)):h for p,h in json.loads((AUDIT/'INPUT_PINS.json').read_text()).items()};inventory=json.loads((AUDIT/'SOURCE_INVENTORY.json').read_text())
 for key in ['AST-LIB-010','AST-AQU-016']:
  a=inventory[key]
  for what in ['source','export']:pins[str(CAT/a[what])]=a[what+'_sha256']
 for p in [CAT/'assets/library_use/source/build_library_use.py',CAT/'assets/library_use/AST-LIB-010.manifest.json',CAT/'assets/library_use/texture_manifest.json',CAT/'materials/material_manifest.json',CAT/'assets/library_use/source/make_use_art.py']:
  pins[str(p)]=sha(p)
 for role in ['ivory_enamel','warm_walnut','dark_rubber','champagne_metal']:
  p=CAT/'materials'/(role+'.png');pins[str(p)]=sha(p)
 p=CAT/'assets/library_use/textures/display_glass.png';pins[str(p)]=sha(p)
 for f in ['MEDIA_FITTING_CANDIDATES.json','PLANTING_ENVELOPE_CANDIDATES.json','WET_POT_FULLNESS_CANDIDATES.json','INSPECTED_IMAGES.json','SOURCE_INVENTORY.json']:
  p=AUDIT/f;pins[str(p)]=sha(p)
 catalogue=json.loads((CAT/'catalogue_manifest.json').read_text());catalogue_exports={a['export']:a for a in catalogue['assets']}
 for contract_path in [CAT/'assets/grand_pool_first_pass/source/placement_contract.json',CAT/'assets/grand_pool_first_pass/finish_envelope/stock/stock_placement_contract.json']:
  pc=json.loads(contract_path.read_text());expected={}
  for a in pc['input_inventory'].values():
   export=a.get('export',a.get('path'));expected[export]=a.get('export_sha256',a.get('sha256'))
   source_path=a.get('source',a.get('editable_source'));source_hash=a.get('source_sha256',a.get('editable_source_sha256'))
   if source_path:pins[str(CAT/source_path)]=source_hash
  for placement in pc['placements']:
   export=placement['retained_export'];pins[str(CAT/export)]=expected[export] if export in expected else catalogue_exports[export]['export_sha256']
 relocation=AUDIT/'REFERENCE_RELOCATION.json';pins[str(relocation)]=sha(relocation)
 for original,row in json.loads(relocation.read_text())['paths'].items():
  p,h=archived_reference(original);pins[str(p)]=h
 for p,h in pins.items():assert sha(Path(p))==h,('changed input',p)
 source=json.loads((CAT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text());floor=next(f for f in source['floor_regions']if f['id']=='D08_grand_pool_wet')
 arch=g.read_glb(CAT/inventory['AST-AQU-016']['export']);T=arch['triangles'];triangle_mesh_names=[m['name']for m in arch['meshes']for _ in m['triangles']]
 candidates=copy.deepcopy(json.loads((AUDIT/'MEDIA_FITTING_CANDIDATES.json').read_text())['candidates']);content=['sun_corp_lagoon','orchard_market_still_life','sun_corp_orbital_tide','grand_pool_wet_deck'];reports=[]
 foliage=json.loads((AUDIT/'PLANTING_ENVELOPE_CANDIDATES.json').read_text())['candidates'];wet=json.loads((AUDIT/'WET_POT_FULLNESS_CANDIDATES.json').read_text())['candidates']
 for c,art in zip(candidates,content):
  lo,hi,ylo,yhi=c['image_rect'];c['content_role']=art;c['parent_design_id']='AST-LIB-010';c['family']='library_use';c['interface_owner']='AST-AQU-016'
  c['origin_world_xyz']=[(lo+hi)/2,(ylo+yhi)/2,c['face']]if c['axis']=='z'else[c['face'],(ylo+yhi)/2,(lo+hi)/2]
  c['basis_world_columns']=[[-1,0,0],[0,1,0],[0,0,-1]]if c['axis']=='z'else[[0,0,1],[0,1,0],[-1,0,0]]
  c['screen_plane_treatment']='20 mm recessed image behind open walnut front lip'if c['axis']=='z'else'Flush front optical plane; no part protrudes forward of exact X -41.35 reservation'
  assert abs(np.linalg.det(np.asarray(c['basis_world_columns']).T)-1)<1e-12
  contacts=[];planes=[]
  if c['axis']=='z':
   iw=hi-lo;ih=yhi-ylo
   for i,(u,v)in enumerate([(s*iw*.32,t*ih*.30)for s in [-1,1]for t in [-1,1]]):
    origin=mg.local_to_world(c,(u,v,-.10));hits=tri_hits(origin,[0,0,1],T,0,.12);assert hits,(c['name'],i,'no support hit');dist,idx,pt=hits[0];n=c['face']-pt[2]
    assert abs(pt[2]-c['bounds'][1][2])<1e-4,(c['name'],'wrong first support',pt)
    witnesses=[]
    for du,dv in [(0,0),(-.04,-.065),(-.04,.065),(.04,-.065),(.04,.065)]:
     o=mg.local_to_world(c,(u+du,v+dv,n+.01));hs=tri_hits(o,[0,0,1],T,0,.02);assert hs
     witnesses.append({'world_xyz':hs[0][2],'retained_triangle_index':hs[0][1],'retained_triangle':T[hs[0][1]],'mesh':triangle_mesh_names[hs[0][1]]})
     assert abs(hs[0][2][2]-pt[2])<1e-8
    planes.append(n);contacts.append({'backplate_index':i,'support_source_object':c['support'],'actual_retained_face_z':pt[2],'local_n':n,'witnesses':witnesses})
   parts=mg.recipes(c,wall_back_planes=planes)
  else:
   parts=mg.recipes(c,floor_y=floor['floor_y']);c['floor_plane_y']=floor['floor_y'];c['floor_contract_triangles_xz']=floor['triangles'];c['floor_support_qualification']='Exact compiler floor-region triangles/plane from pinned connected contract; AST-AQU-016 exported decorative underlay at Y45.96 is not misreported as walking surface.'
   for p in parts:
    if p.get('contact',{}).get('kind')=='floor_triangle_contact':
     centre=p['contact']['local_centre'];witnesses=[]
     for du,dn in [(0,0),(-.066,-.192),(-.066,.192),(.066,-.192),(.066,.192)]:
      point=mg.local_to_world(c,(centre[0]+du,centre[1],centre[2]+dn));hits=[]
      for idx,t in enumerate(floor['triangles']):
       ts=[(q[0],floor['floor_y'],q[1])for q in t]
       if g.bary_xz(point,ts) is not None:hits.append(idx)
      assert hits,(p['name'],'off floor',point);witnesses.append({'world_xyz':point,'compiler_triangle_indices':hits})
     contacts.append({'part':p['name'],'support_floor_region':floor['id'],'actual_floor_contract_y':floor['floor_y'],'witnesses':witnesses})
  c['mount_contacts']=contacts;c['parts']=parts;c['source_file']='source/AST-LIB-010_pool_leisure_displays.blend'
  vs=[mg.local_to_world(c,p)for q in parts for p in q['vertices_local_uvn_m']]
  assert all(inside_box(c['bounds'],p)for p in vs),(c['name'],'outside audited reservation',g.bounds(vs),c['bounds'])
  for p in parts:
   edges=collections.Counter(tuple(sorted((a,b)))for f in p['faces']for a,b in zip(f,f[1:]+[f[0]]))
   if p['kind']!='art':assert set(edges.values())=={2},(p['name'],'not closed')
   assert len(mg.triangles(p))>0
  ownT=[t for p in parts if p['kind']!='art'for t in mg.triangles(p,c)]
  rayreports=[]
  for ray in c['sampled_current_triangle_sightlines']:
   e=np.asarray(ray['eye_xyz']);target=np.asarray(ray['target_xyz']);d=target-e;hits=tri_hits(e,d,ownT,1e-7,1-1e-6)
   assert not hits,(c['name'],'display self occlusion',ray,hits[:1])
   leafhits=[p['support']+'/'+l['name']for p in foliage for l in p['layers']if segment_box(e,target,l['bounds'])]
   leafhits += [p['name']for p in wet if segment_box(e,target,p['bounds'])]
   assert not leafhits,(c['name'],'reserved foliage occlusion',leafhits)
   # Actual content-plane triangles must be reached by each proposed eye ray.
   artpart=next(p for p in parts if p['kind']=='art');ah=tri_hits(e,d,mg.triangles(artpart,c),.99999,1.00001);assert ah
   rayreports.append({'eye_xyz':list(e),'target_xyz':list(target),'self_occlusions':0,'actual_recipe_content_plane_hit':True,'all_reserved_foliage_clear':True})
  c['recipe_bounds_world_xyz']=g.bounds(vs)
  reports.append({'name':c['name'],'parts':len(parts),'recipe_triangles':sum(len(mg.triangles(p))for p in parts),'bounds':g.bounds(vs),'inside_exact_audited_reservation':True,'mount_witness_count':sum(len(x['witnesses'])for x in contacts),'actual_recipe_image_plane_probes':rayreports,'world_uv_right':c['basis_world_columns'][0],'world_uv_up':c['basis_world_columns'][1]})
 contract={'schema':'astraea-grand-pool-leisure-displays-source-01','status':'RECIPE_PREPARED_NOT_BLENDER_EVALUATED_NOT_EXPORTED_NOT_VISUALLY_ACCEPTED','owner':{'parent_design_id':'AST-LIB-010','family':'library_use','existing_support_owner':'AST-AQU-016','catalogue_id_creation':False},'destination_proposal':'assets/grand_pool_first_pass/comfort_greenery/media','source_axes':'Blender Z-up; world contract uses glTF/Godot XYZ with Y up; world -> Blender (x,-z,y)','display_local_axes':'u image-right, v image-up, n front; positive determinant for both wall and stand','metres_tolerance':.00005,'light_count':0,'new_renderer_or_palette_changes':False,'original51_retained48_mutation':False,'export_status':'PROHIBITED_PENDING_SOURCE_QA_AND_INDEPENDENT_RETENTION','content_manifest':'content_manifest.json','candidates':candidates,'remaining_gates':['Run source-only Blender build in parent-issued two-thread slot','Run independent fresh Blender reopen; evaluated mount/body/contact/UV/material/image-plane tests','Retain independently verified source files/hashes without overwriting existing work','Full leafy scene paired visual comparison in real market and pool poses at 640x360','Only then seek approved export/promotion gate; no Game writes authorized here']}
 (ROOT/'source_contract.json').write_text(json.dumps(contract,indent=2)+'\n');(ROOT/'dependency_pins.json').write_text(json.dumps({pin_name(p):h for p,h in pins.items()},indent=2)+'\n');(ROOT/'qa/PURE_PREFLIGHT.json').write_text(json.dumps({'status':'PASS_RECIPE_ONLY','checks':reports,'all_pinned_inputs_unchanged':True,'blender_or_engine_started':False,'triangle_geometry_measured_where_available':True,'visual_acceptance':False},indent=2)+'\n')
 print('PURE_PREFLIGHT_PASS',[(r['name'],r['parts'],r['recipe_triangles'])for r in reports])
if __name__=='__main__':main()
