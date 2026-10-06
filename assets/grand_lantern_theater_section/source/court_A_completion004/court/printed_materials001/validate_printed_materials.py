"""Pure geometry/UV/schema/material/contact QA. Does not import Blender or Godot."""
from pathlib import Path
import ast,collections,hashlib,json,math,sys,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import jsonschema
R=Path(__file__).resolve().parent;G=R.parent
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
helper=C/'assets/grand_lantern_theater_section/source/firstpass_003/dependencies/geometry_review.py'
sys.path.insert(0,str(helper.parent))
from geometry_review import glb,Query
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def clip_rect(p,lo,hi):
 p=[np.array(a,dtype=float)for a in p]
 for axis,edge,sign in [(0,lo[0],1),(0,hi[0],-1),(1,lo[1],1),(1,hi[1],-1)]:
  q=[]
  for a,b in zip(p,p[1:]+p[:1]):
   ia=sign*(a[axis]-edge)>=0;ib=sign*(b[axis]-edge)>=0
   if ia:q.append(a)
   if ia!=ib:q.append(a+(b-a)*(edge-a[axis])/(b[axis]-a[axis]))
  p=q
  if not p:break
 return p

def area(poly):
 if len(poly)<3:return 0.
 a=np.asarray(poly);return abs(float(np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1)))/2)

