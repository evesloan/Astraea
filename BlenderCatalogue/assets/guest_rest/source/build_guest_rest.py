"""Original guest sleeping furniture, authored from the approved residential palette.
Uses the catalogue's existing rounded-ring upholstery tools. Not room/berth assignment.
"""
from pathlib import Path
import bpy,importlib.util,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('day_furniture',CAT/'assets/furniture/build_furniture.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def marker(name,point):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=point
for aid,width,places in [('AST-SLP-001',1.16,1),('AST-SLP-002',2.06,2)]:
 F.reset()
 linen=F.M['oatmeal_weave'].copy();linen.name='ASTRAEA_guest_linen';linen['astraea_material_role']='guest_linen';linen.diffuse_color=(225/255,225/255,220/255,1)
 for node in linen.node_tree.nodes:
  if node.type=='TEX_IMAGE':node.image=bpy.data.images.load(str(ROOT/'textures/guest_linen.png'),check_existing=True);node.image.pack()
 F.M['guest_linen']=linen
 F.pill_slab('REST_RecessedToeBase',width-.22,1.96,0,.24,'dark_rubber',r=.12,bevel=.008)
 F.pill_slab('REST_RolledTimberPlinth',width,2.30,.18,.34,'warm_walnut',r=.17,grain='y',bevel=.016)
 F.pill_slab('REST_RecessedMattressDeck',width-.10,2.17,.32,.375,'ivory_enamel',r=.14,bevel=.008)
 # Side rail and headboard have real layered profiles, not unmodified cubes.
 profile=[(.96,.20),(1.21,.20),(1.26,1.25),(1.18,1.37),(1.04,1.34),(.94,.94)]
 F.extrusion('REST_SweptHeadboard',profile,-width/2-.035,width/2+.035,'warm_walnut',bevel=.015,grain='z')
 F.cushion('REST_HeadboardPad',width-.09,.83,.10,(0,.92,.92),'teal_weave',angle=82)
 rings=[(.36,.93),(.40,1),(.565,1),(.607,.97),(.615,.85)];verts=[]
 for z,scale in rings:verts.extend((x,y,z)for x,y in F.rounded_outline((width-.12)*scale,2.08*scale,.085*scale,n=5))
 faces=[tuple(reversed(range(20))),tuple(range(80,100))]+[(k*20+j,k*20+(j+1)%20,(k+1)*20+(j+1)%20,(k+1)*20+j)for k in range(4)for j in range(20)]
 F.mesh_obj('REST_FittedMattress',verts,faces,'guest_linen')
 # Quilt crown and a separate turned-back lip give the foot a soft silhouette.
 F.cushion('REST_Quilt',width-.06,1.38,.075,(0,-.32,.64),'guest_linen')
 F.cushion('REST_TurnedFold',width-.07,.24,.085,(0,.31,.667),'guest_linen')
 F.cushion('REST_TealRunner',width+.015,.50,.028,(0,-.64,.675),'teal_weave')
 xs=[0] if places==1 else [-.46,.46]
 for i,x in enumerate(xs):
  F.cushion('REST_Pillow_'+str(i),.73,.45,.15,(x,.77,.65),'guest_linen',angle=-6)
  marker('sleep_'+str(i),(x,.0,.615))
 for side in [-1,1]:marker('side_approach_'+str(side),(side*(width/2+.60),-.15,0))
 marker('foot_approach',(0,-1.8,0))
 bpy.context.view_layer.update();stats=F.evaluated_stats(F.COMPONENTS)
 bpy.ops.file.pack_all();source=ROOT/'source'/(aid+'.blend');export=ROOT/'exports'/(aid+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
 # Evaluate and batch export copies only; editable source remains untouched.
 deps=bpy.context.evaluated_depsgraph_get();copies=[];bpy.ops.object.select_all(action='DESELECT')
 for ob in F.COMPONENTS:
  mesh=bpy.data.meshes.new_from_object(ob.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
  copy=bpy.data.objects.new('EXPORT_'+ob.name,mesh);bpy.context.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy();copies.append(copy);copy.select_set(True)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();visual=bpy.context.object;visual.name=aid+'_static_visual'
 for ob in bpy.context.scene.objects:
  if ob.type=='EMPTY':ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 (ROOT/(aid+'.manifest.json')).write_text(json.dumps({'catalogue_id':aid,'name':'Guest single rest bed' if places==1 else 'Guest double rest bed','source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','units':'metres','pivot':'floor centre; Blender +Z up, head +Y; GLB head -Z','source_sha256':sha(source),'export_sha256':sha(export),'dimensions_blender_xyz_m':stats['dimensions_m'],'evaluated_triangles':stats['triangles_evaluated'],'semantic_parts':len(F.COMPONENTS),'places_proposal':places,'status':'New editable component; no room, capacity, species or final art acceptance','reference':'Approved intimate/premium suite images; visual guidance only, no pixels copied','checks_pending':['Source/export roundtrip','Contact and declared dimensions','In-context visual review','Actor sleeping poses and collision']},indent=2)+'\n')
 print('GUEST_REST_AUTHORED',aid,stats['triangles_evaluated'])
