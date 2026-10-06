"""Independent read-only Court A reopen QA; no saves, exports, engines or renders.

Pure inspection: python -B reopen_court_A_readonly.py --inspect
Parent-owned Blender slot: blender -b --python this.py -- --check
Only a successful source-only report is created beside the built scratch source.
Failure evidence is written exclusively in this new QA directory. Existing files
are never overwritten. No Blender work occurs on import or during --inspect.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, struct, sys, time
sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
R = D.parent
PRINT = R / 'printed_materials001'
OUT = PRINT / 'authored_preview001'
CAT = Path('/workspace/shared/astraea-catalogue-continuation-20261002')
HELPER = CAT / 'assets/grand_lantern_theater_section/source/firstpass_001/firstpass_common.py'
BUILDER = PRINT / 'build_court_A_source_printed_DRAFT.py'
EXPECTED_BUILDER = '0577a0336d26b8999bd86d97261e3b56d8623d695fb4003affd463047c06673c'
EXPECTED_HELPER = '6d115e349b0b2ec1999a70808a04f546d88038b081dab4fb8f09c5c3be920544'
EXPECTED_BASE = 'dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
MAT_SOURCES = [CAT / p for p in (
    'assets/furniture/AST-FUR-001_day_window_bench.blend',
    'assets/furniture/AST-FUR-002_day_reading_chair.blend',
    'assets/botanical_planter/AST-BOT-004.blend',
    'assets/botanical_understory/source/AST-BOT-002.blend')]
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
unsuffix = lambda s: re.sub(r'(?:\.\d{3})+$', '', s)


def require(condition, code, detail=None):
    if not condition:
        raise AssertionError(json.dumps({'gate': code, 'detail': detail}, default=str)[:1800])


def close(a, b, tolerance=2e-5):
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tolerance) for x, y in zip(a, b))
    return math.isfinite(float(a)) and abs(float(a) - float(b)) <= tolerance


def flatten(value):
    if isinstance(value, (list, tuple)):
        for x in value:
            yield from flatten(x)
    else:
        yield value


def identity(matrix):
    return close([list(r) for r in matrix], [[int(i == j) for j in range(4)] for i in range(4)], 1e-7)


def source_world(ob):
    # Works for unlinked collection definitions, independent of depsgraph state.
    return source_world(ob.parent) @ ob.matrix_parent_inverse @ ob.matrix_basis if ob.parent else ob.matrix_basis.copy()


def role_of(mat):
    return mat.get('astraea_material_role') or unsuffix(mat.name).removeprefix('ASTRAEA_')


def scalar_properties(value, omit=()):
    """Shader-affecting scalar/enum/array RNA values, with no name normalization."""
    out = {}
    for prop in value.bl_rna.properties:
        key = prop.identifier
        if key in set(omit) | {'rna_type'} or prop.type not in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            continue
        if key in {'is_updated', 'is_updated_data', 'is_updated_transform', 'users', 'session_uid', 'is_library_indirect', 'is_embedded_data', 'is_missing', 'is_runtime_data', 'tag'}:
            continue
        try:
            item = getattr(value, key)
            if isinstance(item, (str, bool, int, float)):
                out[key] = item
            elif isinstance(item, set):
                out[key] = sorted(item)
            else:
                out[key] = list(item)
        except (TypeError, AttributeError):
            continue
    return out


def image_record(im):
    require(im is not None and im.packed_file is not None, 'used_image_must_be_packed', im.name if im else None)
    packed = list(im.packed_files)
    require(len(packed) == 1, 'single_packed_texture_expected', im.name)
    return {
        'name': unsuffix(im.name), 'packed_sha256': hashlib.sha256(im.packed_file.data).hexdigest(),
        'packed_bytes': len(im.packed_file.data), 'size': list(im.size),
        'source': im.source, 'colorspace': im.colorspace_settings.name,
        'alpha_mode': im.alpha_mode, 'use_view_as_render': im.use_view_as_render,
        'is_float': im.is_float, 'channels': im.channels,
    }


def graph_record(mat, common_record):
    base = common_record(mat)
    base['name'] = unsuffix(base['name'])
    for n in base['nodes']:
        if 'image' in n:
            n['image']['name'] = unsuffix(n['image']['name'])
    def tree_record(tree, visiting):
        if tree is None:
            return None
        require(tree.as_pointer() not in visiting, 'recursive_material_node_group', mat.name)
        visiting = visiting | {tree.as_pointer()}
        nodes = []
        for n in tree.nodes:
            row = {'name': n.name, 'type': n.bl_idname,
                   'properties': scalar_properties(n, {'name', 'name_full', 'location', 'dimensions', 'width', 'width_hidden', 'height', 'select', 'show_options', 'show_preview', 'show_texture', 'hide'})}
            row['inputs'] = []
            for socket in n.inputs:
                v = getattr(socket, 'default_value', None)
                if v is not None:
                    try: v = v if isinstance(v, (str, int, float, bool)) else list(v)
                    except TypeError: v = str(v)
                row['inputs'].append({'identifier': socket.identifier, 'type': socket.bl_idname, 'default': v})
            if n.type == 'TEX_IMAGE':
                row['image'] = image_record(n.image) if n.image else None
                row['image_user'] = scalar_properties(n.image_user)
            if hasattr(n, 'color_ramp'):
                cr = n.color_ramp
                row['color_ramp'] = {'properties': scalar_properties(cr), 'elements': [[x.position, list(x.color)] for x in cr.elements]}
            if hasattr(n, 'mapping'):
                mp = n.mapping
                row['mapping'] = {'properties': scalar_properties(mp), 'curves': [[{'location': list(p.location), 'handle_type': p.handle_type} for p in curve.points] for curve in mp.curves]}
            if n.type == 'GROUP':
                row['group'] = tree_record(n.node_tree, visiting)
            row['outputs'] = [{'identifier': s.identifier, 'type': s.bl_idname,
                               'default': (list(s.default_value) if not isinstance(s.default_value, (int,float,str,bool)) else s.default_value)}
                              for s in n.outputs if hasattr(s, 'default_value')]
            nodes.append(row)
        return {'nodes': sorted(nodes, key=lambda x: x['name']),
                'links': sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in tree.links)}
    return {'common': base, 'material_properties': scalar_properties(mat, {'name', 'name_full', 'preview', 'asset_data', 'use_fake_user'}),
            'graph': tree_record(mat.node_tree if mat.use_nodes else None, set())}


def canonical_mesh(me, mesh_record):
    record = mesh_record(me)
    record['materials'] = [unsuffix(n) if n else None for n in record['materials']]
    return record


def closed_topology(me, name, Vector, support=None):
    edges = collections.defaultdict(list)
    faces = [list(p.vertices) for p in me.polygons]
    for fi, face in enumerate(faces):
        require(len(face) >= 3 and len(face) == len(set(face)), 'face_distinct_vertices', [name, fi])
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))].append((a, b, fi))
    require(all(len(v) == 2 and v[0][:2] == v[1][:2][::-1] for v in edges.values()), 'closed_opposite_directed_edges', name)
    # Separate connected components must each have positive signed volume.
    neighbors = collections.defaultdict(set)
    for uses in edges.values():
        a, b = uses[0][2], uses[1][2]
        neighbors[a].add(b); neighbors[b].add(a)
    unseen = set(range(len(faces))); volumes = []
    me.calc_loop_triangles()
    while unseen:
        todo = [next(iter(unseen))]; component = set()
        while todo:
            fi = todo.pop()
            if fi in component: continue
            component.add(fi); unseen.discard(fi)
            todo.extend(neighbors[fi] - component)
        origin = me.vertices[faces[min(component)][0]].co
        volume = 0.0
        for t in me.loop_triangles:
            if t.polygon_index in component:
                a, b, c = [me.vertices[i].co - origin for i in t.vertices]
                volume += a.dot(b.cross(c)) / 6
        require(volume > 1e-13, 'positive_component_signed_volume', [name, volume])
        volumes.append(volume)
    normal_min = 1.0
    if support is not None:
        sides = support['sides']; rings = len(support['centerline'])
        require(len(me.vertices) == sides * rings and len(faces) == sides*(rings-1)+2, 'support_ring_topology', name)
        centers = [sum((me.vertices[i*sides+j].co for j in range(sides)), Vector()) / sides for i in range(rings)]
        for fi, poly in enumerate(me.polygons):
            if fi < sides*(rings-1):
                ring = fi // sides
                direction = poly.center - (centers[ring] + centers[ring+1])/2
            elif fi == len(faces)-2:
                direction = centers[0] - centers[1]
            else:
                direction = centers[-1] - centers[-2]
            d = poly.normal.dot(direction.normalized())
            require(d > 0.0, 'every_closed_support_face_outward', [name, fi, d])
            normal_min = min(normal_min, d)
    return {'closed_components': len(volumes), 'positive_component_volumes_m3': volumes,
            'closed_support_minimum_outward_normal_dot': normal_min if support else None}


def open_leaf_topology(me, name):
    uses = collections.defaultdict(list)
    for f in me.polygons:
        vs = list(f.vertices)
        for a,b in zip(vs,vs[1:]+vs[:1]): uses[tuple(sorted((a,b)))].append((a,b))
    require(all(len(v) <= 2 for v in uses.values()), 'leaf_nonmanifold_edge', name)
    require(all(len(v)==1 or v[0]==v[1][::-1] for v in uses.values()), 'leaf_consistent_normals', name)
    boundary = [e for e,v in uses.items() if len(v)==1]
    degrees = collections.Counter(i for e in boundary for i in e)
    require(boundary and all(v==2 for v in degrees.values()), 'leaf_boundary_closed_loop', name)
    require(len(me.vertices)-len(uses)+len(me.polygons)==1, 'whole_open_leaf_disk_euler', name)
    require(len({v.index for v in me.vertices})==len({i for f in me.polygons for i in f.vertices}), 'leaf_no_loose_vertices', name)
    return {'boundary_edges':len(boundary),'euler_characteristic':1}


def polygon_distance(point, poly):
    x,y=point; inside=False; distance=float('inf')
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ax,ay=a; bx,by=b; dx=bx-ax; dy=by-ay
        t=max(0.,min(1.,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
        distance=min(distance,math.hypot(x-ax-t*dx,y-ay-t*dy))
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: inside=not inside
    return distance if inside else -distance


def inspect():
    c=read(R/'COURT_A_GEOMETRY_CONTRACT.json'); f=read(R/'FULLER_REAR_MASS_CANDIDATE.json')
    p=read(PRINT/'PRINTED_MATERIALS_CONTRACT.json')
    names=[r['name'] for r in c['objects']]+[r['id'] for r in c['retained_instances']]+[r['name'] for r in f['asset']['parts']]+[r['name'] for r in [p['display_plate']]+p['pieces']]
    require(len(names)==len(set(names)), 'contract_name_bijection')
    require(all(len(n.encode())<=63 for n in names), 'no_truncated_contract_names')
    require(sha(BUILDER)==EXPECTED_BUILDER, 'frozen_source_builder_sha256')
    require(sha(HELPER)==EXPECTED_HELPER, 'frozen_common_helper_sha256')
    return {'status':'PREPARED_NOT_EXECUTED','source':str(OUT/c['standalone_source_proposal']),
            'new_base_pieces':len(c['objects']),'retained_instances':len(c['retained_instances']),
            'optional_fuller_pieces':len(f['asset']['parts']),'printed_pieces':1+len(p['pieces']),
            'maximum_contract_name_bytes':max(len(n.encode()) for n in names),
            'source_exists':(OUT/c['standalone_source_proposal']).exists(),'builder_sha256':sha(BUILDER),
            'limits':['No engine or Blender run in inspection','No geometric, load, visual, runtime or broad-species acceptance']}


def check():
    pre=inspect(); contract=read(R/'COURT_A_GEOMETRY_CONTRACT.json')
    screen=read(R/'COURT_A_PURE_SCREEN.json'); printed=read(PRINT/'PRINTED_MATERIALS_CONTRACT.json')
    fuller=read(R/'FULLER_REAR_MASS_CANDIDATE.json'); gate=read(R/'PARENT_SOURCE_BUILD_GATE.json')
    source=OUT/contract['standalone_source_proposal']; report_path=OUT/'REOPEN_REPORT.json'
    require(not report_path.exists(), 'never_overwrite_reopen_report')
    require(gate['parent_authorized_scratch_source_job'] is True and gate['production_install_authorized'] is False, 'scratch_parent_gate')
    require(sha(contract['base_source'])==contract['base_source_sha256']==EXPECTED_BASE, 'protected_base_before')
    require(screen['contract_sha256']==sha(R/'COURT_A_GEOMETRY_CONTRACT.json') and not screen['failures'] and not screen['warnings'], 'frozen_pure_screen')
    build=read(OUT/'BUILD_REPORT.json'); initial_sha=sha(source)
    require(build['source']==str(source) and build['sha256']==initial_sha, 'saved_source_build_sha256')
    require(build['protected_base_sha256']==EXPECTED_BASE and build['audience_chairs_rebuilt_or_exported']==0 and build['runtime_exported'] is False, 'build_scope')
    require(build['printed_materials_contract_sha256']==sha(PRINT/'PRINTED_MATERIALS_CONTRACT.json'), 'printed_contract_pin')
    require(build['fuller_mass_included']==bool(gate.get('include_fuller_rear_mass',False)), 'optional_fuller_gate')
    import bpy
    from mathutils import Matrix, Vector
    sys.path.insert(0,str(HELPER.parent))
    from firstpass_common import bvec,wvec,mesh_record,material_record,digest,image_nodes,verify_new_geometry
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    original_objects=list(bpy.data.objects); original_materials=list(bpy.data.materials)
    scene=bpy.context.scene; collection=bpy.data.collections.get('A4_COMPLETED_COURT'); root=bpy.data.objects.get('A4_SOURCE_ONLY')
    require(collection is not None and root is not None, 'court_root_and_collection')
    require(root.parent is None and identity(root.matrix_basis) and root['standalone_addition'] is True, 'identity_source_root')
    require(root['base_source_sha256']==EXPECTED_BASE and root['visual_acceptance'] is False and root['runtime_installed'] is False, 'unaccepted_source_only_flags')
    require(scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1, 'metre_units')
    require(not any(o.type in {'LIGHT','CAMERA'} or o.get('existing_family')=='AST-CUL-003' or o.get('retained_family')=='AST-CUL-003' for o in original_objects), 'no_lights_cameras_or_chair_definitions')
    require(all('AST-CUL-003' not in (o.name+' '+str(o.get('firstpass_retained_source_object',''))) for o in original_objects), 'no_audience_chair_rebuild')
    expected_rows=[]
    for r in contract['objects']:
        expected_rows.append((r,'architecture',None))
    if build['fuller_mass_included']:
        origin=fuller['asset']['position_xyz']
        for p in fuller['asset']['parts']:
            at=0;uv=[]
            for face in p['faces']:uv.append(p['loop_uvs'][at:at+len(face)]);at+=len(face)
            expected_rows.append(({'name':p['name'],'vertices_world':[[origin[0]+v[0],origin[1]+v[2],origin[2]-v[1]] for v in p['vertices']],
                                  'faces':p['faces'],'face_uv':uv,'material_family':p['material_role'],'surface_kind':p['surface_kind']},p['surface_kind'],p))
    for r in [printed['display_plate']]+printed['pieces']:expected_rows.append((r,'printed',None))
    expected_mesh_names={r['name'] for r,_,_ in expected_rows}
    require({o.name for o in collection.objects if o.type=='MESH'}==expected_mesh_names, 'exact_new_mesh_name_bijection')
    require({o.name for o in collection.objects}==expected_mesh_names|{r['id'] for r in contract['retained_instances']}|{root.name}, 'exact_court_object_bijection')
    require({o.name for o in scene.objects}=={o.name for o in collection.objects}, 'standalone_scene_only_court')
    require(set(build['mesh_uv_fingerprints'])==expected_mesh_names,'build_fingerprint_name_bijection')
    geometry=[]; new_material_set=set()
    for row,kind,part in expected_rows:
        ob=bpy.data.objects.get(row['name']); me=ob.data
        require(ob.parent==root and identity(ob.matrix_basis) and identity(ob.matrix_parent_inverse), 'new_mesh_world_identity',row['name'])
        require(not ob.modifiers and not ob.constraints and ob.animation_data is None, 'no_hidden_geometry_modifiers',row['name'])
        require([list(v.co) for v in me.vertices]==[[f32(x) for x in bvec(v)] for v in row['vertices_world']], 'exact_float32_vertices',row['name'])
        require([list(p.vertices) for p in me.polygons]==row['faces'],'exact_ordered_faces',row['name'])
        require(len(me.uv_layers)==1 and me.uv_layers[0].name=='MetricUV' and me.uv_layers[0].active_render,'metric_uv_layer',row['name'])
        actual_uv=[[list(me.uv_layers[0].data[i].uv) for i in p.loop_indices] for p in me.polygons]
        expected_uv=[[[f32(x) for x in v] for v in face] for face in row['face_uv']]
        require(actual_uv==expected_uv,'exact_float32_per_face_uv_loops',row['name'])
        expected_roles=row.get('face_material_roles') or [row['material_family']]*len(me.polygons)
        roles=[role_of(me.materials[p.material_index]) for p in me.polygons]
        require(roles==expected_roles,'exact_per_face_material_roles',row['name'])
        require([role_of(m) for m in me.materials]==list(dict.fromkeys(expected_roles)),'material_slot_role_order',row['name'])
        new_material_set.update(me.materials)
        if 'semantic_id' in row:require(ob.get('semantic_id')==row['semantic_id'],'exact_semantic_id',row['name'])
        if 'collides' in row:require(ob.get('collides')==row['collides'],'collision_metadata',row['name'])
        require(digest(mesh_record(me))==build['mesh_uv_fingerprints'][row['name']],'saved_new_mesh_uv_fingerprint',row['name'])
        topo=open_leaf_topology(me,row['name']) if kind=='open_shaped_leaf' else closed_topology(me,row['name'],Vector,part['shape_controls'] if kind=='closed_support' else None)
        geometry.append({'name':row['name'],'kind':kind,'vertices':len(me.vertices),'faces':len(me.polygons),'semantic_id':ob.get('semantic_id'),**topo})
    degeneracy=verify_new_geometry(bpy,sorted(expected_mesh_names))
    # Capture actual reopened material graphs before independent library appends.
    used={m for o in original_objects if o.type=='MESH' for m in o.data.materials if m}
    actual_graphs={m:graph_record(m,material_record) for m in used}
    # Every image used anywhere in a retained prototype is covered, not just new mats.
    packed_images=[]
    for m in sorted(used,key=lambda m:m.name):
        imgs=[image_record(n.image) for n in image_nodes(m.node_tree if m.use_nodes else None)]
        packed_images.append({'material':m.name,'role':role_of(m),'images':imgs})
    # Native libraries appended only to memory; this file is never saved again.
    libraries={str(Path(r['source'])):r['source_sha256'] for r in contract['retained_instances']}
    for path in MAT_SOURCES:
        libraries.setdefault(str(path),sha(path))
    for record in build['material_provenance'].values():
        if 'source' in record:require(libraries.get(record['source'])==record['source_sha256'],'native_material_source_hash',record['source'])
    native_materials=[]; native_objects={}; library_audit=[]
    for path,pin in sorted(libraries.items()):
        require(sha(path)==pin,'native_library_immutable_hash',path)
        with bpy.data.libraries.load(path,link=False) as (src,dst):
            mat_names=list(src.materials); dst.materials=mat_names
            object_names=list(src.objects) if path in {r['source'] for r in contract['retained_instances']} else []
            dst.objects=object_names
        require(len(dst.materials)==len(mat_names) and all(dst.materials),'native_material_append',path)
        native_materials.extend((path,n,m,graph_record(m,material_record)) for n,m in zip(mat_names,dst.materials))
        native_objects[path]=dict(zip(object_names,dst.objects))
        library_audit.append({'source':path,'sha256':pin,'materials':len(mat_names),'objects':len(object_names)})
    retained_graph_checks=[]; paper_graph_checks=[]
    for mat,actual in actual_graphs.items():
        role=role_of(mat)
        if role in printed['materials']:
            require(material_record(mat)==build['paper_material_graphs'][role],'paper_graph_exact_build_reopen',mat.name)
            spec=printed['materials'][role]; bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            for field,socket in [('roughness','Roughness'),('metallic','Metallic'),('coat_weight','Coat Weight'),('transmission_weight','Transmission Weight'),('emission_strength','Emission Strength'),('specular_ior_level','Specular IOR Level')]:
                require(close(bs.inputs[socket].default_value,spec[field],1e-7),'paper_recipe_socket',[role,socket])
            images=[image_record(n.image) for n in image_nodes(mat.node_tree)]
            require(mat.get('original_paper_material') is True and mat.get('retained_fabric_relabelled') is False,'paper_identity',role)
            require(len(images)==int(bool(spec.get('image'))),'paper_image_count',role)
            if images:require(images[0]['packed_sha256']==spec['image_sha256'] and images[0]['colorspace']=='sRGB','original_paper_image',role)
            paper_graph_checks.append({'material':mat.name,'role':role,'graph_sha256':digest(actual)})
        else:
            matches=[(p,n) for p,n,m,g in native_materials if g==actual]
            require(bool(matches),'exact_independent_native_material_graph',{'material':mat.name,'role':role})
            if mat in new_material_set and role in build['material_provenance']:
                provenance=build['material_provenance'][role]
                require((provenance['source'],provenance['requested_datablock']) in matches,'retained_material_provenance_graph',[mat.name,provenance])
            if role in contract['material_contracts']:
                hashes=[image_record(n.image)['packed_sha256'] for n in image_nodes(mat.node_tree)]
                require(contract['material_contracts'][role]['sha256'] in hashes,'mapped_material_texture_contract',role)
            retained_graph_checks.append({'material':mat.name,'role':role,'graph_sha256':digest(actual),'native_matches':matches})
    require({r['role'] for r in paper_graph_checks}==set(printed['materials']),'all_four_paper_roles')
    definitions={r['asset']:r for r in build['retained_definitions']}
    require(set(definitions)=={r['asset'] for r in contract['retained_instances']},'retained_definition_asset_bijection')
    prototype_checks=[]; instance_checks=[]; collection_for_asset={}
    prototype_objects=set()
    for row in contract['retained_instances']:
        ob=bpy.data.objects.get(row['id']); col=ob.instance_collection
        require(ob.type=='EMPTY' and ob.instance_type=='COLLECTION' and col is not None,'retained_collection_instance',row['id'])
        require(ob.parent==root and identity(ob.matrix_parent_inverse) and list(ob.scale)==[1,1,1], 'unscaled_retained_instance',row['id'])
        expected=Matrix.Translation(Vector([f32(v) for v in bvec(row['position_world'])])) @ Matrix.Rotation(f32(row['yaw_radians']),4,'Z')
        require(close([list(r) for r in ob.matrix_basis],[list(r) for r in expected],2e-7),'actual_retained_instance_matrix',row['id'])
        require(ob.get('source_sha256')==row['source_sha256'] and ob.get('retained_family')==row['asset'] and ob.get('whole_plant_or_furniture_scale_unchanged') is True,'retained_instance_source_properties',row['id'])
        require(not ob.constraints and ob.animation_data is None,'static_retained_instance',row['id'])
        instance_checks.append({'id':row['id'],'asset':row['asset'],'matrix_basis':[list(r) for r in ob.matrix_basis],'collection':col.name})
        if row['asset'] in collection_for_asset:
            require(collection_for_asset[row['asset']]==col,'single_prototype_per_asset',row['asset']); continue
        collection_for_asset[row['asset']]=col
        report=definitions[row['asset']]
        require(report['source']==row['source'] and report['source_sha256']==row['source_sha256'],'retained_definition_source',row['asset'])
        named={}
        for obj in col.objects:
            key=obj.get('firstpass_retained_source_object')
            require(key and key not in named,'prototype_source_name_bijection',row['asset'])
            require(obj.name==key or re.fullmatch(re.escape(key)+r'\.\d{3}',obj.name),'prototype_names_not_truncated',[key,obj.name])
            named[key]=obj; prototype_objects.add(obj)
        require(set(named)==set(report['source_objects']),'prototype_report_source_bijection',row['asset'])
        require({n for n,o in named.items() if o.type=='MESH'}==set(report['retained_mesh_uv_fingerprints']),'prototype_mesh_report_bijection',row['asset'])
        native=native_objects[row['source']]
        source_root=native.get(row['asset'])
        def belongs(obj):
            if source_root is None:return True
            while obj:
                if obj==source_root:return True
                obj=obj.parent
            return False
        expected_members={n for n,o in native.items() if o and o.type in {'MESH','EMPTY','CURVE','FONT'} and belongs(o)}
        require(set(named)==expected_members,'independent_native_member_bijection',row['asset'])
        reverse={o:n for n,o in native.items()}
        for name,actual in named.items():
            native_ob=native[name]
            require(actual.type==native_ob.type and [list(r) for r in actual.matrix_basis]==[list(r) for r in native_ob.matrix_basis] and [list(r) for r in actual.matrix_parent_inverse]==[list(r) for r in native_ob.matrix_parent_inverse], 'native_prototype_exact_source_matrices',[row['asset'],name])
            require((actual.parent.get('firstpass_retained_source_object') if actual.parent else None)==(reverse[native_ob.parent] if native_ob.parent else None),'native_prototype_parent',[row['asset'],name])
            require(not actual.modifiers and not actual.constraints and actual.animation_data is None,'no_unevaluated_retained_geometry',[row['asset'],name])
            if actual.type=='MESH':
                require(digest(mesh_record(actual.data))==report['retained_mesh_uv_fingerprints'][name], 'retained_report_mesh_uv_fingerprint',[row['asset'],name])
                require(canonical_mesh(actual.data,mesh_record)==canonical_mesh(native_ob.data,mesh_record),'independent_native_mesh_uv_materials',[row['asset'],name])
            prototype_checks.append({'asset':row['asset'],'source_name':name,'generated_name':actual.name,'type':actual.type})
    require(set(original_objects)==set(collection.objects)|prototype_objects,'no_unexpected_standalone_objects')
    # Actual source matrices/meshes against the frozen soil receivers. Existing
    # rear basin itself remains in the separately hash-verified base source.
    soils={s['id']:s for s in contract['soil_receivers']}; root_checks=[]
    frozen_roots={r['instance']:r for r in screen['roots']}
    actual_root_circles=[]
    for row in contract['retained_instances']:
        if 'root_receiver' not in row:continue
        ob=bpy.data.objects[row['id']]; soil=soils[row['root_receiver']]
        require(ob.get('root_receiver')==soil['id'] and ob.get('collides') is False,'plant_receiver_metadata',row['id'])
        origin=wvec(source_world(ob).translation); points=[]
        for proto in ob.instance_collection.objects:
            if proto.type=='MESH':
                matrix=source_world(ob) @ Matrix.Translation(-ob.instance_collection.instance_offset) @ source_world(proto)
                points.extend(wvec(matrix @ v.co) for v in proto.data.vertices)
        basal=[p for p in points if p[1]<=soil['top_y']+1e-5]
        require(basal,'actual_source_basal_vertices',row['id'])
        margins=[polygon_distance([p[0],p[2]],soil['polygon_xz']) for p in points]
        require(min(margins)>=-.001 and min(polygon_distance([p[0],p[2]],soil['polygon_xz']) for p in basal)>=-.0001,'actual_plant_vertices_in_soil_projection',row['id'])
        root_margin=polygon_distance([origin[0],origin[2]],soil['polygon_xz'])
        require(root_margin>=row['soil_patch_radius_m']-2e-5 and root_margin>=row['root_radius_m']-2e-5,'actual_source_root_and_patch_fit',row['id'])
        embed=soil['top_y']-origin[1];depth=soil['top_y']-soil['bottom_y']
        require(close(embed,frozen_roots[row['id']]['embed_m'],2e-5) and depth>=row['minimum_soil_depth_m'],'actual_root_embed_and_soil_depth',row['id'])
        root_checks.append({'id':row['id'],'soil':soil['id'],'actual_root_world':list(origin),'embed_m':embed,'soil_depth_m':depth,'source_vertices_tested':len(points),'basal_vertices_tested':len(basal),'minimum_foliage_projection_margin_m':min(margins)})
        actual_root_circles.append({'id':row['id'],'xz':[origin[0],origin[2]],'radius':row['root_radius_m']})
    fuller_checks=[]
    if build['fuller_mass_included']:
        soil=soils[fuller['asset']['support']]
        for part in fuller['asset']['parts']:
            ob=bpy.data.objects[part['name']];points=[wvec(source_world(ob)@v.co) for v in ob.data.vertices]
            margin=min(polygon_distance([p[0],p[2]],soil['polygon_xz']) for p in points)
            require(margin>=-2e-5,'fuller_all_actual_vertices_within_soil',part['name'])
        byname={p['name']:p for p in fuller['asset']['parts']}
        for rr in fuller['fit']['roots']:
            obj=bpy.data.objects[rr['part']];sides=byname[rr['part']]['shape_controls']['sides']
            ring=[wvec(source_world(obj)@v.co) for v in list(obj.data.vertices)[:sides]]
            center=[sum(p[i] for p in ring)/len(ring) for i in range(3)]
            require(close(center,rr['world'],2e-5),'fuller_actual_root_center',rr['part'])
            require(close(soil['top_y']-center[1],rr['embed_m'],2e-5) and soil['top_y']-soil['bottom_y']>=rr['minimum_proposed_soil_depth_m'],'fuller_root_embed_depth',rr['part'])
            fuller_checks.append({'part':rr['part'],'actual_center_world':center,'embed_m':soil['top_y']-center[1]})
            actual_root_circles.append({'id':rr['part'],'xz':[center[0],center[2]],'radius':rr['root_radius_m']})
    all_circles=[r for r in screen['all_preserved_and_new_root_collars']['circles'] if r['retained']]+actual_root_circles
    root_clearances=[]
    for i,a in enumerate(all_circles):
        for b in all_circles[i+1:]:
            if a.get('retained') and b.get('retained'):continue
            clearance=math.dist(a['xz'],b['xz'])-a['radius']-b['radius']
            require(clearance>=-.0001,'actual_source_root_vs_preserved_collar',[a['id'],b['id'],clearance])
            root_clearances.append(clearance)
    # Printed reading directions are checked from actual vertices and UVs.
    print_checks=[]
    for row in [printed['display_plate']]+printed['pieces']:
        ob=bpy.data.objects[row['name']]; index=row['printed_face_index']
        if index is None:continue
        face=ob.data.polygons[index];normal=wvec(face.normal)
        expected_normal=row.get('front_normal_world',[0,1,0])
        require(close(normal,expected_normal,1e-6),'printed_front_normal',row['name'])
        uv=[ob.data.uv_layers[0].data[i].uv for i in face.loop_indices]
        verts=[wvec(ob.data.vertices[i].co) for i in face.vertices]
        corners={(round(float(p[0])),round(float(p[1]))):Vector(v) for p,v in zip(uv,verts)}
        require(set(corners)=={(0,0),(1,0),(1,1),(0,1)},'one_full_artwork_uv',row['name'])
        right=(corners[(1,0)]-corners[(0,0)]).normalized();top=(corners[(0,1)]-corners[(0,0)]).normalized()
        require(close(list(right),[1,0,0],1e-6),'text_right_world_positive_x',row['name'])
        require(close(list(top),row.get('printed_top_direction_world',[0,0,-1]),1e-6),'printed_top_direction',row['name'])
        image_role=row['face_material_roles'][index]
        require(ob.get('original_art_sha256')==printed['materials'][image_role]['image_sha256'],'printed_object_art_hash',row['name'])
        print_checks.append({'name':row['name'],'front_normal_world':list(normal),'text_right_world':list(right),'image_top_world':list(top)})
    require(len(print_checks)==4 and len(printed['pieces'])==9 and len(printed['stacks'])==3,'one_plate_three_stack_images')
    # Contact witnesses sample actual retained triangles (all corners, edges and
    # interior of the rectangle). Exact template fidelity is verified above.
    contacts=[]
    for stack in printed['stacks']:
        support=bpy.data.objects[stack['source_support']]; triangles=[]
        for proto in support.instance_collection.objects:
            if proto.type!='MESH':continue
            matrix=source_world(support) @ Matrix.Translation(-support.instance_collection.instance_offset) @ source_world(proto)
            proto.data.calc_loop_triangles()
            for tri in proto.data.loop_triangles:
                mat=proto.data.materials[proto.data.polygons[tri.polygon_index].material_index]
                if role_of(mat)!='warm_stone':continue
                pts=[wvec(matrix@proto.data.vertices[v].co) for v in tri.vertices]
                if max(p[1] for p in pts)-min(p[1] for p in pts)<2e-5:triangles.append(pts)
        bottom=bpy.data.objects[stack['piece_names'][0]];verts=[wvec(v.co) for v in bottom.data.vertices]
        lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
        def supports(x,z):
            for t in triangles:
                if max(abs(p[1]-lo[1]) for p in t)>2e-5:continue
                a,b,c=[(p[0],p[2]) for p in t]
                den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                if abs(den)<1e-14:continue
                u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(z-c[1]))/den
                v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(z-c[1]))/den
                if min(u,v,1-u-v)>=-1e-5:return True
            return False
        for i in range(9):
            for j in range(9):require(supports(lo[0]+(hi[0]-lo[0])*i/8,lo[2]+(hi[2]-lo[2])*j/8),'actual_printed_stack_triangle_support',stack['id'])
        interfaces=[]
        for first,second in zip(stack['piece_names'],stack['piece_names'][1:]):
            top=max(wvec(v.co)[1] for v in bpy.data.objects[first].data.vertices)
            bottom_y=min(wvec(v.co)[1] for v in bpy.data.objects[second].data.vertices)
            require(top==bottom_y,'exact_stack_interface',stack['id']);interfaces.append(top)
        contacts.append({'stack':stack['id'],'source_support':stack['source_support'],'actual_bottom_y':lo[1],'actual_support_triangle_witnesses':81,'interface_planes_world_y':interfaces,'limitation':'81 grid witnesses, not continuous support/load certification'})
    require(sha(source)==initial_sha and sha(contract['base_source'])==EXPECTED_BASE,'sources_unchanged_after_qa')
    for library in library_audit:require(sha(library['source'])==library['sha256'],'native_libraries_unchanged_after_qa',library['source'])
    result={'status':'PASS_SOURCE_ONLY','source':str(source),'sha256':initial_sha,'source_resaved':False,'script_sha256':sha(__file__),
            'contract_sha256':sha(R/'COURT_A_GEOMETRY_CONTRACT.json'),'pure_screen_sha256':sha(R/'COURT_A_PURE_SCREEN.json'),
            'build_report_sha256':sha(OUT/'BUILD_REPORT.json'),'printed_contract_sha256':sha(PRINT/'PRINTED_MATERIALS_CONTRACT.json'),
            'protected_base_sha256':EXPECTED_BASE,'audience_chairs_rebuilt_or_exported':0,'runtime_exported':False,
            'architecture_count':len(contract['objects']),'retained_instance_count':len(instance_checks),'fuller_count':len(fuller['asset']['parts']) if build['fuller_mass_included'] else 0,
            'printed_closed_count':10,'geometry':geometry,'finite_nondegenerate_triangle_uv_checks':degeneracy,
            'instance_matrices':instance_checks,'prototype_generated_name_bijection':prototype_checks,'native_libraries':library_audit,
            'retained_material_graph_checks':retained_graph_checks,'paper_material_graph_checks':paper_graph_checks,
            'all_used_material_packed_images':packed_images,'plant_root_soil_checks':root_checks,'fuller_root_checks':fuller_checks,
            'actual_root_collar_pairs':len(root_clearances),'minimum_actual_to_any_root_edge_clearance_m':min(root_clearances),
            'printed_front_orientation_checks':print_checks,'stack_actual_source_contact_witnesses':contacts,
            'pending':['Actual composition and artwork legibility review','Source archival/retention handoff','Continuous contacts and physical load certification','Runtime export/import/collision/physics verification','Six-species circulation and reach verification'],
            'limits':['Read-only source fidelity checks only; no visual/runtime/native acceptance','Old soil and old collars are frozen pure-contract receivers tied to the unchanged base hash; no old assembly or chairs loaded/rebuilt','New mesh floats and UVs are compared exactly after float32 conversion; source instance matrices use stated 2e-7 tolerance','Source contact witnesses do not establish load capacity or continuous full-area support','No route simulation, joint-contact/leaf support penetration test, botanical growth model or engine is run']}
    with report_path.open('x') as handle:json.dump(result,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'status':result['status'],'source_sha256':initial_sha,'architecture':len(contract['objects']),'retained_instances':len(instance_checks),'fuller':result['fuller_count'],'printed':10,'used_materials':len(used),'report':str(report_path)}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inspect',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    if not args.check:print(json.dumps(inspect(),indent=2));return
    try:check()
    except Exception as error:
        failure={'status':'FAIL_SOURCE_ONLY_CHECK','exception_type':type(error).__name__,'detail':str(error),'script_sha256':sha(__file__),'source_resaved':False}
        target=D/('REOPEN_FAILURE_'+str(time.time_ns())+'.json')
        with target.open('x') as handle:json.dump(failure,handle,indent=2);handle.write('\n')
        print(json.dumps({'status':failure['status'],'detail':str(error),'evidence':str(target)}))
        raise


if __name__=='__main__':main()
