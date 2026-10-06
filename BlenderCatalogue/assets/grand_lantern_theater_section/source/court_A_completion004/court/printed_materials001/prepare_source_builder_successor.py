"""Prepare (never execute) the exact successor to the preserved source draft."""
from pathlib import Path
import difflib,ast
D=Path(__file__).resolve().parent;R=D.parent
original=(R/'build_court_A_source_DRAFT.py').read_text();s=original
s=s.replace('python -B build_court_A_source_DRAFT.py --inspect','python -B build_court_A_source_printed_DRAFT.py --inspect')
s=s.replace('R=Path(__file__).resolve().parent','D=Path(__file__).resolve().parent\nR=D.parent # immutable geometry contract and original parent gate location')
s=s.replace(" assert art.is_relative_to(R) and sha(art)==gate['original_programme_png_sha256']\n outdir=R/'authored_preview001';outdir.mkdir(exist_ok=True)",""" assert art.is_relative_to(D) and sha(art)==gate['original_programme_png_sha256']
 printed=read(D/'PRINTED_MATERIALS_CONTRACT.json')
 pure=read(D/'PRINTED_MATERIALS_PURE_CHECK.json')
 assert gate['original_programme_art_reviewed'] is True
 assert sha(D/'PRINTED_MATERIALS_CONTRACT.json')==gate['printed_materials_contract_sha256']==pure['contract_sha256']
 assert sha(D/'PRINTED_MATERIALS_PURE_CHECK.json')==gate['printed_materials_pure_check_sha256']
 assert pure['status']=='PASS_PURE_PRINTED_MATERIALS_ONLY' and not pure['failures']
 assert len(printed['stacks'])==3 and len(printed['pieces'])==9
 for filename,pin in printed['source_inputs'].items():assert sha(R/filename)==pin
 for filename,pin in pure['builder_dependency_sha256'].items():assert sha(D/filename)==pin
 for role,spec in printed['materials'].items():
  if spec.get('image'):assert sha(D/spec['image'])==spec['image_sha256']
 assert art==D/printed['materials']['court_A_original_programme']['image']
 cover_art=Path(gate['programme_cover_png']).resolve()
 assert cover_art==D/printed['materials']['court_A_printed_paper']['image']
 assert sha(cover_art)==gate['programme_cover_png_sha256']
 outdir=D/'authored_preview001';outdir.mkdir(exist_ok=True)""")
s=s.replace('from firstpass_common import bvec,verify_new_geometry,mesh_record,digest','from firstpass_common import bvec,verify_new_geometry,mesh_record,material_record,digest')
s=s.replace(" for role in contract['material_contracts']:exact_material(role)\n names=[]", """ for role in contract['material_contracts']:exact_material(role)
 # New paper is explicitly authored as matte paper, never a relabelled fabric.
 # Only the two image-bearing materials load/pack images; edges and pages stay blank.
 paper_image_records=[]
 def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
 for role,spec in printed['materials'].items():
  assert spec['uses_retained_fabric'] is False
  mat=bpy.data.materials.new(role);mat.use_nodes=True
  mat['astraea_material_role']=role;mat['surface_kind']=spec['surface']
  mat['original_paper_material']=True;mat['retained_fabric_relabelled']=False
  bs=mat.node_tree.nodes.get('Principled BSDF')
  h=spec['base_color_srgb_hex'].lstrip('#');rgba=[linear(int(h[i:i+2],16)/255)for i in (0,2,4)]+[1.]
  bs.inputs['Base Color'].default_value=rgba;mat.diffuse_color=rgba
  for key,target in [('roughness','Roughness'),('metallic','Metallic'),('coat_weight','Coat Weight'),('transmission_weight','Transmission Weight'),('emission_strength','Emission Strength')]:
   assert target in bs.inputs,('Expected Principled socket',target)
   bs.inputs[target].default_value=spec[key]
  assert 'Specular IOR Level' in bs.inputs
  bs.inputs['Specular IOR Level'].default_value=spec['specular_ior_level']
  if spec.get('image'):
   image_path=D/spec['image'];im=bpy.data.images.load(str(image_path),check_existing=False)
   im.colorspace_settings.name='sRGB';im.pack()
   assert im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==spec['image_sha256']
   node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='OriginalPaperArtwork';node.image=im
   node.extension='EXTEND';node.interpolation='Linear';mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
   paper_image_records.append({'material':role,'image':spec['image'],'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest(),'size':list(im.size)})
  mats[role]=mat;material_provenance[role]={'kind':'new_original_matte_paper_recipe','recipe_sha256':digest(spec),'image_sha256':spec.get('image_sha256'),'retained_fabric_used':False}
 names=[]""")
