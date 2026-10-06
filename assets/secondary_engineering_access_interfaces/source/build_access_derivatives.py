"""Bounded existing-family derivatives. Blender execution requires parent's allocated slot.
No originals, runtime, registry or shared material writes. Saves editable unbatched source.
"""
from pathlib import Path
import json, hashlib, sys
R=Path(__file__).resolve().parents[1]; C=R.parents[1]
PINS=json.loads((R/'source/input_pins.json').read_text())['inputs']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_inputs():
    for p,h in PINS.items():assert sha(p)==h, ('input changed',p)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def material_snapshot():
    out={}
    for m in bpy.data.materials:
        nodes=[];links=[]
        if m.use_nodes:
            for n in m.node_tree.nodes:
                row={'name':n.name,'type':n.bl_idname,'properties':{k:str(n[k]) for k in n.keys()},'inputs':[]}
                for q in n.inputs:
                    if hasattr(q,'default_value'):
                        value=q.default_value
                        if not isinstance(value,(int,float,str,bool)):value=list(value) if hasattr(value,'__iter__') else str(value)
                        row['inputs'].append((q.identifier,value))
                if n.type=='TEX_IMAGE':
                    row.update(interpolation=n.interpolation,extension=n.extension,image=n.image.name if n.image else None)
                    if n.image:
                        row['image_colorspace']=n.image.colorspace_settings.name
                        row['packed_image_sha256']=hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest() if n.image.packed_file else None
                nodes.append(row)
            links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]
        out[m.name]=digest({'properties':{k:str(m[k]) for k in m.keys()},'nodes':nodes,'links':links,'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'surface_render_method':getattr(m,'surface_render_method',None)})
    return out

def snapshot():
    out={}
    for o in bpy.context.scene.objects:
        row={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_local], 'properties':{k:str(o[k]) for k in o.keys()},'modifiers':[(m.name,m.type) for m in o.modifiers],'constraints':[(c.name,c.type) for c in o.constraints],'location':list(o.location),'scale':list(o.scale),'rotation_euler':list(o.rotation_euler),'rotation_quaternion':list(o.rotation_quaternion)}
        if o.type=='MESH':
            d=o.data;row.update(vertices=[list(v.co) for v in d.vertices],edges=[list(e.vertices) for e in d.edges],faces=[list(p.vertices) for p in d.polygons],material_slots=[m.name if m else None for m in d.materials],face_materials=[p.material_index for p in d.polygons],uv={u.name:[list(q.uv) for q in u.data] for u in d.uv_layers},normals=[list(p.normal) for p in d.polygons],smooth=[p.use_smooth for p in d.polygons],mesh_properties={k:str(d[k]) for k in d.keys()},uv_active=d.uv_layers.active.name if d.uv_layers.active else None,attributes={a.name:{'domain':a.domain,'type':a.data_type,'data':[str(x.value) if hasattr(x,'value') else list(x.vector) if hasattr(x,'vector') else list(x.color) if hasattr(x,'color') else str(x) for x in a.data]} for a in d.attributes if a.name not in ['position','UVMap','MetreScaled']})
        out[o.name]={'sha256':digest(row),'payload':row}
    return out
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def metre_uv(o,faces=None,section=False):
    from mathutils import Vector
    d=o.data;d.update();uv=d.uv_layers.get('MetreScaled') or d.uv_layers.new(name='MetreScaled')
    scale=d.materials[0].get('meters_per_tile_uv',[1,1])
    for p in d.polygons:
        if faces is not None and p.index not in faces:continue
        n=p.normal.normalized()
        if section:
            u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized()
        else:u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized()
        v=n.cross(u).normalized()
        for li in p.loop_indices:
            q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
def box(name,bounds,material,owner,section=False):
    x0,x1,y0,y1,z0,z1=bounds
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for y in [y0,y1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],[],F);me.update()
    import bmesh
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material);o['parent_design_id']=owner;o['derivative_scope']='bounded secondary engineering access';metre_uv(o,section=section);return o

def save(stem,owner,before,changed,extra):
    after=snapshot();assert material_snapshot()==BASE_MATERIALS,'Material/texture payload changed';unaffected=set(before)-set(changed)
    assert unaffected<=set(after)
    for n in unaffected:assert before[n]['sha256']==after[n]['sha256'], ('unaffected changed',n)
    removed=set(before)-set(after);added=set(after)-set(before)
    assert removed<=set(changed)
    report={'catalogue_id':owner,'new_unique_design_count':0,'changed_originals':changed,'removed':sorted(removed),'added':sorted(added),'material_graph_image_hashes':BASE_MATERIALS,'unaffected_objects':len(unaffected),'unaffected_hashes':{n:before[n]['sha256'] for n in sorted(unaffected)},'before_changed':{n:before[n] for n in changed},'after_changed':{n:after[n] for n in changed if n in after},**extra,'stage':'source/export only; actual triangle and runtime acceptance pending'}
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all()
    src=R/'source'/(stem+'.blend');out=R/'exports'/(stem+'.glb');assert not src.exists() and not out.exists(), 'Do not overwrite a surviving derivative'
    bpy.ops.wm.save_as_mainfile(filepath=str(src))
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if not o.get('preview_only',False):o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True,use_selection=True)
    report.update(source_sha256=sha(src),export_sha256=sha(out),source=str(src),export=str(out));verify_inputs()
    (R/'qa'/(stem+'.preservation.json')).write_text(json.dumps(report,indent=2)+'\n')