def main():
 c=read(R/'PRINTED_MATERIALS_CONTRACT.json');base=read(G/'COURT_A_GEOMETRY_CONTRACT.json')
 num={'type':'number'};vec3={'type':'array','minItems':3,'maxItems':3,'items':num};vec2={'type':'array','minItems':2,'maxItems':2,'items':num}
 prism={'type':'object','required':['name','vertices_world','faces','face_uv','face_material_roles','closed_solid','bounds_world'],'properties':{'name':{'type':'string'},'vertices_world':{'type':'array','minItems':8,'maxItems':8,'items':vec3},'faces':{'type':'array','minItems':6,'maxItems':6,'items':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'integer','minimum':0,'maximum':7}}},'face_uv':{'type':'array','minItems':6,'maxItems':6,'items':{'type':'array','minItems':4,'maxItems':4,'items':vec2}},'face_material_roles':{'type':'array','minItems':6,'maxItems':6,'items':{'enum':list(c['materials'])}},'closed_solid':{'const':True},'bounds_world':{'type':'array','minItems':2,'maxItems':2,'items':vec3}}}
 schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','required':['schema_version','pieces','stacks','display_plate','materials','acceptance'],'properties':{'schema_version':{'const':1},'pieces':{'type':'array','minItems':9,'maxItems':9,'items':prism},'display_plate':prism,'stacks':{'type':'array','minItems':3,'maxItems':3},'materials':{'type':'object','minProperties':4,'maxProperties':4},'acceptance':{'type':'object','additionalProperties':{'const':False}}}}
 (R/'PRINTED_MATERIALS_SCHEMA.json').write_text(json.dumps(schema,indent=2)+'\n');jsonschema.Draft202012Validator(schema).validate(c)
 for n,pin in c['source_inputs'].items():assert sha(G/n)==pin,('Changed immutable input',n)
 assert sha(c['protected_source']['path'])==c['protected_source']['sha256']
 assert sha(R/'ART_RECEIPT.json')==c['art_receipt_sha256']
 receipt=read(R/'ART_RECEIPT.json');e=receipt['retained_title_evidence'];assert sha(e['path'])==e['sha256']
 assert read(e['path'])['details']['programme']=='A Thousand Small Worlds'
 images=[]
 for variant in receipt['variants']:
  for ext in ['png','svg']:assert sha(R/variant[ext])==variant[ext+'_sha256']
  im=Image.open(R/variant['png']);assert list(im.size)==variant['dimensions_px'];assert im.mode in ['RGB','RGBA'];assert im.getextrema()!=((0,0),)*3
  svg=ET.parse(R/variant['svg']);txt=' '.join(t.text.strip()for t in svg.iter()if t.tag.endswith('text')and t.text)
  for line in receipt['display_text']:assert line in txt
  assert not any(x in txt.upper()for x in ['STUDY','WIP','$','£','€',':'])
  images.append({'path':variant['png'],'sha256':sha(R/variant['png']),'size':list(im.size),'editable_text':txt})
 assert c['display_plate']['bounds_world']==base['original_programme_art']['bounds_world']
 assert c['display_plate']['source_support']==base['original_programme_art']['support']
 assert Image.open(R/'SUNCORP_GRAND_LANTERN_PROGRAMME.png').size==(1250,990)
 assert Image.open(R/'SUNCORP_GRAND_LANTERN_COVER.png').size==(1400,1000)
 geometry=[]
 allrows=c['pieces']+[c['display_plate']]
 assert len({r['name']for r in allrows})==10
 for row in allrows:
  v=np.array(row['vertices_world']);lo,hi=np.array(row['bounds_world']);assert np.all(np.isfinite(v)) and np.all(hi>lo)
  assert np.allclose(v.min(0),lo,atol=1e-12,rtol=0) and np.allclose(v.max(0),hi,atol=1e-12,rtol=0)
  edges=collections.Counter();directed=collections.Counter();volume=0;center=(lo+hi)/2;printed_faces=[]
  for fi,(face,uv,role)in enumerate(zip(row['faces'],row['face_uv'],row['face_material_roles'])):
   pts=v[face];uv=np.array(uv);assert np.all(np.isfinite(uv));assert area(uv)>1e-14
   normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);assert np.dot(normal,pts.mean(0)-center)>0
   for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted([a,b]))]+=1;directed[(a,b)]+=1
   for i in [1,2]:
    a,b,d=pts[[0,i,i+1]]-center;volume+=np.dot(a,np.cross(b,d))/6
   if c['materials'][role]['image']:
    printed_faces.append(fi);assert set(map(tuple,uv))=={(0,0),(1,0),(1,1),(0,1)}
    for pt,pair in zip(pts,uv):
     if fi==4:assert np.allclose(pair,[(pt[0]-lo[0])/(hi[0]-lo[0]),(hi[2]-pt[2])/(hi[2]-lo[2])])
     elif fi==1:assert np.allclose(pair,[(pt[0]-lo[0])/(hi[0]-lo[0]),(pt[1]-lo[1])/(hi[1]-lo[1])])
     else:raise AssertionError('Print on unintended face')
   else:
    for i in range(4):assert abs(np.linalg.norm(pts[(i+1)%4]-pts[i])/.25-np.linalg.norm(uv[(i+1)%4]-uv[i]))<1e-10
  assert set(edges.values())=={2};assert all(directed[(b,a)]==1 for a,b in directed)
  assert len(v)-len(edges)+len(row['faces'])==2
  expected=float(np.prod(hi-lo));assert abs(volume-expected)<1e-12
  assert printed_faces==([]if row['printed_face_index']is None else[row['printed_face_index']])
  geometry.append({'name':row['name'],'vertices':8,'quad_faces':6,'triangles':12,'edge_incidence':2,'outward_winding':True,'signed_volume_m3':float(volume),'printed_faces':printed_faces,'metric_blank_uvs':True,'full_image_oriented_uvs':True})
 for role,spec in c['materials'].items():
  assert spec['shader']=='Principled BSDF' and spec['roughness']>=.88 and spec['metallic']==0 and spec['coat_weight']==0 and spec['emission_strength']==0
  assert not spec['uses_retained_fabric'] and 'paper'in spec['surface']
  if spec['image']:assert spec['extension']=='EXTEND' and sha(R/spec['image'])==spec['image_sha256']
 contacts=[];cache={};low_wing=None
 for stack in c['stacks']:
  row=next(r for r in base['retained_instances']if r['id']==stack['source_support'])
  assert row['yaw_radians']==0 and row['scale']==[1,1,1]
  assert sha(row['source'])==row['source_sha256']
  if row['asset']not in cache:cache[row['asset']]=glb(row['export'])
  model=cache[row['asset']];assert model['sha256']==row['export_sha256']
  meshes=[dict(m,triangles=m['triangles']+np.array(row['position_world']))for m in model['meshes']]
  lo,hi=np.array(stack['bounds_world']);contact=float(lo[1]);footarea=(hi[0]-lo[0])*(hi[2]-lo[2]);covered=0.;n=0;ys=[];witnesses=[]
  for mesh in meshes:
   t=mesh['triangles'];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);at=t[(normal[:,1]>1e-9)&np.all(abs(t[:,:,1]-contact)<1e-8,axis=1)]
   for tri in at:
    overlap=area(clip_rect(tri[:,[0,2]],lo[[0,2]],hi[[0,2]]))
    if overlap>1e-12:
     assert 'warm_stone'in mesh['material'];covered+=overlap;n+=1;ys.extend(tri[:,1].tolist());witnesses.append({'mesh':mesh['node'],'material':mesh['material'],'triangle_world':tri.tolist(),'bearing_overlap_m2':overlap})
  assert abs(covered-footarea)<1e-9,('Missing contact area',stack['id'],covered,footarea)
  assert max(abs(y-contact)for y in ys)<1e-8
  interior=Query(meshes).prism_hits([lo[0],lo[1]+1e-6,lo[2],hi[0],hi[1],hi[2]],tolerance=1e-7);assert not interior
  pieces=[next(x for x in c['pieces']if x['name']==n)for n in stack['piece_names']]
  assert [p['semantic_part']for p in pieces]==['bottom_cover','pages','top_cover']
  assert pieces[0]['bounds_world'][0]==stack['bounds_world'][0] and pieces[-1]['bounds_world'][1]==stack['bounds_world'][1]
  for a,b in zip(pieces,pieces[1:]):assert a['bounds_world'][1][1]==b['bounds_world'][0][1]
  assert stack['viewing_front_world']==[0,0,1]
  contacts.append({'stack_id':stack['id'],'support':row['id'],'source_sha256':row['source_sha256'],'retained_glb_sha256':model['sha256'],'support_y_world':contact,'stack_bottom_y_world':contact,'max_support_height_error_m':max(abs(y-contact)for y in ys),'bottom_footprint_m2':float(footarea),'actual_triangle_bearing_area_m2':covered,'source_solid_interior_hits':0,'internal_layer_gap_or_overlap_m':0,'bearing_triangle_witnesses':witnesses})
  if row['asset']=='AST-CUL-002':
   lower=[]
   for m in meshes:
    t=m['triangles'];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);lower.extend(t[(normal[:,1]>1e-9)&np.all(abs(t[:,:,1]-(row['position_world'][1]+.805))<1e-6,axis=1)])
   lower=np.array(lower);assert len(lower)>0
   maxx=float(lower[:,:,0].max());gap=float(lo[0]-maxx);assert gap>0
   low_wing={'source_support':row['id'],'actual_lower_writing_triangle_count':len(lower),'actual_lower_writing_surface_bounds':[lower.min((0,1)).tolist(),lower.max((0,1)).tolist()],'stack_bounds':stack['bounds_world'],'minimum_axis_x_separation_m':gap,'horizontal_overlap_m2':0.,'lower_writing_surface_clear':True}
 # Confirm no overlap between any of the nine closed parts except intended shared faces.
 for i,a in enumerate(c['pieces']):
  alo,ahi=np.array(a['bounds_world'])
  for b in c['pieces'][i+1:]:
   blo,bhi=np.array(b['bounds_world']);assert not np.all(np.minimum(ahi,bhi)-np.maximum(alo,blo)>1e-10)
 builder=(R/'build_court_A_source_printed_DRAFT.py').read_text();ast.parse(builder)
 original=(G/'build_court_A_source_DRAFT.py').read_text()
 preserved=["assert gate['parent_authorized_scratch_source_job'] is True","assert gate['static_stage_checkpoint_verified'] is True","assert gate['source_job_slot_granted'] is True","assert gate['production_install_authorized'] is False","assert not output.exists() and not report.exists()","assert sha(contract['base_source'])==contract['base_source_sha256']"]
 for line in preserved:assert line in original and line in builder
 assert builder.index("assert gate['source_job_slot_granted'] is True")<builder.index(' import bpy')
 assert not any(x in builder for x in ['bpy.ops.export_scene','subprocess','os.system'])
 assert not(R/'authored_preview001').exists()
 deps=['build_court_A_source_printed_DRAFT.py','validate_printed_materials.py','ART_RECEIPT.json','ART_VISUAL_REVIEW.json']
 report={'status':'PASS_PURE_PRINTED_MATERIALS_ONLY','contract_sha256':sha(R/'PRINTED_MATERIALS_CONTRACT.json'),'schema_sha256':sha(R/'PRINTED_MATERIALS_SCHEMA.json'),'builder_dependency_sha256':{n:sha(R/n)for n in deps},'read_only_geometry_helper':{'path':str(helper),'sha256':sha(helper)},'protected_base_source_sha256':sha(c['protected_source']['path']),'failures':[],'warnings':[],'schema_valid':True,'images':images,'stack_count':3,'stack_prism_count':9,'stack_triangles':108,'separate_display_plate_triangles':12,'closed_mesh_geometry':geometry,'source_top_face_contacts':contacts,'lower_writing_wing':low_wing,'paper_material_recipes_checked':list(c['materials']),'builder_syntax_valid':True,'preserved_parent_gate_assertions':preserved,'performed_engine_runs':0,'performed_source_saves':0,'performed_exports':0,'production_writes':0,'acceptance':c['acceptance'],'limits':['Triangle-contact screen uses hash-verified retained GLBs; requires independent source reopen verification after build','Paper shader recipe and builder are inspected, not evaluated in Blender','Artwork pixels are reviewed standalone; fitted Court A composition remains unreviewed','No physics, six-species fit, acoustic/load certification, runtime/native or retention acceptance']}
 (R/'PRINTED_MATERIALS_PURE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'stack_prisms':9,'closed_meshes':len(geometry),'contacts':[{'stack':x['stack_id'],'area':x['actual_triangle_bearing_area_m2'],'height_error_m':x['max_support_height_error_m']}for x in contacts],'lower_writing_wing_gap_m':low_wing['minimum_axis_x_separation_m'],'engine_runs':0,'source_saves':0},indent=2))
if __name__=='__main__':main()
