from pathlib import Path
import json,hashlib,copy
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union,triangulate
from shapely.geometry.polygon import orient
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());source=R/'Game/data/generated/structural_meshes.json';D=json.loads(source.read_text());C=json.loads((R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json').read_text())
byid={r['id']:r for r in D['regions']};cuts=C['shared_floor_cuts'];masks={};witnesses=[];replacements=[];checks=0
def serial(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def parts(g):return list(g.geoms) if hasattr(g,'geoms') else [g]
protected_axis=box(-2,-530,2,530);protected_bypass=LineString(C['protected_polyline_xz']).buffer(2,cap_style=2,join_style=2)
for cut in cuts:
 mask=box(*cut['bounds_xz']);assert mask.intersection(protected_axis).area<1e-9 and mask.intersection(protected_bypass).area<1e-9;checks+=2
 for owner in cut['owners']:masks.setdefault(owner,[]).append(mask)
 original=unary_union([Polygon(t) for owner in cut['owners'] for t in byid[owner]['triangles']]);area=mask.intersection(original).area;assert abs(area-cut['area_m2'])<1e-7;checks+=1
 witnesses.append({'station':cut['station'],'actual_removed_m2':area,'owner_ids':cut['owners'],'mask_xz':cut['bounds_xz'],'protected_axis_or_bypass_cut':False})
for owner,owner_masks in masks.items():
 original=byid[owner];mask=unary_union(owner_masks);oldshape=unary_union([Polygon(t) for t in original['triangles']]);after=oldshape.difference(mask);assert after.is_valid
 triangles=[]
 for old in original['triangles']:
  for piece in parts(Polygon(old).difference(mask)):
   if piece.is_empty or piece.area<1e-9:continue
   for face in triangulate(piece):
    if piece.covers(face):triangles.append([list(p) for p in list(face.exterior.coords)[:3]])
 rebuilt=unary_union([Polygon(t) for t in triangles]);assert rebuilt.symmetric_difference(after).area<1e-8;assert abs(sum(Polygon(t).area for t in triangles)-after.area)<1e-8;checks+=2
 rings=[]
 for poly in parts(after):
  poly=orient(poly,sign=1.0);rings.append([list(p) for p in list(poly.exterior.coords)[:-1]])
  rings.extend([[list(p) for p in list(hole.coords)[:-1]] for hole in poly.interiors])
 replacement=copy.deepcopy(original);replacement.update(triangles=triangles,rings=rings,structural_area_m2=after.area)
 chunks=[]
 for chunk in original.get('render_chunks',[]):
  changed=copy.deepcopy(chunk);changed['triangles']=[]
  for old in chunk['triangles']:
   for piece in parts(Polygon(old).difference(mask)):
    if piece.is_empty or piece.area<1e-9:continue
    changed['triangles'].extend([[list(p) for p in list(t.exterior.coords)[:3]] for t in triangulate(piece) if piece.covers(t)])
  if changed['triangles']:chunks.append(changed)
 replacement['render_chunks']=chunks
 assert oldshape.intersection(protected_axis).symmetric_difference(after.intersection(protected_axis)).area<1e-9;checks+=1
 replacements.append({'owner_id':owner,'preimage_region_sha256':hashlib.sha256(serial(original)).hexdigest(),'removed_area_m2':oldshape.area-after.area,'preimage_floor_y':original['floor_y'],'replacement':replacement})
assert len(replacements)==3 and len(witnesses)==4 and abs(sum(r['removed_area_m2'] for r in replacements)-24.8)<1e-7;checks+=3
out={'schema':'astraea.group4.floor_receiving.patch.v1','active':False,'apply_owner_thread':'01a11d7f-8ef6-70bc-858d-bdf8deb7000b','base_group4_commit':'943c20d694e405a4deac54e62cbede05c71bc183','baseline_main':'affc5c807087ff87da29f3642c2d6e418241b896','original_source_file':'Game/data/generated/structural_meshes.json','original_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'owner_record_hash_encoding':'UTF8 JSON sort_keys=True,separators=(comma,colon),ensure_ascii=True','original_owner_count':len(D['regions']),'replaced_owner_count':3,'shared_pit_count':4,'total_removed_m2':24.8,'checks':checks,'all_owner_ids_materials_deck_datums_and_other_records_preserved':True,'protected_four_metre_axis_and_sixpoint_bypass_preserved':True,'no_new_generic_slab_over_owned_group4_annex':True,'north_physical_stop_adopted':False,'normal_main_floor_source_modified':False,'capacity_or_species_or_loaded_physics_accepted':False,'witnesses':witnesses,'replacements':replacements}
(W/'GROUP4_FLOOR_RECEIVING_PATCH.json').write_text(json.dumps(out,indent=2)+'\n');print('GROUP4_FLOOR_PATCH_READY',checks,'checks;4 bounded pits,3 exact replacement owners,24.8m2; shared original unchanged')
