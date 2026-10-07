"""Deterministic isolated Quiet Grove successor; no retained source mutation."""
from pathlib import Path
import json,hashlib,math,copy
from collections import Counter
R=Path(__file__).resolve().parents[1]; W=R.parents[1]
P=R.parent/'outputs/sf_house_r002/PLAN.json'
B=W/'residential-batch-neighborhood-20261006/scale_domestic_r011'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P)=='d0bf2e894aa2347ff50ea8580f0ff1d94c16754708732bb7ac94357f61a5775a'
p=json.loads(P.read_text());old=json.loads((B/'RESIDENTIAL_500_CURRENT_APPLICATION.json').read_text()); ids={r['address'] for r in p['rooms']}
edges=[e for e in old['adjacency_edges'] if set(e)<=ids]
adj={a:set() for a in ids}
for a,b in edges:adj[a].add(b);adj[b].add(a)
# Include directly opposing doors and immediate same-bank neighbours even where a
# specialty reservation separates the source-supported room records.
for a in p['rooms']:
 for b in p['rooms']:
  if a['address']>=b['address'] or a['deck']!=b['deck']:continue
  ax,az=a['historical_door_marker_xz'];bx,bz=b['historical_door_marker_xz']
  if (abs(ax-bx)<.1 and abs(az-bz)<7.5) or (abs(ax-bx)>3 and abs(az-bz)<.1):
   adj[a['address']].add(b['address']);adj[b['address']].add(a['address'])
