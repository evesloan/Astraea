"""Two independent original, script-assisted editable library stock assets.
Run texture generator with Python, then blender -b -t 2 --python this_file.
All authored coordinates are metres, front -Y. No original game files used.
"""
from pathlib import Path
import bpy,bmesh,math,json,sys,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parents[1]
sys.path.insert(0,str(BASE/'standards'))
from materials import materials
M={};PARTS=[];BOOKS=[]
def reset():
 global M,PARTS,BOOKS
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 M=materials();PARTS=[];BOOKS=[]
 for role,r in json.loads((ROOT/'texture_manifest.json').read_text())['materials'].items():
  m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;m['astraea_material_role']=role;m['meters_per_tile_uv']=r['meters_per_tile_uv'];m['texture_revision']='Original book details 01'
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=r['roughness'];bs.inputs['Metallic'].default_value=0
  im=bpy.data.images.load(str(ROOT/'textures'/r['base_color_file']),check_existing=True);im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';tex.extension='REPEAT';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);M[role]=m

def metric_uv(ob):
 me=ob.data;uv=me.uv_layers.new(name='UV_Metric_Metres');uv.active_render=True
 role=ob['semantic_role'];scale=M[role]['meters_per_tile_uv']
 for p in me.polygons:
  axis=max(range(3),key=lambda a:abs(p.normal[a]));axes=[a for a in range(3) if a!=axis]
  # Page edge lines follow each leaf: Z for upright foreedges, X on head/tail.
  if role=='book_paper_edges' and axis==2:axes=[1,0]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])

def mesh(name,verts,faces,role,parent=None):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(M[role]);ob['semantic_role']=role;ob.parent=parent;metric_uv(ob);PARTS.append(ob);return ob

def extrude(name,profile,lo,hi,role,axis='z',parent=None):
 n=len(profile)
 if axis=='z':v=[(a,b,z) for z in (lo,hi) for a,b in profile]
 elif axis=='y':v=[(a,y,b) for y in (lo,hi) for a,b in profile]
 else:v=[(x,a,b) for x in (lo,hi) for a,b in profile]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,role,parent)

def box(name,lo,hi,role,parent=None):
 return extrude(name,[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],lo[2],hi[2],role,parent=parent)

def book(name,w,d,h,role,matrix=None,bands=2,mark=1):
 group=bpy.data.objects.new(name+'_editable_volume',None);bpy.context.collection.objects.link(group)
 group.matrix_world=matrix or Matrix.Identity(4);start=len(PARTS);t=.0027
 profile=[(-w/2,d/2),(-w/2,-d/2+.007),(-w/2+.0035,-d/2+.0015),(0,-d/2),(w/2-.0035,-d/2+.0015),(w/2,-d/2+.007),(w/2,d/2),(w/2-t,d/2),(w/2-t,-d/2+.010),(-w/2+t,-d/2+.010),(-w/2+t,d/2)]
 cover=extrude(name+'_continuous_boards_and_rounded_spine',profile,0,h,role,parent=group)
 cover['construction']='One closed U-profile cloth case: two continuous cover boards and five-point rounded spine; page block is separate and recessed'
 pages=box(name+'_recessed_bound_leaf_block',(-w/2+t+.0008,-d/2+.009,.0038),(w/2-t-.0008,d/2-.004,h-.0038),'book_paper_edges',group)
 arc=profile[1:6]
 for k,z in enumerate([h*.13,h*.83] if bands==2 else [h*.17]):
  v=[(x,y-.00045,zz) for zz in (z,z+.0024) for x,y in arc];n=len(arc)
  mesh(name+'_raised_spine_band_'+str(k+1),v,[(i,i+1,i+1+n,i+n) for i in range(n-1)],'book_label_paper',group)
 x0=-w*.32;x1=w*.32;zz=h*.48;labelh=min(.030,h*.15);yy=-d/2-.00055
 label=mesh(name+'_catalogue_paper_label',[(x0,yy,zz),(x1,yy,zz),(x1,yy,zz+labelh),(x0,yy,zz+labelh)],[(0,1,2,3)],'book_label_paper',group)
 # Two deliberate ink strokes: short classification bar + Roman-volume stroke.
 for k,(xa,xb,za,zb) in enumerate([(x0*.70,x1*.70,zz+labelh*.69,zz+labelh*.76),(-w*.06,w*.06,zz+labelh*.21,zz+labelh*.53)]):
  mesh(name+'_original_catalogue_mark_'+str(k+1),[(xa,yy-.00013,za),(xb,yy-.00013,za),(xb,yy-.00013,zb),(xa,yy-.00013,zb)],[(0,1,2,3)],'book_print_ink',group)
 group['binding']='cloth board case, recessed page edges, raised spine bands, original catalogue label'
 BOOKS.append({'name':name,'group':group,'parts':PARTS[start:],'local_dimensions_m':[w,d,h]})
 return group

