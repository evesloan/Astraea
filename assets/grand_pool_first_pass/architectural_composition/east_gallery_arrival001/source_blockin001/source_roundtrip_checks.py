"""Pure reusable exact source roundtrip checks. No bpy, I/O or tolerances.
World-space roundtrip evidence is compared to the actual saved build snapshot.
Only the core's explicit identity-transform path is predicted from plan values;
retained transformed instances use their own recorded evaluated snapshot.
"""
import struct

def f32(value):
    return struct.unpack('<f',struct.pack('<f',float(value)))[0]

def predict_blender_local_from_godot(vertex):
    x,y,z=vertex
    return [f32(x),f32(-z),f32(y)]

def predict_godot_world_for_identity(vertex):
    # This is exactly the core builder's B -> identity matrix_world -> G path.
    # There are no translations, rotations, scales, parent transforms or extra
    # double-precision arithmetic to approximate in this path.
    x,by,bz=predict_blender_local_from_godot(vertex)
    return [x,bz,-by]

IDENTITY_4=[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
EXACT_FIELDS=('vertices_xyz','local_vertices_blender','matrix_world_blender',
              'faces','evaluated_triangles','uv_loops','material_indices',
              'material_states','source_transform')

def compare_reopened_parts(actual_parts,built_parts,part_names=None):
    """Exact saved-build equality; optional subset permits combined assemblies.

    Call with all parts for a complete combined gate, or with explicit core
    names while the combined wrapper separately handles retained objects.
    This helper imposes no whole-scene MESH/EMPTY count.
    """
    actual={p['name']:p for p in actual_parts};built={p['name']:p for p in built_parts}
    assert len(actual)==len(actual_parts),'Duplicate actual part names'
    assert len(built)==len(built_parts),'Duplicate saved-build part names'
    if part_names is None:
        assert set(actual)==set(built),('Saved/reopened part names differ',set(actual)^set(built))
        names=sorted(built)
    else:
        names=list(part_names);assert len(names)==len(set(names))
        assert set(names)<=set(actual) and set(names)<=set(built),'Missing requested part'
    results=[]
    for name in names:
        a,b=actual[name],built[name]
        for key in EXACT_FIELDS:
            assert key in a and key in b,(name,'Missing exact evidence',key)
            assert a[key]==b[key],(name,'Saved/reopened data differs',key)
        results.append(dict(name=name,saved_evaluated_geometry_exact=True,
                            saved_uv_loops_exact=True,saved_material_state_exact=True,
                            saved_local_vertices_and_transform_exact=True))
    return results

def verify_core_plan_conversion(actual_parts,plan_parts):
    """Verify explicit float32 conversion with no tolerance or guessed codec.

    This is intentionally core-only: it rejects nonidentity transforms rather
    than pretending Python doubles emulate transformed retained source meshes.
    """
    actual={p['name']:p for p in actual_parts};results=[]
    for row in plan_parts:
        a=actual[row['name']]
        assert a['matrix_world_blender']==IDENTITY_4,(row['name'],'Nonidentity core matrix requires a different explicit transform contract')
        t=a['source_transform'];assert t==dict(location=[0.,0.,0.],rotation_euler=[0.,0.,0.],scale=[1.,1.,1.]),(row['name'],'Unexpected core object transform')
        local=[predict_blender_local_from_godot(v)for v in row['vertices_xyz']]
        world=[predict_godot_world_for_identity(v)for v in row['vertices_xyz']]
        assert a['local_vertices_blender']==local,(row['name'],'Source-to-Blender float32 prediction differs')
        assert a['vertices_xyz']==world,(row['name'],'Identity-evaluated Godot prediction differs')
        results.append(dict(name=row['name'],plan_to_blender_float32_exact=True,
                            identity_world_frame_conversion_exact=True,
                            plan_already_float32=all(float(x)==f32(x)for v in row['vertices_xyz']for x in v)))
    return results