edges=sorted({tuple(sorted((a,b))) for a,vs in adj.items() for b in vs})
colors={}; source={r['address']:r for r in p['rooms']}
while len(colors)<len(ids):
 a=sorted(ids-set(colors),key=lambda a:(-len({colors[x] for x in adj[a] if x in colors}),-len(adj[a]),source[a]['census_source_index']))[0]
 preferred=(source[a]['census_source_index']//6+int(source[a]['deck'][1:]))%4
 allowed=[(preferred+i)%4 for i in range(4) if (preferred+i)%4 not in {colors[x] for x in adj[a] if x in colors}]
 assert allowed;colors[a]=allowed[0]
variants={};rows=[];provenance=[]
for r0 in sorted(p['rooms'],key=lambda x:x['census_source_index']):
 r=copy.deepcopy(r0); c=colors[r['address']]; design='staggered_side' if c<2 else 'opposed_retreats';hand=1 if c%2==0 else -1;cl=r['historical_class'];key=f'QG_r001__{cl}__{design}__'+('L' if hand==1 else 'R')
 if design=='staggered_side': beds=[(-1.56,5.80,math.pi/2),(-1.90,8.80,math.pi/2)]+([(1.90,6.65,0)] if cl=='family' else [])
 else: beds=[(-1.90,6.05,0),(1.90,7.05,0)]+([(-1.90,9.60,math.pi/2)] if cl=='family' else [])
 beds=[([round(hand*x,5),y,0],yaw*hand) for x,y,yaw in beds]
 # All furniture is a proper rigid transform; mirroring changes placement only,
 # never negatively scales an operable door or a retained source component.
 placements=[]
 def add(label,path,xyz,yaw=0,candidate=False):
  row={'label':label,'source_xyz':[round(float(v),6) for v in xyz],'source_yaw':yaw}
  if candidate:row.update(candidate_source=str(B/path),candidate_export=str((B/path).with_suffix('.glb')),catalogue_source=None)
  else:row['catalogue_source']=path
  placements.append(row)
 for i,(pt,yaw) in enumerate(beds):add('HistoricalBedAnchor_'+str(i),'assets/guest_rest/source/AST-SLP-001.blend',pt,yaw)
 add('GardenFacingSalonBench','assets/furniture/AST-FUR-001_day_window_bench.blend',(hand*1.7,10.7,0),math.pi)
 add('SharedTable','assets/furniture/AST-FUR-003_day_table.blend',(hand*1.7,11.8,0))
 add('WindowReadingChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-hand*1.9,11.65,0),hand*math.pi/2)
 for label,asset,pt in [('bath_vanity','001',(-3.44,3.1,0)),('bath_wc','002',(-2.8,.9,0)),('bath_shower','003',(-1.38,.905,0))]: add(label,'assets/guest_wash/source/AST-SAN-'+asset+'.blend',pt)
 add('EntryDoor','assets/guest_entry_door/source/AST-DOR-002.blend',(0,-.05,0))
 add('BathroomDoor','assets/guest_privacy_door/source/AST-DOR-001.blend',(-.7,2.9,0),math.pi/2)
 add('SuiteKitchenette','domestic_correction/outputs/kitchenette_r001/suite_kitchenette.blend',(3.025,1.4,0),-math.pi/2,True)
 def world(pt):
  x,y,z=pt; ox,oy,oz=r['source_origin_world_xyz'];a=r['source_yaw_godot'];return [round(ox+x*math.cos(a)-y*math.sin(a),6),round(oy+z,6),round(oz-x*math.sin(a)-y*math.cos(a),6)]
 newanchors=[];newbindings=[]
 for i,((pt,yaw),oldanchor,binding) in enumerate(zip(beds,r0['bed_anchors'],r0['anchor_bindings'])):
  assert oldanchor['historical_anchor_index']==i and binding['unit_anchor_index']==i and binding['prototype_anchor_index']==i
  nw=world(pt);prov={'source_index':r['census_source_index'],'unit_id':r['address'],'slot_id':binding['unit_slot_key'],'ordinal':i,'old_source_xyz':oldanchor['source_xyz'],'old_world_xyz':oldanchor['world_xyz'],'old_source_yaw':r0['component_placements'][i]['source_yaw'],'old_evidence':oldanchor['evidence'],'new_source_xyz':pt,'new_world_xyz':nw,'new_source_yaw':yaw,'coordinate_status':'Revised unregistered proposal; no historical anchor coordinate recovered','reason':'Quiet Grove protected retreat and window-side sitting composition'};provenance.append(prov)
  newanchors.append({'historical_anchor_index':i,'source_xyz':pt,'world_xyz':nw,'source_yaw':yaw,'evidence':prov['coordinate_status']})
  b=copy.deepcopy(binding);b.update(source_xyz=pt,world_xyz=nw,source_yaw=yaw,coordinate_evidence=prov['coordinate_status']);newbindings.append(b)
 r.update(quiet_grove_variant=key,quiet_grove_design=design,quiet_grove_handing=hand,source_recipe_key=key,prior_source_recipe_key=r0['source_recipe_key'],bed_anchors=newanchors,anchor_bindings=newbindings,component_placements=placements,view_policy='planned_authored_outlook',finished=False,instance_adoption_ready=False,runtime_enabled=False)
 r['source_shell']=f'outputs/source_r001/{key}/shell.glb';r['source_shell_sha256']=None;r['source_recipe_sha256']=None
 r['source_detail_props_layer']=None;r['source_props_variant']='Quiet Grove coordinated kit';r['props_variation_status']='No unsupported per-instance random prop promise'
 r['full_house_receiving_source']=str(P);r['receiving_geometry_status']='Actual full-house source garden/planting only; runtime and cross-court privacy unaccepted'
 r['privacy_acceptance']={'sealed_aperture_profile':'sealed_window_r010','shader_profile':'residential_privacy_v001','clear_inside_opaque_polished_outside_required':True,'new_variant_runtime_tested':False,'opposite_interiors_visible_allowed':False}
 rows.append(r)
 if key not in variants:
  v=copy.deepcopy(r);v.update(address=key,representative_unit_id=r['address'],representative_source_index=r['census_source_index'],layout='B_twin_retreat',palette='oatmeal',emphasize_ceiling_joinery=True,preserve_installed=False);variants[key]=v
result={'schema':'astraea.quiet_grove_interiors.v1','status':'83-unit source successor; not adopted','house_id':p['house_id'],'full_house_plan_sha256':sha(P),'counts':dict(Counter(r['historical_class'] for r in rows)),'unit_count':83,'rest_slot_count':len(provenance),'prototype_count':len(variants),'units':rows,'prototypes':list(variants.values()),'adjacency_edges':edges,'adjacency_pass':all(colors[a]!=colors[b] for a,b in edges),'whole_ship_capacity':'880 upper + 120 independent D04 = 1000 units; no change','specialty_vip_policy':'47 specialty + 17 VIP remain distinct reservations; no invented anatomy or scaled regular rooms','prior_proposal_coordinates_retained_in':'REST_SLOT_PROVENANCE.json','limits':['No Game/Catalogue writes or imports','No runtime door/cart/privacy acceptance','No retained room source overwritten','Both installed D13 pilots are outside this successor']}
assert len(rows)==83 and len(provenance)==215 and result['counts']=={'standard':34,'family':49}
assert len({x['slot_id'] for x in provenance})==215 and result['adjacency_pass']
(R/'QUIET_GROVE_83_PLACEMENT_MAP.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'REST_SLOT_PROVENANCE.json').write_text(json.dumps({'source_plan_sha256':sha(P),'coordinates_are_proposals':True,'rest_slot_identity_ordinal_and_count_unchanged':True,'rows':provenance},indent=2)+'\n')
refs=[Path('/workspace/shared/astraea-godot-production-20261003/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx'),Path('/workspace/shared/astraea-catalogue-continuation-20261002/references/intimate/image(20261002-000722).png'),Path('/workspace/shared/astraea-catalogue-continuation-20261002/references/dense/image(20261002-001051).png'),Path('/workspace/shared/astraea-catalogue-continuation-20261002/references/landings/guest_suite_hall.png'),W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png']
(R/'qa/REFERENCE_INSPECTION.json').write_text(json.dumps({'actual_docx_chapters_read':[5,6,32],'actual_full_image_pixels_inspected':True,'references':[{'path':str(x),'sha256':sha(x)} for x in refs],'design_translation':['Layered acoustic entry, tangible luggage/book storage and a genuinely separate sleep approach','Side-facing berths and window-side sitting from intimate image, distributed among coordinated plans rather than repeated everywhere','Warm curved ceiling hierarchy and practical recessed door from guest-suite hallway','Outside opacity is a required source/runtime material gate; visible opposite suite interiors in reference are not copied']},indent=2)+'\n')
print('PLAN_READY',len(rows),len(provenance),len(variants),len(edges),Counter(r['quiet_grove_variant'] for r in rows))
