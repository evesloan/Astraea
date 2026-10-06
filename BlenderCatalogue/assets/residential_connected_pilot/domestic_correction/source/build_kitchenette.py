"""Original compact suite kitchenette source candidate; no cooking simulation.

Standalone reusable domestic module. Source local X follows the2.15m worktop,
front is-Y, up is+Z. It will be fitted with the revised room/view profiles.
No catalogue ID is allocated and no Game/Catalogue files are changed.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,os,sys,argparse
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];BATCH=ROOT.parent;CAT=Path(os.environ['ASTRAEA_CATALOGUE_ROOT']).resolve() if os.environ.get('ASTRAEA_CATALOGUE_ROOT') else next(p for p in Path(__file__).resolve().parents if (p/'catalogue_manifest.json').is_file())
parser=argparse.ArgumentParser();parser.add_argument('--revision',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=ROOT/'outputs'/args.revision;assert not OUT.exists(),'Fresh revision required';OUT.mkdir(parents=True)
text=(BATCH/'inputs/build_residential_suite.py').read_text().split('# Local +Y')[0]
text=text.replace("ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]","ROOT=CAT/'assets/residential_suite'")
ns={'__file__':__file__,'CAT':CAT};exec(compile(text,'retained_suite_primitives','exec'),ns)
mesh,ex,datum=[ns[k]for k in ['mesh','extrusion','datum']];mats=ns['mats']
def box(name,x,y,z,role):return ex(name,[(x[0],y[0]),(x[1],y[0]),(x[1],y[1]),(x[0],y[1])],z[0],z[1],role)
def pipe(name,points,r=.018,role='champagne_metal'):
    verts=[];n=8
    for i,p in enumerate(points):
        p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();a=t.cross(Vector((1,0,0))).normalized();b=t.cross(a).normalized()
        for j in range(n):verts.append(tuple(p+r*(a*math.cos(j*math.tau/n)+b*math.sin(j*math.tau/n))))
    faces=[tuple(reversed(range(n))),tuple(range((len(points)-1)*n,len(points)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j)for i in range(len(points)-1)for j in range(n)]
    return mesh(name,verts,faces,role)
def ellipse(cx,cy,rx,ry,n=24):return[(cx+rx*math.cos(i*math.tau/n),cy+ry*math.sin(i*math.tau/n))for i in range(n)]
# Recessed service plinth and genuinely hollow cabinet bays.
box('KIT_RecessedToePlinth',[-.99,.99],[-.25,.31],[0,.10],'warm_walnut')
box('KIT_BaseDeck',[-1.035,1.035],[-.33,.33],[.10,.15],'warm_walnut')
box('KIT_BackPanel',[-1.035,1.035],[.295,.33],[.15,.915],'ivory_enamel')
for i,x in enumerate([-1.035,-.325,.195,1.035]):box('KIT_CarcassSide_'+str(i),[x-.022,x+.022],[-.33,.33],[.15,.915],'warm_walnut')
box('KIT_HeaderBeam',[-1.035,1.035],[-.33,-.29],[.85,.92],'warm_walnut')
# Counter is a ring around the sink opening, not a hidden solid slab.
for name,x,y in [('left',[-1.075,.31],[-.37,.37]),('right',[.91,1.075],[-.37,.37]),('front',[.31,.91],[-.37,-.22]),('back',[.31,.91],[.22,.37])]:box('KIT_Worktop_'+name,x,y,[.92,.975],'warm_stone')
box('KIT_Splashback',[-1.075,1.075],[.335,.375],[.975,1.30],'ivory_enamel')
box('KIT_SplashCap',[-1.075,1.075],[.32,.39],[1.30,1.335],'warm_walnut')
# Open tapered basin, rolled lip, low drain and a real gooseneck spout.
profiles=[(.99,.295,.215),(.965,.27,.195),(.78,.235,.17),(.735,.14,.10),(.73,.03,.025)]
n=24;verts=[(.61+rx*math.cos(i*math.tau/n),ry*math.sin(i*math.tau/n),z)for z,rx,ry in profiles for i in range(n)]
faces=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i)for k in range(len(profiles)-1)for i in range(n)]+[tuple(range((len(profiles)-1)*n,len(profiles)*n))]
mesh('KIT_OpenSinkBowl',verts,faces,'champagne_metal')
ex('KIT_Drain',ellipse(.61,0,.027,.022),.729,.732,'champagne_metal')
pipe('KIT_GooseneckSpout',[(.61,.28,.975),(.61,.28,1.15),(.61,.225,1.265),(.61,.11,1.265),(.61,.04,1.19)])
box('KIT_TapBase',[.82,.90],[.24,.31],[.975,1.015],'champagne_metal')
pipe('KIT_TapLever',[(.86,.28,1.01),(.86,.20,1.075),(.86,.10,1.075)],.014)
datum('tap_control',(.86,.12,1.075));datum('sink_use',(.61,-.95,0))
# Small cooking/reheating provision: two compact induction rings and a clear
# work strip, explicitly distinct from a full luxury kitchen/oven installation.
box('KIT_HobFrame',[-.98,-.37],[-.26,.26],[.975,.992],'champagne_metal')
box('KIT_HobSurface',[-.955,-.395],[-.235,.235],[.992,.999],'ivory_enamel')
for i,(x,rx)in enumerate([(-.79,.115),(-.535,.09)]):
    outer=ellipse(x,.035,rx,rx);inner=ellipse(x,.035,rx-.008,rx-.008)
    verts=[(u,v,1.002)for ring in [outer,inner]for u,v in ring];mesh('KIT_InductionRing_'+str(i),verts,[(j,(j+1)%24,(j+1)%24+24,j+24)for j in range(24)],'champagne_metal')
for i,x in enumerate([-.82,-.55]):box('KIT_HobControl_'+str(i),[x-.032,x+.032],[-.20,-.16],[1.001,1.008],'champagne_metal')
datum('reheat_control',(-.685,-.18,1.02));datum('work_stance',(-.20,-1.00,0))
# Undercounter refrigerator has a real inner bay, two shelves and separate
# hinged door/hardware; it is not a solid cabinet volume behind a moving leaf.
for i,z in enumerate([.30,.56]):box('KIT_ColdShelf_'+str(i),[-.965,-.38],[-.245,.275],[z,z+.025],'ivory_enamel')
hinge=bpy.data.objects.new('HINGE_KITCHEN_FRIDGE',None);bpy.context.collection.objects.link(hinge);hinge.location=(-1.005,-.36,.13)
bpy.context.view_layer.update()
moving=[]
def fridge_part(ob):
    ob.parent=hinge;ob.matrix_parent_inverse=hinge.matrix_world.inverted();moving.append(ob);return ob
fridge_part(box('KIT_FridgeDoor',[-1.005,-.35],[-.405,-.34],[.13,.85],'ivory_enamel'))
fridge_part(box('KIT_FridgeTimberInset',[-.965,-.39],[-.42,-.405],[.20,.79],'teal_weave'))
fridge_part(pipe('KIT_FridgeHandle',[(-.42,-.44,.36),(-.42,-.48,.40),(-.42,-.48,.69),(-.42,-.44,.73)],.015))
datum('fridge_control',(-.42,-.49,.56))
for i,(x0,x1)in enumerate([(-.29,.16),(.23,1.005)]):
    box('KIT_StorageDoor_'+str(i),[x0,x1],[-.37,-.335],[.15,.845],'warm_walnut')
    pipe('KIT_StorageHandle_'+str(i),[(x1-.09,-.385,.43),(x1-.09,-.43,.47),(x1-.09,-.43,.70),(x1-.09,-.385,.74)],.012)
# One shallow overhead pantry and an actual under-cabinet task lens.
box('KIT_UpperPantryBack',[-1.02,.16],[.28,.34],[1.66,2.08],'ivory_enamel')
for x in [-1.02,.16]:box('KIT_UpperPantrySide_'+str(x),[x-.025,x+.025],[-.03,.34],[1.66,2.08],'warm_walnut')
for z in [1.66,2.055]:box('KIT_UpperPantryShelf_'+str(z),[-1.02,.16],[-.03,.34],[z,z+.025],'warm_walnut')
box('KIT_UpperPantryFront',[-.995,.135],[-.045,-.025],[1.71,2.03],'oatmeal_weave')
box('KIT_TaskHousing',[-.95,.095],[.025,.20],[1.625,1.66],'champagne_metal')
box('KIT_TaskLens',[-.91,.055],[.04,.18],[1.615,1.625],'lens');datum('task_light',(-.43,.11,1.59))
datum('installation_origin',(0,0,0));datum('clear_standing_center',(-.20,-1.00,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.view_layer.update()
# Correct and freeze the parent transform so the closed door stays exactly at
# its authored position while rotation of the hinge has meaningful motion.
for ob in moving:
    world=ob.matrix_world.copy();ob.matrix_parent_inverse=hinge.matrix_world.inverted();ob.matrix_world=world
bpy.ops.file.pack_all();source=OUT/'suite_kitchenette.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(OUT/'suite_kitchenette.glb'),export_format='GLB',export_yup=True,export_extras=True)
receipt={'status':'source_candidate_not_installed','catalogue_id':None,'scope':'Compact sink,two-ring cooking/reheating provision,undercounter refrigerator,hollow storage,task fixture. No cooking simulation.',
 'source_frame':'Blender X width,Y depth(front−Y),Zup','bounds_nominal_m':{'width':2.15,'depth':.865,'height':2.08},
 'standing_space_proposal':{'center':[-.20,-1.00,0],'width':1.30,'depth':.90,'host_clearance_verified':False},
 'fridge_hinge_source_xyz':list(hinge.location),'door_moving_parts':[o.name for o in moving],'door_motion_status':'Authored hinge and cavity; actual motion/obstruction/host integration not tested',
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((OUT/'suite_kitchenette.glb').read_bytes()).hexdigest(),
 'bed_or_capacity_changes':False,'game_or_catalogue_edits':False}
(OUT/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('KITCHENETTE_SOURCE_CANDIDATE_CREATED',flush=True)