def core():
    bpy.ops.wm.open_mainfile(filepath=str(C/'assets/grand_pool_orchard_section/source/AST-CIR-005_forward_pool_market.blend'));before=snapshot();global BASE_MATERIALS;BASE_MATERIALS=material_snapshot()
    changed=['CORE_OuterWall_01_1','CORE_WallDado_01_1']
    for n,xb,yb in [(changed[0],(7.72,7.88),(6,11.76)),(changed[1],(7.635,7.685),(6.12,6.78))]:
        o=bpy.data.objects[n];v=[o.matrix_world@q.co for q in o.data.vertices]
        actual=[min(q[i] for q in v) for i in range(3)]+[max(q[i] for q in v) for i in range(3)]
        expected=[xb[0],-20,yb[0],xb[1],13,yb[1]];assert all(abs(a-b)<2e-5 for a,b in zip(actual,expected)),(n,actual)
        material=o.data.materials[0];bpy.data.objects.remove(o,do_unlink=True)
        for label,z0,z1 in [('N',-13,-1.8),('S',1.8,20)]:box('SEC_'+n+'_'+label,(*xb,*yb,z0,z1),material,'AST-CIR-005')
        if n==changed[0]:box('SEC_D02_STARBOARD_LINTEL',(*xb,8.7,11.76,-1.8,1.8),material,'AST-CIR-005')
    save('AST-CIR-005_forward_pool_market_engineering_access','AST-CIR-005',before,changed,{'aperture_world_xyz':[7.635,7.88,6,8.7,-433.8,-430.2],'root_world_xyz':[0,0,-432],'connector_floor':'compiler-owned, not source-authored'})

def door():
    bpy.ops.wm.open_mainfile(filepath=str(C/'assets/guest_entry_door/source/AST-DOR-002_wide.blend'));before=snapshot();global BASE_MATERIALS;BASE_MATERIALS=material_snapshot();changed=[];faces={}
    for o in bpy.context.scene.objects:
        n=o.name;mapping=None
        if n=='ENTRY_Header':mapping={2.5:2.7,2.66:2.86}
        elif n.startswith('ENTRY_PocketSkin_'):mapping={2.5:2.7}
        elif n.startswith('ENTRY_ClosedPocketEnd_'):mapping={2.64:2.84}
        elif n.startswith('ENTRY_FrontTrim_'):mapping={2.32:2.52,2.5:2.7}
        elif n.startswith('ENTRY_MovingPanel_'):mapping={2.445:2.645,2.485:2.685}
        elif n=='ENTRY_OverlappingMeetingSeal':mapping={2.485:2.685}
        if mapping is None:continue
        assert o.type=='MESH';changed.append(n);indices=set()
        for v in o.data.vertices:
            for old,new in mapping.items():
                if abs(v.co.z-old)<2e-6:v.co.z=new;indices.add(v.index);break
        assert indices,n
        fs=[p.index for p in o.data.polygons if any(i in indices for i in p.vertices)];faces[n]=fs;metre_uv(o,fs)
        old=before[n]['payload'];assert old['faces']==[list(p.vertices) for p in o.data.polygons]
        for i,v in enumerate(o.data.vertices):assert list(v.co)[:2]==old['vertices'][i][:2]
        for uv in o.data.uv_layers:
            untouched={li for p in o.data.polygons if p.index not in fs for li in p.loop_indices}
            for li in untouched:assert list(uv.data[li].uv)==old['uv'][uv.name][li]
    assert len(changed)==12,(len(changed),changed)
    save('AST-DOR-002_wide270','AST-DOR-002',before,changed,{'changed_metre_uv_faces':faces,'leaf_root_positions_unchanged':True,'clear_opening_m':[2.4,2.7],'leaf_width_m':1.18,'travel_m':1.24,'enclosure_width_m':5.16,'maximum_height_m':2.86,'runtime_ready':False,'required_new_contacts':{'height':2.65,'centre_y':1.36},'required_new_sweep':{'height':2.86,'centre_y':1.43}})

def shoulders():
    bpy.ops.wm.open_mainfile(filepath=str(C/'assets/secondary_engineering_section/source/AST-ENG-008.blend'));before=snapshot();global BASE_MATERIALS;BASE_MATERIALS=material_snapshot()
    mat=bpy.data.objects['visitor_west_wall0'].data.materials[0]
    for label,z0,z1 in [('N',-433.8,-433.2),('S',-430.8,-430.2)]:
        o=box('SEC_VISITOR_RECEIVING_SHOULDER_'+label,(8.31,8.69,6,8.7,z0,z1),mat,'AST-ENG-008',True);o['catalogue_id']='AST-ENG-008';o['collision_contract']='static_surface';o['preview_only']=False
    save('AST-ENG-008_receiving_shoulders','AST-ENG-008',before,[],{'fitting_world_xyz':[8.8,6,-432],'fitting_yaw_radians':1.5707963267948966,'original_surfaces_unchanged':175,'original_triangles_unchanged':3700,'new_shoulders':2,'new_triangles':24,'pocket_cavity_world_x':[8.745,8.855]})

def main():
    verify_inputs()
    if '--execute-in-parent-slot' not in sys.argv:raise SystemExit('Prepared only. Parent must allocate Blender slot and explicitly pass --execute-in-parent-slot')
    global bpy
    import bpy
    core();door();shoulders();verify_inputs()
if __name__=='__main__':main()
