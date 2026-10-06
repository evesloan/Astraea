"""Pure JSON geometry and material recipe for nine programme-stack prisms.
No bpy import, source modification, engine execution or export.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;G=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
FACES=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]

def prism(name,lo,hi,role,print_face=None,image_role=None):
 vs=[[x,y,z]for z in[lo[2],hi[2]]for x,y in[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
 uvs=[]
 # Real face-local metre-density UVs at 0.25 m/tile, including each thin edge.
 for f,(u,v) in zip(FACES,[(0,1),(0,1),(0,2),(2,1),(0,2),(2,1)]):
  uvs.append([[(vs[i][u]-lo[u])/.25,(vs[i][v]-lo[v])/.25]for i in f])
 face_roles=[role]*6
 if print_face is not None:
  if print_face==1:uvs[1]=[[0,0],[1,0],[1,1],[0,1]] # vertical +Z front; top = +Y
  elif print_face==4:uvs[4]=[[1,1],[0,1],[0,0],[1,0]] # horizontal +Y face; viewer is +Z
  else:raise AssertionError('Unsupported printed face')
  face_roles[print_face]=image_role
 return {'name':name,'bounds_world':[lo,hi],'vertices_world':vs,'faces':FACES,'face_uv':uvs,'face_material_roles':face_roles,'collides':False,'closed_solid':True,'metric_blank_paper_uv_tile_m':[.25,.25],'printed_face_index':print_face,'print_uv_policy':'One complete image with no repeat; no print on sides or underside'if print_face is not None else'Blank matte paper/cover stock only'}

def create():
 c=read(G/'COURT_A_GEOMETRY_CONTRACT.json');contents=read(G/'TABLE_AND_COUNTER_CONTENTS_DRAFT.json');art=read(R/'ART_RECEIPT.json')
 paper={'surface':'matte uncoated paper','shader':'Principled BSDF','base_color_srgb_hex':'#e4dac4','roughness':.92,'metallic':0.,'specular_ior_level':.18,'coat_weight':0.,'transmission_weight':0.,'emission_strength':0.,'image':None,'uses_retained_fabric':False}
 cover={**paper,'surface':'matte navy-dyed paper cover stock','base_color_srgb_hex':'#142e34','roughness':.88}
 printed={**cover,'surface':'original ink on matte paper','base_color_srgb_hex':'#ffffff','image':'SUNCORP_GRAND_LANTERN_COVER.png','image_sha256':art['variants'][1]['png_sha256'],'colorspace':'sRGB','extension':'EXTEND','interpolation':'Linear','uv':'Explicit per-face UV; printed top spans exactly [0,1]²'}
 plate={**printed,'image':'SUNCORP_GRAND_LANTERN_PROGRAMME.png','image_sha256':art['variants'][0]['png_sha256'],'surface':'original print on opaque matte paper-faced display plate','uv':'Explicit front (+Z) UV exactly [0,1]²'}
 stacks=[];pieces=[]
 for row in contents['items']:
  lo,hi=row['bounds_world'];b=row['cover_thickness_m'];page=row['body_size_m'][1]
  assert abs(hi[1]-lo[1]-(2*b+page))<1e-10
  heights=[lo[1],lo[1]+b,lo[1]+b+page,hi[1]]
  stack_names=[]
  for i,part in enumerate(['bottom_cover','pages','top_cover']):
   r=prism(row['id']+'_'+part,[lo[0],heights[i],lo[2]],[hi[0],heights[i+1],hi[2]],'court_A_matte_paper'if i==1 else'court_A_cover_stock',4 if i==2 else None,'court_A_printed_paper'if i==2 else None)
   r.update({'stack_id':row['id'],'source_support':row['source_support'],'semantic_part':part,'contact_y_lower':heights[i],'contact_y_upper':heights[i+1]})
   pieces.append(r);stack_names.append(r['name'])
  stacks.append({**row,'piece_names':stack_names,'viewing_front_world':[0,0,1],'cover_top_direction_world':[0,0,-1],'viewing_basis':'Common public court approach from +Z; printed bottom edge faces viewer; rightward text is +X','total_height_m':2*b+page,'source_contact_y_world':lo[1]})
 lo,hi=c['original_programme_art']['bounds_world']
 sign=prism('A4_original_programme_face',lo,hi,'court_A_cover_stock',1,'court_A_original_programme')
 sign.update({'semantic_id':'D11.CourtA.Completion004.original_programme','source_support':'A4_sign_frame','front_normal_world':[0,0,1],'printed_top_direction_world':[0,1,0]})
 d={'schema_version':1,'status':'PURE_PRINTED_MATERIALS_DRAFT_SOURCE_UNBUILT','coordinate_frame':'world X right, Y up, Z toward public/front; source adapter bvec maps [x,y,z] to [x,-z,y]','source_inputs':{n:sha(G/n)for n in ['COURT_A_GEOMETRY_CONTRACT.json','TABLE_AND_COUNTER_CONTENTS_DRAFT.json','build_court_A_source_DRAFT.py','HANDOFF.md']},'protected_source':{'path':c['base_source'],'sha256':c['base_source_sha256']},'art_receipt_sha256':sha(R/'ART_RECEIPT.json'),'text_override':{'PROGRAMME STUDY':'EVENING PROGRAMME'},'materials':{'court_A_matte_paper':paper,'court_A_cover_stock':cover,'court_A_printed_paper':printed,'court_A_original_programme':plate},'stacks':stacks,'pieces':pieces,'display_plate':sign,'stack_piece_limit':9,'stack_triangles':108,'display_plate_triangles':12,'preservation':{'existing_objects_moved':0,'existing_lower_writing_wing_clear':True,'new_lights':0,'audience_chairs_rebuilt':0,'production_writes':False,'engine_runs':False,'exports':False,'source_build':False},'remaining_gates':['Parent static checkpoint and source-job slot','Parent original-art review acknowledgement','Blender source build and independent reopen','Material graphs, packed image hashes and source UV validation','Same-camera/seated/service visual review','Independent source retention','Native collision, six-species fit and any later separately authorized export/integration'],'acceptance':{'source_built':False,'source_reopened':False,'retained':False,'native_verified':False,'visually_accepted_in_court':False}}
 (R/'PRINTED_MATERIALS_CONTRACT.json').write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({'stacks':len(stacks),'pieces':len(pieces),'stack_triangles':108,'source_built':False}))
if __name__=='__main__':create()
