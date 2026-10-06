from pathlib import Path
import json,hashlib,math,numpy as np
from PIL import Image
S=Path('/workspace/scratch/375c2e438292');B=S/'pool-east-gallery-canopy-correction001';source=S/'pool-opposite-gallery-proposal001/combined_source002/qa/BUILD_EVALUATED_CORE.json';d=json.loads(source.read_text());parts={p['name']:p for p in d['parts']};cap=S/'pool-east-gallery-resume002/native_capture001/output/upper_arrival_installed_effects_off.png';meta=json.loads(Path(str(cap)+'.caption.json').read_text());eye=np.array(meta['actual_eye']);forward=np.array(meta['actual_camera_forward']);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward);pixels=np.array(Image.open(cap).convert('RGB'));H,W=pixels.shape[:2];scale=math.tan(math.radians(meta['fov'])/2)
def project(p):
 v=np.array(p)-eye;z=np.dot(v,forward)
 return [(np.dot(v,right)/(z*scale*W/H)+1)*W/2,(1-np.dot(v,up)/(z*scale))*H/2,z]
def ray_hit(origin,direction,tri):
 a,b,c=tri;e1=b-a;e2=c-a;cross=np.cross(direction,e2);det=np.dot(e1,cross)
 if abs(det)<1e-11:return None
 tvec=origin-a;u=np.dot(tvec,cross)/det
 if u<0 or u>1:return None
 q=np.cross(tvec,e1);v=np.dot(direction,q)/det
 if v<0 or u+v>1:return None
 t=np.dot(e2,q)/det
 return t if t>1e-7 else None
rows=[]
for name in ['EAST_Bay_WarmRearCanopy','EAST_Bay_PaleFrontCanopy','EAST_Bay_ForeSweptReturn','EAST_Bay_AftSweptReturn','EAST_Bay_FixtureCup_0','EAST_Bay_FixtureCup_1','EAST_Display_Hanger_Fore','EAST_Display_Hanger_Aft']:
 p=parts[name];v=np.array(p['vertices_xyz']);screen=np.array([project(x)for x in v]);rows.append({'part':name,'bounds_xyz':[v.min(0).tolist(),v.max(0).tolist()],'projected_bounds_pixels':[screen[:,:2].min(0).tolist(),screen[:,:2].max(0).tolist()],'declared_supports':p['support'],'signed_volume_m3':p['signed_volume_m3']})
# Sample visible triangle interiors of the pale canopy against actual image pixels.
canopy=parts['EAST_Bay_PaleFrontCanopy'];v=np.array(canopy['vertices_xyz']);alltri=[(p['name'],np.array(p['vertices_xyz'])[indices])for p in d['parts']for indices in p['evaluated_triangles']];samples=[]
for ti,ix in enumerate(canopy['evaluated_triangles']):
 tri=v[ix];centre=tri.mean(0);normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal)
 if np.dot(normal,eye-centre)<=0:continue
 px,py,z=project(centre);x,y=round(px),round(py)
 if not(2<=x<W-2 and 2<=y<H-2):continue
 direction=centre-eye;dist=np.linalg.norm(direction);direction/=dist
 closest=(float('inf'),None)
 for name,t in alltri:
  distance=ray_hit(eye,direction,t)
  if distance is not None and distance<closest[0]:closest=(distance,name)
 if closest[1]!='EAST_Bay_PaleFrontCanopy':continue
 samples.append({'triangle':ti,'world_xyz':centre.tolist(),'pixel_xy':[x,y],'actual_rgb':pixels[y,x].tolist(),'outward_normal_xyz':normal.tolist(),'first_new_core_part':closest[1]})
ends=[]
for z in [-454,-445]:
 points=np.array([x for x in canopy['vertices_xyz']if abs(x[2]-z)<1e-6]);ends.append({'end_z':z,'return_top_y':55.95,'canopy_lowest_y':float(points[:,1].min()),'open_gap_m':float(points[:,1].min()-55.95)})
result={'status':'READ_ONLY_ACTUAL_SOURCE_AND_NATIVE_PIXEL_DIAGNOSIS','source_snapshot_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_image_sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'native_image':str(cap),'parts':rows,'open_end_return_joints':ends,'visible_pale_canopy_samples':samples,'pale_canopy_rgb_range':{'min':np.array([s['actual_rgb']for s in samples]).min(0).tolist(),'max':np.array([s['actual_rgb']for s in samples]).max(0).tolist()}if samples else None,'limits':'Exact source geometry already matched native import in focused pass. Pixel correspondence uses captured camera; this read-only probe considers new core surfaces for closest-part classification, not the entire ship. No engine or source edit.'}
(B/'DIAGNOSIS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'end_joints':ends,'samples':len(samples),'rgb_range':result['pale_canopy_rgb_range'],'parts':rows},indent=2))
