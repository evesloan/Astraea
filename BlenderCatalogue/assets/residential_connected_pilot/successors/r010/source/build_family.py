"""Source-only D13 modular candidate. Blender -b -t 2 --python this_file -- --samples.

Reuses the hash-pinned authored shell primitives and retained furniture; writes only
to a fresh scratch output directory. Never edits Game, the catalogue, or old builders.
The reconstructed production method is data-driven; original 600-room code is absent.
"""
from pathlib import Path
import sys, json, hashlib, math, argparse, os, importlib.util
import bpy, bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
catalogue_candidates=[Path(os.environ['ASTRAEA_CATALOGUE_ROOT'])] if os.environ.get('ASTRAEA_CATALOGUE_ROOT') else []
catalogue_candidates += list(ROOT.parents)
CAT=next((p for p in catalogue_candidates if (p/'catalogue_manifest.json').is_file()),None)
assert CAT is not None,'Set ASTRAEA_CATALOGUE_ROOT to the retained catalogue root.'
inputs=json.loads((ROOT/'qa/GENERATOR_INPUTS.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def input_path(row):
    if row['project']=='Blender':return CAT/row['checkpoint_relative']
    game_candidates=[Path(os.environ['ASTRAEA_GAME_ROOT'])] if os.environ.get('ASTRAEA_GAME_ROOT') else []
    game_candidates += [CAT.parent/'Game',Path('/workspace/shared/astraea-godot-production-20261003')]
    return next((p/row['checkpoint_relative'] for p in game_candidates if (p/row['checkpoint_relative']).is_file()),Path(row['path']))
for row in inputs['files']:
    assert sha(input_path(row))==row['sha256'], 'Source drift: '+str(input_path(row))
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser();parser.add_argument('--samples',action='store_true');parser.add_argument('--addresses',nargs='*');parser.add_argument('--revision',default='r001');parser.add_argument('--render',action='store_true');parser.add_argument('--plan',default='COURT_PILOT_PLAN.json');parser.add_argument('--domestic',action='store_true')
args=parser.parse_args(argv)
plan_path=ROOT/args.plan;plan=json.loads(plan_path.read_text())
addresses=args.addresses or plan['representative_sample_addresses']
out=ROOT/'outputs'/args.revision
assert not out.exists(), 'Fresh revision required; preserve earlier source and failed evidence.'
out.mkdir(parents=True)
rooms={r['address']:r for r in plan['rooms']}

def replace_once(text,old,new):
    assert text.count(old)==1, 'Template contract changed: '+old[:70]
    return text.replace(old,new)

def author_shell(cfg):
    template='build_twin_retreat_suite.py' if cfg['layout']=='B_twin_retreat' else 'build_residential_suite.py'
    code=(ROOT/'inputs'/template).read_text()
    # The retained script's output section is excluded, so executing its geometry
    # can never save over retained sources or exports.
    code=code.split('scene=bpy.context.scene;')[0]
    assert 'save_as_mainfile' not in code and 'export_scene' not in code and '.write_text' not in code
    code=replace_once(code,"ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]", "ROOT=CAT/'assets/residential_suite'")
    if cfg['layout']=='C_gathering_gallery':
        code=replace_once(code,'left=[(-3.50,.12),(-3.50,4.0),(-3.40,4.8),(-3.0,5.5),(-2.85,6.3),(-3.15,7.2),(-3.50,7.8),(-3.50,12.75)]',
          'left=[(-3.50,.12),(-3.50,4.0),(-3.50,4.8),(-3.38,5.5),(-3.30,6.3),(-3.30,7.2),(-3.50,7.8),(-3.50,12.75)]')
        code=replace_once(code,'right=[(3.50,.12),(3.50,2.8),(3.35,3.5),(2.95,4.2),(2.75,5.1),(2.90,6.2),(3.35,7.25),(3.50,8),(3.50,12.75)]',
          'right=[(3.50,.12),(3.50,2.8),(3.15,3.5),(2.78,4.2),(2.78,5.1),(3.05,6.2),(3.40,7.25),(3.50,8),(3.50,12.75)]')
    if args.domestic:
        # Native differential privacy testing exposed 10mm central and 5mm
        # outer glass/frame slits. Widen the existing source mullions, with
        # positive pane overlap; keep the finite glass aperture unchanged.
        code=replace_once(code,"for x in [-3.45,0,3.45]:wall('SUI_WindowMullion_'+str(x),(x,12.72),(x,12.86),.48,3.60,3.60,'champagne_metal',.09)",
          "for x in [-3.45,0,3.45]:wall('SUI_WindowMullion_'+str(x),(x,12.72),(x,12.86),.48,3.60,3.60,'champagne_metal',.13)")
        # Close the whole aperture perimeter, including the original 10mm
        # sill/header seams. The extra glass is hidden5mm into each fixed frame.
        code=replace_once(code,"for a,b in [(-3.40,-.055),(.055,3.40)]:wall('SUI_WindowPane_'+str(a),(a,12.78),(b,12.78),.49,3.59,3.59,'glass',.018)",
          "for a,b in [(-3.40,-.055),(.055,3.40)]:wall('SUI_WindowPane_'+str(a),(a,12.78),(b,12.78),.475,3.605,3.605,'glass',.018)")
    ns={'__file__':str(ROOT/'inputs'/template),'CAT':CAT}
    exec(compile(code,str(ROOT/'inputs'/template),'exec'),ns)
    mesh,wall,extrusion,datum=[ns[k] for k in ['mesh','wall','extrusion','datum']]
    def remove_prefixes(prefixes):
        for ob in list(bpy.context.scene.objects):
            if any(ob.name.startswith(p) for p in prefixes):bpy.data.objects.remove(ob,do_unlink=True)
    # Floor field and built-in positions are authored with each plan, not random
    # offsets into a generic shell. No new opening is inferred outside the atrium.
    if cfg['view_policy'] not in ['real_atrium_candidate','authored_court_candidate']:
        remove_prefixes(['SUI_WindowPane','SUI_WindowMullion','SUI_WindowSill','SUI_WindowHead'])
        wall('SUI_RearOpaqueBoundary',(-3.50,12.78),(3.50,12.78),0,3.90,3.90,'ivory_enamel',.18)
        for side in [-1,1]:
            a,b=sorted([side*.16,side*3.25]);wall('SUI_RearAcousticInset_'+str(side),(a,12.675),(b,12.675),1.30,2.72,2.72,'oatmeal_weave',.025)
            wall('SUI_RearPictureRail_'+str(side),(a,12.63),(b,12.63),2.75,2.79,2.79,'warm_walnut',.06)
    if cfg['layout']=='C_gathering_gallery':
        remove_prefixes(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','DATUM_writing_chair','SUI_LoungeCarpet'])
        # A bay-like shared table on the left faces a recessed library/writing
        # edge on the right; its folded fascia frames the separate sleep zone.
        extrusion('SUI_GalleryCarpet',[(-3.25,4.25),(-.3,4.25),(.2,4.65),(.2,7.6),(-3.25,7.6)],.013,.019,'teal_weave')
        for z in [.24,.83,1.42]:
            extrusion('SUI_LibraryShelf_'+str(z),[(2.93,6.0),(3.30,6.0),(3.30,7.35),(2.93,7.35)],z,z+.055,'warm_walnut')
        extrusion('SUI_GalleryDesk',[(1.78,7.5),(3.28,7.5),(3.28,7.98),(1.9,7.98),(1.70,7.78)],.74,.80,'warm_walnut')
        for x in [1.88,3.16]:extrusion('SUI_GalleryDeskSupport_'+str(x),[(x-.05,7.55),(x+.05,7.55),(x+.05,7.91),(x-.05,7.91)],0,.74,'champagne_metal')
        datum('writing_chair',(2.20,6.75,0))
        section=[(-3.4,2.6),(-1.55,2.6),(-1.05,3.2),(1.05,3.2),(1.55,2.9),(3.4,2.9),(3.4,3.45),(-3.4,3.45)]
        n=len(section);mesh('SUI_GatheringFoldedFascia',[(x,y,z) for y in [7.95,8.15] for x,z in section],
          [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'ivory_enamel')
        extrusion('SUI_GatheringLowShelf',[(-3.37,7.9),(-1.38,7.9),(-1.16,8.1),(-1.38,8.25),(-3.37,8.25)],0,.84,'warm_walnut')
    if cfg['historical_class']=='specialty':
        remove_prefixes(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','DATUM_bed_','DATUM_bed_table_','DATUM_bed_light_','SUI_BedSconce','SUI_LoungeCarpet'])
        # One quiet acoustic enclosure surrounds the one historical rest anchor.
        # Dimensions are architectural candidates, not a claimed Mantelid fit.
        profile='S' if cfg['layout']=='S_acoustic_cove' else 'T'
        front=8.35 if profile=='S' else 8.10
        shell=[(-1.38,.32),(-1.44,1.22),(-1.20,2.18),(-.62,2.62),(.62,2.62),(1.20,2.18),(1.44,1.22),(1.38,.32)]
        for j,(a,b) in enumerate(zip(shell,shell[1:])):
            q=[(a[0],front,a[1]),(b[0],front,b[1]),(b[0],12.25,b[1]),(a[0],12.25,a[1])]
            mid=(Vector((a[0],a[1]))+Vector((b[0],b[1])))/2
            # Faceted hollow thickness stays outside usable support, no convex fill.
            n=Vector((b[1]-a[1],-(b[0]-a[0]))).normalized()*.08
            mesh('SUI_CocoonAcousticPetal_'+str(j),q+[(x+n.x,y,z+n.y)for x,y,z in q],
              [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
        # Offset privacy screens leave the front approach readable and open.
        side=-1 if profile=='S' else 1
        wall('SUI_CocoonPrivacyWing',(side*1.48,front-.1),(side*2.65,front-.55),0,1.72,1.88,'teal_weave',.16)
        wall('SUI_CocoonWingCap',(side*1.48,front-.1),(side*2.65,front-.55),1.72,1.78,1.94,'warm_walnut',.20)
        extrusion('SUI_QuietRug',[(-3.17,4.3),(-.65,4.3),(-.35,4.65),(-.35,7.55),(-3.17,7.55)],.013,.019,'clay_weave')
        if profile=='T':
            wall('SUI_QuietGalleryScreen',(-2.85,4.5),(-2.2,6.0),0,1.15,1.40,'ivory_enamel',.12)
            for y in [4.75,5.20,5.65]:
                extrusion('SUI_GalleryBookPlinth_'+str(y),[(-3.36,y),(-2.95,y),(-2.95,y+.26),(-3.36,y+.26)],.28,1.08,'warm_walnut')
        datum('cocoon_entry',(0,front-.5,0));datum('care_stance',(2.15,10.25,0))
        datum('bed_light_0',(0,11.8,2.48))
        extrusion('SUI_CocoonLightHousing',[(-.23,11.65),(.23,11.65),(.23,11.95),(-.23,11.95)],2.50,2.57,'champagne_metal')
        extrusion('SUI_CocoonLightLens',[(-.20,11.68),(.20,11.68),(.20,11.92),(-.20,11.92)],2.485,2.50,'lens')
    if cfg['historical_class']=='family':
        # Three adult-usable proposed rest positions, never an automatic nursery.
        # The same architectural grammar fits the documented family class, with
        # an explicit new sleeping composition rather than cloning a twin.
        third=min(cfg['bed_anchors'],key=lambda a:a['source_xyz'][1])['source_xyz'];side=1 if third[0]>0 else -1
        remove_prefixes(['SUI_Writing','SUI_GalleryDesk','SUI_LibraryShelf','DATUM_writing_chair','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_LivingCase','SUI_GatheringLowShelf'])
        # The atlas places the third berth in a side bay at depth6.45m. Retain
        # that exact point and move the writing edge to the opposite side.
        a,b=sorted([-side*3.28,-side*1.42]);extrusion('SUI_FamilyWritingTop',[(a,7.52),(b,7.52),(b,8.02),(a,8.02)],.74,.80,'warm_walnut')
        for x in [a+.1,b-.1]:extrusion('SUI_FamilyWritingSupport_'+str(x),[(x-.05,7.57),(x+.05,7.57),(x+.05,7.96),(x-.05,7.96)],0,.74,'champagne_metal')
        datum('writing_chair',(-side*2.18,7.04,0))
        # A high ceiling fold, not a low screen across the berth approach.
        a,b=sorted([side*.95,side*2.65]);extrusion('SUI_FamilySideBerthCanopy',[(a,5.12),(b,5.12),(b,7.82),(a,7.82)],2.62,2.72,'oatmeal_weave')
        # Existing outer bedside fixtures remain; the third place gets a real
        # source-bound head lens without a new species-specific technology.
        x=third[0];v=third[1]+1.02
        extrusion('SUI_FamilySideBedHousing',[(x-.16,v),(x+.16,v),(x+.16,v+.12),(x-.16,v+.12)],2.43,2.62,'champagne_metal')
        extrusion('SUI_FamilySideBedLens',[(x-.12,v+.01),(x+.12,v+.01),(x+.12,v+.11),(x-.12,v+.11)],2.415,2.43,'lens')
        datum('family_third_bed_light',(x,v+.06,2.40))
    if cfg.get('view_lounge_replan',False):
        remove_prefixes(['SUI_LivingCase','SUI_SleepThresholdWing','SUI_ThresholdTimberCap','SUI_SleepingValance','SUI_Writing','DATUM_writing_chair','SUI_LoungeCarpet','SUI_BedSconce','DATUM_bed_light_','DATUM_bed_table_'])
        # The unregistered pilot's previously proposed beds move to two
        # side-facing rest alcoves, freeing the panoramic end for shared living.
        # Retained historical anchors and the two installed rooms never use it.
        wall('SUI_RestAlcovePrivacyReturn',(-3.34,7.56),(-.72,7.56),0,1.72,1.72,'ivory_enamel',.14)
        wall('SUI_RestAlcoveCap',(-3.34,7.56),(-.72,7.56),1.72,1.78,1.78,'warm_walnut',.19)
        for i,(front,back) in enumerate([(4.38,7.12),(8.14,10.75)]):
            a=ns['at'](ns['left'],front)+.09;b=ns['at'](ns['left'],back)+.09
            q=[(a,front,2.70),(-.56,front,2.94),(-.56,back,2.94),(b,back,2.70)]
            mesh('SUI_SideRestCanopy_'+str(i),q+[(u,v,w+.09)for u,v,w in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
        extrusion('SUI_ViewLoungeCarpet',[(-.40,10.20),(.55,9.65),(3.28,9.65),(3.28,12.62),(-3.25,12.62),(-3.25,11.2),(-.40,11.2)],.013,.019,'clay_weave')
        extrusion('SUI_ViewWritingDesk',[(2.70,8.05),(3.28,8.05),(3.28,9.45),(2.70,9.45)],.74,.80,'warm_walnut')
        for v in [8.15,9.32]:extrusion('SUI_ViewWritingSupport_'+str(v),[(2.74,v-.045),(3.20,v-.045),(3.20,v+.045),(2.74,v+.045)],0,.74,'champagne_metal')
        datum('writing_chair',(2.08,8.72,0))
        for i,a in enumerate(cfg['bed_anchors']):
            v=a['source_xyz'][1];u=ns['at'](ns['left'],v)+.085
            extrusion('SUI_ViewBedSconce_'+str(i),[(u,v-.18),(u+.10,v-.18),(u+.10,v+.18),(u,v+.18)],1.43,1.86,'champagne_metal')
            extrusion('SUI_ViewBedLens_'+str(i),[(u+.101,v-.14),(u+.112,v-.14),(u+.112,v+.14),(u+.101,v+.14)],1.48,1.81,'lens')
            datum('bed_light_'+str(i),(u+.14,v,1.64))
    # Stable local bed identity derives from historical marker coordinates.
    for ob in list(bpy.context.scene.objects):
        if ob.name in ['DATUM_bed_0','DATUM_bed_1']:bpy.data.objects.remove(ob,do_unlink=True)
    for a in cfg['bed_anchors']:datum('bed_'+str(a['historical_anchor_index']),a['source_xyz'])
    # Palettes swap only compatible woven roles, retaining metric UV scale and
    # roughness. The base timber/stone/metal language remains coherent.
    palette=cfg['palette']; roles={'clay':{},'teal':{'clay_weave':'teal_weave','teal_weave':'clay_weave'},'oatmeal':{'clay_weave':'oatmeal_weave','oatmeal_weave':'teal_weave'}}[palette]
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':
            for i,m in enumerate(ob.data.materials):
                if m.name in roles:ob.data.materials[i]=ns['mats'][roles[m.name]]
    if args.domestic:
        spec=importlib.util.spec_from_file_location('bathroom_enclosure_patch',ROOT/'domestic_correction/bathroom_review/bathroom_enclosure_patch.py');patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
        cfg['bathroom_enclosure_correction']=patch.apply_bathroom_enclosure(ns)
        remove_prefixes(['SUI_EntryStorage','SUI_StorageFront'])
        # Domestic provision occupies the prior storage footprint. A separate
        # shaped coat/storage tower remains behind it, outside the main route.
        extrusion('SUI_EntryCoatTower',[(2.58,2.67),(3.34,2.67),(3.25,3.37),(2.72,3.37),(2.58,3.18)],0,2.18,'warm_walnut')
        wall('SUI_CoatTowerFront',(2.56,2.75),(2.56,3.13),.22,2.00,2.00,'oatmeal_weave',.025)
        datum('kitchenette_origin',(3.025,1.40,0));datum('kitchenette_standing',(2.025,1.60,0))
    return ns

def append_source(relative,name,point=(0,0,0),yaw=0):
    path=Path(relative) if Path(relative).is_absolute() else CAT/relative
    with bpy.data.libraries.load(str(path),link=False) as (source,target):target.objects=list(source.objects)
    loaded=[ob for ob in target.objects if ob is not None and ob.type in ['MESH','EMPTY','CURVE']]
    for ob in loaded:bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update()
    root_matrices={ob:ob.matrix_world.copy() for ob in loaded if ob.parent is None}
    transform=Matrix.Translation(Vector(point))@Matrix.Rotation(yaw,4,'Z')
    for ob in loaded:
        if ob.parent is None:ob.matrix_world=transform@root_matrices[ob]
        ob.name=name+'__'+ob.name;ob['source_asset']=str(relative);ob['assembly_member']=name
    bpy.context.view_layer.update()
    for ob,original in root_matrices.items():
        expected=transform@original
        assert max(abs(ob.matrix_world[i][j]-expected[i][j])for i in range(4)for j in range(4))<1e-5,'Source-asset transform drift'
    return loaded

def marker(name):return bpy.data.objects['DATUM_'+name].location.copy()

def add_furnishings(cfg,ns):
    placements=[]
    def add(rel,label,point,yaw=0):
        append_source(rel,label,point,yaw);placements.append({'label':label,'catalogue_source':rel,'source_xyz':list(point),'source_yaw':yaw})
    bed='assets/guest_rest/source/AST-SLP-001.blend'
    for a in cfg['bed_anchors']:add(bed,'HistoricalBedAnchor_'+str(a['historical_anchor_index']),a['source_xyz'],float(a.get('source_yaw',0)))
    furniture='assets/furniture/'
    # Catalogue furniture actually exists; no invented model IDs or substitute boxes.
    if cfg.get('view_lounge_replan',False):
        seats=[];table=(1.75,11.72,0)
    elif cfg['historical_class']=='family':
        third=min(cfg['bed_anchors'],key=lambda a:a['source_xyz'][1])['source_xyz'];side=1 if third[0]>0 else -1
        seats=[];table=(-side*1.10,5.44,0)
    elif cfg['layout']=='C_gathering_gallery':
        seats=[(-2.0,5.25,0,math.pi),(-2.0,7.02,0,0)]
        table=(-2.0,6.15,0)
    elif cfg['layout']=='T_quiet_gallery':
        seats=[(-1.35,6.0,0,math.pi)];table=(-1.40,6.90,0)
    else:
        seats=[(-2.30,5.65,0,math.pi/2)];table=(-1.10 if cfg['layout']=='A_open_salon' else -1.15,5.95,0)
    if cfg.get('view_lounge_replan',False):
        add(furniture+'AST-FUR-001_day_window_bench.blend','GardenFacingSalonBench',(2.0,10.62,0),math.pi)
    elif cfg['historical_class']=='family':
        add(furniture+'AST-FUR-001_day_window_bench.blend','FamilyGatheringBench',(-side*2.18,5.29,0),side*math.pi/2)
    elif cfg['layout'] in ['A_open_salon','B_twin_retreat']:
        add(furniture+'AST-FUR-001_day_window_bench.blend','SalonBench',(-2.25 if cfg['layout']=='A_open_salon' else -2.30,5.65,0),math.pi/2)
    else:
        for i,(x,y,z,a) in enumerate(seats):add(furniture+'AST-FUR-002_day_reading_chair.blend','SalonChair_'+str(i),(x,y,z),a)
    add(furniture+'AST-FUR-003_day_table.blend','SharedTable',table)
    add(furniture+'AST-FUR-002_day_reading_chair.blend','WritingChair',tuple(marker('writing_chair')),math.pi/2 if cfg.get('view_lounge_replan',False) else math.pi)
    for definition,aid in [('bath_vanity','AST-SAN-001'),('bath_wc','AST-SAN-002'),('bath_shower','AST-SAN-003')]:
        add('assets/guest_wash/source/'+aid+'.blend',definition,tuple(marker(definition)))
    add('assets/guest_entry_door/source/AST-DOR-002.blend','EntryDoor',(0,-.05,0))
    # Same parent coordinate conversion as the current Godot bath adapter.
    add('assets/guest_privacy_door/source/AST-DOR-001.blend','BathroomDoor',(-.7,2.9,0),math.pi/2)
    if args.domestic:
        path=ROOT/'domestic_correction/outputs/kitchenette_r001/suite_kitchenette.blend'
        append_source(path,'SuiteKitchenette',(3.025,1.40,0),-math.pi/2)
        placements.append({'label':'SuiteKitchenette','candidate_source':str(path.relative_to(ROOT)),
          'candidate_export':str(path.with_suffix('.glb').relative_to(ROOT)),'catalogue_source':None,
          'source_xyz':[3.025,1.40,0],'source_yaw':-math.pi/2,'status':'new domestic source candidate; not registered or installed'})
    # Layered original book-like possessions and folded textiles stay in bounded
    # supports. No extra berths or capacity are created by these static props.
    ex=ns['extrusion'];variant=cfg['occupant_props_variant']
    book_y=7.64 if cfg['layout']=='C_gathering_gallery' or cfg['historical_class']=='family' else 7.25
    book_bottom=.80 if cfg['layout']=='C_gathering_gallery' or cfg['historical_class']=='family' else .79
    for j in range(3+variant):
        if cfg.get('view_lounge_replan',False):
            x=2.85;v=8.20+j*.18;outline=[(x,v),(x+.21,v),(x+.21,v+.12),(x,v+.12)];bottom=.80
        else:
            x=(-2.9+j*.18 if side>0 else 1.75+j*.18) if cfg['historical_class']=='family' else 1.75+j*.18
            outline=[(x,book_y),(x+.12,book_y),(x+.12,book_y+.21),(x,book_y+.21)];bottom=book_bottom
        ex('SUI_DeskBook_'+str(j),outline,bottom,.98+.06*(j%3),['teal_weave','clay_weave','oatmeal_weave'][j%3])
    tx,ty,_=table
    for j in range(2):ex('SUI_TableBook_'+str(j),[(tx-.2,ty-.14),(tx+.18,ty-.14),(tx+.18,ty+.12),(tx-.2,ty+.12)],.665+j*.035,.700+j*.035,'clay_weave' if j else 'teal_weave')
    return placements

def visual_mesh_stats():
    deps=bpy.context.evaluated_depsgraph_get();bounds=[];tri=0;count=0
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);count+=1
        bounds.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    return {'mesh_count':count,'triangles':tri,'source_bounds':[list(map(min,zip(*bounds))),list(map(max,zip(*bounds)))]}

def camera(name,point,target,ortho=None):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=point;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=22
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    return o

def render_source(cfg,dest):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    world=bpy.data.worlds.new('SourceReviewNeutralWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.16,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
    for j,(point,power,size) in enumerate([((0,4.0,3.0),450,3),((0,8.5,3.3),500,3),((0,12.4,2.5),180,2)]):
        d=bpy.data.lights.new('QA_area_'+str(j),'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=point
    views=[('entry_eye',(0,1.85,1.65),(-.20,9.2,1.45),None),('salon_eye',(2.25,5.05,1.65),(-.55,9.1,1.45),None),('plan_cutaway',(0,6.45,23),(0,6.45,0),15.3)]
    for name,point,target,ortho in views:
        hidden=[]
        if ortho:
            for o in scene.objects:
                if o.type=='MESH' and (o.name.startswith('SUI_Ceiling') or o.name.startswith('SUI_BathCeiling') or o.name.startswith('SUI_SleepingValance') or o.name.startswith('SUI_GatheringFoldedFascia')):o.hide_render=True;hidden.append(o)
        scene.camera=camera(name,point,target,ortho);scene.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
        for o in hidden:o.hide_render=False

results=[]
for address in addresses:
    cfg=rooms[address];assert not cfg['preserve_installed'],'Existing rooms must remain byte-for-byte; do not regenerate them.'
    dest=out/address;dest.mkdir()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ns=author_shell(cfg)
    # Shell export remains separate from reusable furniture and operable doors.
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    shell_stats=visual_mesh_stats();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'shell.blend'))
    # Batch only temporary export copies; preserve semantic editable source.
    groups={};copies=[]
    for ob in list(scene.objects):
        if ob.type!='MESH':continue
        copy=ob.copy();copy.data=ob.data.copy();bpy.context.collection.objects.link(copy);copies.append(copy)
        key=tuple(m.name for m in ob.data.materials);groups.setdefault(key,[]).append(copy)
    export_meshes=[]
    for key,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='SUI_Runtime_'+key[0];export_meshes.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in export_meshes:ob.select_set(True)
    for ob in scene.objects:
        if ob.type=='EMPTY':ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(dest/'shell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
    for ob in export_meshes:bpy.data.objects.remove(ob,do_unlink=True)
    placements=add_furnishings(cfg,ns);assembly_stats=visual_mesh_stats()
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest/'assembly.blend'))
    receipt={'address':address,'layout':cfg['layout'],'view_policy':cfg['view_policy'],'input_plan_sha256':sha(plan_path),
      'source_frame':'Blender +X right, +Y inward, +Z up; origin is room entry-wall floor datum',
      'source_origin_world_xyz':cfg['source_origin_world_xyz'],'source_yaw_godot':cfg['source_yaw_godot'],
      'historical_bed_anchors':cfg['bed_anchors'],'shell_stats':shell_stats,'assembly_stats':assembly_stats,'placements':placements,
      'files':{n:sha(dest/n) for n in ['shell.blend','shell.glb','assembly.blend']},
      'status':'source-only representative candidate; geometry/visual/runtime review pending',
      'game_writes':False,'catalogue_writes':False,'render_is_game_evidence':False,'handing_applied':False,
      'limits':['No Game imports or tests','No final species-body fit','No functional privacy/molt/service claim','No invented exterior view','Room source does not construct the missing street support']}
    (dest/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');results.append(receipt)
    if args.render:render_source(cfg,dest)
    print('ROOM_SOURCE_COMPLETE',address,flush=True)
for row in inputs['files']:assert sha(input_path(row))==row['sha256'], 'Source drift after build: '+str(input_path(row))
(out/'BATCH_RECEIPT.json').write_text(json.dumps({'status':'source_only','rooms':results,'input_hashes_unchanged':True,'retained_input_count':len(inputs['files']),'game_or_catalogue_writes':False},indent=2)+'\n')
print('BATCH_SOURCE_COMPLETE',len(results),str(out),flush=True)
