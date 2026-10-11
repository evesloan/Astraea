from pathlib import Path
import ast,json,hashlib,math,subprocess
from shapely.geometry import box,Polygon,mapping,shape
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for node in ast.parse(text).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['add','cube','prism']:exec(compile(ast.get_source_segment(text,node),'<reviewed local receiving geometry helper>','exec'))
S=json.load(open(W/'SUPPORT_PREFLIGHT.json'));assert S['status']=='PASS';assert not S['staff_bridge_headspace_blockers']
reservation=box(63,-384,97,-356);stair_void=box(63,-383,69.3,-372.2);upper=box(63,-384,85,-356.2).difference(stair_void);lower=unary_union([box(4,-383.4,63.2,-379),box(60,-383.4,69.3,-367.8)]);roof=box(63,-384,85,-356.2)
prism('D04SC_CommonsFloor',upper,16.26,16.5);prism('D04SC_CommonsRoof',roof,20.48,20.7,role='ivory_enamel',category='roof');prism('D04SC_StaffLowerBridgeFloor',lower,11.76,12,role='staff_panel',category='staff_floor')
# Do not floor the stair well or outer hull-maintenance reservation.
for i,f in enumerate(S['results']):
 x,y,z=f['chosen']['foot'];top=f['candidate']['top_y'];cube(f'D04SC_KeelPier_{i:02d}',[x-.14,y,z-.14],[x+.14,top,z+.14]);cube(f'D04SC_KeelShoe_{i:02d}',[x-.14,y,z-.14],[x+.14,y+.08,z+.14])
for z in [-383.4,-375.4,-369.9,-363.5,-356.7]:
 x0=69.3 if -383<z<-372.2 else 63
 cube('D04SC_UpperTransfer_'+str(z),[x0,15.98,z-.14],[85,16.3,z+.14])
for x in [70.5,77.4,82.45]:cube('D04SC_UpperLong_'+str(x),[x-.14,15.98,-384],[x+.14,16.3,-356.2])
for z in [-383.15,-379.25]:cube('D04SC_LowerBridgeLong_'+str(z),[4,11.48,z-.14],[63.2,11.80,z+.14])
for x in [8.5,20,32,44,56,61.4]:cube('D04SC_LowerBridgeCross_'+str(x),[x-.14,11.48,-383.4],[x+.14,11.80,-379])
for z in [-372.05,-368.05]:cube('D04SC_LowerLandingTransfer_'+str(z),[60,11.48,z-.14],[69.3,11.8,z+.14])
for x in [60.2,68.95]:cube('D04SC_LowerTurnLong_'+str(x),[x-.14,11.48,-383.4],[x+.14,11.8,-367.8])
# Lower screened staff bridge joins the existing D03 fore spine, turns around retained receiving piers, and reaches the original stair lower entry.
for i,(a,b)in enumerate(zip(lower.exterior.coords,list(lower.exterior.coords)[1:])):
 if a[0]==4 and b[0]==4:continue
 poly=Polygon([a,b,(b[0]+.10,b[1]+.10),(a[0]+.10,a[1]+.10)])
 if a[0]==b[0]:lo=[a[0],12,min(a[1],b[1])];hi=[a[0]+.12,15.20,max(a[1],b[1])]
 else:lo=[min(a[0],b[0]),12,a[1]];hi=[max(a[0],b[0]),15.20,a[1]+.12]
 cube(f'D04SC_LowerServiceWall_{i}',lo,hi,role='staff_panel',category='wall')
