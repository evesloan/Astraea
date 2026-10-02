"""Actual imported-GLB source reload + pixel evidence, QA fixtures only.
Use -- --preflight-only, or --views comma,separated,names after lead render slot.
"""
import bpy,bmesh,json,math,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
PREFLIGHT='--preflight-only' in sys.argv
SELECTED=sys.argv[sys.argv.index('--views')+1].split(',') if '--views' in sys.argv else None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def point(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def source_checks():
 records=[]
 for path in sorted(ROOT.rglob('*.blend')):
  bpy.ops.wm.open_mainfile(filepath=str(path));parts=[];issues=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(ob.data);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
   if nm or vol<=0:issues.append(ob.name)
   parts.append({'name':ob.name,'nonmanifold_edges':nm,'signed_volume_m3':vol,'uv_layers':[u.name for u in ob.data.uv_layers],'scale':list(ob.scale),'modifiers':[m.type for m in ob.modifiers]})
  records.append({'source':str(path.relative_to(ROOT)),'sha256':sha(path),'parts':parts,'issues':issues,'status':'PASS' if not issues else 'FAIL'})
 (ROOT/'qa/source_reload_validation.json').write_text(json.dumps(records,indent=2)+'\n')
 assert all(r['status']=='PASS' for r in records),[(r['source'],r['issues']) for r in records if r['issues']]
source_checks()

def clear():bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def imported(asset,loc=(0,0,0),yaw=0,mirror=False):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/(asset+'.glb')))
 T=Matrix.Translation(Vector(loc))@Matrix.Rotation(yaw,4,'Z')
 if mirror:T=T@Matrix.Diagonal((-1,1,1,1))
 obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 for ob in obs:ob.matrix_world=T@ob.matrix_world;ob.name=asset+'_'+ob.name
 return obs

def qa_box(name,lo,hi,color=(.18,.21,.22,1)):
 mat=bpy.data.materials.get('QA_ONLY_'+name) or bpy.data.materials.new('QA_ONLY_'+name);mat.diffuse_color=color;mat.use_nodes=True
 mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
 bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((lo[k]+hi[k])/2 for k in range(3)));ob=bpy.context.object;ob.name='QA_ONLY_'+name;ob.dimensions=tuple(hi[k]-lo[k] for k in range(3));ob.data.materials.append(mat)
 return ob

