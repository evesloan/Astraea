"""Compile explicitly authored structural polygons; never generate room programmes.
Requires Shapely2.1.2. Output is runtime-independent cached mesh data.
"""
from pathlib import Path
import json,hashlib,math
import shapely
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
root=Path(__file__).resolve().parents[1]
source=root/'data/spatial_layout.json';layout=json.loads(source.read_text())
contract=json.loads((root/'data/design_contract.json').read_text())
elevations={x['deck_id']:x['floor_elevation_m'] for x in contract['deck_datums']}
from theater_surface_policy import verify_theater_surfaces
theater_ids=verify_theater_surfaces(root,layout,elevations)
from theater_source_volumes import TheaterSourceVolumes
source_volumes=TheaterSourceVolumes(root,layout,theater_ids)
from theater_incremental_preservation import preserve_prior_records
from medical_incremental_preservation import preserve_medical_predecessor
from medical_triage_incremental_preservation import preserve_medical_triage_successor
from botanical_court_incremental_preservation import preserve_botanical_court_successor
from team_lounge_incremental_preservation import preserve_team_lounge_successor
from movement_studio_incremental_preservation import preserve_movement_studio_successor
from moss_sanctuary_incremental_preservation import preserve_moss_sanctuary_successor
from sports_care_incremental_preservation import preserve_sports_care_successor
from night_table_incremental_preservation import preserve_night_table_successor, canonicalize_night_table_predecessor_chunks
from laundry_incremental_preservation import preserve_laundry_successor, canonicalize_laundry_predecessor_chunks
from crew_batch_incremental_preservation import preserve_crew_batch_successor, canonicalize_crew_batch_predecessor_chunks
levels={item['id']:elevations[item['deck']]+item.get('offset_y',0) for item in layout['regions']}
def coplanar(a,b):
    return abs(levels[a['id']]-levels[b['id']]) < 1e-6
shapes={}
for item in layout['regions']:
    shape=Polygon(item['boundary'],item.get('holes',[]));assert shape.is_valid,item['id']
    exemptions=item.get('void_exemptions',[])
    assert set(exemptions)<= ({'theater_upper_volume'} if item['id']in theater_ids else {'central_atrium'}),('Protected void exemption',item['id'])
    if exemptions and item['id']not in theater_ids:
        kind=item.get('kind')
        assert kind=='atrium_terrace' or (kind=='atrium_garden_base' and item['deck']=='D02' and 5.2<=levels[item['id']]<=6.0),item['id']
    for void in layout['voids']:
        if item['deck'] in void['decks'] and void['id'] not in exemptions:shape=shape.difference(Polygon(void['boundary']))
    shapes[item['id']]=shape
outputs=[];owned={};checks=[];superseded=[]
for item in layout['regions']:
    shape=shapes[item['id']]
    for other in layout['regions']:
        if coplanar(other,item) and other.get('priority',0)>item.get('priority',0):shape=shape.difference(shapes[other['id']])
    assert shape.is_valid,item['id'];owned[item['id']]=shape
    if shape.is_empty:
        superseded.append(item['id']);continue
    if item.get('provided_by_asset'):continue
    triangles=shapely.constrained_delaunay_triangles(shape)
    total=sum(t.area for t in triangles.geoms)
    assert abs(total-shape.area)<1e-7*max(1,shape.area),(item['id'],total,shape.area)
    for t in triangles.geoms:assert shape.covers(t)
    rings=[]
    for component in shapely.get_parts(shape):
        if component.geom_type!='Polygon':continue
        p=orient(component,sign=1.0)
        rings.append([list(c) for c in p.exterior.coords[:-1]])
        rings.extend([[list(c) for c in ring.coords[:-1]] for ring in p.interiors])
    draw_chunks=[]
    cell=item.get('render_cell_m')
    if cell:
        x0,z0,x1,z1=shape.bounds
        chunk_area=0.0
        for cx in range(math.floor(x0/cell),math.ceil(x1/cell)):
            for cz in range(math.floor(z0/cell),math.ceil(z1/cell)):
                piece=shape.intersection(box(cx*cell,cz*cell,(cx+1)*cell,(cz+1)*cell))
                if piece.area<1e-8:continue
                chunk_area+=piece.area
                draw_chunks.append({'id':f'cell_{cx}_{cz}','triangles':[[list(c) for c in t.exterior.coords[:3]] for t in shapely.constrained_delaunay_triangles(piece).geoms]})
        assert abs(chunk_area-shape.area)<1e-6*max(1,shape.area)
    outputs.append({'id':item['id'],'deck':item['deck'],'floor_y':elevations[item['deck']]+item.get('offset_y',0),'thickness':item.get('thickness',.24),'triangles':[[list(c) for c in t.exterior.coords[:3]] for t in triangles.geoms],'rings':rings,'structural_area_m2':shape.area,'render_chunks':draw_chunks,'status':item['status'],'material_role':item.get('material_role','guest_floor')})
