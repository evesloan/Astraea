"""Batch retained room geometry for runtime while reserving existing door controllers.
Original editable assemblies remain source-of-truth, untouched. No default adoption.
"""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1];E=O/'exports';E.mkdir(exist_ok=True)
C=json.loads((O/'INPUT_CONTRACT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();reports=[]
assert sha(R/C['application_source'])==C['application_sha256']
for item in C['prototypes']:
 source=R/item['assembly'];assert sha(source)==item['assembly_sha256'];out=E/(item['key']+'.glb');assert not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
 assert all(Path(bpy.path.abspath(l.filepath)).exists()for l in bpy.data.libraries)
 old_objects=list(bpy.context.scene.objects);groups={};markers=[];excluded={'EntryDoor':0,'BathroomDoor':0};count=0;source_vertices=0;horizontal_checks=0
 for ob in old_objects:
  door=next((p for p in excluded if ob.name.startswith(p+'__')),None)
  if door:
   excluded[door]+=1;continue
  if ob.type=='EMPTY':
   markers.append((ob.name,ob.matrix_world.copy(),dict(ob.items())));continue
  if ob.type!='MESH':continue
  count+=1;me=ob.data;coords=[tuple(ob.matrix_world@v.co)for v in me.vertices];source_vertices+=len(coords)
  if ob.name=='SUI_Floor':
   lo=min(v[2]for v in coords);hi=max(v[2]for v in coords)
   for poly in me.polygons:
    zs=[coords[j][2]for j in poly.vertices]
    if max(zs)-min(zs)>1e-5:continue
    normal=ob.matrix_world.to_3x3()@poly.normal
    assert normal.z>0 if abs(zs[0]-hi)<1e-5 else normal.z<0,(item['key'],ob.name,'floor winding')
    horizontal_checks+=1
  semantic='window_glass' if 'WindowPane' in ob.name else 'bath_glass' if 'GlassPane' in ob.name else 'static'
  for mi in sorted(set(p.material_index for p in me.polygons)):
   material=me.materials[mi] if len(me.materials)>mi else None
   key=(material.name if material else 'Unassigned',semantic)
   g=groups.setdefault(key,{'verts':[],'faces':[],'uv':[],'smooth':[],'sources':[],'material':material});off=len(g['verts']);g['verts'].extend(coords);start=len(g['faces']);polycount=0
   for poly in me.polygons:
    if poly.material_index!=mi:continue
    g['faces'].append(tuple(off+j for j in poly.vertices));g['smooth'].append(poly.use_smooth);polycount+=1
    for li in poly.loop_indices:g['uv'].append(tuple(me.uv_layers.active.data[li].uv)if me.uv_layers.active else (0,0))
   g['sources'].append({'name':ob.name,'vertex_start':off,'vertex_count':len(coords),'face_start':start,'face_count':polycount})
 assert all(excluded.values()) and horizontal_checks>0
 for ob in old_objects:ob.select_set(False)
 col=bpy.data.collections.new('EXPORT_STATIC_ROOM');bpy.context.scene.collection.children.link(col)
 for index,(key,g)in enumerate(groups.items()):
  me=bpy.data.meshes.new('NIGHT_GARDENRoomBatch_'+str(index));me.from_pydata(g['verts'],[],g['faces']);me.update()
  if g['material']:me.materials.append(g['material'])
  uv=me.uv_layers.new(name='RetainedSourceUV');assert len(uv.data)==len(g['uv'])
  for a,b in zip(uv.data,g['uv']):a.uv=b
  for face,smooth in zip(me.polygons,g['smooth']):face.use_smooth=smooth
  ob=bpy.data.objects.new('NIGHT_GARDENRoomBatch_'+str(index),me);col.objects.link(ob);ob.select_set(True);ob['source_parts']=g['sources'];ob['semantic']=key[1];ob['source_assembly_sha256']=item['assembly_sha256'];ob['geometry_status']='retained geometry batched; room adoption unaccepted'
 for name,matrix,properties in markers:
  marker=bpy.data.objects.new('SOURCE_'+name,None);marker.matrix_world=matrix;col.objects.link(marker);marker.select_set(True)
  for k,v in properties.items():
   try:marker[k]=v
   except TypeError:pass
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 assert sha(source)==item['assembly_sha256']
 report={**item,'runtime_file':str(out.relative_to(R)),'runtime_sha256':sha(out),'bytes':out.stat().st_size,'retained_static_meshes':count,'source_vertices':source_vertices,'runtime_mesh_batches':len(groups),'source_marker_count':len(markers),'excluded_door_source_objects':excluded,'floor_orientation_checks':horizontal_checks,'coordinates_edited':False,'source_original_unchanged':True,'runtime_adopted':False}
 reports.append(report);(O/'SOURCE_BATCH_REPORT.json').write_text(json.dumps({'status':'IN_PROGRESS'if len(reports)<len(C['prototypes'])else'EXPORTED_NOT_ADOPTED','prototypes':reports,'source_placements':80,'installed_units':0},indent=2)+'\n');print('NIGHT_GARDEN_ROOM_EXPORTED',item['key'],count,'meshes to',len(groups),'batches',flush=True)
print('NIGHT_GARDEN_ROOM_EXPORT_COMPLETE',len(reports),flush=True)