def point_bounds(objects):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[];tris=0;records=[]
 for ob in objects:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();pv=[tuple(ob.matrix_world@v.co) for v in me.vertices];pts+=pv;tris+=len(me.loop_triangles)
  lo=[min(p[a] for p in pv) for a in range(3)];hi=[max(p[a] for p in pv) for a in range(3)]
  records.append({'name':ob.name,'semantic_role':ob['semantic_role'],'triangles':len(me.loop_triangles),'bounds_min_m':lo,'bounds_max_m':hi});eo.to_mesh_clear()
 lo=[min(p[a] for p in pts) for a in range(3)];hi=[max(p[a] for p in pts) for a in range(3)]
 return {'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[hi[a]-lo[a] for a in range(3)],'triangles_evaluated':tris,'parts':records}

def upright():
 widths=[.042,.029,.052,.038,.034,.062,.026,.048,.036,.047]
 heights=[.278,.233,.263,.251,.226,.271,.238,.257,.246,.269]
 depths=[.214,.191,.207,.220,.184,.215,.202,.220,.193,.210]
 cursor=-.195;contacts=[];first_left=cursor
 for i,(w,h,d) in enumerate(zip(widths,heights,depths)):
  cx=cursor+w/2;cy=(.220-d)/2 # rear foreedges share one coherent backing plane
  book('STOCK_volume_%02d'%(i+1),w,d,h,['book_cover_teal','book_cover_ochre','book_cover_clay'][[0,1,2,0,2,1,0,2,1,0][i]],Matrix.Translation((cx,cy,0)),bands=1 if i in [1,4,6,8] else 2,mark=i)
  contacts.append({'book':'STOCK_volume_%02d'%(i+1),'base_z_m':0,'support':'shelf surface at asset pivot Z0','side_support':'Adjacent broad cover touching at X %.6f'%cursor if i else 'Leaning volume crown touches left board'})
  cursor+=w
 theta=math.radians(8);w=.038;h=.246;d=.210
 cx=first_left-w/2*math.cos(theta)-h*math.sin(theta);cz=w/2*math.sin(theta)
 book('STOCK_volume_11_supported_lean',w,d,h,'book_cover_clay',Matrix.Translation((cx,.005,cz))@Matrix.Rotation(theta,4,'Y'),bands=1)
 contact=(first_left,.005,h*math.cos(theta))
 contacts.append({'book':'STOCK_volume_11_supported_lean','lean_angle_degrees':8,'minimum_base_z_m':0,'base_contact_edge_m':[[cx+w/2*math.cos(theta),-.093,0],[cx+w/2*math.cos(theta),.110,0]],'support':'Bottom right cover edge on shelf; upper right cover crown touches volume01 left cover','neighbor_contact_m':list(contact),'neighbor':'STOCK_volume_01','neighbor_left_face_x_m':first_left})
 # Weighted prismatic endstops: no plate under books, so all book bases remain Z0.
 right=cursor
 extrude('STOCK_R_weighted_champagne_endstop',[(right,0),(right+.029,0),(right+.008,.176),(right,.176)],-.073,.107,'champagne_metal',axis='y')
 leftbase=cx-w/2*math.cos(theta);zbase=w*math.sin(theta)
 # Top of short heel is coincident with the leaning book's lower outside corner.
 extrude('STOCK_L_weighted_champagne_heel',[(leftbase-.027,0),(leftbase,0),(leftbase,zbase),(leftbase+.005,.038),(leftbase-.005,.038)],-.073,.107,'champagne_metal',axis='y')
 return {'catalogue_id':'AST-LIB-006','name':'Astraea Bound Collection Stock','intended_use':'Static reusable shelf stock: ten mutually supported upright volumes plus one crown-supported leaning volume and two weighted bookstops',
  'support_contact_proposal':{'pivot_m':[0,0,0],'stock_base_z_m':0,'stock_top_z_m':max(heights),'book_base_contacts':contacts,'upright_cover_gaps_m':0,'stock_envelope_max_m':[.68,.24,.29],'placement':'Place origin on declared shelf-top anchor; keep -Y spines facing accessible aisle. Rotation about Z is supported.','ordinary_reach':'Upper stock requires staff access planning; no guest standing-reach claim'},
  'resource_api':{'load_glb':'AST-LIB-006_upright_book_group.glb','placement_origin':'Actual shelf/book base Z0; row near centred at X0, with rear edges Y .11','forward_blender':[0,-1,0],'forward_glTF':[0,0,1],'animation':'None; one static mesh with semantic material primitives','instancing':'Reuse same imported mesh/material resources. Separate selected volumes only in future interaction work'},
  'contact_joins':[{'members':['volume_11_supported_lean','volume_01'],'intent':'Exact transformed crown/board contact','contact_m':list(contact)},{'members':['volume_10','R_weighted_champagne_endstop'],'intent':'Exact side contact X '+str(right)}]}

def folio():
 # Closed books are the same actual bound construction laid horizontally.
 baseh=.298;basew=.026
 a=Matrix.Translation((-baseh/2,0,basew/2))@Matrix.Rotation(math.pi/2,4,'Y')
 book('FOLIO_lower_closed_volume',basew,.221,baseh,'book_cover_teal',a,bands=2)
 h=.276;w=.022
 # Second book rotates by a restrained 3 degrees in plan and bears fully on lower book.
 b=Matrix.Translation((-.008,.006,.026+w/2))@Matrix.Rotation(math.radians(-3),4,'Z')@Matrix.Translation((-h/2,0,0))@Matrix.Rotation(math.pi/2,4,'Y')
 book('FOLIO_upper_closed_volume',w,.204,h,'book_cover_ochre',b,bands=1)
 # Hinged spread overlaps the upper volume at Z .048. The outer cover corners are clipped.
 for sign,label in [(-1,'L'),(1,'R')]:
  xa,xb=(-.185,-.003) if sign<0 else (.003,.185)
  p=[(xa+.004,-.116),(xb-.004,-.116),(xb,-.112),(xb,.112),(xb-.004,.116),(xa+.004,.116),(xa,.112),(xa,-.112)]
  cover=extrude('FOLIO_'+label+'_open_cover_board',p,.048,.052,'book_cover_clay');cover['construction']='Separate editable cover board, clipped corners, thin board thickness, exact lower face resting on upper book top'
  if sign<0:profile=[(-.176,.052),(-.005,.052),(-.005,.061),(-.037,.080),(-.105,.077),(-.176,.063)]
  else:profile=[(.005,.052),(.176,.052),(.176,.063),(.105,.077),(.037,.080),(.005,.061)]
  page=extrude('FOLIO_'+label+'_shaped_bound_page_block',profile,-.1095,.1095,'book_paper_edges',axis='y');page['construction']='Wedge-shaped leaf block with raised shoulders and a lower sewn gutter'
  tops=[(-.176,.0631),(-.105,.0771),(-.037,.0801),(-.005,.0611)] if sign<0 else [(.005,.0611),(.037,.0801),(.105,.0771),(.176,.0631)]
  v=[(x,y,z) for y in (-.1095,.1095) for x,z in tops];n=len(tops)
  ob=mesh('FOLIO_'+label+'_printed_open_page',v,[(i,i+1,i+1+n,i+n) for i in range(n-1)],'folio_text_page' if sign<0 else 'folio_chart_page')
  uv=ob.data.uv_layers.active
  # This single page has a stated physical metric extent, and one role/layout.
  for poly in ob.data.polygons:
   for li in poly.loop_indices:
    q=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((q.x-tops[0][0])/.171,(q.y+.1095)/.219)
  ob['uv_layout']='Page-local original layout, 0.171 m width by 0.219 m depth, no mixed-role atlas'
 box('FOLIO_sewn_gutter_spine',(-.005,-.110,.049),(.005,.110,.061),'book_cover_ochre')
 # Bookmark is attached below the near page edge and hangs only 24 mm past the boards.
 extrude('FOLIO_cloth_bookmark_fishtail',[(-.067,-.092),(-.052,-.092),(-.052,-.140),(-.0595,-.135),(-.067,-.140)],.054,.0554,'book_cover_teal')
 return {'catalogue_id':'AST-LIB-007','name':'Astraea Open Field Folio','intended_use':'Static reading-table display, shaped open folio borne on two individually bound closed volumes',
  'support_contact_proposal':{'pivot_m':[0,0,0],'tabletop_contact_z_m':0,'tabletop_contact_rectangle_m':[[-.149,-.1105],[.149,.1105]],'closed_volume_stack_contacts_z_m':[0,.026,.048],'open_cover_lower_face_z_m':.048,'open_page_gutter_z_m':.0611,'open_page_shoulder_z_m':.0801,'open_cover_overhang_past_bottom_book_m':{'left_x':.036,'right_x':.036,'back_y':.0055,'front_y':.0055},'bookmark_extension_y_min_m':-.140,'placement':'Place origin on study surface Z .74–.76 m; front -Y faces reader. Display entirely inside tabletop safe perimeter.','interaction':'Static grouped display; picking individual books, page turning, page text interpretation and actor hand contact are future work'},
  'resource_api':{'load_glb':'AST-LIB-007_open_folio_stack.glb','placement_origin':'Bottom closed volume lower cover on support plane Z0','forward_blender':[0,-1,0],'forward_glTF':[0,0,1],'animation':'None; static semantic material primitives'},
  'contact_joins':[{'members':['lower_closed_volume','upper_closed_volume'],'support_z_m':.026},{'members':['upper_closed_volume','open_cover_boards'],'support_z_m':.048},{'members':['open_cover_boards','shaped_bound_page_block'],'gap_m':0,'intent':'Page blocks bear directly on cover top Z .052; sewn gutter joins both halves'}]}

def finish(info,slug):
 root=bpy.data.objects.new(info['catalogue_id']+'_support_origin',None);bpy.context.collection.objects.link(root)
 root['pivot']='Metres, Z up, front -Y, actual support origin at Z0';root['catalogue_id']=info['catalogue_id']
 for ob in list(bpy.context.scene.objects):
  if ob!=root and ob.parent is None:ob.parent=root
 for ob in PARTS:ob['catalogue_id']=info['catalogue_id'];ob['provenance']='Original independent script-assisted geometry, 2026-10-02'
 info.update(point_bounds(PARTS))
 info['book_parts']=[]
 for b in BOOKS:
  bb=point_bounds(b['parts']);info['book_parts'].append({'name':b['name'],'source_local_dimensions_m':b['local_dimensions_m'],'bounds_min_m':bb['bounds_min_m'],'bounds_max_m':bb['bounds_max_m'],'base_contact_z_m':bb['bounds_min_m'][2],'triangles':bb['triangles_evaluated']})
 info.update({'units':'metres','front_axis':'-Y','pivot_m':[0,0,0],'blender_version':bpy.app.version_string,'authoring':'Reproducible script-assisted intentional construction; separately editable covers, pages, labels, bands, bookstops, cover leaves and printed leaf surfaces',
 'provenance':'New original 2026-10-02 catalogue work, independent of missing game recovery. Four library reference PNGs inspected for collection rhythm and useful reading details only; no copied pixels or book art; no downloaded models; no Tripo.',
 'source_generator':'build_library_contents.py','texture_generator':'make_book_textures.py','qa_scope':'Blender component evidence only; original game, Godot integration, actor acceptance, collision behavior and runtime performance are untested',
 'materials':sorted(set(ob['semantic_role'] for ob in PARTS)),'export':{'format':'GLB','Y_up':True,'geometry':'One static visual mesh consolidated into semantic material primitives','active_uv_name':'UV_Metric_Metres','embedded_textures':True,'collision_exported':False},
 'shared_material_source_sha256':hashlib.sha256((BASE/'standards/materials.py').read_bytes()).hexdigest(),'shared_material_manifest_sha256':hashlib.sha256((BASE/'materials/material_manifest.json').read_bytes()).hexdigest(),
 'source_generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'texture_generator_sha256':hashlib.sha256((ROOT/'make_book_textures.py').read_bytes()).hexdigest()})
 lo=info['bounds_min_m'];hi=info['bounds_max_m']
 col={'catalogue_id':info['catalogue_id'],'status':'Proposal only, not exported or engine tested. Static grouping; interaction breakup must generate new per-volume collisions.','coordinates':'Blender metres Z up, front -Y','proposed_static_shapes':[]}
 if info['catalogue_id']=='AST-LIB-006':
  col['proposed_static_shapes']=[{'type':'box','center_m':[(lo[0]+hi[0])/2,0,(hi[2])/2],'size_m':[hi[0]-lo[0],.222,hi[2]],'use':'Optional simple shelf-stock obstruction only. May omit collisions when inaccessible inside existing shelf collision. Conservative empty space above shorter books is accepted for static props only.'}]
 else:
  col['proposed_static_shapes']=[{'type':'box','center_m':[0,0,.024],'size_m':[.298,.221,.048],'use':'Closed stack support body'},{'type':'box','center_m':[0,0,.06405],'size_m':[.370,.232,.0321],'use':'Conservative open folio envelope; omit bookmark detail'}]
 (ROOT/(slug+'.collision_proposal.json')).write_text(json.dumps(col,indent=2))
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(slug+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
 for source in PARTS:
  me=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
  assert me.uv_layers.active,'Missing UV '+source.name
  uv=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='UV_Metric_Metres';uv.active_render=True
  ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=source.matrix_world.copy();ob.select_set(True);copies.append(ob)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();combined=bpy.context.object;combined.name=info['catalogue_id']+'_static_visual';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);combined.parent=root;root.select_set(True)
 combined['catalogue_id']=info['catalogue_id'];combined['source_part_count']=len(PARTS);combined['geometry']='Editable per-book semantic pieces retained in paired .blend'
 bpy.ops.export_scene.gltf(filepath=str(ROOT/(slug+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_extras=True)
 info['export']['source_semantic_part_count']=len(PARTS);info['export']['static_mesh_count']=1;info['export']['material_primitive_count']=len(combined.data.materials)
 for ext in ['blend','glb']:info[ext+'_sha256']=hashlib.sha256((ROOT/(slug+'.'+ext)).read_bytes()).hexdigest()
 (ROOT/(slug+'.manifest.json')).write_text(json.dumps(info,indent=2));return info
if __name__=='__main__':
 results=[]
 for fn,slug in [(upright,'AST-LIB-006_upright_book_group'),(folio,'AST-LIB-007_open_folio_stack')]:
  reset();results.append(finish(fn(),slug))
 (ROOT/'family_summary.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in ['parts','book_parts']} for r in results],indent=2))
 print('BOOK_DETAIL_COMPLETE',[(r['catalogue_id'],r['dimensions_m'],r['triangles_evaluated']) for r in results])