# Roof/bridge ceiling stops outside the stair opening; full lower arrival remains legible, not a route inside a floor void.
lowroof=lower.difference(box(63,-383,69.3,-372.2));prism('D04SC_LowerStaffCeiling',lowroof,15.2,15.34,role='staff_panel',category='staff_roof')
cube('D04SC_StairWestScreen',[63,12,-383],[63.18,20.48,-372.2],role='staff_panel',category='wall')
# Primary commons enclosure and deep supported public threshold at the retained X63 approach.
for name,lo,hi in [('SouthWall',[63,16.5,-384],[85,20.48,-383.82]),('NorthWall',[63,16.5,-356.38],[85,20.48,-356.2]),('WestSouth',[63,16.5,-384],[63.18,20.48,-383]),('WestEntrySouth',[63,16.5,-372.2],[63.18,20.48,-371.9]),('WestEntryNorth',[63,16.5,-367.2],[63.18,20.48,-356.2]),('PublicPortalHead',[63,19.15,-371.9],[63.18,20.48,-367.2])]:cube('D04SC_'+name,lo,hi,role='ivory_enamel',category='wall')
for z in [-371.97,-367.13]:cube('D04SC_PublicPortalReveal_'+str(z),[62.92,16.5,z-.06],[63.32,19.3,z+.06],category='portal')
# East perimeter glazing looks into its own retained maintenance/overhang volume; no new hull window or neighbor view claim.
cube('D04SC_EastDado',[84.82,16.5,-383.82],[85,17.05,-356.38],role='warm_walnut',category='wall');cube('D04SC_EastGlass',[84.86,17.05,-383.82],[84.94,19.9,-356.38],role='hospitality_glass',category='window');cube('D04SC_EastHead',[84.82,19.9,-383.82],[85,20.48,-356.38],role='ivory_enamel',category='wall')
for z in [-383.6,-375.8,-362.2,-356.5]:cube('D04SC_EastMullion_'+str(z),[84.76,16.5,z-.065],[85,20.48,z+.065],category='window_frame')
# Private planted outlook, screened from service destinations and external maintenance volume.
court=box(81.8,-375.8,84.82,-362.2);cube('D04SC_GardenDado',[81.71,16.5,-375.8],[81.89,17.1,-362.2],role='warm_walnut',category='wall');cube('D04SC_GardenGlass',[81.76,17.1,-375.8],[81.84,19.9,-362.2],role='hospitality_glass',category='window');cube('D04SC_GardenHead',[81.71,19.9,-375.8],[81.89,20.48,-362.2],role='ivory_enamel',category='wall')
for z in [-375.8,-362.2]:cube('D04SC_GardenEnd_'+str(z),[81.8,16.5,z-.09],[84.82,20.48,z+.09],role='ivory_enamel',category='wall')
for z in [-373.5,-369,-364.5]:
 cube('D04SC_Planter_'+str(z),[82.4,16.5,z-.55],[84.2,17.18,z+.55],role='warm_walnut',category='planter');cube('D04SC_Soil_'+str(z),[82.47,17.16,z-.48],[84.13,17.19,z+.48],role='warm_stone',category='planter')
 for j,(x,h)in enumerate([(82.9,.95),(83.3,1.45),(83.7,1.15)]):
  poly=Polygon([(x-.32,z-.24),(x+.22,z-.33),(x+.38,z),(x+.20,z+.32),(x-.28,z+.26)]);prism('D04SC_LeafMass_'+str(z)+'_'+str(j),poly,17.18,17.18+h,role='foliage',category='plant_detail');parts[-1]['runtime_collision']=False
# Two distinct service cells, separate front thresholds and closed returned-textile destination. No processing department duplicated.
for label,x0,x1 in [('Clean',68.2,73.8),('ClosedReturn',74.1,77.7)]:
 for name,lo,hi in [('West',[x0,16.5,-362],[x0+.16,20.48,-356.38]),('East',[x1-.16,16.5,-362],[x1,20.48,-356.38])]:cube('D04SC_'+label+name,lo,hi,role='staff_panel',category='wall')
 center=(x0+x1)/2
 for name,a,b in [('FrontL',x0,center-.9),('FrontR',center+.9,x1)]:cube('D04SC_'+label+name,[a,16.5,-362],[b,20.48,-361.82],role='staff_panel',category='wall')
 cube('D04SC_'+label+'DoorHead',[center-.9,19.15,-362],[center+.9,20.48,-361.82],role='staff_panel',category='wall')
 for z in [-357.8]:
  if label=='ClosedReturn':
   for j,x in enumerate([75.0,76.7]):cube('D04SC_ClosedBinFoot_'+str(j),[x-.36,16.5,z-.45],[x+.36,16.62,z+.45],category='fitting');cube('D04SC_ClosedBinShell_'+str(j),[x-.33,16.62,z-.42],[x+.33,17.50,z+.42],role='ivory_enamel',category='closed_return');cube('D04SC_ClosedBinLid_'+str(j),[x-.36,17.50,z-.45],[x+.36,17.60,z+.45],role='warm_walnut',category='closed_return')
