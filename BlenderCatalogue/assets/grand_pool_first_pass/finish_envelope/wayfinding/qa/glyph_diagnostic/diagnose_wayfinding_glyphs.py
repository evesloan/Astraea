"""Read-only-input, diagnostic-only Blender task. Parent must own the engine slot.
Creates only one fresh scratch JSON report; never saves .blend, exports, renders or edits source.

Factorial controls: both actual main captions at BOTH main origins, through all
three coordinate pipelines. Raw font unit geometry and every cleanup stage are
measured. No rejection threshold is changed; no candidate is silently adopted.
"""
import argparse,hashlib,itertools,json,math,struct,sys,traceback
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
EXPECTED_BUILDER='740acda6087a98a97f744049a5da9168a53acfee26c69451f48bb545fd6de3df'
AREA_GUARD=1e-12

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,k):return [x*k for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):return math.sqrt(dot(a,a))
def bounds(v):return [[min(q[k] for q in v) for k in range(3)],[max(q[k] for q in v) for k in range(3)]]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def key(v):return b''.join(struct.pack('<f',x) for x in v).hex()
def xyz_local(s,p):return add(mul(s['right_xyz'],p[0]),add(mul(s['up_xyz'],p[1]),mul(s['normal_xyz'],p[2])))
def xyz_world(s,p):return add(s['origin_xyz'],xyz_local(s,p))
def to_blender(p):return [p[0],-p[2],p[1]]
def area64(v):return norm(cross(sub(v[1],v[0]),sub(v[2],v[0])))/2

def exact_cross_evidence(v):
    vv=[[Fraction.from_float(float(x)) for x in p] for p in v];c=cross(sub(vv[1],vv[0]),sub(vv[2],vv[0]));sq=sum(x*x for x in c)
    return {'exactly_collinear_stored_float32':sq==0,'squared_cross_fraction':str(sq),
            'cross_component_fractions':[str(x) for x in c]}