source_volumes.validate_owned_shapes(owned)
for i,a in enumerate(layout['regions']):
    for b in layout['regions'][i+1:]:
        overlap=owned[a['id']].intersection(owned[b['id']]).area
        if a['id'] in theater_ids or b['id'] in theater_ids:
            if overlap>1e-7:source_volumes.check_pair(a,b,owned,levels)
            continue
        if coplanar(a,b):assert overlap<1e-7,(a['id'],b['id'])
        elif overlap>1e-7:
            ay,by=levels[a['id']],levels[b['id']]
            slab_overlap=min(ay,by)-max(ay-a.get('thickness',.24),by-b.get('thickness',.24))
            assert slab_overlap<1e-6,('intersecting structural slabs',a['id'],b['id'])
outputs=canonicalize_crew_batch_predecessor_chunks(root,layout,elevations,owned,outputs)
outputs,preservation=preserve_prior_records(root,layout,elevations,owned,outputs)
outputs,medical_preservation,triage_preservation,botanical_preservation,team_lounge_preservation,movement_preservation,moss_preservation,sports_care_preservation,night_table_preservation,laundry_preservation,crew_batch_preservation=preserve_crew_batch_successor(root,layout,elevations,owned,outputs,preserve_laundry_successor,preserve_night_table_successor,preserve_sports_care_successor,preserve_moss_sanctuary_successor,preserve_movement_studio_successor,preserve_team_lounge_successor,preserve_botanical_court_successor,preserve_medical_triage_successor,preserve_medical_predecessor)
checks={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'shapely':shapely.__version__,'geos':shapely.geos_version_string,'fully_superseded_regions':superseded,'regions':len(outputs),'triangles':sum(len(x['triangles']) for x in outputs),'polygon_validity':True,'triangle_area_conservation':True,'no_triangles_cross_applicable_voids':True,'central_terrace_exemptions_explicit':True,'theater_generic_void_preserved':True,'theater_authored_surface_allowlist_verified':sorted(theater_ids),'no_coplanar_region_overlap':True,'no_intersecting_slab_volumes':True,'ownership_uses_absolute_elevation':True,'scope':'Structural geometry only; not finished rooms, route acceptance, or capacity acceptance'}
checks['theater_source_part_vertical_guard']=source_volumes.receipt()
checks['theater_additive_preservation']=preservation
checks['medical_additive_preservation']=medical_preservation
checks['medical_triage_additive_preservation']=triage_preservation
checks['botanical_court_additive_preservation']=botanical_preservation
checks['team_lounge_additive_preservation']=team_lounge_preservation
checks['movement_studio_additive_preservation']=movement_preservation
checks['moss_sanctuary_additive_preservation']=moss_preservation
checks['sports_care_additive_preservation']=sports_care_preservation
checks['night_table_additive_preservation']=night_table_preservation
checks['laundry_additive_preservation']=laundry_preservation
checks['crew_batch_additive_preservation']=crew_batch_preservation
(root/'data/generated/structural_meshes.json').write_text(json.dumps({'source_checks':checks,'regions':outputs},separators=(',',':'))+'\n')
(root/'docs/LAYOUT_COMPILE_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks))
