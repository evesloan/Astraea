import bpy,json,pathlib,hashlib,math,gzip,sys
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;unit=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+1 else 876;__import__('sys').path.insert(0,str(R));from source_paths import section,inside_polygon;_,O,native_path,_=section(unit);contract=json.loads((O/'SECTION_CONTRACT.json').read_text());poly=contract['reservation']['proposed_floor_boundary'];bound_min=[min(v[0] for v in poly),contract['reservation']['floor_y'],min(v[1] for v in poly)];bound_max=[max(v[0] for v in poly),contract['reservation']['proposed_external_roof_limit_y'],max(v[1] for v in poly)]
p=native_path;bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();rows=[];fail=[];coordinates={}
for ob in bpy.context.scene.objects:
 if ob.type not in {'MESH','FONT'}:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vv=[ev.matrix_world@v.co for v in me.vertices]
 if not vv:ev.to_mesh_clear();continue
 world=[(v.x,v.z,-v.y) for v in vv]
 bad=[list(v) for v in world if not (all(bound_min[k]-.0001<=v[k]<=bound_max[k]+.0001 for k in range(3)) and inside_polygon(v[0],v[2],poly))]
 deg=sum((vv[t.vertices[1]]-vv[t.vertices[0]]).cross(vv[t.vertices[2]]-vv[t.vertices[0]]).length<1e-10 for t in me.loop_triangles)
 row={'name':ob.name,'type':ob.type,'vertices':len(vv),'triangles':len(me.loop_triangles),'bounds_world':[[min(v[c] for v in world) for c in range(3)],[max(v[c] for v in world) for c in range(3)]],'uv_layers':[u.name for u in me.uv_layers],'material_roles':[m.name for m in me.materials if m],'degenerate_triangles':deg,'out_of_boundary_vertices':len(bad)}
 rows.append(row);coordinates[ob.name]=world
 if bad or deg or not me.uv_layers:fail.append(row)
 ev.to_mesh_clear()
assert not any('PREVIEW' in r['name'] for r in rows),'preview floor saved in native'
images=[{'name':x.name,'packed':bool(x.packed_file),'sha256':hashlib.sha256(bytes(x.packed_file.data)).hexdigest() if x.packed_file else None} for x in bpy.data.images if x.type!='RENDER_RESULT']
if any(not x['packed'] for x in images):fail.append({'unpacked_images':images})
# Actual saved equipment support, plus proposed floor-bearing contacts.
contract=json.loads((O/'SECTION_CONTRACT.json').read_text(encoding='utf-8'));rowmap={x['name']:x for x in rows};supports=[]
for imp in contract['imports']:
 if 'part_names' not in imp:continue
 group=[rowmap[n] for n in imp['part_names'] if n in rowmap]
 if not group:continue
 bottom=min(x['bounds_world'][0][1] for x in group);expected=imp['world_xyz'][1];err=abs(bottom-expected)
 support={'catalogue_id':imp['catalogue_id'],'group':imp['part_names'][0],'bottom_y':bottom,'proposed_bearing_y':expected,'error_m':err,'bearing_status':'ROOT_OWNED_FLOOR_PROPOSAL' if abs(expected-102)<.001 else 'SOURCE_CONTACT_CHECK'}
 if imp.get('mount_contact_plane'):
  plane=imp['mount_contact_plane'];cabinet=next(x for x in group if 'VAN_WallCabinet' in x['name']);normal=plane['normal_xyz'];point=plane['point_xyz'];values=[sum((v[k]-point[k])*normal[k] for k in range(3)) for v in coordinates[cabinet['name']]];err=min(abs(min(values)),abs(max(values)));support.update(bearing_status='ACTUAL_FITTED_BATH_MOUNT_PLANE',mount_contact_error_m=err)
 elif imp['catalogue_id']=='AST-SAN-001':
  cabinet=next(x for x in group if 'VAN_WallCabinet' in x['name']);wall=rowmap['BathEast'];contact=min(abs(cabinet['bounds_world'][0][0]-wall['bounds_world'][1][0]),abs(cabinet['bounds_world'][1][0]-wall['bounds_world'][0][0]));support.update({'bearing_status':'ACTUAL_EAST_BATH_WALL','mount_contact_error_m':contact});err=contact
 if err>.001:fail.append({'retained_group_support':support})
 supports.append(support)
