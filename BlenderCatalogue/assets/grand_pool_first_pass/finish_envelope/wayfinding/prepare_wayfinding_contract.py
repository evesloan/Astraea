"""Read retained source records. Write this scratch package only; never invoke engines."""
import argparse,json,math
from pathlib import Path
from wayfinding_geometry import *
HERE=Path(__file__).resolve().parent
DEFAULT_CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
DEFAULT_GAME=Path('/workspace/shared/astraea-godot-production-20261003')

def prepare(cat,game):
    section_path='assets/grand_pool_orchard_section/source/connected_contract.json'
    section=json.loads((cat/section_path).read_text());parts={p['name']:p for p in section['source_parts'] if not p.get('export_excluded')}
    runtime_path='data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json';runtime=json.loads((game/runtime_path).read_text())
    placements={p['name']:p for p in runtime['placements']}
    towel_path='assets/aquatic_towel_use/qa/source_geometry.json';towel=json.loads((cat/towel_path).read_text())
    supports={};signs=[]
    core_path='assets/grand_pool_orchard_section/exports/AST-CIR-005_forward_pool_market.glb'
    core_triangles=glb_triangles(cat/core_path,[0,0,-432])
    def core_support(name,floor,ceiling):
        b=[[-7.88,floor+3.2,-435],[-7.72,ceiling,-429]]
        tri=[t for t in core_triangles if all(all(b[0][i]-1e-4<=v[i]<=b[1][i]+1e-4 for i in range(3)) for v in t)]
        assert len(tri)>=12,(name,len(tri))
        vs=[v for t in tri for v in t];faces=[list(range(i,i+3)) for i in range(0,len(vs),3)]
        supports[name]={'record':core_path,'object':name,'owner':'AST-CIR-005','kind':'source_named_export_triangles','bounds_xyz':bounds(vs),'world_vertices':vs,'triangles':faces,'world_translation':[0,0,-432],'source_generator':'assets/grand_pool_orchard_section/source/build_source_derivatives.py','source_equality_evidence':'assets/grand_pool_orchard_section/qa/source_export_verification.json'}
        return supports[name]
    def section_support(name):
        if name not in supports:
            p=parts[name];b=bounds(p['world_vertices'])
            assert len(p['world_vertices'])==8 and all(any(norm(sub(q,v))<1e-4 for v in p['world_vertices']) for q in corners(b)),name
            supports[name]={'record':section_path,'object':name,'owner':p['parent_design_id'],'kind':'source_record_axis_aligned_box','bounds_xyz':b,'world_vertices':p['world_vertices']}
        return supports[name]
    def towel_support(aid,name,placement_name):
        key=placement_name+'/'+name
        if key not in supports:
            p=next(p for p in towel[aid]['parts'] if p['name']==name);assert p['motion_group']=='fixed'
            vs=[blender_to_world(v,placements[placement_name]) for v in p['vertices']]
            supports[key]={'record':towel_path,'asset':aid,'object':name,'owner':aid,'kind':'evaluated_source_triangles','placement_name':placement_name,'placement':placements[placement_name], 'bounds_xyz':bounds(vs),'world_vertices':vs,'triangles':p['triangles']}
        return supports[key]
    def sign(sid,text,origin,normal,w,h,support,letter_height,min_letter_height=None):
        n=normal;up=[0,1,0];right=cross(up,n)
        s={'id':sid,'text_lines':text,'origin_xyz':origin,'normal_xyz':n,'right_xyz':right,'up_xyz':up,'width_m':w,'height_m':h,'frame_border_m':min(.05,h*.14),'frame_depth_m':.08,'backing_depth_m':.015,'glyph_depth_m':.004,'glyph_cap_height_m':letter_height,'minimum_glyph_cap_height_m':min_letter_height or letter_height*.88,'primary_support':support,'components':[],'contact_patches':[],'collision_contract':'static frame/backing/mount geometry; glyphs and fastener heads visual only','source_family':'residential_wayfinding_bay','catalogue_id':'AST-RES-001','design_reference_objects':['RES_MapFrame','RES_MapBacking']}
        border=s['frame_border_m']
        s['components']=[{'name':'MapFrame','role':'warm_walnut','local_bounds_uvd':[[-w/2,-h/2,.03],[w/2,h/2,.11]],'collision':True},
                         {'name':'MapBacking','role':'ivory_enamel','local_bounds_uvd':[[-w/2+border,-h/2+border,.109],[w/2-border,h/2-border,.124]],'collision':True}]
        for i,(u,v) in enumerate([(-w/2+border*.45,-h/2+border*.45),(w/2-border*.45,-h/2+border*.45),(-w/2+border*.45,h/2-border*.45),(w/2-border*.45,h/2-border*.45)]):
            s['components'].append({'name':'FrameFastener_'+str(i),'role':'champagne_metal','local_bounds_uvd':[[u-.006,v-.006,.108],[u+.006,v+.006,.118]],'collision':False,'shape':'octagonal_fastener'})
        s['glyph_envelope_local_uvd']=[[-w/2+border+.025,-h/2+border+.015,.123],[w/2-border-.025,h/2-border-.015,.129]]
        signs.append(s);return s
    def component(s,name,b,world=False):
        key='world_bounds_xyz' if world else 'local_bounds_uvd'
        s['components'].append({'name':name,'role':'champagne_metal',key:b,'collision':True})
    def face_contact(s,key,u_range,v_range):
        # All four corners are on the named source face. A 2 mm root engages source.
        bb=local_box(s,[[u_range[0],v_range[0],0],[u_range[1],v_range[1],0]])
        axis=max(range(3),key=lambda k:abs(s['normal_xyz'][k]))
        s['contact_patches'].append({'support':key,'bounds_xyz':bb,'normal_axis':axis,'outward_normal_xyz':s['normal_xyz']})
    def pads(s,key,centre_v=0):
        for i,u in enumerate([-s['width_m']*.30,s['width_m']*.30]):
            b=[[u-.05,centre_v-.035,-.002],[u+.05,centre_v+.035,.031]]
            component(s,'FixedPad_'+str(i),b);face_contact(s,key,[u-.05,u+.05],[centre_v-.035,centre_v+.035])
    def straps(s,key,contact_y):
        cv=contact_y-s['origin_xyz'][1]
        pads(s,key,cv)
        for i,u in enumerate([-s['width_m']*.30,s['width_m']*.30]):
            component(s,'UpstandingBackstrap_'+str(i),[[u-.025,cv,.014],[u+.025,s['height_m']*.28,.033]])
    for suffix,floor,header,label in [('D08',44,'GPM_CORE_PortalHeader_07','Grand Pool'),('D09',52.5,'GPM_CORE_PortalHeader_08','Orchard Market')]:
        b=core_support(header,floor,52.26 if floor==44 else 60.76)['bounds_xyz'];s=sign('main_'+suffix,[label],[b[1][0],floor+3.75,-432],[1,0,0],2.4,.6,header,.23,.19);pads(s,header)
        s['protected_public_clear_height_m']=3.2;s['floor_y']=floor;s['viewpoint_xyz']=[-4.9,floor+1.65,-432]
    for sid,header,normal,label in [('threshold_stairs','GP_WetSealDoorHeader',[0,0,-1],'Pool stairs'),('threshold_lift','GP_WetSealDoorHeader.001',[0,0,1],'Pool lift')]:
        b=section_support(header)['bounds_xyz'];face=b[0][2] if normal[2]<0 else b[1][2]
        s=sign(sid,[label],[-14.55,55.46,face],normal,1.4,.4,header,.155,.135);straps(s,header,55.24)
        s['viewpoint_xyz']=[-14.55,54.15,face+normal[2]*3];s['floor_y']=52.5
    key='GP_LocalLiftHeader';b=section_support(key)['bounds_xyz']
    s=sign('lower_lift',['Orchard Market'],[b[1][0],49.47,-412.4],[1,0,0],1.4,.4,key,.145,.12);straps(s,key,49.195)
    s['viewpoint_xyz']=[-10.8,47.85,-412.4];s['floor_y']=46.2
    key='GP_RaisedEdgeFascia';b=section_support(key)['bounds_xyz']
    s=sign('ramp_lower',['Step-free','Grand Pool'],[-12,45.55,b[0][2]],[0,0,-1],1.2,.6,key,.13,.105);pads(s,key)
    s['arrow']=arrow_projection(section['public_interfaces']['D08_route_xyz'][-2],section['public_interfaces']['D08_route_xyz'][-1],s['right_xyz'],s['up_xyz'],s['normal_xyz'])
    s['route_semantics']='At the lower approach decision, turn toward the ramp entrance on the final D08 arrival segment. This arrow does not claim the following switchback is straight.'
    s['viewpoint_xyz']=[-9.4,45.65,-447.8];s['floor_y']=44
    key='GP_RampPocketCap';b=section_support(key)['bounds_xyz']
    s=sign('ramp_upper',['Step-free','Arrival'],[b[1][0],47.68,-449.75],[1,0,0],1.2,.6,key,.13,.105);straps(s,key,47.28)
    route=section['accessible_ramp']['route_xyz'];s['arrow']=arrow_projection(route[-2],route[-3],s['right_xyz'],s['up_xyz'],s['normal_xyz'])
    s['route_semantics']='At the upper landing, take the upper ramp run toward the lower arrival. Viewing plane is the east face of the west pocket guard cap.'
    s['viewpoint_xyz']=[-15.2,47.85,-447.8];s['floor_y']=46.2
    s['mount_note']='Side-mounted to pocket guard cap, not either sloping ramp handrail. Frame stays at least 1.46 m west of the upper clear run and 0.15 m south of the top landing.'
    for sid,aid,placement_name,label,height,width,depth,xs,objects in [
        ('towels','AST-AQU-007','clean_towel_retrieval','Towels',2.01,.90,.16,[-.30,.30],['dry_continuous_sculpted_hood']*2),
        ('used_towels','AST-AQU-008','used_towel_return','Used towels',1.44,.94,.10,[-.451,.451],['return_L_formed_load_cheek','return_R_formed_load_cheek'])]:
        place=placements[placement_name];sup=[towel_support(aid,n,placement_name) for n in objects]
        keys=[placement_name+'/'+n for n in objects]
        s=sign(sid,[label],yaw_point([0,height,depth],place),[1,0,0],width,.24,keys[0],.105,.085)
        s['attached_instance']=placement_name;s['viewpoint_xyz']=add(place['position_xyz'],[.9,1.65,0]);s['floor_y']=46.2
        for i,(x,record,key) in enumerate(zip(xs,sup,keys)):
            # Top foot uses the evaluated flat crown/cheek triangles, not its AABB top.
            pts=[yaw_point([x+dx,0,depth+dz],place) for dx in [-.020,.020] for dz in [-.025,.025]]
            ys=[];tri=[[record['world_vertices'][j] for j in t] for t in record['triangles']]
            for p in pts:
                origin=[p[0],record['bounds_xyz'][1][1]+1,p[2]];hits=[t for q in tri if (t:=ray_triangle(origin,[0,-1,0],q)) is not None]
                assert hits,(key,p);ys.append(origin[1]-min(hits))
            assert max(ys)-min(ys)<1e-5,(key,ys)
            y=sum(ys)/len(ys);foot=bounds(pts);foot[0][1]=y;foot[1][1]=y
            s['contact_patches'].append({'support':key,'bounds_xyz':foot,'normal_axis':1,'outward_normal_xyz':[0,1,0]})
            bb=[foot[0].copy(),foot[1].copy()];bb[0][1]-=.002;bb[1][1]=s['origin_xyz'][1]-.035
            # Reach the frame rear plane while keeping the complete mount in housing footprint.
            bb[1][0]=s['origin_xyz'][0]+.04
            component(s,'CrownFootAndUpright_'+str(i),bb,True)
    for sid,header,floor in [('staff_wet','GP_WestDoorHeader',46.2),('staff_market','GP_WestDoorHeader.001',52.5)]:
        b=section_support(header)['bounds_xyz'];s=sign(sid,['Staff only'],[b[1][0],floor+2.84,-463],[1,0,0],1.0,.28,header,.115,.095);pads(s,header)
        s['floor_y']=floor;s['viewpoint_xyz']=[-52.1,floor+1.65,-463]
    for s in signs:
        for c in s['components']:
            if 'world_bounds_xyz' not in c:c['world_bounds_xyz']=local_box(s,c['local_bounds_uvd'])
        s['glyph_envelope_world_xyz']=local_box(s,s['glyph_envelope_local_uvd'])
        s['complete_envelope_xyz']=bounds([p for c in s['components'] for p in corners(c['world_bounds_xyz'])]+corners(s['glyph_envelope_world_xyz']))
        s['viewing_distance_m']=norm(sub(s['viewpoint_xyz'],local_point(s,[0,0,.129])))
    assert len(signs)==11
    cat_paths=[section_path,towel_path,'catalogue_manifest.json','materials/material_manifest.json',
      'assets/residential_wayfinding_bay/source/build_residential_wayfinding_bay.py','assets/residential_wayfinding_bay/source/AST-RES-001.blend','assets/residential_wayfinding_bay/exports/AST-RES-001.glb',
      'assets/grand_pool_orchard_section/source/AST-AQU-016.blend','assets/grand_pool_orchard_section/source/build_connected_section.py','assets/grand_pool_orchard_section/exports/AST-AQU-016.glb',
      core_path,'assets/grand_pool_orchard_section/source/AST-CIR-005_forward_pool_market.blend','assets/grand_pool_orchard_section/source/build_source_derivatives.py','assets/grand_pool_orchard_section/qa/source_export_verification.json','assets/grand_pool_first_pass/source/placement_contract.json','assets/grand_pool_orchard_section/qa/plan_route_verification.json',
      'assets/guest_entry_door/source/build_guest_entry_door_wide.py','assets/guest_entry_door/source/AST-DOR-002_wide.blend','assets/guest_entry_door/exports/AST-DOR-002_wide.glb',
      'assets/aquatic_towel_use/source/build_towel_use.py']
    for aid in ['AST-AQU-007','AST-AQU-008']:
        cat_paths += [f'assets/aquatic_towel_use/{aid}.manifest.json',f'assets/aquatic_towel_use/source/{aid}.blend',f'assets/aquatic_towel_use/exports/{aid}.glb']
    cat_paths += ['assets/aquatic_towel_use/exports/AST-AQU-008_withdrawn.glb']
    material_manifest=json.loads((cat/'materials/material_manifest.json').read_text())['materials'];materials={k:material_manifest[k] for k in ['ivory_enamel','warm_walnut','champagne_metal']}
    cat_paths += ['materials/'+v['base_color_file'] for v in materials.values()]
    game_paths=[runtime_path,'data/architecture/GRAND_POOL_SECTION_RUNTIME.json','data/generated/structural_meshes.json','data/spatial_layout.json','scripts/ship.gd','scripts/grand_pool_section.gd','scripts/grand_pool_first_pass.gd','scripts/commons_lift.gd','scripts/guest_entry_door.gd','scripts/lift_gate.gd','scripts/lift_button.gd','tests/validate_grand_pool_first_pass.gd']
    game_paths += ['assets/models/'+n for n in ['AST-AQU-016.glb','AST-CIR-005_forward_pool_market.glb','AST-AQU-007.glb','AST-AQU-008.glb','AST-DOR-002_wide.glb']]
    assert all((game/p).is_file() for p in game_paths),'A required retained runtime input is missing'
    result={'schema':1,'status':'scratch_source_contract_pre_engine','catalogue_id':'AST-RES-001','family':'residential_wayfinding_bay','derivative_export':'AST-RES-001_pool_wayfinding.glb','new_design_ids':0,
      'coordinate_system':'Godot XYZ metres; Blender=(X,-Z,Y); sign UV plane uses right/up with outward normal right cross up',
      'source_defaults':{'catalogue':str(cat),'game':str(game)},'material_roles':materials,'supports':supports,'signs':signs,
      'pins':[{'root':root,'path':p,'sha256':sha(base/p)} for root,base,paths in [('catalogue',cat,cat_paths),('game',game,game_paths)] for p in sorted(set(paths))],
      'source_part_identity':'RES_MapFrame walnut body + RES_MapBacking ivory inset. All 11 boards are fitted derivatives owned by AST-RES-001; no change to original resting bay.',
      'protected':{'no_changes_to_original_sources':True,'main_aperture_height_m':3.2,'all_51_existing_placements_unchanged':True,'retained_route_contracts':True,'existing_gate_leaf_control_motion_unchanged':True,'old_lights':25},
      'required_gates':['source_build_not_run','evaluated_mesh_contact_and_uv_check','normal_and_effects_off_640x360_approach_legibility','source_to_export_equivalence','import_and_capsule_door_lift_cart_towel_checks','matched_full_regression','root_export_and_adoption_approval'],
      'unresolved_mounting_compromises':[], 'limitations':['Triangle source attachment verification is geometric fit, not engineering load certification.','Conservative clear volumes and sampled route envelopes do not replace Godot capsule/cart/door/regrip tests.','Source and in-engine visual acceptance have not run.']}
    dump(HERE/'wayfinding_contract.json',result)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--catalogue',type=Path,default=DEFAULT_CAT);p.add_argument('--game',type=Path,default=DEFAULT_GAME);p.add_argument('--replace-contract',action='store_true');a=p.parse_args()
    existing=HERE/'wayfinding_contract.json'
    if existing.exists():
        if not a.replace_contract:raise SystemExit('Contract already exists. Preserve it; --replace-contract requires unchanged retained pins.')
        old=json.loads(existing.read_text())
        for pin in old['pins']:
            path=(a.catalogue if pin['root']=='catalogue' else a.game)/pin['path']
            if not path.is_file() or sha(path)!=pin['sha256']:raise SystemExit('Refusing to rebaseline changed retained input: '+str(path))
    d=prepare(a.catalogue,a.game);print('Prepared',len(d['signs']),'signs;',len(d['pins']),'read-only preservation pins')
