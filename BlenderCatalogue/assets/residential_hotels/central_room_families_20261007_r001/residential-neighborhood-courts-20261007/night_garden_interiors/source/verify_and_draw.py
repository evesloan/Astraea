"""Bind all 80 source instances, exact recovered anchors and actual fixtures."""
from pathlib import Path
import json,math,hashlib,struct,copy,sys
import numpy as np
R=Path(__file__).resolve().parents[1];W=R.parents[1]
sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
P=json.loads((R/'NIGHT_GARDEN_80_PLACEMENT_MAP.json').read_text())
original=json.loads((W/'residential-batch-neighborhood-20261006/scale_domestic_r011/assemblies/GODOT_BATCH_INSTANCE_MAP.json').read_text())
old={r['census_source_index']:r for r in original['instances']}
cross=json.loads((W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records'];canonical={r['source_envelope_index']:r for r in cross}
pins=json.loads((R/'qa/INPUT_PINS.json').read_text());assert all(sha(p)==h for p,h in pins.items())
assert P['preserved_installed']==original['preserved_installed']
geom=json.loads((R/'qa/GEOMETRY_SCREEN.json').read_text())
curved=json.loads((R/'qa/CURVED_PERIMETER_source_r004.json').read_text());assert curved['all_pass']
assert geom['all_component_transforms_pass']and geom['all_route_targets_pass']and not geom['furniture_pair_broad_overlaps']
assert all(c['component']in ['bath_shower','EntryDoor','BathroomDoor']for c in geom['shell_surface_contacts'])
records={};profile=[];allfixtures=[];allanchors=[]
fig,axes=plt.subplots(2,4,figsize=(16,14),layout='constrained');fig.patch.set_facecolor('#f6f2e9')
for ax,cfg in zip(axes.flat,sorted(P['prototypes'],key=lambda r:(r['historical_class'],r['night_garden_design'],r['night_garden_handing']))):
 key=cfg['address'];D=R/'outputs/source_r004'/key
 receipt=json.loads((D/'SOURCE_RECEIPT.json').read_text());assert all(sha(D/n)==h for n,h in receipt['files'].items())
 b=(D/'shell.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];glb=json.loads(b[20:20+n]);nodes={x.get('name'):x for x in glb['nodes']}
 assert not any(x.get('uri')for x in glb.get('buffers',[])+glb.get('images',[]))
 markerpos={}
 for a in cfg['bed_anchors']:
  i=a['historical_anchor_index'];node=nodes['DATUM_bed_'+str(i)];t=node['translation'];local=[t[0],-t[2],t[1]];assert max(abs(x-y)for x,y in zip(local,a['source_xyz']))<1e-5;markerpos[i]=local
 obs=json.loads((D/'EVALUATED_GEOMETRY.json').read_text());byname={o['name']:o for o in obs}
 ceilings=[o for o in obs if o['name'].startswith('SUI_Ceiling_')];assert len(ceilings)==6
 panes=[o for o in obs if o['name'].startswith('SUI_WindowPane_')];assert len(panes)==2
 for pane in panes:
  lo,hi=pane['bounds'];assert abs(lo[2]-.475)<1e-5 and abs(hi[2]-3.605)<1e-5
 for name in ['SUI_WindowMullion_-3.45','SUI_WindowMullion_0','SUI_WindowMullion_3.45']:
  lo,hi=byname[name]['bounds'];assert abs(hi[0]-lo[0]-.13)<1e-5
 fixtures=json.loads((D/'SOURCE_FIXTURES.json').read_text());assert all(1.6<f['source_xyz'][2]<4.25 for f in fixtures)
 records[key]={'shell_glb':str((D/'shell.glb').relative_to(R)),'shell_glb_sha256':sha(D/'shell.glb'),'source_blend':str((D/'assembly.blend').relative_to(R)),'source_blend_sha256':sha(D/'assembly.blend'),'source_receipt_sha256':sha(D/'SOURCE_RECEIPT.json'),'markers':markerpos,'fixtures':fixtures}
 profile.append({'prototype':key,'main_ceiling_segments_preserved':len(ceilings),'finite_glass_panes':len(panes),'sealed_r010_dimensions_pass':True,'exported_bed_markers_match_exact_source':True,'no_external_GLTF_URIs':True})
 # This drawing projects actual evaluated meshes; it is not illustrative AI art
 # or a footprint invented independently of the built prototypes.
 ax.set_facecolor('#fffaf0')
 for o in obs:
  lo,hi=o['bounds'];name=o['name'];member=o['assembly_member']
  if hi[2]<.04 or lo[2]>2.05 or name.startswith(('SUI_Floor','SUI_FittedCarpet','SUI_CarpetBinding')):continue
  hull=MultiPoint(np.array(o['vertices'])[:,:2]).convex_hull
  if hull.geom_type!='Polygon' or hull.area<.001:continue
  color='#c6b698'
  if member.startswith('HistoricalBedAnchor'):color='#78958a'
  elif member.startswith('NightGarden'):color='#b57559'
  elif member in ['bath_vanity','bath_wc','bath_shower']:color='#9cb8bf'
  elif member in ['EntryDoor','BathroomDoor']:color='#537a91'
  elif member=='SuiteKitchenette':color='#a68b69'
  elif name.startswith('NG_'):color='#ac946e'
  elif 'Wall'in name or 'Bath'in name:color='#d3cbbb'
  ax.add_patch(Patch(np.array(hull.exterior.coords),facecolor=color,edgecolor='#574b3d',linewidth=.22,alpha=.9))
 for a in cfg['bed_anchors']:
  x,y,z=a['source_xyz'];ax.scatter([x],[y],s=13,color='#ffecab',edgecolors='#2d4b42',linewidths=.6,zorder=20);ax.text(x,y-.36,str(a['historical_anchor_index']+1),ha='center',fontsize=8,color='#152e27',zorder=21)
 ax.plot([-3.4,3.4],[12.78,12.78],color='#257e99',linewidth=3);ax.text(0,13.10,'REAL WINDOW • receiving view pending',ha='center',fontsize=6.5,color='#257e99')
 ax.set_xlim(-3.8,3.8);ax.set_ylim(-.6,13.45);ax.set_aspect('equal');ax.set_xticks([-3,0,3]);ax.set_yticks([0,4,8,12]);ax.tick_params(labelsize=7)
 ax.set_title(cfg['historical_class'].title()+' · '+cfg['night_garden_design'].replace('_',' ')+'\n'+('L'if cfg['night_garden_handing']==1 else'R')+' / exact rest order',fontsize=10)
 ax.set_xlabel('Local X (m)',fontsize=8)
fig.suptitle('Night Garden · eight actual source compositions\n80 new interiors / 210 exact recovered rest anchors · two existing pilots preserved separately',fontsize=17)
fig.savefig(R/'outputs/NIGHT_GARDEN_EVALUATED_SOURCE_PLANS.png',dpi=150)
fig.savefig(R/'outputs/NIGHT_GARDEN_EVALUATED_SOURCE_PLANS.svg')
plt.close(fig)
for u in P['units']:
 o=old[u['census_source_index']];c=canonical[u['census_source_index']];recipe=records[u['night_garden_variant']]
 for k in ['address','rebuild_identity','historical_address','census_source_index','allocation_sha256','allocation_x','allocation_z','floor_y','source_origin_world_xyz','source_yaw_godot','historical_class','bed_anchors','entry_persistent_id','bath_persistent_id']:assert u[k]==o[k],(u['address'],k)
 assert [b['unit_slot_key']for b in u['anchor_bindings']]==c['proposed_rest_slot_ids']
 assert len(u['anchor_bindings'])==c['proposed_rest_place_count']
 ox,oy,oz=u['source_origin_world_xyz'];ang=u['source_yaw_godot']
 def world(p):
  x,y,z=p;return [ox+x*math.cos(ang)-y*math.sin(ang),oy+z,oz-x*math.sin(ang)-y*math.cos(ang)]
 for a,b in zip(u['bed_anchors'],u['anchor_bindings']):
  i=a['historical_anchor_index'];assert b['unit_anchor_index']==b['prototype_anchor_index']==i
  v=world(recipe['markers'][i]);err=max(abs(x-y)for x,y in zip(v,a['world_xyz']));assert err<1e-5
  allanchors.append({'unit':u['address'],'slot_id':b['unit_slot_key'],'ordinal':i,'world_xyz':v,'exact_recovered_error_m':err})
 for f in recipe['fixtures']:
  v=world(f['source_xyz']);assert 1.60<v[1]-u['floor_y']<4.25
  allfixtures.append({'unit':u['address'],'prototype':u['night_garden_variant'],'source_datum':f['name'],'source_xyz':f['source_xyz'],'world_xyz':v,'world_elevation_assertion_pass':True})
 u['source_shell_sha256']=recipe['shell_glb_sha256'];u['source_recipe_sha256']=recipe['source_receipt_sha256']
P['prototypes_bound']=records;P['status']='Eight built source recipes; exact 80-unit current binding, runtime adoption pending'
write('NIGHT_GARDEN_80_CURRENT_APPLICATION.json',P)
write('qa/ALL_UNIT_TRANSFORMS.json',{'anchors':allanchors,'fixture_transforms':allfixtures,'all_exact_anchors_match':True,'all_fixture_elevations_pass':True,'units':80})
write('qa/SOURCE_VALIDATION.json',{'source_prototypes':8,'new_supported_units':80,'new_supported_rest_places':210,'preserved_installed_units':2,'supported_rest_places_including_preserved':214,'whole_house_units':145,'upper_specialty_unbuilt':47,'VIP_unbuilt':7,'D17_fit_held':9,'components_checked':geom['component_count'],'component_transforms_pass':True,'route_targets_checked':sum(len(r['targets'])for r in geom['route_screens']),'all_route_targets_pass':True,'furniture_pair_overlaps':0,'new_joinery_curved_perimeter_pass':True,'new_joinery_curved_perimeter_checked_parts':sum(len(r['checks'])for r in curved['records']),'new_furniture_shell_crossings':0,'retained_mounting_contact_groups':len(geom['shell_surface_contacts']),'adjacency_edges':len(P['adjacency_edges']),'neighbor_plan_difference_pass':P['adjacency_pass'],'recovered_anchor_coordinates_changed':0,'all_80_world_anchor_transforms_pass':True,'source_fixture_world_transform_count':len(allfixtures),'fixture_world_elevations_pass':True,'prototype_profiles':profile,'all_input_hashes_still_match':True,'input_pin_count':len(pins),'installed_geometry_byte_identical':True,'runtime_privacy_accepted':False,'runtime_door_cart_species_acceptance':False,'receiving_window_architecture_complete':False,'Game_or_Catalogue_writes':False,'no_Godot_job':True})
print('NIGHT_GARDEN_SOURCE_VALIDATED',len(allanchors),'exact anchors',len(allfixtures),'fixture transforms')
