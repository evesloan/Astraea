"""Exact bounded compiler/support proposal and contact witnesses. No load certification."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
parts=json.loads((R/'source/geometry_parts.json').read_text());contract=json.loads((R/'source/section_contract.json').read_text());layout=json.loads((G/'data/spatial_layout.json').read_text());plan=json.loads((G/'data/architecture/packages/crew_living/SECTION_DISTRIBUTION_PROPOSAL.json').read_text())
def geom(p):return Polygon(p['boundary'],p.get('holes',[]))
def poly(g):return [dict(boundary=list(p.exterior.coords)[:-1],holes=[list(h.coords)[:-1] for h in p.interiors]) for p in ([g] if g.geom_type=='Polygon' else g.geoms) if not p.is_empty]
def foot(p):
 a=p['world_aabb'];return box(a[0],a[4],a[1],a[5])
retained=unary_union([geom(r) for r in layout['regions'] if r.get('deck')=='D03']);reviewed=unary_union([geom(p) for p in contract['compiler_preview_floor_polygons']]);owned=retained.union(reviewed)
clear=unary_union([geom(p) for p in contract['source_clear_polygons']]);walls=[p for p in parts if p['name'].endswith('_LowerPanel')];upper=[p for p in parts if p['name'].endswith('_Enamel')];caps=[p for p in parts if p['kind']=='ceiling_cap'];actual_base_union=unary_union([foot(p) for p in walls]);base_union=unary_union([foot(p) for p in parts if p['name'].startswith('CRW_Wall_')]);all_needed=clear.union(base_union)
branch_add=clear.difference(owned);wall_add=base_union.difference(owned.union(branch_add));addition=all_needed.difference(owned);available=owned.union(addition)
# Floor-top contact by positive area. This witnesses proposed support, not installed floor.
base_witness=[]
for p in walls:
 f=foot(p);base_witness.append(dict(part=p['name'],base_y=12,base_area_m2=f.area,retained_contact_area_m2=f.intersection(retained).area,reviewed_contact_area_m2=f.intersection(reviewed).area,candidate_contact_area_m2=f.intersection(addition).area,total_supported_contact_area_m2=f.intersection(available).area,uncovered_area_m2=f.difference(available).area))
assert all(w['total_supported_contact_area_m2']>1e-8 and w['uncovered_area_m2']<1e-7 for w in base_witness)
# Every upper panel has the same footprint on its matching base panel.
base_map={p['name'].replace('_LowerPanel',''):p for p in walls};upper_witness=[]
for p in upper:
 q=base_map[p['name'].replace('_Enamel','')];a=foot(p).intersection(foot(q)).area;assert a>1e-8
 upper_witness.append(dict(part=p['name'],supports=[q['name']],contact_y=13.03,contact_area_m2=a))
# Continuous cap components must each have positive wall-top contact.
cap_union=unary_union([foot(p) for p in caps]);walltop=unary_union([foot(p) for p in upper]);components=[cap_union] if cap_union.geom_type=='Polygon' else list(cap_union.geoms);cap_components=[]
for i,g in enumerate(components):
 a=g.intersection(walltop).area;assert a>1e-8
 cap_components.append(dict(component=i,area_m2=g.area,wall_top_contact_y=15.2,wall_top_contact_area_m2=a))
cap_witness=[]
for p in caps:
 f=foot(p);i=next(i for i,g in enumerate(components) if g.covers(f));cap_witness.append(dict(part=p['name'],connected_cap_component=i,direct_wall_top_contact_area_m2=f.intersection(walltop).area,support_path='continuous same-level cap component to positive-area wall tops; engineering span/load design untested'))
fixtures=[]
for p in parts:
 if p['kind']!='fixture_support':continue
 prefix=p['name'].rsplit('_Hanger',1)[0];q=next(q for q in parts if q['name']==prefix+'_Housing');f=foot(p);housing=f.intersection(foot(q)).area;cap=f.intersection(cap_union).area
 assert housing>1e-8 and cap>1e-8
 fixtures.append(dict(part=p['name'],housing=q['name'],housing_contact_y=15.14,housing_contact_area_m2=housing,cap_contact_area_m2=cap,cap_vertical_overlap_m=.01))
# Decoration attachments use actual coincident panel faces; neither rests on an imaginary slab.
attachments=[]
for p in parts:
 if not p['name'].endswith(('_Bumper','_ServiceRecessLip')):continue
 stem=p['name'].rsplit('_',1)[0];q=base_map[stem] if p['name'].endswith('_Bumper') else next(q for q in upper if q['name']==stem+'_Enamel')
 a=p['world_aabb'];b=q['world_aabb'];span=max(a[1]-a[0],a[5]-a[4]);vertical=min(a[3],b[3])-max(a[2],b[2]);assert vertical>0
 attachments.append(dict(part=p['name'],parent_panel=q['name'],vertical_face_contact_area_m2=span*vertical))
# Fixture opal face is actually held by housing (positive volume overlap).
opal=[]
for p in parts:
 if not p['name'].endswith('_Opal'):continue
 q=next(q for q in parts if q['name']==p['name'].replace('_Opal','_Housing'));a=p['world_aabb'];b=q['world_aabb'];dz=min(a[3],b[3])-max(a[2],b[2]);area=foot(p).intersection(foot(q)).area;assert dz>0 and area>0
 opal.append(dict(part=p['name'],housing=q['name'],contact_footprint_area_m2=area,overlap_depth_m=dz))
banks=unary_union([box(a['x'][0],a['z'][0],a['x'][1],a['z'][1]) for a in plan['bank_source_records']]);children=unary_union([box(a['x'][0],a['z'][0],a['x'][1],a['z'][1]) for a in plan['subspaces'] if a['package_local_key']!='home_quiet_lobby']);voids=unary_union([geom(a) for a in layout['voids'] if 'D03' in a.get('decks',[])]);public=unary_union([geom(a) for a in layout['regions'] if a.get('deck')=='D03' and ('public_core' in a['id'] or a['id'] in ['D03_fore_route','D03_aft_route'])])
programmes=[p for p in json.loads((G/'data/programme_ledger.json').read_text())['destinations'] if p['historical_deck']=='D03'];programme_contacts=[]
for p in programmes:
 a=p['historical_envelope'];g=box(a['x'][0],a['z'][0],a['x'][1],a['z'][1]);ar=addition.intersection(g).area
 if ar>1e-8:programme_contacts.append(dict(parent=p['programme_key'],candidate_support_area_m2=ar,ownership='parent approval required; proposed receiving/vestibule strip only; no child-room overlap'))
rings=json.loads((G/'data/architecture/LOWER_HULL_BODY.json').read_text())['rings'];lo=next(r for r in rings if r['y']==6);hi=next(r for r in rings if r['y']==12);t=(11.76-6)/6;bottom_hull=Polygon([(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])) for a,b in zip(lo['inner'],hi['inner'])]);top_hull=Polygon(hi['inner'])
checks=dict(slab_bottom_y=11.76,slab_top_y=12,slab_thickness_m=.24,candidate_bank_overlap_m2=addition.intersection(banks).area,candidate_child_room_overlap_m2=addition.intersection(children).area,candidate_void_overlap_m2=addition.intersection(voids).area,candidate_public_core_overlap_m2=addition.intersection(public).area,candidate_outside_bottom_hull_m2=addition.difference(bottom_hull).area,candidate_outside_top_hull_m2=addition.difference(top_hull).area,duplicate_retained_or_reviewed_floor_m2=addition.intersection(owned).area,wall_bases=len(base_witness),all_bases_fully_supported_under_proposal=True,all_cap_components_have_positive_wall_contact=True,fixture_hangers=len(fixtures),structural_load_certification=False,installed_support=False,engine_run=False)
oldparts=json.loads((C/'assets/lower_staff_network/source/geometry_parts.json').read_text())['boxes'];slab_hits=[]
for p in oldparts:
 a=p['world_aabb'];height=min(12,a[3])-max(11.76,a[2])
 if height>1e-8:
  ar=addition.intersection(foot(p)).area
  if ar>1e-8:slab_hits.append(dict(part=p['name'],overlap_area_m2=ar,overlap_height_m=height))
checks['candidate_slab_AST_STF_009_intersections']=slab_hits
assert not slab_hits
assert all(checks[k]<1e-7 for k in ['candidate_bank_overlap_m2','candidate_child_room_overlap_m2','candidate_void_overlap_m2','candidate_public_core_overlap_m2','candidate_outside_bottom_hull_m2','candidate_outside_top_hull_m2','duplicate_retained_or_reviewed_floor_m2'])
D=dict(schema='astraea_crew_service_support_proposal_v1',catalogue_id='AST-STF-010',approval_status='separate parent approval required; no compiler/layout edits',original_reviewed_floor_polygons_unchanged=contract['compiler_preview_floor_polygons'],original_reviewed_area_m2=reviewed.area,branch_turn_additional_polygons=poly(branch_add),branch_turn_additional_area_m2=branch_add.area,wall_base_additional_polygons=poly(wall_add),wall_base_additional_area_m2=wall_add.area,exact_additional_compiler_support_polygons=poly(addition),exact_additional_area_m2=addition.area,source_wall_base_union_polygons=poly(actual_base_union),continuous_wall_profile_foundation_polygons=poly(base_union),foundation_detail='full0.18m projected wall/bumper/recess profile, closing0.03m strip between clear slab edge and0.15m panel base',programme_parent_contacts=programme_contacts,checks=checks,section_conflict_scope='D03 void/public/bank/child/hull at slab11.76–12 checked; D02 actual imported plant/support penetration needs parent source/export survey',witness_file='../qa/SUPPORT_CONTACT_WITNESSES.json')
(R/'source/SUPPORT_OWNERSHIP_PROPOSAL.json').write_text(json.dumps(D,indent=2)+'\n');(R/'qa/SUPPORT_CONTACT_WITNESSES.json').write_text(json.dumps(dict(wall_bases=base_witness,upper_panel_contacts=upper_witness,cap_components=cap_components,cap_cells=cap_witness,fixture_hangers=fixtures,opal_housing=opal,panel_attachments=attachments),indent=2)+'\n')
contract['support_ownership_proposal']='SUPPORT_OWNERSHIP_PROPOSAL.json';contract['source_support_installed']=False;(R/'source/section_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
print(json.dumps(dict(branch_turn_m2=branch_add.area,wall_base_m2=wall_add.area,total_additional_m2=addition.area,programme_parent_contacts=programme_contacts,checks=checks),indent=2))