def run(a):
    import bpy,bmesh
    from mathutils import Vector
    report_path=a.report.resolve()
    if report_path.exists():raise FileExistsError('Preserve prior diagnostic evidence; use a fresh JSON report')
    scratch=Path('/workspace/scratch/375c2e438292').resolve()
    if scratch not in report_path.parents or report_path.suffix.lower()!='.json' or not report_path.parent.is_dir():raise ValueError('Report must be a fresh JSON in an existing authorized scratch directory')
    if report_path==a.builder.resolve() or report_path==a.contract.resolve():raise ValueError('Input paths are read-only')
    out=Path('details')
    if sha(a.builder)!=EXPECTED_BUILDER:raise ValueError('Builder differs from pinned build-002 candidate')
    d=json.loads(a.contract.read_text());before={str(p.resolve()):sha(p) for p in [a.builder,a.contract]}
    for pin in d['pins']:
        p=Path(d['source_defaults'][pin['root']])/pin['path']
        if not p.is_file() or sha(p)!=pin['sha256']:raise ValueError('Retained input changed: '+str(p))
    summary={'schema':1,'status':'diagnostic_running','blender_version':bpy.app.version_string,'input_sha256':before,
             'area_rejection_guard_m2_unchanged':AREA_GUARD,'no_blend_save_export_render_runtime_or_installed_source_write':True,
             'raw_fonts':[],'variants':[],'comparisons':[],'conclusions':[],'detail_records':{},'mesh_snapshots':{}}
    def flush():dump(report_path,summary)
    def keep_detail(path,record):summary['detail_records'][str(path)]=record
    flush()
    def raw_font(body):
        cu=bpy.data.curves.new('DIAG_raw_font','FONT');cu.body=body;cu.size=1;cu.align_x='LEFT';cu.extrude=.002;cu.resolution_u=6
        ob=bpy.data.objects.new('DIAG_raw_font',cu);bpy.context.scene.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        ob=bpy.context.object;me=ob.data;me.calc_loop_triangles();vs=[list(v.co) for v in me.vertices];fs=[list(p.vertices) for p in me.polygons]
        return ob,vs,fs
    def origin_for(me,index):
        attr=me.attributes.get('diag_raw_polygon')
        return int(attr.data[index].value)-1 if attr else index
    def snapshot(me,label,path,raw_vs,raw_fs,pre_transform_vs,operation,include_geometry=False):
        me.update();me.calc_loop_triangles();v=[list(p.co) for p in me.vertices];bad=[];areas32=[];areas64=[]
        identical={}
        for i,p in enumerate(v):identical.setdefault(key(p),[]).append(i)
        faces=[list(p.vertices) for p in me.polygons];digest=hashlib.sha256()
        for p in v:digest.update(bytes.fromhex(key(p)))
        for face in faces:digest.update(struct.pack('<I',len(face)));digest.update(struct.pack('<'+'I'*len(face),*face))
        edge_to_triangles={}
        for ti,t in enumerate(me.loop_triangles):
            ii=list(t.vertices)
            for aidx,bidx in zip(ii,ii[1:]+ii[:1]):
                edge_to_triangles.setdefault(tuple(sorted((key(v[aidx]),key(v[bidx])))),[]).append(ti)
        for ti,t in enumerate(me.loop_triangles):
            tri=[v[i] for i in t.vertices];v0,v1,v2=[me.vertices[i].co for i in t.vertices]
            ar32=float((v1-v0).cross(v2-v0).length/2);ar64=area64(tri);areas32.append(ar32);areas64.append(ar64)
            if ar32<AREA_GUARD or ar64<AREA_GUARD:
                original=origin_for(me,t.polygon_index);poly=me.polygons[t.polygon_index]
                exact=exact_cross_evidence(tri);repeated=len({key(p) for p in tri})<3
                if repeated:classification='coincident_saved_vertices'
                elif exact['exactly_collinear_stored_float32']:classification='exactly_collinear_saved_vertices'
                elif ar32<AREA_GUARD<=ar64:classification='float32_area_evaluation_only_guard_failure'
                else:classification='genuinely_positive_area_below_guard'
                entry={'loop_triangle_index':ti,'mesh_polygon_index':t.polygon_index,'source_raw_polygon_index_propagated':original,
                       'triangle_vertex_indices':list(t.vertices),'triangle_vertices_blender_saved_float32':tri,
                       'triangle_coordinate_bits':[key(p) for p in tri],'area_mathutils_float32_m2':ar32,'area_python_double_m2':ar64,
                       'classification':classification,'exact_arithmetic':exact,
                       'current_source_polygon_vertex_indices':list(poly.vertices),'current_source_polygon_vertices':[v[i] for i in poly.vertices]}
                if 0<=original<len(raw_fs):
                    entry['raw_font_polygon_vertex_indices']=raw_fs[original]
                    entry['raw_font_polygon_vertices_unit_font']=[raw_vs[i] for i in raw_fs[original]]
                    entry['same_source_polygon_before_float32_and_cleanup']=[pre_transform_vs[i] for i in raw_fs[original]]
                    entry['source_lineage_note']='Face integer custom-data provenance propagated through BMesh; use the included pre/post polygon vertices if an operation merged or deleted faces.'
                else:entry['source_lineage_note']='No valid propagated source polygon; lineage is explicitly unresolved.'
                neighbors=[]
                for ia,ib in zip(list(t.vertices),list(t.vertices)[1:]+list(t.vertices)[:1]):
                    edge_key=tuple(sorted((key(v[ia]),key(v[ib]))))
                    for ni in edge_to_triangles.get(edge_key,[]):
                        if ni==ti:continue
                        nt=me.loop_triangles[ni];nv=[v[j] for j in nt.vertices];vv=[me.vertices[j].co for j in nt.vertices]
                        neighbors.append({'shared_edge_vertex_indices':[ia,ib],'shared_edge_coordinate_bits':list(edge_key),'adjacent_triangle_index':ni,'adjacent_polygon_index':nt.polygon_index,'adjacent_raw_polygon_index_propagated':origin_for(me,nt.polygon_index),'adjacent_triangle_vertex_indices':list(nt.vertices),'adjacent_vertices_blender_saved_float32':nv,'adjacent_area_mathutils_float32_m2':float((vv[1]-vv[0]).cross(vv[2]-vv[0]).length/2),'adjacent_area_python_double_m2':area64(nv),'same_index_edge':ia in nt.vertices and ib in nt.vertices})
                entry['shared_edge_adjacency']=neighbors
                entry['shape_preserving_collinear_flip_candidates']=[]
                if not repeated and exact['exactly_collinear_stored_float32']:
                    ii=list(t.vertices);ia,ic=max(itertools.combinations(ii,2),key=lambda pair:norm(sub(v[pair[1]],v[pair[0]])));ib=next(j for j in ii if j not in [ia,ic])
                    av,bv,cv=v[ia],v[ib],v[ic];ac=sub(cv,av);between=0<dot(sub(bv,av),ac)<dot(ac,ac)
                    for neighbor in neighbors:
                        if set(neighbor['shared_edge_coordinate_bits'])!={key(av),key(cv)} or neighbor['adjacent_area_python_double_m2']<AREA_GUARD:continue
                        nv=neighbor['adjacent_vertices_blender_saved_float32'];dv=next((p for p in nv if key(p) not in {key(av),key(cv)}),None)
                        if dv is None:continue
                        normal=cross(sub(nv[1],nv[0]),sub(nv[2],nv[0]));proposed=[[av,bv,dv],[bv,cv,dv]]
                        for q in proposed:
                            if dot(cross(sub(q[1],q[0]),sub(q[2],q[0])),normal)<0:q[0],q[1]=q[1],q[0]
                        areas=[area64(q) for q in proposed];f32areas=[]
                        for q in proposed:
                            a32,b32,c32=[Vector(p) for p in q];f32areas.append(float((b32-a32).cross(c32-a32).length/2))
                        def rational_cross(q):
                            r=[[Fraction.from_float(float(x)) for x in p] for p in q];return cross(sub(r[1],r[0]),sub(r[2],r[0]))
                        old=rational_cross(nv);new=add(rational_cross(proposed[0]),rational_cross(proposed[1]));exact_area_vector_preserved=old==new
                        entry['shape_preserving_collinear_flip_candidates'].append({'adjacent_triangle_index':neighbor['adjacent_triangle_index'],'old_long_edge_coordinate_bits':[key(av),key(cv)],'middle_vertex_is_strictly_between':between,'proposed_triangles_saved_coordinates':proposed,'proposed_areas_double_m2':areas,'proposed_areas_mathutils_float32_m2':f32areas,'same_exact_oriented_area_vector':exact_area_vector_preserved,'eligible_without_threshold_change_or_feature_removal':between and exact_area_vector_preserved and min(areas)>=AREA_GUARD and min(f32areas)>=AREA_GUARD,'status':'Evidence only. No flip applied to any mesh.'})
                bad.append(entry)
        row={'stage':label,'operation':operation,'vertex_count':len(v),'polygon_count':len(faces),'triangle_count':len(me.loop_triangles),
             'exact_duplicate_coordinate_groups':sum(len(g)>1 for g in identical.values()),'exact_unique_coordinates':len(identical),
             'minimum_area_mathutils_float32_m2':min(areas32,default=None),'minimum_area_python_double_m2':min(areas64,default=None),
             'float32_guard_failure_count':sum(x<AREA_GUARD for x in areas32),'double_guard_failure_count':sum(x<AREA_GUARD for x in areas64),
             'coordinate_and_polygon_sha256':digest.hexdigest(),'bad_triangles':bad}
        if include_geometry or (bad and any(tag in str(path) for tag in ['world_then_local_002','direct_local_uvd'])):
            triangles=[list(t.vertices) for t in me.loop_triangles];triangle_polygons=[t.polygon_index for t in me.loop_triangles];polygon_origins=[origin_for(me,i) for i in range(len(me.polygons))]
            snapshot_key=hashlib.sha256(json.dumps({'v':v,'p':faces,'t':triangles,'tp':triangle_polygons,'orig':polygon_origins},separators=(',',':')).encode()).hexdigest()
            summary['mesh_snapshots'].setdefault(snapshot_key,{'all_vertices_saved_float32':v,'all_polygons':faces,'all_triangles':triangles,'all_triangle_polygon_indices':triangle_polygons,'all_polygon_raw_source_indices':polygon_origins,'coordinate_frame':'Saved Blender mesh coordinates; parent variant identifies world-baked, sign-local or raw unit-font frame','threshold_m2_unchanged':AREA_GUARD})
            row['complete_mesh_snapshot_key']=snapshot_key
        keep_detail(path,row)
        return {k:v for k,v in row.items() if k not in ['bad_triangles','all_vertices_saved_float32','all_polygons']}|{'detail_record_key':str(path)}
    def bm_snapshot(bm,label,path,*extra,operation):
        me=bpy.data.meshes.new('DIAG_stage_snapshot');bm.to_mesh(me);r=snapshot(me,label,path,*extra,operation);bpy.data.meshes.remove(me);return r
    fonts={}
    try:
        for label,body in [('reference_H','H'),('caption_Grand_Pool','Grand Pool'),('caption_Orchard_Market','Orchard Market')]:
            ob,vs,fs=raw_font(body);row=snapshot(ob.data,'raw_font_unit',out/(label+'_raw.json'),vs,fs,vs,'Unmodified built-in FONT conversion: size1, extrude0.002, resolution_u6',True)
            row['text']=body;summary['raw_fonts'].append(row);fonts[body]=(vs,fs);me=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me);flush()
        hb=bounds(fonts['H'][0]);unit_cap=hb[1][1]-hb[0][1]
        all_saved={};all_records={}
        signs=[next(s for s in d['signs'] if s['id']==name) for name in ['main_D08','main_D09']]
        for body in ['Grand Pool','Orchard Market']:
            raw_vs,raw_fs=fonts[body];rb=bounds(raw_vs)
            for s in signs:
                lo,hi=s['glyph_envelope_local_uvd'];factor=min(s['glyph_cap_height_m']/unit_cap,(hi[0]-lo[0])/(rb[1][0]-rb[0][0]),(hi[1]-lo[1])/(rb[1][1]-rb[0][1]))
                cx,cy=(rb[0][0]+rb[1][0])/2,(rb[0][1]+rb[1][1])/2;mid=(lo[0]+hi[0])/2;zd=rb[1][2]-rb[0][2]
                uvd=[[(v[0]-cx)*factor+mid,(v[1]-cy)*factor,.123+(v[2]-rb[0][2])/zd*.006] for v in raw_vs]
                world=[xyz_world(s,p) for p in uvd]
                for strategy in ['world_baked_001','world_then_local_002','direct_local_uvd']:
                    name=body.replace(' ','_')+'__'+s['id']+'__'+strategy;folder=out/name
                    if strategy=='world_baked_001':coords=[to_blender(p) for p in world]
                    elif strategy=='world_then_local_002':coords=[to_blender(sub(p,s['origin_xyz'])) for p in world]
                    else:coords=[to_blender(xyz_local(s,p)) for p in uvd]
                    all_saved[(body,s['id'],strategy)]=[[f32(x) for x in p] for p in coords]
                    mesh=bpy.data.meshes.new('DIAG_input');mesh.from_pydata(coords,[],raw_fs);mesh.update()
                    attr=mesh.attributes.new('diag_raw_polygon','INT','FACE')
                    for i,data in enumerate(attr.data):data.value=i+1
                    row={'text':body,'origin_sign':s['id'],'origin_xyz':s['origin_xyz'],'strategy':strategy,'scale':factor,'actual_cap_height_m':factor*unit_cap,'stages':[]}
                    row['stages'].append(snapshot(mesh,'constructed_pre_weld',folder/'00_pre_weld.json',raw_vs,raw_fs,coords,'from_pydata float32 conversion only'))
                    bm=bmesh.new();bm.from_mesh(mesh);bpy.data.meshes.remove(mesh);bm.verts.ensure_lookup_table();bm.verts.index_update()
                    before_vertices={v:(v.index,list(v.co)) for v in bm.verts}
                    targetmap=bmesh.ops.find_doubles(bm,verts=list(bm.verts),dist=1e-7).get('targetmap',{})
                    groups=[]
                    for src,target in targetmap.items():
                        i,p=before_vertices[src];j,q=before_vertices[target];groups.append({'from_index':i,'to_index':j,'from_coordinates':p,'to_coordinates':q,'distance_m':norm(sub(p,q)),'coordinates_bit_identical':key(p)==key(q)})
                    keep_detail(folder/'01_weld_candidate_pairs.json',{'unchanged_weld_distance_m':1e-7,'pairs':groups})
                    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
                    row['stages'].append(bm_snapshot(bm,'after_remove_doubles',folder/'02_after_weld.json',raw_vs,raw_fs,coords,operation='Same remove_doubles dist1e-7 as builder; no relaxed threshold'))
                    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
                    row['stages'].append(bm_snapshot(bm,'after_dissolve_degenerate',folder/'03_after_dissolve.json',raw_vs,raw_fs,coords,operation='Same dissolve_degenerate dist1e-9 as builder'))
                    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
                    row['stages'].append(bm_snapshot(bm,'after_recalc_normals_final',folder/'04_final.json',raw_vs,raw_fs,coords,operation='Same recalc_face_normals as builder, followed by its exact loop-triangle area test'))
                    bm.free();row['weld_candidate_pair_count']=len(groups);row['nonidentical_weld_candidate_pair_count']=sum(not g['coordinates_bit_identical'] for g in groups)
                    row['first_failing_stage']=next((x['stage'] for x in row['stages'] if x['float32_guard_failure_count']),None)
                    summary['variants'].append(row);all_records[(body,s['id'],strategy)]=row;flush()
        # Evidence separates caption content, origin, arithmetic representation and cleanup.
        for body in ['Grand Pool','Orchard Market']:
            for sid in ['main_D08','main_D09']:
                b=all_saved[(body,sid,'world_then_local_002')];c=all_saved[(body,sid,'direct_local_uvd')]
                differing=[i for i,(p,q) in enumerate(zip(b,c)) if key(p)!=key(q)]
                summary['comparisons'].append({'comparison':'002_vs_direct_local_float32_input','text':body,'origin':sid,'different_vertex_count':len(differing),'different_indices':differing,'maximum_saved_coordinate_delta_m':max((max(abs(x-y) for x,y in zip(p,q)) for p,q in zip(b,c)),default=0),
                  'conclusion':'Identical float32 mesh input: direct-local authoring cannot fix this failure by coordinate precision alone.' if not differing else 'Inputs differ; consult exact stages and source polygon records before attributing causality.'})
            for strategy in ['world_then_local_002','direct_local_uvd']:
                p=all_saved[(body,'main_D08',strategy)];q=all_saved[(body,'main_D09',strategy)]
                summary['comparisons'].append({'comparison':'matched_caption_D08_vs_D09_local_storage','text':body,'strategy':strategy,'bit_identical_vertex_arrays':all(key(x)==key(y) for x,y in zip(p,q)),'same_vertex_count':len(p)==len(q),
                  'D08_first_failing_stage':all_records[(body,'main_D08',strategy)]['first_failing_stage'],'D09_first_failing_stage':all_records[(body,'main_D09',strategy)]['first_failing_stage']})
        for raw in summary['raw_fonts']:
            if raw['float32_guard_failure_count']:summary['conclusions'].append({'finding':'raw_font_already_fails_area_guard','text':raw['text'],'bad_triangle_count':raw['float32_guard_failure_count'],'detail_record_key':raw['detail_record_key'],'meaning':'Do not attribute all failure to section world coordinates. Inspect font polygon/triangulation evidence.'})
        summary['status']='diagnostic_complete_no_candidate_adopted';summary['source_fix_decision']='Pending parent review of exact causal stage. Never increase area tolerance, discard positive-area features or filter failed triangles merely to pass.'
    except Exception as exc:
        summary['status']='diagnostic_failed';summary['error']=str(exc);summary['traceback']=traceback.format_exc()
    summary['input_bytes_unchanged']=all(sha(p)==h for p,h in before.items());flush()
    print(json.dumps({'status':summary['status'],'summary':str(report_path),'raw_fonts':summary['raw_fonts'],'comparisons':summary['comparisons'],'input_bytes_unchanged':summary['input_bytes_unchanged']},indent=2))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--builder',type=Path,required=True);p.add_argument('--contract',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);result=run(a);raise SystemExit(0 if result['status']=='diagnostic_complete_no_candidate_adopted' and result['input_bytes_unchanged'] else 1)
