"""Read exact published Group1 Git blobs; write only owned integration-support artifacts."""
from pathlib import Path
import ast,difflib,hashlib,json,re,struct,subprocess
import numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];G1='47eb8359caa5531e04122b6e56292f8c44d4281a'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git_file(path):return subprocess.check_output(['git','-C',str(R),'show',G1+':'+path])
def read(path):return json.loads(git_file(path))
def save(name,data):(W/name).write_text(json.dumps(data,indent=2)+'\n')
snapshot=json.load(open(W/'EXACT_SOURCE_SNAPSHOT.json'))
for path,pin in snapshot['inputs'].items():assert sha(git_file(path))==pin['sha256'],path
def apply_exact(text,patch):
    hunks=re.split(r'^@@ .*?@@.*\n',patch,flags=re.M)[1:];assert hunks
    for hunk in hunks:
        before=[];after=[]
        for line in hunk.splitlines(keepends=True):
            if line.startswith(('---','+++')):break
            if line.startswith((' ','-')):before.append(line[1:])
            if line.startswith((' ','+')):after.append(line[1:])
        old=''.join(before);new=''.join(after);assert old and text.count(old)==1,('Exact patch preimage absent/nonunique',old[:150]);text=text.replace(old,new,1)
    return text
def patch(path,before,after,name):
    out=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
    assert apply_exact(before,out)==after
    (W/name).write_text(out);return {'path':path,'before_sha256':sha(before.encode()),'after_sha256':sha(after.encode()),'patch':name,'patch_sha256':sha(out.encode())}
checks=[]
ship=git_file('Game/scripts/ship.gd').decode();after=ship
old='\tload("res://scripts/medical_welcome.gd").build($ShipSpace/Districts,self)\n'
assert after.count(old)==1 and 'group8/medical_privacy.gd'not in after
after=after.replace(old,old+'\tload("res://scripts/group8/medical_privacy.gd").build(self)\n')
marker='\tif OS.get_environment("ASTRAEA_TRACE_STARTUP")=="1":print("STARTUP load(res://scripts/staff_section.gd).build($ShipSpace/Districts,self)")\n'
assert after.count(marker)==1 and 'group8/synthesis_plant.gd'not in after
after=after.replace(marker,marker+'\t# Floor-first adoption and visual hold:see Group8 integration support.\n\tload("res://scripts/group8/synthesis_plant.gd").build(self,true)\n')
for existing in ['group8/crown_interiors.gd','group8/orchard_service.gd','group8/arrivals_service.gd']:assert ship.count(existing)==after.count(existing)==1
checks.append(patch('Game/scripts/ship.gd',ship,after,'group1_ship_floor_first_and_medical.patch'))
stream=git_file('Game/scripts/remaining_batch_receiving.gd').decode();marker='\troom.set_meta("stream_loaded",true)\n';assert stream.count(marker)==1
after=stream.replace(marker,'\tif str(item.key)=="D05_directory_02":load("res://scripts/group8/medical_bay.gd").build(ship,room)\n'+marker)
for existing in ['group8/library_service.gd','group8/dining_service.gd']:assert stream.count(existing)==after.count(existing)==1
checks.append(patch('Game/scripts/remaining_batch_receiving.gd',stream,after,'group1_stream_medical_bay_preserving_installed.patch'))
before=git_file('Game/scripts/received_sections.gd').decode();after=apply_exact(before,(R/'Game/docs/group8/received_dining_fixture_adaptation.patch').read_text());checks.append(patch('Game/scripts/received_sections.gd',before,after,'group1_received_two_dining_fixture_hooks.patch'))
before=git_file('Game/tests/validate_medical_structure.gd').decode();after=apply_exact(before,(R/'Game/docs/group8/medical_privacy_structure_successor.patch').read_text());checks.append(patch('Game/tests/validate_medical_structure.gd',before,after,'group1_optional_medical_fitted_guard.patch'))
assert sha((R/'Game/tests/group8/medical_privacy_successor_guard.gd').read_bytes())=='cc10243828a2d167ae516b350387a3b7b31dff17807b1a611035daa7ad37c179'
assert sha((R/'Game/data/architecture/group8/MEDICAL_PRIVACY_SUCCESSOR_PROOF.json').read_bytes())=='66991f0e183c4ec60a9ce9d921e7f3c3d90b0375e0c9d02b244e75323d3b752b'
save('PATCH_PREIMAGE_AND_PRESERVATION_CHECKS.json',{'status':'PASS_EXACT_STATIC_PATCH_CHECKS','group1_commit':G1,'patches':checks,'existing_crown_arrivals_orchard_library_dining_hooks_preserved':True,'strict_original_static_medical_path_preserved':True,'runtime_or_shared_proof_acceptance':False})
# Independent existing GLB parser:extract only its pure reader;do not execute the old report writer.
source=R/'BlenderCatalogue/assets/group8_dining_service_20261012/verify_dining_export.py'
tree=ast.parse(source.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='triangles')
namespace={'np':np,'struct':struct,'json':json,'hashlib':hashlib};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),namespace)
synth=json.load(open(R/'BlenderCatalogue/assets/group8_synthesis_plant_20261012/PLAN.json'))
unbatched=R/'BlenderCatalogue/assets/group8_synthesis_plant_20261012'/synth['unbatched_export']['file'];assert sha(unbatched.read_bytes())==synth['unbatched_export']['sha256']
_,bounds,_=namespace['triangles'](unbatched)
definition=read('Game/data/generated/structural_meshes.json');retained=next(r for r in definition['regions']if r['id']=='D01_synthesis_service_bay')
original=unary_union([Polygon(t)for t in retained['triangles']]);proposal=json.load(open(R/'Game/data/architecture/group8/synthesis_floor_proposal.json'))
candidate=unary_union([Polygon(t)for r in proposal['regions']for t in r['triangles']]);combined=unary_union([original,candidate]);assert original.intersection(candidate).area<1e-8
assert sha(git_file('Game/data/generated/structural_meshes.json'))==proposal['original_structural_sha256']
pad_results=[]
for pad in synth['supports']:
    x,y,z=pad['at'];assert abs(y)<1e-7 and combined.buffer(1e-7).covers(Point(x,z));pad_results.append({'unit':pad['unit'],'at':pad['at'],'centre_covered':True})
