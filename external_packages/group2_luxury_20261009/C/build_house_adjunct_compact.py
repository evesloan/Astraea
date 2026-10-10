"""Private house entry/gallery adjuncts; explicit proposals, never public commons."""
import bpy,bmesh,pathlib,json,hashlib,math,sys,gzip,collections,itertools
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));from glb_tools import read_glb,projected_grid,route_check
from source_paths import inside_polygon
from editable_label import repair_label
house=sys.argv[sys.argv.index('--')+1];cross=json.loads((R/'EXCLUSIVE_FACILITIES_CROSSWALK.json').read_text());proposal=next(x for x in cross['source_proposals'] if x['house']==house)
assert not proposal['programme_claim_intersections'] and not proposal['actual_retained_tidal_triangle_intersections']
precise=next(x for x in json.loads((R/'EXCLUSIVE_FACILITIES_PRECISE_LINE_SCREEN.json').read_text())['records'] if x['house']==house)
assert not precise['actual_triangles_or_degenerate_projected_lines_touching'],'Retained actual geometry conflict: hold adjunct without modifying neighbour'
O=R/'facilities'/house;O.mkdir(parents=True,exist_ok=True);assert not (O/'house_adjunct.blend').exists(),'Preserve previous source attempt'
seed=R/'build_first_deluxe.py';seed_sha=hashlib.sha256(seed.read_bytes()).hexdigest();exec(compile(seed.read_text().split('# Weighted compartment envelope')[0],str(seed),'exec'),globals())
O=R/'facilities'/house;poly=proposal['source_proposal_boundary'];xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly);zmin=min(p[1] for p in poly);zmax=max(p[1] for p in poly);star=xmin>0;depth=xmax-xmin;length=zmax-zmin
origin=[xmin if star else xmax,102,zmax if star else zmin];ua=1 if star else -1;va=-1 if star else 1

def xyz(u,v,h):return Vector((origin[0]+ua*u,-origin[2]-va*v,102+h))
def w(u,v,h=0):return [origin[0]+ua*u,102+h,origin[2]+va*v]
def put(aid,u,v,h=0,yaw=0,label=None):return asset(aid,u,v,h,yaw-(math.pi if star else 0),label)
# A quiet resting bay looks across the broad arrival/service spine. The
# fitted fan-shaped cover bears on outer backing and two inner posts.
box('QuietGalleryBacking',depth-.30,depth-.10,length*.20,length*.75,0,3.05,'ivory_enamel','privacy')
fan=[(depth-4.5,length*.25),(depth-.30,length*.20),(depth-.30,length*.75),(depth-4.5,length*.65)]
prism('QuietFanCover',fan,3.05,3.23,'ivory_enamel','cover')
for j,v in enumerate([length*.25,length*.65]):box(f'FanBearingPost{j}',depth-4.50,depth-4.30,v-.08,v+.08,0,3.06,'warm_walnut','bearing')
box('FittedQuietBenchFoot',depth-1.70,depth-.45,length*.28,length*.65,0,.34,'warm_walnut','quiet_rest')
box('FittedQuietBenchCushion',depth-1.74,depth-.45,length*.28,length*.65,.34,.50,'teal_weave','quiet_rest')
box('FittedQuietBenchBack',depth-.64,depth-.45,length*.28,length*.65,.50,1.18,'oatmeal_weave','quiet_rest')
put('AST-FUR-003',depth-3.0,length*.43,0,0,'QuietSideTable')
put('AST-BOT-002',depth-2.1,length*.83,.14,0,'GalleryPlant')
box('GalleryPlantPlinth',depth-2.65,depth-1.55,length*.83-.38,length*.83+.40,0,.14,'warm_stone','plant_support')
# Open privacy returns leave the centre spine available to both guests and
# care carts; clean/used-care storage stays in a separate end pocket.
for j,v in enumerate([length*.30,length*.58]):
 box(f'InnerPrivacyReturn{j}',.25,1.80,v-.08,v+.08,0,2.05,'warm_walnut','privacy')
 for k in range(4):box(f'InnerScreenSlat{j}_{k}',1.95+k*.28,2.04+k*.28,v-.065,v+.065,.15,2.05,'warm_walnut','privacy')
