"""Instance the reviewed shared source families into their real ship allocations.

Requires an explicit representative review receipt. Produces editable linked Blender
sections and a Godot-ready data map, not Game installation or final acceptance.
"""
from pathlib import Path
import sys,json,hashlib,math,collections,os
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
revision=os.environ.get('ASTRAEA_PRODUCTION_REVISION','production_r004')
review=ROOT/'qa/TRIPLE_FAMILY_REVIEW.json'
assert review.exists(),'Triple-family visual gate is still pending.'
approved=json.loads(review.read_text());assert approved.get('source_expansion_allowed') is True
plan=json.loads((ROOT/'RESIDENTIAL_500_PLAN.json').read_text());protos=json.loads((ROOT/'PROTOTYPE_PLAN.json').read_text())
crosswalk={r['source_envelope_index']:r for r in json.loads((ROOT/'inputs/REGULAR_500_SOURCE_CROSSWALK.json').read_text())['records']}
prototype_configs={r['prototype_key']:r for r in protos['rooms']}
out=ROOT/'outputs'/revision/'sections';assert not out.exists(),'Do not overwrite section source';out.mkdir()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
collections_by_key={};prototype_files={}
for p in protos['rooms']:
    file=ROOT/'outputs'/revision/p['address']/'assembly.blend';assert file.exists()
    detail=file.parent/'detail_props.glb';assert detail.exists(),'Export the actual source book layer before assembly.'
    prototype_files[p['prototype_key']]={'source':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
      'shell_glb':str((file.parent/'shell.glb').relative_to(ROOT)),'shell_glb_sha256':hashlib.sha256((file.parent/'shell.glb').read_bytes()).hexdigest(),
      'detail_props_glb':str(detail.relative_to(ROOT)),'detail_props_glb_sha256':hashlib.sha256(detail.read_bytes()).hexdigest()}
    with bpy.data.libraries.load(str(file),link=True) as (src,dst):dst.objects=list(src.objects)
    col=bpy.data.collections.new('SharedSource__'+p['prototype_key'])
    for ob in dst.objects:
        if ob is not None and ob.type in ['MESH','EMPTY','CURVE']:col.objects.link(ob)
    collections_by_key[p['prototype_key']]=col
sections={};instances=[]
for r in plan['rooms']:
    if r['preserve_installed']:continue
    key=r['deck']+'__'+r['house']
    if key not in sections:
        col=bpy.data.collections.new(key);scene.collection.children.link(col);sections[key]=col
    col=collections_by_key[r['prototype_key']]
    ob=bpy.data.objects.new(r['rebuild_identity'],None);ob.instance_type='COLLECTION';ob.instance_collection=col
    x,y,z=r['source_origin_world_xyz'];ob.location=(x,-z,y);ob.rotation_euler.z=r['source_yaw_godot'];sections[key].objects.link(ob)
    ob['allocation_index']=r['census_source_index'];ob['identity_status']=r['identity_status'];ob['production_status']='source_only_not_installed';ob['historical_class']=r['historical_class']
    p=json.loads((ROOT/'outputs'/revision/('PROTO__'+r['prototype_key'])/'SOURCE_RECEIPT.json').read_text())
    bindings=[]
    for anchor in r['bed_anchors']:
        matches=[a for a in p['historical_bed_anchors'] if all(abs(x-y)<1e-5 for x,y in zip(a['source_xyz'],anchor['source_xyz']))];assert len(matches)==1
        i=matches[0]['historical_anchor_index'];slot=anchor['historical_anchor_index']
        bindings.append({'unit_slot_key':crosswalk[r['census_source_index']]['proposed_rest_slot_ids'][slot],'slot_identity_status':'source-schedule proposed slot; not accepted runtime save identity','unit_anchor_index':slot,'prototype_anchor_index':i,
          'prototype_marker_name':'DATUM_bed_'+str(i),'prototype_component_label':'HistoricalBedAnchor_'+str(i),'source_xyz':anchor['source_xyz'],'world_xyz':anchor['world_xyz'],'coordinate_evidence':anchor['evidence']})
    mapping={**r,'shell_source':prototype_files[r['prototype_key']]['shell_glb'],'component_placements':p['placements'],'anchor_bindings':bindings,
      'bed_anchor_binding_rule':'Match canonical prototype bed positions to exact or explicitly proposed local anchor coordinates; retain each instance slot identity separately',
      'source_collection_instance':ob.name,'godot_extras_rule':"Read node.get_meta('extras') Dictionary; canonicalize source node names with validate_node_name()",'installed':False}
    requested=r['occupant_props_variant'];realized=prototype_configs[r['prototype_key']]['occupant_props_variant']
    mapping['requested_occupant_props_variant']=requested;mapping['occupant_props_variant']=realized
    mapping['props_variation_status']='shared-prototype realization; independently seeded per-unit variation is deferred' if requested!=realized else 'matches shared prototype realization'
    mapping['source_detail_props_layer']=prototype_files[r['prototype_key']]['detail_props_glb']
    mapping['source_detail_props_scope']='Desk and table books matching actual shared source assembly; separate from shell and catalogue furnishings.'
    instances.append(mapping)
assert len(instances)==498 and len(sections)==18
scene['source_status']='498 new regular/family source instances plus2 installed rooms retained separately; no new corridors, Game adoption or completed districts'
scene['plan_sha256']=hashlib.sha256((ROOT/'RESIDENTIAL_500_PLAN.json').read_bytes()).hexdigest()
file=out/'Astraea_500_regular_family_source.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file))
# Keep portable relative links within this candidate package. No link is changed
# in an upstream prototype, source asset or Game file.
for library in bpy.data.libraries:
    library.filepath=bpy.path.relpath(library.filepath,start=str(out))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Astraea_500_regular_family_portable.blend'))
summary={'status':'mass_source_assemblies_built_not_installed','regular_units_in_plan':500,'new_source_instances':498,'existing_instances_preserved':2,
 'class_counts':plan['counts'],'shared_prototypes':len(prototype_files),'district_sections':{k:len(v.objects)for k,v in sections.items()},
 'prototype_sources':prototype_files,'source_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob('*.blend')},
 'unit_count_delta':0,'source_plan_sha256':scene['plan_sha256'],'review_receipt_sha256':hashlib.sha256(review.read_bytes()).hexdigest(),
 'game_or_catalogue_writes':False,'views':'Source assemblies preserve candidate rear-view policy; surrounding neighborhoods and actual hull/internal vistas remain separate construction',
 'per_unit_seeded_props_variants_deferred':sum(r['requested_occupant_props_variant']!=r['occupant_props_variant']for r in instances),
 'materialized_variation':'Three coordinated standard/family architecture profiles, actual view-policy variants, two recovered family handed rest layouts and profile palettes. Additional per-unit seeded book counts are explicitly deferred.',
 'remaining':['Full500-source contact/clearance review','Physical connected corridor/floor ownership package','Independent retention','Reviewed Game adoption','Normal input/cart/door/light/persistence/runtime verification']}
(out/'MASS_SOURCE_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'GODOT_BATCH_INSTANCE_MAP.json').write_text(json.dumps({'schema':'astraea.residential_batch_candidate.v1','summary':summary,'instances':instances,
 'preserved_installed':[r for r in plan['rooms']if r['preserve_installed']]},indent=2)+'\n')
print(json.dumps(summary,indent=2),flush=True)