ground=[];missing=[];max_bound_error=0.0
for row in synth['meshes']:
    a=row['world_aabb'];v=bounds[row['name']];actual=[v[0][0],v[1][0],v[0][1],v[1][1],v[0][2],v[1][2]];max_bound_error=max(max_bound_error,max(abs(x-y)for x,y in zip(a,actual)))
    if abs(a[2])>1e-7:continue
    face=box(a[0],a[4],a[1],a[5]);gap=face.difference(combined)
    ground.append({'source_mesh':row['name'],'footprint_m2':face.area,'covered_m2':face.intersection(combined).area,'uncovered_m2':gap.area})
    if gap.area>1e-7:missing.append(gap)
assert max_bound_error<.00002
strips=unary_union(missing);assert abs(strips.area-21.252)<1e-6
regions=[]
for i,poly in enumerate(list(strips.geoms)if strips.geom_type=='MultiPolygon'else[strips]):
    triangles=[list(t.exterior.coords)[:-1]for t in constrained_delaunay_triangles(poly).geoms]
    assert abs(sum(Polygon(t).area for t in triangles)-poly.area)<1e-8
    assert all(poly.covers(Polygon(t))for t in triangles)
    regions.append({'id':'g8_synthesis_wall_bearing_PROPOSAL_%02d'%i,'deck':'D01','floor_y':0,'thickness':.24,'rings':[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1]for r in poly.interiors],'triangles':triangles,'render_chunks':[{'id':'bearing_strip','triangles':triangles}],'material_role':'staff_floor','structural_area_m2':poly.area,'navigation_surface':False,'walking_area_credit':False,'status':'Owner decision proposal;not adopted or primary engineering accepted'})
assert strips.intersection(original).area<1e-8 and strips.intersection(candidate).area<1e-8
assert box(-98,-34,-52,34).covers(strips)
all_supported=unary_union([combined,strips])
for row in synth['meshes']:
    a=row['world_aabb']
    if abs(a[2])<1e-7:assert all_supported.buffer(1e-7).covers(box(a[0],a[4],a[1],a[5]))
