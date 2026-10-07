"""Deterministic Tidal Garden successor; preserve identities and retained files."""
from pathlib import Path
import json,hashlib,math,copy
from collections import Counter
R=Path(__file__).resolve().parents[1];W=R.parents[1]
B=W/'residential-batch-neighborhood-20261006/scale_domestic_r011'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/'assemblies/GODOT_BATCH_INSTANCE_MAP.json';p=json.loads(source.read_text())
old=[r for r in p['instances'] if r['house']=='port_forward_upper_house'];assert len(old)==85
ids={r['address']for r in old};adj={a:set()for a in ids};by={r['address']:r for r in old}
for a in old:
 for b in old:
  if a['address']>=b['address'] or a['deck']!=b['deck']:continue
  ax,az=a['historical_door_marker_xz'];bx,bz=b['historical_door_marker_xz']
  if (abs(ax-bx)<.1 and abs(az-bz)<7.5)or(abs(ax-bx)>3 and abs(az-bz)<.1):adj[a['address']].add(b['address']);adj[b['address']].add(a['address'])
colors={}
while len(colors)<len(ids):
 a=sorted(ids-set(colors),key=lambda a:(-len({colors[x]for x in adj[a]if x in colors}),-len(adj[a]),by[a]['census_source_index']))[0]
 preferred=(by[a]['census_source_index']//6+int(by[a]['deck'][1:]))%4
 colors[a]=next(c for c in [(preferred+i)%4 for i in range(4)]if c not in {colors[x]for x in adj[a]if x in colors})
rows=[];prototypes={};provenance=[]
for r0 in sorted(old,key=lambda r:r['census_source_index']):
 r=copy.deepcopy(r0);color=colors[r['address']];h=1 if color%2==0 else -1;design='broad_salon'if color<2 else'crescent_salon';cl=r['historical_class'];key=f'TG_r001__{cl}__{design}__'+('L'if h==1 else'R')
 if design=='broad_salon':beds=[(-1.62,6.30,0),(1.62,6.70,0)]+([(-1.68,9.10,math.pi/2)]if cl=='family'else[])
 else:beds=[(-1.45,6.10,math.pi/2),(-1.75,8.60,math.pi/2)]+([(1.70,6.70,0)]if cl=='family'else[])
 beds=[([round(h*x,5),y,0],yaw*h)for x,y,yaw in beds];placements=[]
 def add(label,path,point,yaw=0,candidate=False):
  v={'label':label,'source_xyz':list(point),'source_yaw':yaw}
  if candidate:v.update(candidate_source=str(B/path),catalogue_source=None)
  else:v['catalogue_source']=path
  placements.append(v)
 for i,(pt,yaw)in enumerate(beds):add('HistoricalBedAnchor_'+str(i),'assets/guest_rest/source/AST-SLP-001.blend',pt,yaw)
 add('TidalWindowBench','assets/furniture/AST-FUR-001_day_window_bench.blend',(h*1.45,10.60,0),math.pi)
 add('TidalSalonTable','assets/furniture/AST-FUR-003_day_table.blend',(h*1.45,11.74,0))
 add('TidalOutlookChair','assets/furniture/AST-FUR-002_day_reading_chair.blend',(-h*1.90,11.54,0),h*math.pi/2)
 for label,asset,pt in [('bath_vanity','001',(-3.44,3.1,0)),('bath_wc','002',(-2.8,.9,0)),('bath_shower','003',(-1.38,.905,0))]:add(label,'assets/guest_wash/source/AST-SAN-'+asset+'.blend',pt)
 add('EntryDoor','assets/guest_entry_door/source/AST-DOR-002.blend',(0,-.05,0))
 add('BathroomDoor','assets/guest_privacy_door/source/AST-DOR-001.blend',(-.7,2.9,0),math.pi/2)
 add('SuiteKitchenette','domestic_correction/outputs/kitchenette_r001/suite_kitchenette.blend',(3.025,1.4,0),-math.pi/2,True)
 def world(pt):
  x,y,z=pt;ox,oy,oz=r['source_origin_world_xyz'];a=r['source_yaw_godot'];return[round(ox+x*math.cos(a)-y*math.sin(a),6),round(oy+z,6),round(oz-x*math.sin(a)-y*math.cos(a),6)]
 newanchors=[];newbindings=[]
 for i,((pt,yaw),oa,ob)in enumerate(zip(beds,r0['bed_anchors'],r0['anchor_bindings'])):
  assert oa['evidence']=='explicit proposed rest placement; count and allocation are historical, original coordinate unknown'
  assert oa['historical_anchor_index']==ob['unit_anchor_index']==ob['prototype_anchor_index']==i
  nw=world(pt);status='Revised unregistered proposed coordinates; historical coordinate unknown'
  provenance.append({'source_index':r['census_source_index'],'unit_id':r['address'],'slot_id':ob['unit_slot_key'],'ordinal':i,'old_source_xyz':oa['source_xyz'],'old_world_xyz':oa['world_xyz'],'old_evidence':oa['evidence'],'new_source_xyz':pt,'new_world_xyz':nw,'new_source_yaw':yaw,'coordinate_status':status,'reason':'Tidal deep entrance and broad outlook salon, preserving real rest count'})
  newanchors.append({'historical_anchor_index':i,'source_xyz':pt,'world_xyz':nw,'source_yaw':yaw,'evidence':status});v=copy.deepcopy(ob);v.update(source_xyz=pt,world_xyz=nw,source_yaw=yaw,coordinate_evidence=status);newbindings.append(v)
 r.update(tidal_variant=key,tidal_design=design,tidal_handing=h,source_recipe_key=key,prior_source_recipe_key=r0['source_recipe_key'],bed_anchors=newanchors,anchor_bindings=newbindings,component_placements=placements,view_policy='planned_authored_outlook',finished=False,instance_adoption_ready=False,runtime_enabled=False)
 r.update(source_shell=f'outputs/interiors_r002/{key}/shell.glb',source_shell_sha256=None,source_recipe_sha256=None,source_detail_props_layer=None,source_props_variant='Tidal authored family',props_variation_status='Deterministic eight-source mapping; no random prop promise')
 r['privacy_acceptance']={'finite_sealed_profile':'sealed_window_r010','opaque_exterior_clear_interior_required':True,'whole_house_runtime_accepted':False}
 rows.append(r)
 if key not in prototypes:
  cfg=copy.deepcopy(r);cfg.update(address=key,representative_unit_id=r['address'],representative_source_index=r['census_source_index'],layout='A_open_salon',palette='teal',emphasize_ceiling_joinery=True,preserve_installed=False);prototypes[key]=cfg
 result=None
edges=sorted({tuple(sorted((a,b)))for a,v in adj.items()for b in v})
result={'schema':'astraea.tidal_garden_interiors.v1','status':'85-unit proposed source successor, not adopted','house_id':'port_forward_upper_house','source_map_sha256':sha(source),'counts':dict(Counter(r['historical_class']for r in rows)),'unit_count':len(rows),'rest_slot_count':len(provenance),'prototype_count':len(prototypes),'units':rows,'prototypes':list(prototypes.values()),'adjacency_edges':edges,'adjacency_pass':all(colors[a]!=colors[b]for a,b in edges),'whole_ship_units_unchanged':1000,'independent_D04_units':120,'specialty_vip_unbuilt':63,'installed_pilots_preserved_outside_this_house':[16,40],'known_historical_anchor_coordinates_changed':0}
assert result['counts']=={'standard':34,'family':51}and len(provenance)==221 and len(prototypes)==8 and result['adjacency_pass']
(R/'TIDAL_GARDEN_85_PLACEMENT_MAP.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'REST_SLOT_PROVENANCE.json').write_text(json.dumps({'source_map_sha256':sha(source),'identity_ordinal_count_unchanged':True,'rows':provenance},indent=2)+'\n')
print('TIDAL_INTERIOR_PLAN_READY',len(rows),len(provenance),len(prototypes),len(edges))