# Supported stock shelf makes original bottle silhouettes visibly meaningful without creating inventory or duplicate product state.
cube('D04SC_StockShelfTop',[68.6,17.65,-359.6],[70.2,17.75,-358.9],role='warm_walnut',category='fitting')
for x in [68.68,70.12]:cube('D04SC_StockShelfLeg_'+str(x),[x-.055,16.5,-359.55],[x+.055,17.65,-358.95],category='fitting')
# Activity ceiling and weighted fluted/chamfered piers, fitted to actual shared activity rather than an empty hall.
outer=Polygon([(70.3,-372.7),(71,-373.3),(78,-373.3),(78.7,-372.7),(78.7,-366.3),(78,-365.7),(71,-365.7),(70.3,-366.3)]);inner=outer.buffer(-.38,join_style=2);prism('D04SC_ActivityCanopy',outer.difference(inner),19.85,20.15,role='ivory_enamel',category='roof')
for i,(x,z)in enumerate([(69.8,-375.7),(79.2,-375.7),(69.8,-363.6),(79.2,-363.6)]):
 poly=Polygon([(x-.18,z-.12),(x-.12,z-.18),(x+.12,z-.18),(x+.18,z-.12),(x+.18,z+.12),(x+.12,z+.18),(x-.12,z+.18),(x-.18,z+.12)]);prism('D04SC_ActivityPier_'+str(i),poly,16.62,20.48,role='warm_stone',category='frame');cube('D04SC_ActivityPierPlinth_'+str(i),[x-.25,16.5,z-.25],[x+.25,16.62,z+.25],category='frame')
bindings=[{'catalogue_id':'AST-LIB-STUDY-01','name':'SharedActivityTable','position':[74.5,16.5,-369.5],'yaw':0}]
for i,(x,z,yaw)in enumerate([(73.8,-371.05,0),(75.2,-371.05,0),(73.8,-367.95,math.pi),(75.2,-367.95,math.pi)]):bindings.append({'catalogue_id':'AST-FUR-002','name':'ActivityChair'+str(i),'position':[x,16.5,z],'yaw':yaw})
for i,(x,yaw)in enumerate([(79.5,math.pi/2),(83,-math.pi/2)]):bindings.append({'catalogue_id':'AST-FUR-002','name':'QuietChair'+str(i),'position':[x,16.5,-358.7],'yaw':yaw})
bindings += [{'catalogue_id':'AST-FUR-003','name':'QuietActivityTable','position':[81.25,16.5,-358.7],'yaw':0},{'catalogue_id':'AST-FUR-001','name':'GardenEdgeBenchSouth','position':[80.6,16.5,-373.6],'yaw':math.pi/2},{'catalogue_id':'AST-FUR-001','name':'GardenEdgeBenchNorth','position':[80.6,16.5,-365.0],'yaw':math.pi/2},{'catalogue_id':'AST-STF-007','name':'CleanStockCabinet','position':[71.2,16.5,-357.0],'yaw':math.pi}]
for i,x in enumerate([68.85,69.2,69.55,69.9]):bindings.append({'catalogue_id':'AST-HSK-006','name':'FixedStockBottle'+str(i),'position':[x,17.75,-359.25],'yaw':0,'fixed_stock_representation_not_loose_inventory':True})
bindings.append({'catalogue_id':'AST-CIR-001','name':'StaffStair450','position':[63.2,12,-372.3],'yaw':0,'source_override':'assets/circulation_architecture/source/AST-CIR-001_H450.blend','variant_manifest':'BlenderCatalogue/assets/circulation_architecture/AST-CIR-001_H450.manifest.json'})
manifest=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));sources=[next(a for a in manifest['assets']if a['catalogue_id']==i)for i in sorted({b['catalogue_id']for b in bindings})]
lights=[]
for i,(x,z,y)in enumerate([(65.2,-369.5,20.1),(74.5,-372.5,19.78),(74.5,-366.5,19.78),(80.5,-373.6,20.1),(80.5,-365,20.1),(81.25,-358.7,20.1),(71.2,-359.5,20.1),(75.9,-359.5,20.1),*[(x,-381.2,14.90)for x in [10,22,34,46,58]],(61.6,-374.5,14.90),(65.8,-370,14.90)]):
 cube(f'D04SC_LampHousing_{i}',[x-.31,y+.04,z-.24],[x+.31,y+.28,z+.24],category='light_source');cube(f'D04SC_LampLens_{i}',[x-.26,y+.015,z-.19],[x+.26,y+.04,z+.19],role='opal_glow',category='light_source');lights.append({'name':f'D04SC_LampLens_{i}','at':[x,y,z],'staff':y<16})
