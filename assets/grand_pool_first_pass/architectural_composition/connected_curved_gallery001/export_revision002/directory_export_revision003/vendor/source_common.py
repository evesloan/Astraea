"""Shared guards/fingerprints for the DEFERRED Blender source-only job.
Import is safe outside Blender. Material functions receive bpy explicitly.
"""
import sys
sys.dont_write_bytecode=True
import json,hashlib,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
CONTRACT=HERE/'plant_mass_contract.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def guard_inputs():
    pins=json.loads((HERE/'INPUT_PINS.json').read_text())['inputs']
    for p,h in pins.items():assert sha(p)==h,'Retained input changed: '+p
    tools=json.loads((HERE/'SOURCE_TOOL_PINS.json').read_text())
    for p,h in tools['files'].items():assert sha(HERE/p)==h,'Prototype tool changed: '+p
    qa=json.loads((HERE/'PURE_PLAN_QA.json').read_text())
    assert qa['status']=='PASS_PURE_PLAN_ONLY' and qa['contract_sha256']==sha(CONTRACT)
    return pins,json.loads(CONTRACT.read_text())
def candidate_path(argument):
    path=(HERE/argument).resolve()
    assert path.is_relative_to(HERE) and path!=HERE,'Only a new scratch descendant is allowed'
    return path

def plain(value):
    if value is None or isinstance(value,(str,int,bool)):return value
    if isinstance(value,float):assert math.isfinite(value);return value
    try:return [plain(v) for v in value]
    except TypeError:return str(value)

def material_signature(mat):
    """Stable shader graph/value/image fingerprint; no datablock rename noise.
    Covers every scalar/enum/string/array RNA property on material/nodes and
    socket default, excluding UI state and runtime identity. Packed image bytes
    and colourspace are included. No material property is modified here.
    """
    skip={'rna_type','name','name_full','id_data','original','library','override_library','preview','asset_data','node_tree','texture_paint_slots','texture_paint_images','active_node_material','animation_data','users','use_fake_user','use_extra_user','is_embedded_data','is_runtime_data','is_evaluated','is_library_indirect','is_missing','session_uid','tag','library_weak_reference','grease_pencil','paint_active_slot','paint_clone_slot','use_nodes','node','type','location','location_absolute','width','width_hidden','height','dimensions','select','hide','show_options','show_preview','show_texture','parent','internal_links','inputs','outputs','image','image_user','color_ramp','mapping','texture_mapping','color_mapping'}
    def props(obj):
        result={}
        for prop in obj.bl_rna.properties:
            name=prop.identifier
            if name in skip or prop.type in {'POINTER','COLLECTION'}:continue
            try:result[name]=plain(getattr(obj,name))
            except (AttributeError,TypeError):pass
        return result
    def socket(s):
        result={'identifier':s.identifier,'name':s.name,'type':s.bl_idname}
        if hasattr(s,'default_value'):result['default']=plain(s.default_value)
        return result
    nodes=[]
    for node in sorted(mat.node_tree.nodes,key=lambda n:n.name):
        n={'name':node.name,'type':node.bl_idname,'properties':props(node),'inputs':[socket(s) for s in node.inputs],'outputs':[socket(s) for s in node.outputs]}
        if hasattr(node,'image') and node.image:
            im=node.image;assert im.packed_file,'Expected packed retained material image'
            n['image']={'sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'size':list(im.size),'channels':im.channels,'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode}
        if hasattr(node,'color_ramp'):
            ramp=node.color_ramp;n['color_ramp']={'color_mode':ramp.color_mode,'hue_interpolation':ramp.hue_interpolation,'interpolation':ramp.interpolation,'elements':[{'position':e.position,'color':list(e.color)} for e in ramp.elements]}
        for key in ['texture_mapping','color_mapping']:
            if hasattr(node,key):n[key]=props(getattr(node,key))
        nodes.append(n)
    links=sorted([[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in mat.node_tree.links])
    result={'properties':props(mat),'custom_properties':{str(k):plain(mat[k]) for k in sorted(mat.keys()) if k!='_RNA_UI'},'nodes':nodes,'links':links}
    encoded=json.dumps(result,sort_keys=True,separators=(',',':'))
    return {'sha256':hashlib.sha256(encoded.encode()).hexdigest(),'graph':result}

def append_materials(bpy,plan):
    roles=sorted({p['material_role'] for a in plan['assets'] for p in a['parts']})
    availability={};sources={};mats={};provenance={}
    for role in roles:
        preferred=Path(plan['role_source_libraries'][role]);name='ASTRAEA_'+role
        with bpy.data.libraries.load(str(preferred),link=False) as(src,dst):
            present=name in src.materials;availability[role]={'preferred':str(preferred),'exact_role_present':present}
            if present:dst.materials=[name]
        if present:mat=dst.materials[0];source=preferred
        else:
            assert role in plan.get('role_fallback_libraries',{}),'Missing exact role with no authorized source fallback: '+role
            source=Path(plan['role_fallback_libraries'][role])
            with bpy.data.libraries.load(str(source),link=False) as(src,dst):
                assert name in src.materials,'Missing exact retained fallback material: '+role
                dst.materials=[name]
            mat=dst.materials[0]
        assert mat is not None and mat.get('astraea_material_role')==role and mat.use_nodes
        mats[role]=mat;sources[role]=source
        provenance[role]={'library':str(source),'library_sha256':sha(source),'requested_datablock':name,'preferred_library_contains_exact_role':present,'fallback_used':not present,'material_signature':material_signature(mat)}
    return mats,provenance,availability

def check_material_spec(mat,role,spec):
    assert mat['astraea_material_role']==role
    assert mat['alpha_contract']=='OPAQUE'
    assert mat.use_backface_culling==(not spec['double_sided'])
    bs=[n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'];assert len(bs)==1
    bs=bs[0];assert abs(bs.inputs['Alpha'].default_value-1)<1e-7
    assert bs.inputs['Metallic'].default_value==0 and abs(bs.inputs['Roughness'].default_value-spec['roughness'])<1e-6
    assert not bs.inputs['Emission Color'].links and not bs.inputs['Emission Strength'].links
    assert max(abs(c*bs.inputs['Emission Strength'].default_value) for c in bs.inputs['Emission Color'].default_value[:3])<1e-8
    assert len(bs.inputs['Base Color'].links)==1
    tex=bs.inputs['Base Color'].links[0].from_node;assert tex.type=='TEX_IMAGE' and tex.image.packed_file
    assert hashlib.sha256(bytes(tex.image.packed_file.data)).hexdigest()==spec['sha256']

def material_specs():
    p=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/comfort_greenery/greenery/INPUT_PINS.json')
    return json.loads(p.read_text())['material_spec']['materials']