def scene_setup():
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=4
 sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.37,.41,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 for name,loc,power,size in [('key',(-2.8,-3.8,5),750,4),('fill',(3,2,3.8),550,3.5),('edge',(-1,3,2),450,3)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;point(ob,(.5,.2,0))
 data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam
 return sc,cam

views=[
 {'key':'edge_chain_full_640','group':'edge','camera_m':[3.5,-3.8,2.3],'target_m':[1.23,-.12,-.10],'resolution':[640,360],'ortho_scale':3.65,'full':True,'purpose':'Straight, curved and closed terminal actual GLBs. Wet bullnose and real slotted trough are both visible'},
 {'key':'edge_chain_standing_640','group':'edge','camera_m':[3.3,-3.7,1.65],'target_m':[1.22,-.1,-.08],'resolution':[640,360],'ortho_scale':None,'lens_mm':48,'full':True,'purpose':'Standing eye Z1.65 above deck; 1.20 m pitch and compatible curved seam'},
 {'key':'drain_bullnose_detail_1280','group':'edge','camera_m':[1.25,-1.1,.72],'target_m':[.67,-.19,-.055],'resolution':[1280,720],'ortho_scale':1.45,'full':False,'purpose':'Intentional close crop: open 22 mm slat slots, formed 55 mm bullnose, aligned start of curve'},
 {'key':'drain_bracket_underside_detail_1280','group':'edge_under','camera_m':[1.5,.66,-.39],'target_m':[.67,-.19,-.14],'resolution':[1280,720],'ortho_scale':1.6,'full':False,'purpose':'Intentional underside crop: real drain throat and closed brackets with exact deck anchor planes'},
 {'key':'entry_full_640','group':'entry','camera_m':[3.4,3.8,2.4],'target_m':[0,.43,.03],'resolution':[640,360],'ortho_scale':5.25,'full':True,'purpose':'Four-riser entry silhouette with returned rails and real tread/stringer contact'},
 {'key':'entry_standing_640','group':'entry','camera_m':[4.3,5.5,1.65],'target_m':[0,.44,.02],'resolution':[640,360],'ortho_scale':None,'lens_mm':42,'full':True,'purpose':'Ordinary standing eye Z1.65 relative to upper deck; no actor fit or accessible-route claim'},
 {'key':'entry_rail_tread_detail_1280','group':'entry','camera_m':[1.55,1.8,.90],'target_m':[.20,.52,-.15],'resolution':[1280,720],'ortho_scale':1.9,'full':False,'purpose':'Actual rail flanges, clear hand space, flush grip rebates and rounded step nosings'},
 {'key':'entry_underside_detail_1280','group':'entry_under','camera_m':[2.3,1.25,-.30],'target_m':[.15,.43,-.38],'resolution':[1280,720],'ortho_scale':2.25,'full':False,'purpose':'Intentional underside crop: shaped stringers meet trays and anchor pads; open stair underside retained'}]
if SELECTED:views=[v for v in views if v['key'] in SELECTED]
last=None;components=[];records=[]
for v in views:
 if last!=v['group']:
  clear();last=v['group'];components=[]
  if v['group'].startswith('edge'):
   components+=imported('derived/AST-AQU-003_START');components+=imported('AST-AQU-003');components+=imported('AST-AQU-004',(1.2,0,0));end=(1.2+3*math.sin(.4),3*(1-math.cos(.4)),0)
   components+=imported('derived/AST-AQU-003_END',end,.4)
   if v['group']=='edge':
    for ident,dx in [('AST-AQU-003',0),('AST-AQU-004',1.2)]:
     for pad in json.loads((ROOT/(ident+'.manifest.json')).read_text())['host_contact_pads']:
      a=pad['bounds_min_m'];b=pad['bounds_max_m'];qa_box('coping_exact_pad_'+ident+'_'+pad['name'],(a[0]+dx-.008,a[1]-.008,-.55),(b[0]+dx+.008,b[1]+.008,pad['receiving_z_m']),(.16,.19,.21,1))
    qa_box('coping_lower_inspection_floor',(-50,-50,-.57),(50,50,-.55),(.16,.18,.20,1))
  else:
   components+=imported('AST-AQU-005')
   if v['group']=='entry':
    # The upper block meets only the rear arrival edge. Exact little receiving
    # ledges under the actual anchor pads are visible, not a slab through steps.
    qa_box('upper_dry_deck',(-1.05,-1.35,-.18),(1.05,-.64,0),(.23,.26,.26,1))
    for xx in [-.53,.53]:qa_box('upper_anchor_shelf_'+str(xx),(xx-.09,-.64,-.30),(xx+.09,-.405,-.18),(.22,.25,.25,1))
    qa_box('lower_foundation',(-1,-.2,-.98),(1,1.70,-.86),(.16,.20,.21,1))
    qa_box('lower_landing_extension',(-1,1.58,-.86),(1,2.25,-.72),(.21,.25,.26,1))
    qa_box('entry_lower_inspection_floor',(-50,-50,-1.0),(50,50,-.99),(.15,.18,.20,1))
  sc,cam=scene_setup()
 cam.location=v['camera_m'];point(cam,v['target_m']);cam.data.type='ORTHO' if v['ortho_scale'] else 'PERSP';cam.data.lens=v.get('lens_mm',48)
 if v['ortho_scale']:cam.data.ortho_scale=v['ortho_scale']
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.025) if v['full'] else frame.frame_report(sc,cam,components,.025)
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
 records.append(v)
report={'scope':'Actual imported GLB component inspection, QA fixtures only; no water, district, engine or actor claim','renderer':'BLENDER_EEVEE_NEXT','samples':48,'denoising':False,'preflight_only':PREFLIGHT,'artifacts':[{'asset':p.stem,'glb_sha256':sha(p),'source_sha256':sha(p.with_suffix('.blend'))} for p in sorted(ROOT.rglob('*.glb'))],'views':records}
out='camera_preflight.json' if PREFLIGHT else 'render_evidence.json'
(ROOT/'qa'/out).write_text(json.dumps(report,indent=2)+'\n')
print('AQUATIC_EDGE_PREFLIGHT_PASS' if PREFLIGHT else 'AQUATIC_EDGE_RENDER_COMPLETE')
