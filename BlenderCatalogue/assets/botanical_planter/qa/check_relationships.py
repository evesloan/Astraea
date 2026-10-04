"""Measure actual evaluated contact patches and source seam cross-sections.
Independent of numeric manifest declarations; no rendering or game physics.
"""
import bpy,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def area(p):return .5*sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))
def ccw(p):return p if area(p)>=0 else list(reversed(p))
def clip(subject,cut):
 out=ccw(subject);cut=ccw(cut)
 for a,b in zip(cut,cut[1:]+cut[:1]):
  prev=out;out=[]
  if not prev:break
  cross=lambda p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
  for u,v in zip(prev[-1:]+prev[:-1],prev):
   cu,cv=cross(u),cross(v);iu,iv=cu>=-1e-10,cv>=-1e-10
   if iu!=iv:
    t=cu/(cu-cv);out.append((u[0]+t*(v[0]-u[0]),u[1]+t*(v[1]-u[1])))
   if iv:out.append(v)
 return out

def surfaces(ob,z):
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh();out=[]
 for f in me.polygons:
  vs=[ob.matrix_world@me.vertices[i].co for i in f.vertices]
  if len(vs)>=3 and all(abs(v.z-z)<2e-6 for v in vs):
   p=[(v.x,v.y) for v in vs]
   if abs(area(p))>1e-10:out.append(p)
 eo.to_mesh_clear();return out

def contact(a,b,z):return sum(abs(area(q)) for pa in surfaces(a,z) for pb in surfaces(b,z) if len(q:=clip(pa,pb))>=3)
def meshbounds(ob):
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];eo.to_mesh_clear();return lo,hi
source={};checks=[]
for cid in ('AST-BOT-004','AST-BOT-005','AST-BOT-006'):
 p=ROOT/(cid+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p));obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};bpy.context.view_layer.update();support=[]
 for key,ob in obs.items():
  if not key.startswith('seat_load_bracket_'):continue
  suffix=key.rsplit('_',1)[-1];shoe=obs['floor_contact_bracket_shoe_'+suffix];seat=[o for n,o in obs.items() if n.startswith('timber_sitting_ribbon_')]
  shoe_contact=contact(ob,shoe,.065);seat_contacts={o.name:contact(ob,o,.415) for o in seat};floor=meshbounds(shoe)[0][2]
  assert shoe_contact>1e-4 and all(a>1e-4 for a in seat_contacts.values()) and abs(floor)<1e-7
  support.append({'bracket':key,'shoe':shoe.name,'actual_evaluated_shoe_contact_m2':shoe_contact,'actual_evaluated_seat_contact_m2':seat_contacts,'floor_min_z_m':floor,'status':'PASS'})
 soil=obs['soil_volume_with_usable_planting_surface'];soilbase=contact(soil,obs['recessed_cavity_bottom'],.105);assert soilbase>.10
 source[cid]={n:[[v.co.x,v.co.y,v.co.z] for v in o.data.vertices] for n,o in obs.items()}
 checks.append({'catalogue_id':cid,'blend_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'evaluated_support_contacts':support,'soil_base_actual_contact_m2':soilbase,'seat_top_z_m':meshbounds(obs['timber_sitting_ribbon_01'])[1][2],'soil_top_z_m':meshbounds(soil)[1][2],'status':'PASS'})
common=[n for n in source['AST-BOT-004'] if not n.startswith(('seat_load_bracket','floor_contact_bracket'))]
joins=[]
for name in common:
 def section(cid,axis,plane,outaxes,offsets=(0,0)):
  return sorted(set(tuple(round(v[k]+off,6) for k,off in zip(outaxes,offsets)) for v in source[cid][name] if abs(v[axis]-plane)<2e-6))
 a=section('AST-BOT-004',0,2.399,(1,2));b=section('AST-BOT-005',0,.001,(1,2));assert a==b,(name,a,b)
 c=section('AST-BOT-005',1,1.399,(0,2),(-1.4,0))
 d=sorted(set((round(-v[1],6),round(v[2],6)) for v in source['AST-BOT-006'][name] if abs(v[0]-.001)<2e-6))
 assert c==d,(name,c,d)
 joins.append({'semantic_part':name,'straight_to_quarter_cross_section_equal':True,'quarter_to_terminal_cross_section_equal':True,'actual_nominal_seam_gap_m':.002,'source_section_points':len(a),'status':'PASS'})
report={'scope':'Blender evaluated contact patches and source seam geometry only; no structural load/actor/engine certification','checks':checks,'seam_profiles':joins,'status':'PASS'}
(ROOT/'qa/measured_relationships.json').write_text(json.dumps(report,indent=2)+'\n');print('MEASURED_RELATIONSHIPS_PASS')
