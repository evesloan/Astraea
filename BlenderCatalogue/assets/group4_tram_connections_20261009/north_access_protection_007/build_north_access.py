from pathlib import Path
import bpy,json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';family='group4_north_access_protection_007';IDS0=['AST-TRM-G4-022'];checked=json.loads((W/'NORTH_ACCESS_LOCAL_CHECK.json').read_text());assert checked['status']=='NORTH_LOW_POCKET_AND_EDGE_SOURCE_PASS';assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in checked['source_pins'].items());geom={'__file__':str(W/'north_access_geometry.py'),'__name__':'geometry'};exec((W/'north_access_geometry.py').read_text(),geom)
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0].replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name","OUT=W;FAMILY=family").replace("assert FAMILY=='group4_tram_connections_20261009'",'').replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=IDS0").replace("'FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'","'NORTH_ACCESS_007_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'").replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)","bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor c in list(bpy.data.collections):bpy.data.collections.remove(c)")
exec(sc,globals());current=collections['NORTH_ACCESS_007_SOURCE'];rows=[]
for q in geom['recipes']:
 vs=[];fs=[];index={}
 for tri in q['triangles']:
  face=[]
  for p in tri:
   key=tuple(float(a) for a in p)
   if key not in index:index[key]=len(vs);vs.append(key)
   face.append(index[key])
  fs.append(tuple(face))
 ob=mesh(q['name'],vs,fs,materials[q['material']],q['role'],q['policy']);ob['retained_receiver_meshes']='; '.join(q['allowed_retained_receiver_meshes']);ob['source_only_unadopted']=True;rows.append({k:v for k,v in q.items() if k!='triangles'})
marker('DATUM_NORTH_PROTECTION_CONTEXT',[-10.65,52.5,-260],'fixed low-pocket protection; existing floors/receivers remain frozen')
marker('DATUM_OPEN_LIFT_APPROACH',[-11.2,52.5,-225.55],'lift entrance, threshold and actual cabin remain clear in bounded source check')
asset='AST-TRM-G4-022_north_access_protection.glb';native='Group4_North_Access_007.blend';bpy.ops.object.select_all(action='DESELECT')
for o in current.objects:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(W/asset),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
(W/'NORTH_ACCESS_MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n');meta=geom['plan'];meta.update(asset=asset,native=native,source_material_pins=texture_pins,retained_source_pins=checked['source_pins']);(W/'NORTH_ACCESS_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(W/native),compress=True);print('NORTH_ACCESS_PROTECTION_EXPORTED',len(parts),'meshes; no existing floor or runtime changes')
