"""Exact static retained modifier-stack inventory and RNA fingerprints.
No bpy import or source mutation. Only the 25 named display BEVEL/WEIGHTED_NORMAL
stacks evidenced by the retained source builder are accepted. Animation and
constraints remain rejected; all geometry is read from evaluated saved source.
"""
import json,hashlib,math
from gate import require

def value(v):
    if v is None or isinstance(v,(str,bool,int)):return v
    if isinstance(v,float):require(math.isfinite(v),'Nonfinite modifier value');return v
    return [value(x) for x in v]

def evaluation_state(ob,g):
    require(not ob.constraints and not ob.animation_data,'Animated/constrained object: '+ob.name)
    if ob.type=='MESH':
        require(not ob.data.animation_data and ob.data.shape_keys is None,'Animated/keyed mesh: '+ob.name)
    expected=g['allowed_static_modifier_stacks'].get(ob.name)
    if expected is None:require(not ob.modifiers,'Unexpected modifier on unapproved object: '+ob.name)
    else:
        require([m.type for m in ob.modifiers]==expected['type_order'] and [m.name for m in ob.modifiers]==expected['name_order'],'Changed static modifier stack: '+ob.name)
        bevel,normal=ob.modifiers
        # The exact saved float32 width is represented directly by Blender.
        import struct
        width=struct.unpack('<f',struct.pack('<f',expected['bevel_width']))[0]
        require(bevel.width==width and bevel.segments==expected['bevel_segments'] and normal.keep_sharp==expected['weighted_normal_keep_sharp'],'Static modifier settings differ from retained builder: '+ob.name)
        require(all(m.show_viewport and m.show_render for m in ob.modifiers),'Disabled source modifiers')
        require(bevel.profile_type=='SUPERELLIPSE','Unsupported custom bevel profile')
    rows=[]
    for m in ob.modifiers:
        properties={}
        for p in m.bl_rna.properties:
            key=p.identifier
            if key in {'rna_type','execution_time','persistent_uid','is_active','show_expanded'}:continue
            if p.type in {'POINTER','COLLECTION'}:continue
            properties[key]=value(getattr(m,key))
        rows.append(dict(name=m.name,type=m.type,properties=properties))
    data=dict(modifiers=rows,constraints=[],object_animation=False,mesh_animation=False,shape_keys=False)
    return dict(sha256=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest(),state=data)
