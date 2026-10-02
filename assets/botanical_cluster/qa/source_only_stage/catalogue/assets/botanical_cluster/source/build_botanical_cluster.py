"""Three original intentionally arranged botanical components; Blender 4.3.2.
Source authoring is script-assisted, with named editable meshes and parameters.
Run: blender -b -t 2 --python-exit-code 1 --python this_file
No game/host/biology/species/load/wind acceptance is implied.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for sub in ('source','exports','qa'):(BASE/sub).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('botanical_materials',CAT/'standards/botanical_materials.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS=mod.materials()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(p):return [float(x)for x in p]
def glb(p):return [p[0],p[2],-p[1]]
def reset(ident):
 global PARTS,JOINS,MARKERS,COLL,PATHS,ROOT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];JOINS=[];MARKERS=[];COLL=[];PATHS={}
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['placement_datum']='Soil plane Z0; negative Z is intentional only on trailing foliage';ROOT['source_to_glb']='(x,y,z) -> (x,z,-y)';ROOT['front_source']=[0,-1,0];ROOT['front_native_glb']=[0,0,1]
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident
 sc['scope']='Original partial planted commons edge component; no recovered ship or biological suitability claim'

def mesh(name,verts,faces,role,thin=False,uvs=None):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
 if not thin:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;me.materials.append(MATS[role]);ob['material_role']=role;ob['surface_kind']='open_folded_surface'if thin else 'closed_support';ob['provenance']='Original deterministic script-assisted design';ob['collision_treatment']='decorative_noncolliding' if thin else 'only_when_listed_in_collision_proposal'
 uv=me.uv_layers.new(name='botanical_shape_uv');uv.active_render=True;scale=MATS[role].get('meters_per_tile_uv',(.4,.4))
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in f.loop_indices:
   vi=me.loops[li].vertex_index;p=me.vertices[vi].co;uv.data[li].uv=uvs[vi]if uvs else (p[axes[0]]/scale[0],p[axes[1]]/scale[1])
 PARTS.append(ob);return ob

def tube(name,points,radii,role='botanical_bark',sides=8,flat=False,collide=False):
 pp=[Vector(p)for p in points];vs=[];faces=[];rings=[]
 for i,(p,r)in enumerate(zip(pp,radii)):
  if flat:u,v=Vector((1,0,0)),Vector((0,1,0))
  else:
   t=(pp[min(i+1,len(pp)-1)]-pp[max(i-1,0)]).normalized();seed=Vector((0,0,1))if abs(t.z)<.85 else Vector((1,0,0));u=t.cross(seed).normalized();v=t.cross(u)
  ring=[p+r*(u*math.cos(2*math.pi*j/sides)+v*math.sin(2*math.pi*j/sides))for j in range(sides)];rings.append(ring);vs.extend(ring)
 for i in range(len(pp)-1):faces += [(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j)for j in range(sides)]
 faces +=[tuple(reversed(range(sides))),tuple((len(pp)-1)*sides+j for j in range(sides))]
 ob=mesh(name,vs,faces,role);ob['centerline_source_m']=json.dumps([xyz(p)for p in pp]);ob['radii_m']=json.dumps(radii);PATHS[name]=(pp,radii)
 # Side UV follows the real path distance; caps retain planar UVs.
 uv=ob.data.uv_layers.active;scale=MATS[role].get('meters_per_tile_uv',(.4,.4));lengths=[0]
 for a,b in zip(pp,pp[1:]):lengths.append(lengths[-1]+(b-a).length)
 for f in ob.data.polygons:
  if f.index>=(len(pp)-1)*sides:continue
  edge=f.index%sides
  for li in f.loop_indices:
   k,j=divmod(ob.data.loops[li].vertex_index,sides);j=sides if edge==sides-1 and j==0 else j;uv.data[li].uv=(2*math.pi*radii[k]*j/sides/scale[0],lengths[k]/scale[1])
 if collide:
  for i in range(len(pp)-1):
   ps=[xyz(p)for p in rings[i]+rings[i+1]];COLL.append({'name':name+'_segment_'+str(i+1),'type':'convex_hull_points','points_source_m':ps,'points_gltf_m':[glb(p)for p in ps],'covered_parts':[name],'approximation_note':'Local closed tapered stem segment; convex hull bridges only the two authored rings. No foliage AABB. Quantified by profile QA.'})
 return ob

def joint(child,parent,p,kind='buried_attachment'):
 JOINS.append({'name':child+'_to_'+parent,'child':child,'parent':parent,'parts':[child,parent],'probe_source_m':xyz(p),'probe_gltf_m':glb(p),'kind':kind,'check':'Probe is on child attachment surface and on or inside closed parent; every mesh has a path to root crown'})

def marker(name,p,part=None,normal=None,kind='physical_soil_contact',description=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o.location=p;o.empty_display_size=.035;o['marker_kind']=kind;o['physical_part']=part or '';o['source_position_m']=p;o['gltf_position_m']=glb(p)
 r={'name':name,'kind':kind,'source_m':p,'gltf_m':glb(p),'physical_part':part,'description':description}
 if normal:r.update(normal_source=normal,normal_gltf=glb(normal));o['normal_source']=normal;o['normal_gltf']=glb(normal)
 MARKERS.append(r)

def leaf(name,base,direction,length,width,rise,arch,fold,role='botanical_leaf_jade'):
 b=Vector(base);di=Vector(direction).normalized();side=Vector((-di.y,di.x,0)).normalized();up=Vector((0,0,1));ts=[.18,.43,.70,.89];us=[-1,0,1]
 def center(t):return b+di*(length*t)+up*(rise*t+arch*math.sin(math.pi*t))
 vs=[b];uvs=[(.5,0)];rows=[]
 for t in ts:
  rows.append(list(range(len(vs),len(vs)+3)))
  for u in us:vs.append(center(t)+side*(u*width*.5*math.sin(math.pi*t)**.78)+up*(abs(u)*fold*math.sin(math.pi*t)));uvs.append((.5+.5*u,t))
 tip=len(vs);vs.append(center(1));uvs.append((.5,1));faces=[(0,rows[0][1],rows[0][0]),(0,rows[0][2],rows[0][1])]
 for a,c in zip(rows,rows[1:]):faces.extend([(a[0],a[1],c[1],c[0]),(a[1],a[2],c[2],c[1])])
 faces.extend([(rows[-1][0],rows[-1][1],tip),(rows[-1][1],rows[-1][2],tip)])
 # Reverse parameter ordering so foliage top has +Z component.
 faces=[tuple(reversed(f))for f in faces];ob=mesh(name,vs,faces,role,True,uvs);ob['leaf_base_source_m']=xyz(base);ob['shape_controls']=json.dumps(dict(length=length,width=width,rise=rise,arch=arch,fold=fold));return ob

def fan(name,base,azimuth,pitch,radius,half_angle,pleat,role):
 b=Vector(base);az=math.radians(azimuth);pi=math.radians(pitch);out=Vector((math.cos(az),math.sin(az),0));axis=out*math.cos(pi)+Vector((0,0,1))*math.sin(pi);side=Vector((-math.sin(az),math.cos(az),0));normal=side.cross(axis).normalized();n=12
 vs=[b];uvs=[(.5,0)];rows=[]
 for t in(.26,.61,1):
  row=[]
  for j in range(n+1):
   a=math.radians(-half_angle+2*half_angle*j/n);rr=radius*t*(1 if j%2==0 else (.94 if t==1 else 1));p=b+(axis*math.cos(a)+side*math.sin(a))*rr+normal*(pleat*t*(1 if j%2==0 else -.28));row.append(len(vs));vs.append(p);uvs.append((j/n,t))
  rows.append(row)
 faces=[(0,rows[0][j],rows[0][j+1])for j in range(n)]
 for a,c in zip(rows,rows[1:]):faces.extend((a[j],c[j],c[j+1],a[j+1])for j in range(n))
 ob=mesh(name,vs,faces,role,True,uvs);ob['shape_controls']=json.dumps(dict(azimuth=azimuth,pitch=pitch,radius=radius,half_angle=half_angle,pleat=pleat));ob['leaf_base_source_m']=xyz(base);return ob

def make_fan_crown():
 tube('joined_root_crown',[(0,0,0),(0,0,.07),(0,0,.15)],[.17,.155,.11],sides=12,flat=True,collide=True)
 paths={
 'left_lift_stem':([(0,0,.08),(-.11,-.015,.48),(-.25,.03,1.04),(-.34,.06,1.51)],[.069,.055,.038,.021]),
 'rear_high_stem':([(0,.015,.10),(.035,.08,.60),(.02,.16,1.24),(.05,.21,1.93)],[.061,.047,.031,.016]),
 'right_outward_stem':([(.025,-.015,.09),(.15,-.035,.54),(.31,-.035,1.12),(.39,-.01,1.60)],[.064,.050,.035,.018])}
 for name,(ps,rs)in paths.items():tube(name,ps,rs,collide=True);joint(name,'joined_root_crown',ps[0])
 layout=[
 ('left_lift_stem',2,195,36,.28,.19,.67,64,.040,'jade'),
 ('right_outward_stem',2,-20,31,.28,.21,.68,67,.045,'sage'),
 ('left_lift_stem',3,155,48,.27,.12,.65,69,.041,'sage'),
 ('rear_high_stem',2,75,48,.26,.19,.68,66,.040,'jade'),
 ('right_outward_stem',3,-52,52,.26,.10,.66,64,.037,'jade'),
 ('rear_high_stem',3,52,50,.17,.05,.60,63,.037,'sage'),
 ('left_lift_stem',3,-122,63,.17,.10,.62,60,.037,'olive'),
 ('right_outward_stem',3,22,58,.20,.10,.65,62,.038,'olive'),
 ('rear_high_stem',3,150,72,.13,.04,.60,54,.035,'jade')]
 for i,(parent,k,az,pitch,reach,rise,radius,ang,pleat,col)in enumerate(layout,1):
  p=Vector(paths[parent][0][k]);a=math.radians(az);out=Vector((math.cos(a),math.sin(a),0));base=p+out*reach+Vector((0,0,rise));pet='fan_petiole_%02d'%i;tube(pet,[p,p+out*(reach*.55)+Vector((0,0,rise*.6)),base],[.018,.014,.007],'botanical_leaf_olive',7);joint(pet,parent,p)
  n='pleated_fan_%02d'%i;fan(n,base,az,pitch,radius,ang,pleat,'botanical_leaf_'+col);joint(n,pet,base,'fan_base_on_petiole_cap')
 marker('SOIL_ROOT_CONTACT',[0,0,0],'joined_root_crown',[0,0,-1]);marker('SOIL_ORIGIN',[0,0,0],kind='placement_origin')
 return {'root_reservation_polygon_source_xy':[[-.22,-.22],[.22,-.22],[.22,.22],[-.22,.22]],'root_reservation_diameter_m':.44,'actual_root_contact_radius_m':.17,'root_below_soil_not_modelled':True,'suggested_spatial_soil_depth_m':.26,'design_intent':'Three visible joined stems and nine pleated fans; lower stem zone remains legible','headroom_claim':False}

def interp(points,index,t):return Vector(points[index]).lerp(Vector(points[index+1]),t)
def make_trailing():
 tube('trailing_root_crown',[(0,0,0),(0,0,.035),(0,.015,.075)],[.085,.08,.045],sides=10,flat=True,collide=True)
 specs=[('left_short',-.24,.69,-.24),('left_long',-.14,.79,-.57),('central_mid',.015,.84,-.42),('right_long',.15,.76,-.53),('right_short',.27,.67,-.16)]
 paths={}
 for i,(tag,x,y,endz)in enumerate(specs):
  ps=[(0,0,.035),(x*.35,.15,.18),(x*.66,.33,.19),(x*.92,.48,.12),(x,y-.09,endz*.37),(x*.92,y,endz)];rs=[.016,.014,.011,.009,.007,.004];name='trailing_'+tag+'_vine';tube(name,ps,rs,'botanical_leaf_olive',7);joint(name,'trailing_root_crown',ps[0]);paths[name]=ps
  # Five unequal, hand-placed leaf pairs follow the rooted stem, not loose cards.
  for j,(seg,t)in enumerate([(0,.68),(1,.62),(2,.72),(3,.56),(4,.68)],1):
   p=interp(ps,seg,t);side=(-1 if(i+j)%2 else 1);d=Vector((side*.86,.36,0));base=p+d*.035+Vector((0,0,.009));pet=name+'_petiole_%02d'%j;tube(pet,[p,base],[.006,.0034],'botanical_leaf_olive',5);joint(pet,name,p)
   nameleaf=tag+'_folded_leaf_%02d'%j;leaf(nameleaf,base,d,.15 if j<4 else .13,.090 if j<3 else .073,-.045 if j>3 else .025,.035,.014,'botanical_leaf_'+('sage'if(i+j)%3==0 else 'jade'));joint(nameleaf,pet,base,'leaf_base_on_petiole_cap')
 marker('SOIL_ROOT_CONTACT',[0,0,0],'trailing_root_crown',[0,0,-1]);marker('SOIL_ORIGIN',[0,0,0],kind='placement_origin');marker('REARWARD_TRAIL_DIRECTION',[0,0,0],kind='placement_direction',description='Source +Y is rear maintenance direction, native GLB -Z')
 return {'root_reservation_polygon_source_xy':[[-.18,-.12],[.18,-.12],[.18,.17],[-.18,.17]],'actual_root_contact_radius_m':.085,'root_below_soil_not_modelled':True,'suggested_spatial_soil_depth_m':.20,'coping_crossing_local_y_m':[.20,.40],'coping_maximum_top_above_soil_m':.075,'crossing_rule':'Place root so local Y .20–.40 covers coping; verified all actual mesh undersides in crossing band','trail_direction_source':[0,1,0],'trail_direction_gltf':[0,0,-1],'negative_z_intent':'Unequal foliage and vine tails drop below soil behind rear coping; never place over seating or front approach'}

def make_flowering():
 tube('flower_bank_root_spine',[(-.25,0,.055),(0,0,.055),(.25,0,.055)],[.035,.038,.035],sides=8,collide=False)
 # Three soil-contact collars overlap the joined root spine. Root contact normal is -Z.
 groups=[(-.25,-.015),(.0,.025),(.25,-.01)]
 for i,(x,y)in enumerate(groups,1):
  n='basal_collar_%02d'%i;tube(n,[(x,y,0),(x,y,.035),(x,y,.07)],[.070,.073,.05],sides=10,flat=True,collide=True);joint(n,'flower_bank_root_spine',(x,y,.055));marker('SOIL_CONTACT_%02d'%i,[x,y,0],n,[0,0,-1])
  for j,(a,le,w,ri,ar)in enumerate([(172,.28,.086,.12,.14),(20,.28,.090,.11,.15),(-88,.24,.078,.13,.14),(96,.21,.070,.26,.10),(48,.24,.065,.36,.07)],1):
   aa=math.radians(a+(i-2)*13);base=(x,y,.05);nn='group_%02d_folded_strap_%02d'%(i,j);leaf(nn,base,(math.cos(aa),math.sin(aa),0),le,w,ri,ar,.024,'botanical_leaf_'+('sage'if j%3==0 else 'jade'));joint(nn,n,base,'strap_root_in_basal_collar')
 stalks=[(1,-.36,-.01,.84),(1,-.19,.045,1.045),(2,-.03,.10,1.11),(2,.09,-.035,.88),(3,.25,.035,1.015),(3,.40,-.01,.78)]
 for i,(g,x,y,h)in enumerate(stalks,1):
  gx,gy=groups[g-1];base=(gx,gy,.053);top=(x,y,h);ps=[base,((gx+x)*.5,(gy+y)*.5,h*.46),(x*.985,y*.98,h*.80),top];name='upright_flower_stalk_%02d'%i;tube(name,ps,[.012,.010,.007,.0045],'botanical_leaf_olive',7);joint(name,'basal_collar_%02d'%g,base)
  for j,(seg,t,ang)in enumerate([(1,.72,40+i*17),(2,.18,165+i*13),(2,.76,-50+i*11)],1):
   p=interp(ps,seg,t);a=math.radians(ang);di=Vector((math.cos(a),math.sin(a),0));tip=p+di*(.055 if j<3 else .033)+Vector((0,0,.025));ped='stalk_%02d_cluster_%02d_pedicel'%(i,j);tube(ped,[p,tip],[.0046,.003],'botanical_leaf_olive',5);joint(ped,name,p)
   recept=ped+'_calyx';tube(recept,[tip-Vector((0,0,.003)),tip+Vector((0,0,.005)),tip+Vector((0,0,.012))],[.004,.012,.008],'botanical_leaf_olive',6,True);joint(recept,ped,tip)
   for k in range(3):
    aa=a+math.radians(k*120);pb=tip+Vector((0,0,.006));pet='stalk_%02d_cluster_%02d_folded_petal_%d'%(i,j,k+1);leaf(pet,pb,(math.cos(aa),math.sin(aa),0),.051 if j!=2 else .057,.038,.025,.017,.010,'botanical_flower');joint(pet,recept,pb,'petal_root_in_calyx')
 marker('SOIL_ORIGIN',[0,0,0],kind='placement_origin')
 # Root spine deliberately roots through the centre collar: graph root remains the spine.
 return {'root_reservation_polygon_source_xy':[[-.40,-.16],[.40,-.16],[.40,.19],[-.40,.19]],'root_contact_collars':3,'root_below_soil_not_modelled':True,'suggested_spatial_soil_depth_m':.24,'design_intent':'Three connected basal groups; six unequal flowering uprights; fifteen folded strap leaves; eighteen three-petal clusters'}

def measure(obs):
 pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(p[k]for p in pts)for k in range(3)];hi=[max(p[k]for p in pts)for k in range(3)];tri=0
 for o in obs:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident):
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in PARTS:o.select_set(True)
 for m in MARKERS:bpy.data.objects[m['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/(ident+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)

def main():
 bpy.context.preferences.filepaths.save_version=0;records=[];collision={}
 for ident,title,fn,rootname in [('AST-BOT-007','Joined pleated fan crown',make_fan_crown,'joined_root_crown'),('AST-BOT-008','Rearward unequal trailing cluster',make_trailing,'trailing_root_crown'),('AST-BOT-009','Upright three-group flowering bank',make_flowering,'flower_bank_root_spine')]:
  reset(ident);placement=fn();bpy.context.view_layer.update();bounds,tri=measure(PARTS);foliage=[o for o in PARTS if o['surface_kind']=='open_folded_surface'];fb,ft=measure(foliage)
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  source=BASE/'source'/(ident+'.blend');out=BASE/'exports'/(ident+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);export(ident)
  rec={'catalogue_id':ident,'title':title,'unique_design':True,'original_script_assisted_design':True,'units':'metres','source':str(source.relative_to(BASE)),'export':str(out.relative_to(BASE)),'generator':'source/build_botanical_cluster.py','source_sha256':sha(source),'glb_sha256':sha(out),'generator_sha256':sha(Path(__file__)),'coordinates':{'source':'X right, Y depth/rear, Z up; front -Y','native_glb':'X right, Y up, Z forward; front +Z','mapping':'(x,y,z)->(x,z,-y)','pivot_source_m':[0,0,0],'pivot_native_glb_m':[0,0,0],'datum':'soil plane; trailing asset intentionally extends below soil'},'bounds_blender_z_up':bounds,'foliage_bounds_blender_z_up':fb,'lowest_foliage_z_m':fb['min_m'][2],'evaluated_triangles':tri,'foliage_triangles':ft,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'root_graph_part':rootname,'material_roles':sorted(set(o['material_role']for o in PARTS)),'material_alpha':'OPAQUE, all existing original botanical roles unchanged','two_sided_roles':[r for r in sorted(set(o['material_role']for o in PARTS))if not MATS[r].use_backface_culling],'thin_surface_treatment':'Intentionally open shaped folded leaves/petals; opaque two-sided material. Supports closed. No alpha cards or enclosing foliage hull.','runtime_semantics':'Named semantic part nodes and original editable source; static component export, no batching or game performance acceptance','physical_and_proposal_markers':MARKERS,'joins':JOINS,'planting_and_placement':placement,'collision_proposal_file':'collision_proposals.json','collision_proposal_count':len(COLL),'reference_manifest':'../../batches/batch13/reference_manifest.json','limitations':['Proposed components only, no recovered host/room/deck geometry','Soil/root reservation and depth are spatial proposals, no biological/species/irrigation/load claim','No engine, actor, collision behavior, wind, LOD or target-PC acceptance','Foliage decorative non-colliding; no foliage AABB as collision','Standing/seated outlook and maintenance clearances require the recorded relative arrangement']}
  (BASE/(ident+'.manifest.json')).write_text(json.dumps(rec,indent=2)+'\n');records.append(rec);collision[ident]={'proposal_only':True,'frame':'Blender source metres plus explicit native GLB points','shapes':COLL,'leaves_and_fine_petiole_collision':'none','not_claimed':'Physics behavior, mesh batching or game performance'}
 (BASE/'manifest.json').write_text(json.dumps({'family':'Joined botanical cluster silhouettes','unique_design_count':3,'assets':records},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n')
 print('BOTANICAL_CLUSTER_BUILT',[(r['catalogue_id'],r['bounds_blender_z_up'],r['evaluated_triangles'])for r in records])
if __name__=='__main__':main()