# Four beverage pads must contact the retained kitchen's actual top triangles.
for ob in [x for x in bpy.context.scene.objects if 'Beverage_' in x.name and 'counter_contact_pad_' in x.name]:
 ev=ob.evaluated_get(dg);pts=[ev.matrix_world@v.co for v in ev.data.vertices];bottom=min(v.z for v in pts);contact_pos=Vector((sum(v.x for v in pts)/len(pts),sum(v.y for v in pts)/len(pts),bottom));hits=[]
 for other in [x for x in bpy.context.scene.objects if 'FittedKitchen_' in x.name and 'continuous_eased_stone_worktop' in x.name]:
  e=other.evaluated_get(dg);inv=e.matrix_world.inverted();hit,loc,norm,idx=e.ray_cast(inv@(contact_pos+Vector((0,0,.10))),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((e.matrix_world@loc).z)
 error=abs(bottom-max(hits)) if hits else None;rec={'part':ob.name,'actual_pad_bottom_y':bottom,'support_surface_y':max(hits) if hits else None,'error_m':error};supports.append(rec)
 if error is None or error>.001:fail.append({'counter_contact':rec})
# Mounts terminate inside the actual cover/roof thickness. Ray upward from
# the bracket's bottom, through its centre, to the intended lower roof face.
fixtures=[]
for ob in [x for x in bpy.context.scene.objects if x.name.endswith('_Bracket')]:
 ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();lo=min(v.z for v in pts);hi=max(v.z for v in pts);centre=Vector((sum(v.x for v in pts)/len(pts),sum(v.y for v in pts)/len(pts),lo-.01));candidates=[]
 target_name=ob.get('source_mount_target') or ('BathAcousticCover' if ob.name.startswith('BathOpal') else 'RestCrown'+('0' if 'Reading0' in ob.name else '1') if ob.name.startswith('RestReading') else 'RisingLivingRoof')
 roof=bpy.context.scene.objects[target_name];e=roof.evaluated_get(dg);inv=e.matrix_world.inverted();hit,loc,norm,idx=e.ray_cast(inv@centre,inv.to_3x3()@Vector((0,0,1)))
 underside=(e.matrix_world@loc).z if hit else None;overlap=hi-underside if hit else None;rec={'fixture_mount':ob.name,'target_roof':target_name,'bracket_top_y':hi,'actual_underside_y':underside,'overlap_m':overlap};fixtures.append(rec)
 if overlap is None or overlap<-.001 or overlap>.06:fail.append({'fixture_mount':rec})
text_rows=[{'object':x.name,'editable_body':x.data.body,'export_mesh_expected':x.name} for x in bpy.context.scene.objects if x.type=='FONT']
(O/'SAVED_NATIVE_VERTICES.json.gz').write_bytes(gzip.compress(json.dumps(coordinates,separators=(',',':')).encode(),mtime=0))
rests=[]
for marker in [x for x in bpy.context.scene.objects if x.name.startswith('DATUM_rest_')]:
 pos=marker.matrix_world.translation;hits=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or not any(token in ob.name for token in contract.get('rest_contact_mesh_tokens',['REST_Quilt'])) or 'seam' in ob.name:continue
  ev=ob.evaluated_get(dg);mat=ev.matrix_world;inv=mat.inverted();start=inv@(pos+Vector((0,0,1)));direction=inv.to_3x3()@Vector((0,0,-1));hit,loc,norm,idx=ev.ray_cast(start,direction)
  if hit:hits.append((mat@loc).z)
 error=abs(pos.z-max(hits)) if hits else None;rests.append({'marker':marker.name,'reservation_id':marker.get('reservation_id'),'actual_quilt_contact_height':max(hits) if hits else None,'marker_height':pos.z,'contact_error_m':error})
 if error is None or error>.001:fail.append({'rest_contact':rests[-1]})
data={'status':'PASS' if not fail else 'FAIL','native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'independent_reopen':True,'floor_meshes':0,'mesh_rows':rows,'packed_images':images,'rest_contacts':rests,'support_contacts':supports,'fixture_contacts':fixtures,'editable_text':text_rows,'evaluated_vertices_file':'SAVED_NATIVE_VERTICES.json.gz','evaluated_vertices_sha256':hashlib.sha256((O/'SAVED_NATIVE_VERTICES.json.gz').read_bytes()).hexdigest(),'failures':fail,'scope':'Saved-source vertices, UVs, packed resources and four proposed support contacts; source-only, not installed gameplay/species acceptance'}
(O/'NATIVE_VERIFICATION.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print('NATIVE RESULT',data['status'],len(rows),'meshes',len(fail),'failures')
if fail:raise RuntimeError('Saved-native verification failed')