save('SYNTHESIS_WALL_BEARING_STRIP_PROPOSAL.json',{'status':'PROPOSED_APPEND_ONLY_GROUND_BEARING','group1_commit':G1,'base_floor_proposal_sha256':sha((R/'Game/data/architecture/group8/synthesis_floor_proposal.json').read_bytes()),'original_floor_unchanged':True,'current_original_synthesis_floor_m2':original.area,'existing_proposal_m2':candidate.area,'extra_missing_only_strip_m2':strips.area,'total_new_proposed_m2':candidate.area+strips.area,'existing_floor_positive_overlap_m2':0,'programme_expansion_or_capacity_change':0,'active_adoption':False,'load_capacity_or_primary_engineering_acceptance':False,'regions':regions})
roofs=[r for r in synth['meshes']if r['name'].startswith('G8S_PlantEnclosure_LocalRoof')];walls=[r for r in synth['meshes']if any(n in r['name']for n in['_LongWall','_EndWall'])]
roof_min=min(r['world_aabb'][2]for r in roofs);wall_max=max(r['world_aabb'][3]for r in walls);roof_max=max(r['world_aabb'][3]for r in roofs);upper=[r for r in definition['regions']if abs(r['floor_y']-6)<1e-7]+[r for r in read('Game/data/generated/received_structural_meshes.json')['regions']if abs(r['floor_y']-6)<1e-7]
upper_matches=[]
for row in upper:
    q=unary_union([Polygon(t)for t in row['triangles']])
    if q.intersects(box(-95,-30,-56,30)):upper_matches.append({'id':row['id'],'underside_y':row['floor_y']-row['thickness'],'gap_above_roof_m':row['floor_y']-row['thickness']-roof_max})
assert all(row['gap_above_roof_m']>0 for row in upper_matches)
save('SYNTHESIS_FLOOR_ROOF_74_PAD_CERTIFICATE.json',{'status':'74_PAD_CENTRES_PASS_FIVE_WALL_BEARING_STRIPS_AND_ROOF_CLOSURE_REQUIRE_DECISION','group1_commit':G1,'preserved_base_floor_positive_overlap_m2':original.intersection(candidate).area,'pad_centres_checked':len(pad_results),'pads':pad_results,'actual_unbatched_glb_bound_max_error_m':max_bound_error,'ground_source_footprints_checked':len(ground),'ground_footprints':ground,'extra_wall_bearing_area_m2':strips.area,'roof_panels':len(roofs),'roof_top_y':roof_max,'wall_to_roof_open_gap_m':roof_min-wall_max,'current_upper_floor_clearances':upper_matches,'actual_shared_adoption_or_primary_engineering_acceptance':False})
# Exact embedded images are export dependencies;do not invoke imports or invent derived pixels.
closure=[];target=W/'exact_embedded_textures';target.mkdir(exist_ok=True)
for file in ['G8_LIBRARY_SERVICE_r006.glb','G8_MEDICAL_PRIVACY_r003.glb','G8_MEDICAL_BAY_r005.glb','G8_SYNTHESIS_PLANT_r002.glb','G8_DINING_SERVICE_r003.glb']:
    raw=(R/'Game/assets/models'/file).read_bytes();size,_=struct.unpack_from('<II',raw,12);j=json.loads(raw[20:20+size]);offset=20+size;length,_=struct.unpack_from('<II',raw,offset);binary=raw[offset+8:offset+8+length];images=[]
    for i,img in enumerate(j.get('images',[])):
        assert 'bufferView'in img,'External texture requires separate provenance'
        v=j['bufferViews'][img['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];digest=sha(data);assert img.get('mimeType','image/png')=='image/png';assert data.startswith(b'\x89PNG\r\n\x1a\n')
        path=target/(digest+'.png')
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
        images.append({'gltf_image_index':i,'gltf_image_name':img.get('name'),'bytes':len(data),'sha256':digest,'exact_bytes_file':'exact_embedded_textures/'+path.name,'generated_dependency_name_candidate':Path(file).stem+'_'+str(img.get('name',i))+'.png','generated_import_path_requires_owner_confirmation':True})
    closure.append({'runtime':file,'runtime_sha256':sha(raw),'images':images,'geometry_or_uv_or_material_changes':0})
save('EXACT_MODEL_TEXTURE_CLOSURE.json',{'status':'PASS_BYTE_EXACT_EMBEDDED_PNG_CLOSURE','models':closure,'source_or_engine_import_changes':0,'owner_action':'Preserve generated PNG and import/remap dependencies before final pack;confirm names from actual imports,never replace pixels or add aliases to reduce memory without proof.'})
print(json.dumps({'status':'PASS_STATIC_INTEGRATION_SUPPORT_WITH_EXPLICIT_HOLDS','group1_commit':G1,'exact_rebased_patches':len(checks),'preserved_installed_hooks':5,'synthesis_pad_centres':len(pad_results),'synthesis_ground_footprints':len(ground),'new_missing_bearing_strips_m2':strips.area,'source_roof_closure_gap_m':roof_min-wall_max,'model_texture_closures':len(closure),'engine_import_build_processes':0}))
