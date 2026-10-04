"""Shared original utility-port geometry, revision utility-port-01.

Blender-only helper. add_flange(name, face, outward, materials) returns
{'objects': [...], 'record': {...}}. face is the FRONT mating-face centre,
outward is the unit port normal in Blender Z-up asset-source coordinates.
Hardware and the whole flange are behind face. All generated mesh UV layers
are named metric_material_uv. Material dict is unchanged staff_materials.materials().
The helper creates a genuine open bore, six Boolean-drilled bolt holes, a
rear-only captive fastener pattern and a hollow neck. No rating is implied.
"""
import math, json
import bpy, bmesh
from mathutils import Vector

REVISION='utility-port-01'
BORE_DIAMETER=.16
PIPE_OD=.20
FLANGE_OD=.32
FLANGE_THICKNESS=.035
BOLT_CIRCLE_DIAMETER=.26
BOLT_HOLE_DIAMETER=.018
BOLT_COUNT=6
RING_SEGMENTS=48

def exchange(p):
    return [float(p[0]),float(p[2]),float(-p[1])]

def basis(outward):
    if len(outward)!=3 or not all(math.isfinite(float(x)) for x in outward):raise ValueError('Port outward must be a finite 3-vector')
    n=Vector(outward)
    if n.length<1e-10:raise ValueError('Port outward must be non-zero')
    n.normalize()
    seed=Vector((0,0,1)) if abs(n.z)<.99 else Vector((0,1,0))
    u=(seed-n*seed.dot(n)).normalized()
    return n,u,n.cross(u).normalized()

def metric_uv(ob, material):
    me=ob.data
    while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
    uv=me.uv_layers.new(name='metric_material_uv')
    size=material.get('meters_per_tile_uv',(.75,.75))
    for f in me.polygons:
        axis=max(range(3),key=lambda j:abs(f.normal[j])); axes=[j for j in range(3) if j!=axis]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(p[axes[0]]/size[0],p[axes[1]]/size[1])
    return ob

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    me.materials.append(material);ob['material_role']=material.get('astraea_material_role',material.name)
    metric_uv(ob,material)
    return ob

def annular(name,face,outward,stations,material,segments=RING_SEGMENTS):
    """Closed hollow revolved section; stations are (axial_offset,inner_radius,outer_radius)."""
    p=Vector(face);n,u,v=basis(outward);verts=[];faces=[]
    for s,ri,ro in stations:
        for r in (ro,ri):
            verts.extend(tuple(p+n*s+r*(u*math.cos(2*math.pi*i/segments)+v*math.sin(2*math.pi*i/segments))) for i in range(segments))
    k2=2*segments
    for k in range(len(stations)-1):
        a=k*k2;b=(k+1)*k2
        for i in range(segments):
            j=(i+1)%segments
            faces.extend([(a+i,a+j,b+j,b+i),(a+segments+j,a+segments+i,b+segments+i,b+segments+j)])
    for i in range(segments):
        j=(i+1)%segments;a=(len(stations)-1)*k2
        faces.extend([(j,i,segments+i,segments+j),(a+i,a+j,a+segments+j,a+segments+i)])
    return mesh(name,verts,faces,material)

def solid_cylinder(name,a,b,r,material,segments=12):
    a,b=Vector(a),Vector(b);n,u,v=basis(b-a);verts=[]
    for p in(a,b):verts.extend(tuple(p+r*(u*math.cos(2*math.pi*i/segments)+v*math.sin(2*math.pi*i/segments))) for i in range(segments))
    faces=[(i,(i+1)%segments,segments+(i+1)%segments,segments+i) for i in range(segments)]
    faces += [tuple(reversed(range(segments))),tuple(segments+i for i in range(segments))]
    return mesh(name,verts,faces,material)

