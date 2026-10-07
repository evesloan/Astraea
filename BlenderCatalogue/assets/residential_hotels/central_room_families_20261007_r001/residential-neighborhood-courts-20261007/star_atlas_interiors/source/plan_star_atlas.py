"""Star Atlas residential source: exact identities, new authored library compositions."""
from pathlib import Path
import json,math,copy,hashlib
from collections import Counter
R=Path(__file__).resolve().parents[1];W=R.parents[1];B=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/'assemblies/GODOT_BATCH_INSTANCE_MAP.json';app=B/'RESIDENTIAL_500_CURRENT_APPLICATION.json';cw=W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';boundary=R.parent/'HOUSE_BUILD_BOUNDARIES.json'
old=[r for r in json.loads(source.read_text())['instances'] if r['house']=='port_central_upper_house'];cross={r['source_envelope_index']:r for r in json.loads(cw.read_text())['records']};house=next(h for h in json.loads(boundary.read_text())['physical_neighborhoods'] if h['physical_membership_id']=='port_central_upper_house')
assert len(old)==85
ids={r['address']for r in old};adj={a:set()for a in ids};by={r['address']:r for r in old}
for a,b in json.loads(app.read_text())['adjacency_edges']:
 if a in ids and b in ids:adj[a].add(b);adj[b].add(a)
for a in old:
 for b in old:
  if a['address']>=b['address'] or a['deck']!=b['deck']:continue
  ax,az=a['historical_door_marker_xz'];bx,bz=b['historical_door_marker_xz']
  if (abs(ax-bx)<.1 and abs(az-bz)<7.5)or(3<abs(ax-bx)<5 and abs(az-bz)<.1):adj[a['address']].add(b['address']);adj[b['address']].add(a['address'])