box('CareClosedStore',.45,1.45,length-2.30,length-.45,0,1.80,'ivory_enamel','care_service')
box('CareWorkBay',1.45,2.45,length-2.30,length-.45,0,.84,'warm_walnut','care_service')
box('CareStoneSurface',1.45,2.45,length-2.30,length-.45,.84,.90,'warm_stone','care_service')
box('CareCleanClosedInset',.46,1.44,length-2.315,length-2.30,.97,1.65,'teal_weave','care_service')
box('CareUsedReturnInset',.46,1.44,length-2.315,length-2.30,.15,.90,'dark_rubber','care_service')
# A cool task fixture bears on the care backing; no unsupported light geometry.
box('CareTaskBacking',.45,2.45,length-.40,length-.25,0,2.60,'ivory_enamel','care_service')
box('CareTaskArm',1.80,2.20,length-1.40,length-.25,2.30,2.40,'champagne_metal','fixture')
box('CareTaskLens',1.65,2.35,length-1.50,length-.90,2.22,2.32,'lens','fixture')
data=bpy.data.lights.new('CareTaskLight','AREA');data.energy=210;data.color=(.70,.85,1.0);data.size=1.6;ob=bpy.data.objects.new('CareTaskLight',data);scene.collection.objects.link(ob);ob.location=xyz(2.0,length-1.20,2.20)
# Built-in reading provision in the sheltered bay, kept off the broad spine.
box('QuietReadingShelf',depth-.64,depth-.38,length*.27,length*.40,1.45,1.53,'warm_walnut','reading')
put('AST-LIB-006',depth-.51,length*.335,1.53,math.pi/2,'QuietReadingStock')
fixture_u,fixture_v=depth-2.50,length*.47
mount=box('GalleryOpal_Bracket',fixture_u-.09,fixture_u+.09,fixture_v-.09,fixture_v+.09,2.91,3.075,'champagne_metal','fixture');mount['source_mount_target']='QuietFanCover'
box('GalleryOpal_Lens',fixture_u-.22,fixture_u+.22,fixture_v-.22,fixture_v+.22,2.87,2.925,'lens','fixture')
data=bpy.data.lights.new('GalleryOpal','AREA');data.energy=240;data.color=(1,.78,.53);data.size=1.6;ob=bpy.data.objects.new('GalleryOpal',data);scene.collection.objects.link(ob);ob.location=xyz(fixture_u,fixture_v,2.83)
entry_v=min(2.6,length*.15)
marker('entry',1.2,entry_v,0,'existing_RMB_focus_E_adoption_only');marker('care_interface',3.2,length-1.4,0,'source_service_interface_proposal')
label=bpy.data.curves.new('HouseLabel','FONT');label.body=house.replace('_upper_house','').replace('_',' ').title();label.size=.13;label.extrude=.001;label.materials.append(mats['champagne_metal']);ob=bpy.data.objects.new('HouseLabel',label);scene.collection.objects.link(ob);ob.location=xyz(.27,length*.30,1.55);ob.rotation_euler=(math.pi/2,0,math.pi/2 if star else -math.pi/2);repair_label(ob);parts.append(ob)
for ob in parts:
 ob['source_scope']='Group2/'+house
 if 'source_envelope_index' in ob:del ob['source_envelope_index']
scene.cycles.samples=4
preview=box('PREVIEW_ROOT_RECEIVER',.01,depth-.01,.01,length-.01,-.18,0,'warm_stone','preview');parts.remove(preview)
# Exact retained context is preview-only and makes no new opening claim.
before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb'));context=set(scene.objects)-before
cam=bpy.data.objects.new('QA_EyeCamera',bpy.data.cameras.new('QA_EyeCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.lens=20;cam.data.clip_start=.05;cam.data.clip_end=100
views=[]
for name,at,to in [('arrival',(1.8,1.2,1.65),(depth-1.1,length*.45,1.3)),('quiet_gallery',(4.0,length*.43,1.65),(depth-.55,length*.47,1.2)),('care_threshold',(3.8,length-3.2,1.65),(1.45,length-2.1,1.1)),('privacy_return',(4.0,length-1.0,1.65),(1.1,length*.38,1.25))]:
 cam.location=xyz(*at);cam.rotation_euler=(xyz(*to)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);views.append({'name':name,'file':name+'.png','sha256':sha(O/(name+'.png')),'camera_world_xyz':w(*at),'target_world_xyz':w(*to),'height_above_local_floor':1.65})
for ob in context:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);bpy.data.objects.remove(cam,do_unlink=True);scene.camera=None;bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
 if ob.type not in ['CAMERA','LIGHT']:ob.select_set(True)
native=O/'house_adjunct.blend';export=O/'house_adjunct.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
contract={'house':house,'status':'BUILT_CANDIDATE_PENDING_SAVED_QA_AND_ACTUAL_PIXELS','source_proposal':proposal,'boundary':poly,'floor_y':102,'roof_limit_y':105.3,'new_guest_units':0,'new_canonical_programme_keys':0,'Root_adoption_held':['Court/receiver floor and structural support','External house connections and service network','Existing RMB/E controllers and actual actor/cart acceptance'],'floor_proposal':{'boundary':poly,'floor_y':102,'thickness':.24,'owner':'Root','exported':False},'native_sha256':sha(native),'export_sha256':sha(export),'rebuild_recipe':pathlib.Path(__file__).name,'rebuild_source_sha256':sha(pathlib.Path(__file__)),'seed_sha256':seed_sha,'imports':imports,'source_views':views,'actual_pixel_review':False,'outside_window_claim':False}
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2))
# Independently reopen the actual saved native. Every evaluated vertex and
# retained bearing is checked; original catalogue files remain unchanged.
bpy.ops.wm.open_mainfile(filepath=str(native));dg=bpy.context.evaluated_depsgraph_get();rows=[];coords={};fail=[]
for ob in bpy.context.scene.objects:
 if ob.type not in ['MESH','FONT']:continue
 e=ob.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();pts=[e.matrix_world@v.co for v in me.vertices];world=[(v.x,v.z,-v.y) for v in pts]
 if not pts:e.to_mesh_clear();continue
 bad=sum(not inside_polygon(v[0],v[2],poly) or v[1]<101.9999 or v[1]>105.3001 for v in world);deg=sum((pts[t.vertices[1]]-pts[t.vertices[0]]).cross(pts[t.vertices[2]]-pts[t.vertices[0]]).length<1e-10 for t in me.loop_triangles)
 row={'name':ob.name,'bounds':[[min(v[k] for v in world) for k in range(3)],[max(v[k] for v in world) for k in range(3)]],'uv_layers':[v.name for v in me.uv_layers],'outside':bad,'degenerate':deg};rows.append(row);coords[ob.name]=world
 if bad or deg or not me.uv_layers or 'PREVIEW' in ob.name:fail.append(row)
 e.to_mesh_clear()
