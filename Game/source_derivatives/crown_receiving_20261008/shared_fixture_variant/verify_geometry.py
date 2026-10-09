from pathlib import Path
import json,numpy as np,math,hashlib
B=Path(__file__).resolve().parent;ns={'__file__':str(B.parent/'audit.py')};exec((B.parent/'audit.py').read_text().split('runtime=json')[0],ns)
j,shared=ns['glb'](B/'AST-CMD-001_crown_fixture_relocation_20261008_r002.glb');q=json.loads((B.parent/'fixture_fit_candidates/MOUNTED_FIXTURE_RELOCATION_PROPOSALS.json').read_text());parts=json.loads(Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/BlenderCatalogue/assets/central_crown/source/geometry_parts.json').read_text())['parts']
def rays(objs,p,d,maxdist):
 out=[]
 for o in objs:
  a=o['tri'][:,0];e1=o['tri'][:,1]-a;e2=o['tri'][:,2]-a;h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);mask=np.abs(det)>1e-9;inv=np.zeros(len(det));inv[mask]=1/det[mask];s=p-a;u=inv*np.einsum('ij,ij->i',s,h);qq=np.cross(s,e1);v=inv*(qq@d);t=inv*np.einsum('ij,ij->i',e2,qq);ok=mask&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-6)&(t<=maxdist)
  if ok.any():out.append({'mesh':o['name'],'distance':float(t[ok].min())})
 return sorted(out,key=lambda r:r['distance'])
records=[]
folders={'D18_directory_02':'D18_directory_02_navigation','D18_directory_04':'D18_directory_04_solar_chart','D18_directory_06':'D18_directory_06_bridge_briefing'}
for prop in q:
 _,incoming=ns['glb'](B.parent/folders[prop['key']]/'exports'/(prop['key']+'.glb'));p=np.array(prop['proposed_marker_position']);h=np.array(prop['housing_bounds']);conflicts=[o['name'] for o in incoming if np.all(o['hi']>h[:3]+1e-5)and np.all(o['lo']<h[3:]-1e-5)];assert not conflicts
 # Test housing top against actual shared mesh roof with upward rays starting 1 mm above contact.
 contacts=[]
 for x in np.linspace(h[0]+.001,h[3]-.001,9):
  for z in np.linspace(h[2]+.001,h[5]-.001,5):
   hit=rays([o for o in shared if o['name'].endswith('ASTRAEA_staff_white_paint')],np.array([x,111-.001,z]),np.array([0.,1,0]),.002);assert hit,(prop['existing_marker'],'no actual roof contact',x,z);assert abs(hit[0]['distance']-.001)<1e-5;contacts.append(hit[0])
 clear=0
 for dx in np.linspace(-.65,.65,9):
  for dz in np.linspace(-.15,.15,5):
   hit=rays(shared+incoming,p+np.array([dx,0,dz]),np.array([0.,-1,0]),p[1]-108.8);assert not hit,(prop['existing_marker'],'blocked lens footprint',hit);clear+=1
 # Bounded full-angle rays describe interception rather than mistaking a broad cone for an empty shaft.
 beam=[]
 for angle in [0,10,20,30,40,50,60,70,76]:
  for az in ([0] if angle==0 else range(0,360,15)):
   a=math.radians(angle);b=math.radians(az);d=np.array([math.sin(a)*math.cos(b),-math.cos(a),math.sin(a)*math.sin(b)]);dist=min(10,(p[1]-108.8)/(-d[1]));hits=rays(shared+incoming,p,d,dist)
   if hits:beam.append({'angle_degrees':angle,'azimuth_degrees':az,'first_hit':hits[0]})
 roof_source=[v['name'] for v in parts if v['name'].startswith('CMD_RoofCeiling') and v['world_aabb'][0]<=p[0]<=v['world_aabb'][1] and v['world_aabb'][4]<=p[2]<=v['world_aabb'][5]]
 ribs=[v['name'] for v in parts if 'CeilingCrossRib' in v['name'] and min(h[3],v['world_aabb'][1])-max(h[0],v['world_aabb'][0])>1e-5 and min(h[5],v['world_aabb'][5])-max(h[2],v['world_aabb'][4])>1e-5]
 records.append({'marker':prop['existing_marker'],'roof_contact_rays':len(contacts),'roof_contact_max_error_m':max(abs(c['distance']-.001)for c in contacts),'roof_source_parts_at_center':roof_source,'cross_rib_overlap_parts':ribs,'incoming_housing_aabb_conflicts':conflicts,'full_shared_and_incoming_lens_footprint_clear_rays_to_y108_8':clear,'cone_sample_count':193,'cone_interceptions_above_y108_8':beam,'cone_note':'Sampled fixed existing 76-degree half-angle and 10m range; off-axis roof/room interception is reported, not treated as proof of photometric or in-engine visual acceptance.'})
 print(prop['existing_marker'],'roof',len(contacts),'clear',clear,'cone interception',len(beam),flush=True)
(B/'GEOMETRY_CHECKS.json').write_text(json.dumps(records,indent=2))