old=json.load(open(R/'BlenderCatalogue/assets/d04_starboard_forward_south_package_20261011/RUNTIME_PLAN.json'));pre=[]
for t in old['receiving_parts']:
 lo=[min(v[i]for v in t['verts'])for i in range(3)];hi=[max(v[i]for v in t['verts'])for i in range(3)]
 if t['category']=='guard'and abs((lo[0]+hi[0])/2-63)<.001 and lo[2]<-369<hi[2]:pre.append({'name':t['name'],'preimage':t,'preimage_sha256':hashlib.sha256(json.dumps(t,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
assert len(pre)==3
paths=['Game/data/spatial_layout.json','Game/data/programme_ledger.json','Game/data/reference/directory_allocations.json','Game/data/whole_ship_layout.json','Game/scripts/ship.gd','Game/scripts/structural_floor_builder.gd','BlenderCatalogue/catalogue_manifest.json','Game/assets/models/D04_STARBOARD_SOUTH_RECEIVING_r003.glb','BlenderCatalogue/assets/d04_starboard_forward_south_package_20261011/RUNTIME_PLAN.json','BlenderCatalogue/assets/circulation_architecture/AST-CIR-001_H450.manifest.json','BlenderCatalogue/assets/circulation_architecture/source/AST-CIR-001_H450.blend','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json']+['BlenderCatalogue/'+a['source']for a in sources];pins={f:sha(R/f)for f in paths}
P={'schema':'astraea.d04.starboard.full_commons.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'programme_key':'D04_directory_02','house_id':old['house_id'],'parts':parts,'rigid_bindings':bindings,'sources':sources,'lights':lights,'source_pins':pins,'preimages':pre,'all_twenty_allocations_unchanged':old['all_twenty_allocations_unchanged'],'commons_floor_geometry':mapping(upper),'lower_staff_floor_geometry':mapping(lower),'commons_floor_m2':upper.area,'lower_staff_floor_m2':lower.area,'reservation_m2':952,'planted_court_geometry':mapping(court),'negative_volume_zones':[{'purpose':'Stair rise, headroom and staff approach','geometry':mapping(stair_void),'m2':stair_void.area},{'purpose':'Outer hull/perimeter maintenance and roof overhang; no added occupied floor','geometry':mapping(box(85,-384,97,-356)),'m2':336},{'purpose':'North boundary end condition','geometry':mapping(box(63,-356.2,85,-356)),'m2':4.4}],'support_preimages':S['results'],'activity':'One informal shared reading/folio/work table with4original chairs; quiet two-chair table and2original benches','service':'Separate locally enclosed stock and closed-return cells, supported original bottles on new shelf; no processing department or inventory acceptance','staff_approach':'New screened D03 bridge from existing fore spine, dogleg around retained piers, original4.5m stair to local commons service approach','new_units':0,'new_rest_places':0,'active':False,'primary_engineering_accepted':False,'full_dedicated_clean_used_connection_accepted':False,'cart_vertical_accepted':False,'provider_occupancy_save_biology_final_accepted':False,'limits':['D03 spine is shared circulation; dedicated connection to port lower staff network remains open','No loaded cart stairs/vertical transport acceptance','Commons/staff floors and overhangs establish geometric continuity, not sized engineering','Horticultural reach, operational stock/returns, service permissions, occupied seats/species/biology/save and final graphics held'],'phase_evidence':{}}
assert abs(upper.area+sum(z['m2']for z in P['negative_volume_zones'])-952)<1e-7
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print({'parts':len(parts),'bindings':len(bindings),'commons_floor_m2':upper.area,'new_staff_bridge_m2':lower.area,'purposeful_floor_free_m2':sum(z['m2']for z in P['negative_volume_zones'])})