colors={}
while len(colors)<len(ids):
 a=sorted(ids-set(colors),key=lambda a:(-len({colors[x]for x in adj[a]if x in colors}),-len(adj[a]),by[a]['census_source_index']))[0];preferred=(by[a]['census_source_index']//6+int(by[a]['deck'][1:]))%4
 colors[a]=next(c for c in [(preferred+i)%4 for i in range(4)]if c not in {colors[x]for x in adj[a]if x in colors})
rows=[];prototypes={};provenance=[]
for r0 in sorted(old,key=lambda r:r['census_source_index']):
 r=copy.deepcopy(r0);color=colors[r['address']];h=1 if color%2==0 else -1;design='shelf_spine'if color<2 else'offset_index';cl=r['historical_class'];key=f'SA_r001__{cl}__{design}__'+('L'if h==1 else'R')
 if design=='shelf_spine':beds=[(-1.65,8.80,0),(1.65,8.80,0)]+([(-1.45,5.95,math.pi/2)]if cl=='family'else[])
 else:beds=[(-1.80,7.80,math.pi/2),(1.95,9.70,-math.pi/2)]+([(-1.95,9.70,math.pi/2)]if cl=='family'else[])
 beds=[([round(h*x,5),y,0],yaw*h)for x,y,yaw in beds];placements=[]
 def add(label,path,point,yaw=0,candidate=False):
  v={'label':label,'source_xyz':list(point),'source_yaw':yaw}
  if candidate:v.update(candidate_source=str(B/path),candidate_export=str((B/path).with_suffix('.glb')),catalogue_source=None)
  else:v['catalogue_source']=path
  placements.append(v)
 for i,(pt,yaw)in enumerate(beds):add('HistoricalBedAnchor_'+str(i),'assets/guest_rest/source/AST-SLP-001.blend',pt,yaw)
 if cl=='family':add('AtlasOutlookBench','assets/furniture/AST-FUR-001_day_window_bench.blend',(h*1.55,11.65,0),math.pi)
 else:add('AtlasOutlookChairEast','assets/furniture/AST-FUR-002_day_reading_chair.blend',(h*1.65,11.65,0),math.pi)
 add('AtlasOutlookChairWest','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*1.65,11.65,0),math.pi)
 add('AtlasSharedTable','assets/furniture/AST-FUR-003_day_table.blend',(0,10.85,0))
 wp=(h*1.1,5.18,0)if design=='shelf_spine'else(h*1.70,5.82,0)
 add('AtlasWritingChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',wp,h*math.pi/2 if design=='shelf_spine'else 0)
 for label,asset,pt in [('bath_vanity','001',(-3.44,3.1,0)),('bath_wc','002',(-2.8,.9,0)),('bath_shower','003',(-1.38,.905,0))]:add(label,'assets/guest_wash/source/AST-SAN-'+asset+'.blend',pt)
 add('EntryDoor','assets/guest_entry_door/source/AST-DOR-002.blend',(0,-.05,0));add('BathroomDoor','assets/guest_privacy_door/source/AST-DOR-001.blend',(-.7,2.9,0),math.pi/2)
 add('SuiteKitchenette','domestic_correction/outputs/kitchenette_r001/suite_kitchenette.blend',(3.025,1.4,0),-math.pi/2,True)
 def world(pt):
  x,y,z=pt;ox,oy,oz=r['source_origin_world_xyz'];a=r['source_yaw_godot'];return[round(ox+x*math.cos(a)-y*math.sin(a),6),round(oy+z,6),round(oz-x*math.sin(a)-y*math.cos(a),6)]
 newanchors=[];newbindings=[];cr=cross[r['census_source_index']]
 assert cr['historical_bed_anchor_markers']==[],'Recovered historical coordinates require a dedicated unchanged recipe'
 assert cr['proposed_rest_slot_ids']==[b['unit_slot_key']for b in r0['anchor_bindings']]
 for i,((pt,yaw),oa,ob)in enumerate(zip(beds,r0['bed_anchors'],r0['anchor_bindings'])):
  assert oa['evidence']=='explicit proposed rest placement; count and allocation are historical, original coordinate unknown'
  assert oa['historical_anchor_index']==ob['unit_anchor_index']==ob['prototype_anchor_index']==i
  nw=world(pt);status='Revised unregistered proposal; historical coordinate unknown'
  provenance.append({'source_index':r['census_source_index'],'unit_id':r['address'],'slot_id':ob['unit_slot_key'],'ordinal':i,'old_source_xyz':oa['source_xyz'],'old_world_xyz':oa['world_xyz'],'old_source_yaw':r0['component_placements'][i]['source_yaw'],'old_evidence':oa['evidence'],'new_source_xyz':pt,'new_world_xyz':nw,'new_source_yaw':yaw,'coordinate_status':status,'reason':'Star Atlas shaped library/writing edge, separated sleep approaches and outward sitting'})
  newanchors.append({'historical_anchor_index':i,'source_xyz':pt,'world_xyz':nw,'source_yaw':yaw,'evidence':status});v=copy.deepcopy(ob);v.update(source_xyz=pt,world_xyz=nw,source_yaw=yaw,coordinate_evidence=status);newbindings.append(v)
 r.update(star_atlas_variant=key,star_atlas_design=design,star_atlas_handing=h,adjacency_color=color,source_recipe_key=key,prior_source_recipe_key=r0['source_recipe_key'],bed_anchors=newanchors,anchor_bindings=newbindings,component_placements=placements,view_policy='planned_authored_outlook',finished=False,instance_adoption_ready=False,runtime_enabled=False)
 r.update(source_shell=f'outputs/source_r001/{key}/shell.glb',source_shell_sha256=None,source_recipe_sha256=None,source_detail_props_layer=None,source_props_variant='Star Atlas authored composition',props_variation_status='Deterministic eight-source mapping; no random prop promise')
 r['privacy_acceptance']={'finite_sealed_profile':'sealed_window_r010','opaque_exterior_clear_interior_required':True,'whole_room_runtime_accepted':False,'view_class_retained':True}
 rows.append(r)
 if key not in prototypes:
  cfg=copy.deepcopy(r);cfg.update(address=key,representative_unit_id=r['address'],representative_source_index=r['census_source_index'],layout='C_gathering_gallery',palette='clay',emphasize_ceiling_joinery=True,preserve_installed=False);prototypes[key]=cfg
edges=sorted({tuple(sorted((a,b)))for a,v in adj.items()for b in v})
result={'schema':'astraea.star_atlas_interiors.v1','status':'85-unit source successor; not runtime adopted','house_id':'port_central_upper_house','source_map_sha256':sha(source),'current_application_sha256':sha(app),'explicit_1296_binding_check_sha256':sha(B/'qa/EXPLICIT_1296_ANCHOR_BINDINGS.json'),'counts':dict(Counter(r['historical_class']for r in rows)),'unit_count':85,'rest_slot_count':221,'prototype_count':len(prototypes),'units':rows,'prototypes':list(prototypes.values()),'adjacency_edges':edges,'adjacency_pass':all(colors[a]!=colors[b]for a,b in edges),'view_classes':dict(Counter(r['view_target_family']for r in rows)),'whole_house_scope':{'total':148,'supported_now':85,'D17_standards_separate_fit':10,'specialty_unbuilt':46,'VIP_unbuilt':7},'whole_ship_units_unchanged':1000,'independent_D04_units':120,'installed_pilots_preserved_outside_this_house':[16,40],'known_historical_anchor_coordinates_changed':0,'existing_public_architecture_replaced':False}
assert result['counts']=={'standard':34,'family':51}and len(provenance)==221 and len(prototypes)==8 and result['adjacency_pass']
assert len({p['slot_id']for p in provenance})==221
(R/'STAR_ATLAS_85_PLACEMENT_MAP.json').write_text(json.dumps(result,indent=2)+'\n');(R/'REST_SLOT_PROVENANCE.json').write_text(json.dumps({'source_map_sha256':sha(source),'identity_ordinal_count_unchanged':True,'rows':provenance},indent=2)+'\n')
refs=[G/'docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',C/'references/intimate/image(20261002-000722).png',C/'references/dense/image(20261002-001051).png',C/'references/landings/guest_suite_hall.png',C/'references/library/image(20261001-191914).png',W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png']
owners={str(G/p):sha(G/p)for p in house['preserved_existing_owners']}
assert all(owners[str(G/p)]==h for p,h in house['preserved_existing_owners'].items())
(R/'qa/REFERENCE_INSPECTION.json').write_text(json.dumps({'actual_docx_chapters_personally_read':[5,6,32],'actual_full_pixels_personally_inspected':True,'references':[{'path':str(p),'sha256':sha(p)}for p in refs],'owners_read_and_protected':owners,'catalogue_architecture_source_read':{'path':str(C/'assets/star_atlas_architecture/source/build_star_atlas_architecture.py'),'sha256':sha(C/'assets/star_atlas_architecture/source/build_star_atlas_architecture.py')},'design_translation':['Fanning lowered reading canopy and shaped writing/browsing edge translate the actual library architecture at domestic scale','Usable deep shelving, book pockets and luggage storage have actual depth and reachable fronts','Purposeful window-side sitting separated from two or three actual rest approaches','Warm timber, patterned textiles, restrained metal and local task fixtures use retained materials','Visible opposite interiors in reference art are not an accepted privacy condition; r010 detail evidence is reused only within its scope']},indent=2)+'\n')
print('STAR_ATLAS_PLAN_READY',len(rows),len(provenance),len(prototypes),len(edges),result['view_classes'])