s=s.replace(' def mesh(name,vertices,faces,role,face_uv,properties):',' def mesh(name,vertices,faces,role,face_uv,properties,face_material_roles=None):')
s=s.replace("  me.materials.append(exact_material(role));uv=me.uv_layers.new(name='MetricUV');uv.active_render=True", """  roles=list(dict.fromkeys(face_material_roles or [role]))
  for item in roles:me.materials.append(exact_material(item))
  if face_material_roles:
   assert len(face_material_roles)==len(me.polygons)
   for face,face_role in zip(me.polygons,face_material_roles):face.material_index=roles.index(face_role)
  uv=me.uv_layers.new(name='MetricUV');uv.active_render=True""")
start=s.index(' # Original graphic face on the already modelled bearing/frame.')
end=s.index(" scene['court_A_status']",start)
s=s[:start]+""" # Closed printed plate and exactly three touching cover/pages/cover stacks.
 # The upper cover alone uses the full cover image. +Z is the public reading edge.
 printed_names=[]
 for row in [printed['display_plate']]+printed['pieces']:
  roles=row['face_material_roles']
  properties={k:v for k,v in row.items()if k not in ['vertices_world','faces','face_uv','face_material_roles']}
  properties['printed_materials_contract_sha256']=sha(D/'PRINTED_MATERIALS_CONTRACT.json')
  if row['printed_face_index'] is not None:
   properties['original_art_sha256']=printed['materials'][roles[row['printed_face_index']]]['image_sha256']
  properties['visual_acceptance']=False;properties['source_retention_verified']=False
  mesh(row['name'],row['vertices_world'],row['faces'],roles[0],row['face_uv'],properties,roles)
  printed_names.append(row['name'])
 assert len(printed_names)==10 # nine stack prisms plus the existing specified plate
"""+s[end:]
s=s.replace("checks=verify_new_geometry(bpy,[r['name']for r in contract['objects']])","checks=verify_new_geometry(bpy,[r['name']for r in contract['objects']]+printed_names)")
s=s.replace("'fuller_mass_included':bool(fuller)","'printed_materials_contract_sha256':sha(D/'PRINTED_MATERIALS_CONTRACT.json'),'printed_stack_count':3,'printed_stack_piece_count':9,'printed_closed_meshes':printed_names,'paper_image_records':paper_image_records,'paper_material_graphs':{role:material_record(mats[role])for role in printed['materials']},'fuller_mass_included':bool(fuller)")
s=s.replace("'output':str(R/'authored_preview001'/c['standalone_source_proposal'])","'printed_stacks':3,'stack_prisms':9,'full_print_plate_front_only':True,'source_native_acceptance':False,'output':str(D/'authored_preview001'/c['standalone_source_proposal'])")
s=s.replace('Parent-coordinated source slot, static checkpoint, original art PNG; scratch only','Parent-coordinated source slot, static checkpoint, both original art PNGs, reviewed print contract and pure-check pins; scratch only')
ast.parse(s)
(D/'build_court_A_source_printed_DRAFT.py').write_text(s)
(D/'SOURCE_BUILDER_SUCCESSOR.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='../build_court_A_source_DRAFT.py',tofile='build_court_A_source_printed_DRAFT.py')))
print('Successor and reviewable diff written; Blender build NOT RUN.')
