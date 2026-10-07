"""Independent read-only Blender scene inspection; writes only its isolated QA receipt."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[2]
deps=bpy.context.evaluated_depsgraph_get(); records=[];floor=[]
for obj in bpy.context.scene.objects:
    if obj.type not in {'MESH','FONT','CURVE'}: continue
    ev=obj.evaluated_get(deps)
    coords=[ev.matrix_world@Vector(v) for v in ev.bound_box]
    world=[(float(v.x)+8,float(v.z)+78,-float(v.y)-466) for v in coords]
    lo=[min(v[k] for v in world) for k in range(3)]
    hi=[max(v[k] for v in world) for k in range(3)]
    record={'name':obj.name,'type':obj.type,'world_min':lo,'world_max':hi,'catalogue_id':obj.get('parent_catalogue_id')}
    (floor if obj.get('exclude_architecture_export') else records).append(record)
images=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'filepath':i.filepath,'source':i.source} for i in bpy.data.images if i.type=='IMAGE']
lo=[min(r['world_min'][k] for r in records) for k in range(3)]
hi=[max(r['world_max'][k] for r in records) for k in range(3)]
roof=next(r for r in records if r['name']=='ROOF_closed_assembly')
def gap(a,b):
    return [max(a['world_min'][k]-b['world_max'][k],b['world_min'][k]-a['world_max'][k],0.0) for k in range(3)]
contacts=[]
for name in ['ARRIVAL_suspended_panel','CARE_ceiling','ROOF_closed_assembly']:
    a=next(r for r in records if r['name']==name)
    nearby=[]
    for b in records:
        if b is a or not b['name'].startswith(('PERIMETER','PORTAL','PIER','BEAM','CARE_screen','CARE_north')):continue
        g=gap(a,b)
        if max(g)<0.011:nearby.append({'name':b['name'],'aabb_gap_xyz':g})
    contacts.append({'surface':name,'supporting_architecture_aabb_contacts_within_1cm':nearby,'limitation':'AABB adjacency screen, not contact-surface, load-path or engineering certification'})
report={'scope':'Fresh independent native reload source-only geometry; no render or engine acceptance','blender':bpy.app.version_string,'source_sha256':hashlib.sha256((P/'source/WP06_long_library.blend').read_bytes()).hexdigest(),'placement_godot':[8,78,-466],'world_bounds':[lo,hi],'architectural_mesh_font_curve_count':len(records),'excluded_floor':floor,'above_y83_203':[r for r in records if r['world_max'][1]>83.203],'roof':roof,'top_structural_members':[r for r in records if r['name'].startswith(('PERIMETER','PORTAL','ROOF','ARRIVAL_suspended','CARE_ceiling','PIER','BEAM'))],'structural_contact_screen':contacts,'images':images,'unpacked_images':[i for i in images if not i['packed']],'external_libraries':[i.filepath for i in bpy.data.libraries],'text_blocks':[t.name for t in bpy.data.texts],'all_bounds':records}
(P/'qa/receiving_source_review/NATIVE_INTERFACE_AUDIT.json').write_text(json.dumps(report,indent=2))
print('INDEPENDENT_INTERFACE_AUDIT',json.dumps({'world_bounds':report['world_bounds'],'native_shapes':len(records),'unpacked_images':len(report['unpacked_images']),'external_libraries':report['external_libraries'],'above_y83_203':len(report['above_y83_203']),'contacts':contacts}))
assert not report['above_y83_203']
assert not report['unpacked_images']
assert not report['external_libraries']
