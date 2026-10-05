from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003';FAMILY='central_crown';AID='AST-CMD-001'
manifest=json.loads((C/'catalogue_manifest.json').read_text());assert len([a for a in manifest['assets'] if a['catalogue_id']==AID and a['family']!=FAMILY])==0
D=json.loads((G/'data/architecture/CENTRAL_CROWN_CONSTRUCTION.json').read_text())
D.update({'catalogue_id':AID,'family':FAMILY,'coordinate_mapping':'Blender=(Godot X,-Godot Z,Godot Y); export_yup=true; root world origin (0,0,0)','origin':[0,0,0],'collision_policy':'All named CMD_CELL meshes concave static surfaces, including visibly present glazing. No floor slab, static duplicate leaves, convex fill, door script, furniture or commands included.','roof_body_ceiling_y':111,'roof_skin_levels_y':[[0,12,114.24,114.44],[12,24,114.06,114.26],[24,36,113.84,114.04]],'doors':[],'light_markers':[],'source_validation':'qa/source_export_validation.json','runtime_limits':['Parent supplies actual working AST-STF-008 doors and owned D18 floors','Parent tests collision, walking, loaded cart, optical exits, window views and pier/tie contacts in the existing main scene','No operational command simulation, role-based access enforcement or capacity addition']})
for p in D['programmes']:
 x,z=p['entry_xz'];D['doors'].append({'name':p['programme_key']+'_entry','programme_key':p['programme_key'],'position':[x,106.5,z],'yaw':p['door_yaw'],'file':'AST-STF-008.glb','marker':'DATUM_door_'+p['programme_key'],'wall_aperture_half_width':1.375,'wall_aperture_height':2.815,'fixed_frame_outer_half_width':1.38,'fixed_frame_outer_height':2.82,'fixed_frame_half_depth':.18,'wall_half_depth_or_inside_thickness':.16,'join_overlap_m':.005})
for i,p in enumerate(D['controlled_crossings']):
 D['doors'].append({'name':'controlled_crossing_%02d'%(i+1),'position':[p['x'],106.5,p['z']],'yaw':p['door_yaw'],'file':'AST-STF-008.glb','marker':'DATUM_door_crossing_%02d'%(i+1),'wall_aperture_half_width':1.375,'wall_aperture_height':2.815,'fixed_frame_outer_half_width':1.38,'fixed_frame_outer_height':2.82,'fixed_frame_half_depth':.18,'screen_half_depth':.08,'join_overlap_m':.005})
D['support']['authored_ties']=[{'name':'CMD_Tie_%s_X%s_Z%s'%(band['deck'],'P'if x>0 else'M','P'if z>0 else'M'),'deck':band['deck'],'floor_y':band['floor_y'],'world_aabb':[x-.34,x+.34,band['floor_y']-.5,band['floor_y']-.12,*sorted([s*(69.8),s*70.42])],'intended_slab_overlap_z_m':.2,'intended_pier_overlap_z_m':.02}for x,z in D['support']['pier_centres_xz']for s in [1 if z>0 else-1]for band in D['support']['intermediate_band_connections']]
D['source_inputs']={str(p.relative_to(C) if p.is_relative_to(C) else p.relative_to(G)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [G/'data/architecture/CENTRAL_CROWN_CONSTRUCTION.json',G/'docs/CROWN_PIER_RUNTIME_AUDIT.json',C/'assets/staff_threshold/source/AST-STF-008.blend',C/'assets/staff_threshold/exports/AST-STF-008.glb']}
(R/'source/section_contract.json').write_text(json.dumps(D,indent=2)+'\n')
protected=[]
for a in manifest['assets']:
 if a['catalogue_id']==AID:continue
 for k in ['source','export']:
  if a.get(k) and (C/a[k]).exists():protected.append({'catalogue_id':a['catalogue_id'],'kind':k,'path':a[k],'sha256':hashlib.sha256((C/a[k]).read_bytes()).hexdigest()})
p=R/'qa/protected_prior_assets.json'
if not p.exists():p.write_text(json.dumps({'catalogue_count':len(manifest['assets']),'baseline_commit':'17619084a96eeddd6076d078313e8ddfcf6b257c','assets':protected},indent=2)+'\n')