lookup={x['name']:x for x in rows};supports=[]
for imp in imports:
 if 'part_names' not in imp:continue
 group=[lookup[n] for n in imp['part_names'] if n in lookup];bottom=min(v['bounds'][0][1] for v in group);error=abs(bottom-imp['world_xyz'][1]);supports.append({'group':imp['part_names'][0],'bearing_y':bottom,'declared_y':imp['world_xyz'][1],'error_m':error})
 if error>.001:fail.append(supports[-1])
if any(not im.packed_file for im in bpy.data.images if im.type!='RENDER_RESULT'):fail.append({'unpacked_resources':True})
(O/'SAVED_NATIVE_VERTICES.json.gz').write_bytes(gzip.compress(json.dumps(coords,separators=(',',':')).encode(),mtime=0))
(O/'NATIVE_VERIFICATION.json').write_text(json.dumps({'status':'FAIL' if fail else 'PASS','native_sha256':sha(native),'mesh_rows':rows,'support_contacts':supports,'independent_reopen':True,'preview_floor_absent':True,'failures':fail},indent=2));assert not fail,'Saved facility source failed'
g,nodes=read_glb(export);fail=[];binsize=.0001
for n in nodes:
 if n['name'] not in coords:fail.append({'unexpected_export_mesh':n['name']});continue
 if n['normal_error']>1e-5 or 'PREVIEW' in n['name']:fail.append({'invalid_export':n['name']})
 for source,target in [(coords[n['name']],n['vertices']),(n['vertices'],coords[n['name']])]:
  bins=collections.defaultdict(list)
  for v in target:bins[tuple(math.floor(x/binsize) for x in v)].append(v)
  for v in source:
   q=tuple(math.floor(x/binsize) for x in v);error=min((math.dist(v,t) for off in itertools.product([-1,0,1],repeat=3) for t in bins.get(tuple(q[k]+off[k] for k in range(3)),[])),default=999)
   if error>.0001:fail.append({'vertex_parity':n['name'],'error':error});break
for name in coords:
 if name not in {n['name'] for n in nodes}:fail.append({'missing_export':name})
assert all('uri' not in x for x in g.get('buffers',[])+g.get('images',[]))
polys,grid=projected_grid(nodes,102.001,2.25);routes=[]
for name,pts,radius in [('arrival_cart',[(1.8,entry_v),(4.0,entry_v),(4.0,length-2.7)],.82),('quiet_body',[(4.0,length*.43),(depth-4.0,length*.43)],.38),('care_body',[(4.0,length-2.7),(3.2,length-1.4)],.38)]:
 path=[(w(u,v)[0],w(u,v)[2]) for u,v in pts];result=route_check(polys,grid,path,radius);result['name']=name;routes.append(result)
 if not result['passed']:fail.append({'route':name,'blocked':result['blocked']})
(O/'EXPORT_VERIFICATION.json').write_text(json.dumps({'status':'FAIL' if fail else 'PASS','native_sha256':sha(native),'export_sha256':sha(export),'actual_vertex_parity_checked':True,'routes':routes,'failures':fail,'scope':'Actual source geometry only, not installed Godot or species/capacity acceptance'},indent=2));assert not fail,'Raw facility export failed';print('HOUSE ADJUNCT SOURCE QA PASS',house,flush=True)