def port_record(name,face,outward):
    n,u,v=basis(outward);p=Vector(face)
    centres=[p+BOLT_CIRCLE_DIAMETER/2*(u*math.cos(2*math.pi*i/BOLT_COUNT)+v*math.sin(2*math.pi*i/BOLT_COUNT)) for i in range(BOLT_COUNT)]
    return {'name':name,'interface_revision':REVISION,'datum':'bare front mating-face centre; hardware lies behind this plane',
      'source_frame':'Blender Z-up asset source, metres','position_blender_source_m':list(face),'normal_blender_source':list(n),'radial_zero_blender_source':list(u),
      'exchange_frame':'GLB Y-up asset exchange, metres','position_gltf_yup_m':exchange(face),'normal_gltf_yup':exchange(n),'radial_zero_gltf_yup':exchange(u),
      'bore_diameter_m':BORE_DIAMETER,'pipe_outer_diameter_m':PIPE_OD,'flange_outer_diameter_m':FLANGE_OD,'flange_thickness_m':FLANGE_THICKNESS,
      'bolt_circle_diameter_m':BOLT_CIRCLE_DIAMETER,'bolt_hole_diameter_m':BOLT_HOLE_DIAMETER,'bolt_count':BOLT_COUNT,
      'bolt_centres_blender_source_m':[list(c) for c in centres],'bolt_centres_gltf_yup_m':[exchange(c) for c in centres],
      'neck_back_offset_m':-.095,'hardware_axial_bounds_relative_face_m':[-.056,-.006],
      'mating_rule':'coincident bare annular front faces; opposed normals; matched six-hole pattern',
      'marker_axis_convention':'marker local axes remain aligned with Blender asset-source axes; outward direction is the explicit normal field, not marker local Z',
      'status':'artistic modular connection proposal, no real operating rating'}

def add_port_marker(name,face,outward,record=None):
    """Create exportable named Empty retaining both-frame port metadata after joins.
    Call once per flange. Returns object; select for export alongside mesh roles.
    Marker is located at face and source-axis aligned, NOT normal-aligned.
    """
    rec=record or port_record(name,face,outward)
    ob=bpy.data.objects.new('PORT_'+name,None);bpy.context.collection.objects.link(ob)
    ob.location=face;ob.empty_display_type='ARROWS';ob.empty_display_size=.035
    for key,value in rec.items():
        if isinstance(value,dict) or (isinstance(value,list) and value and isinstance(value[0],(dict,list))):ob[key+'_json']=json.dumps(value)
        else:ob[key]=value
    return ob

def add_flange(name,face,outward,materials):
    if len(face)!=3 or not all(math.isfinite(float(x)) for x in face):raise ValueError('Port face must be a finite 3-vector')
    p=Vector(face);n,u,v=basis(outward);zinc=materials['staff_zinc'];paint=materials['staff_bluegrey_paint']
    # Front stays exact and flat. Rear easing preserves the nominated dimensions.
    ob=annular(name+'_drilled_flange',face,n,[(-.035,.08,.158),(-.033,.08,.16),(0,.08,.16)],zinc)
    for i in range(BOLT_COUNT):
        q=p+.13*(u*math.cos(2*math.pi*i/BOLT_COUNT)+v*math.sin(2*math.pi*i/BOLT_COUNT))
        cutter=solid_cylinder(name+'_temporary_drill',q-n*.041,q+n*.006,.009,zinc,24)
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('real_fastener_through_hole','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    # Exact booleans leave sub-micron coincident/collinear fragments at radial
    # phase crossings. Weld only 1 micrometre, dissolve zero edges, and bake
    # explicit valid triangles before UV assignment/export.
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    metric_uv(ob,zinc);out=[ob]
    out.append(annular(name+'_hollow_neck',face,n,[(-.095,.08,.10),(-.05,.08,.10),(-.038,.08,.112),(-.034,.08,.112)],paint))
    for i in range(BOLT_COUNT):
        q=p+.13*(u*math.cos(2*math.pi*i/BOLT_COUNT)+v*math.sin(2*math.pi*i/BOLT_COUNT))
        out.append(solid_cylinder(name+f'_captive_shank_{i+1}',q-n*.052,q-n*.006,.006,zinc,12))
        out.append(solid_cylinder(name+f'_rear_hex_{i+1}',q-n*.056,q-n*.036,.014,zinc,6))
    rec=port_record(name,face,outward)
    ob['utility_port_record_json']=json.dumps(rec)
    for part in out:part['utility_port_revision']=REVISION
    return {'objects':out,'record':rec}
