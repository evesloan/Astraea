from pathlib import Path
import bpy,json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';family='group4_foremid_north_candidate_005';IDS0=['AST-TRM-G4-020'];screen=json.loads((W/'NORTH_STATION_LOCAL_SCREEN.json').read_text());assert screen['status']=='NORTH_FOREMID_BOUNDED_SOURCE_CLEAR_WITH_RECEIVING_BINDING_HOLDS';assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in screen['source_geometry_pins'].items());G={'__file__':str(W/'north_candidate_geometry.py'),'__name__':'source_geometry'};exec((W/'north_candidate_geometry.py').read_text(),G)
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0].replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name","OUT=W;FAMILY=family").replace("assert FAMILY=='group4_tram_connections_20261009'",'').replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=IDS0").replace("'FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'","'NORTH_FOREMID_STATION_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'").replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)","bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor c in list(bpy.data.collections):bpy.data.collections.remove(c)")
prep=G;exec(sc,globals());current=collections['NORTH_FOREMID_STATION_SOURCE'];rows=[]
for q in prep['recipes']:
 vs=[];fs=[];index={}
 for tri in q['triangles']:
  face=[]
  for p in tri:
   key=tuple(float(a) for a in p)
   if key not in index:index[key]=len(vs);vs.append(key)
   face.append(index[key])
  fs.append(tuple(face))
 assert q['material'] in materials,q['material'];ob=mesh(q['name'],vs,fs,materials[q['material']],q['role'],q['policy']);ob['retained_source_mesh']=q['retained_source_mesh'] or '';ob['unadopted_station_identity']='FORE_MIDSHIP';ob['source_changes']='; '.join(q['changes']);ps=[G0 for G0 in [tuple(Gf) for Gf in vs]];rows.append({'mesh':ob.name,'role':q['role'],'retained_source_mesh':q['retained_source_mesh'],'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]})
for n,p,role in [('N005_DATUM_PHYSICAL_DOCKING',(-5.6,56.1,-241),'old stop−216→new proposal−241; root binding decision required'),('N005_DATUM_BOARDING_BRIDGE',(-7.8,56.1,-241),'bridge019 yaw0; no moving component installed'),('N005_DATUM_BOARDING_LIFT_ROOT',(-11.2,0,-225),'reuse commons_lift/AST-CIR-003 at yaw−PI/2; two stops52.5/56.1'),('N005_DATUM_LOWER_ANNEX',(-10,52.5,-246),'new missing-only floor proposal, existing core and PaperMoon owners preserved')]:marker(n,p,role)
file='AST-TRM-G4-020_foremid_north_candidate.glb';bpy.ops.object.select_all(action='DESELECT')
for ob in current.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
(W/'NORTH_MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n');meta=prep['plan'];meta.update(asset=file,native='Group4_Foremid_North_Proposal_005.blend',source_material_pins=texture_pins,retained_source_pins=screen['source_geometry_pins'],lower_floor_exported=False,structural_gate='Three source cantilevers received by actual D09_fore_route floor; lower-annex, secondary stair/return and lift receiving still open. No capacity acceptance.');(W/'NORTH_STATION_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(W/meta['native']),compress=True);print('NORTH_STATION_SOURCE_EXPORTED',len(parts),'members; old stop−216, proposal−241; no runtime adoption')
