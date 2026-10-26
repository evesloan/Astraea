"""Pin the aquatic route decision and exact retained lower-floor receiving.

No installed geometry, original controller or source contract is changed.
"""
from pathlib import Path
import hashlib, json, math, sys
import numpy as np
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[2]
E = R.parent / 'Astraea-resume-20261025'
D = R / 'Game/aquatic_tram_interior_20261026/r001'
assert not D.exists(), 'Preserve earlier outputs'
variants = json.loads((E/'aquatic-route-options-001.json').read_text(encoding='utf-8'))
checks = json.loads((E/'aquatic-receiving-check-002/result.json').read_text(encoding='utf-8'))
chosen = 'x18.5_in174_out248'
v = next(v for v in variants['variants'] if v['crossing_z'] == chosen)
c = next(c for c in checks['results'] if c['crossing_z'] == chosen)
assert not c['owners'] and not c['unresolved_sweeps']
floors = json.loads((R/'Game/data/generated/structural_meshes.json').read_text(encoding='utf-8'))
floor = next(f for f in floors['regions'] if f['id'] == 'D09_living_gifts_floor')
assert floor['floor_y'] == 52.5
triangles = np.array(floor['triangles'])
def supported(p):
    a = triangles[:, 0]; u = triangles[:, 1]-a; w = triangles[:, 2]-a
    q = np.asarray(p)-a
    determinant = u[:, 0]*w[:, 1]-u[:, 1]*w[:, 0]
    valid = abs(determinant)>1e-10
    s = np.zeros(len(a)); t = s.copy()
    s[valid] = (q[valid, 0]*w[valid, 1]-q[valid, 1]*w[valid, 0])/determinant[valid]
    t[valid] = (u[valid, 0]*q[valid, 1]-u[valid, 1]*q[valid, 0])/determinant[valid]
    return bool(np.any(valid & (s>=-1e-8) & (t>=-1e-8) & (s+t<=1+1e-8)))
# Proposed rotated original two-stop lift. The complete original cabin, gate,
# shaft and pier envelope must still be checked; these are floor witnesses only.
pit = [19.8, 183.5, 24.2, 187.7]
witnesses = [[float(x),float(z)] for x in np.linspace(pit[0],pit[2],23)
             for z in np.linspace(pit[1],pit[3],22)]
coverage = [{'xz':p,'source_slab':supported(p)} for p in witnesses]
assert all(p['source_slab'] for p in coverage), 'Pit leaves retained slab'
source_paths = ['Game/data/generated/structural_meshes.json',
 'Game/data/aquatic_section.json','Game/data/architecture/D08_D10_aquatic_access.json',
 'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json',
 'Game/orchard_tram_interior_20261025/r006/PLAN.json',
 'Game/scripts/commons_lift.gd','Game/scripts/aquatic_section.gd',
 'Game/scripts/living_gifts.gd','Game/scripts/vesper_watercourse.gd']
pins = {p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in source_paths}
plan = {'schema':'astraea.aquatic.receiving-decision.r001',
 'status':'UNSELECTED_RECEIVING_PLAN_NOT_INSTALLED', 'baseline':'a5ba7e1b3f7cec6b301138edfeb364cfa714d7be',
 'route':v,'snapshot_scope':checks['scope'],
 'alignment_reason':'Enter at Z174 to minimize the northern transition; return at Z248 before the retained public core. Z288 alternatives intersect five retained core contacts. X17.3 intersects the existing aquatic lift enclosure.',
 'station_identity':'AFT_MIDSHIP','catchment_z_preserved':216,
 'provisional_dock_xyz':[18.5,56.1,192], 'door_side':'starboard',
 'provisional_boarding_edge_x':20.7,
 'provisional_platform_xz':[20.7,188,26.1,198],
 'provisional_lift_root_xyz':[22,0,187.7], 'provisional_lift_yaw_rad':math.pi/2,
 'lower_floor_source':floor['id'],'lower_floor_y':floor['floor_y'],
 'lower_floor_thickness':floor['thickness'],'provisional_pit_xz':pit,
 'floor_witnesses':coverage,
 'originals_to_preserve':['aquatic_lift_001 three-stop lift, its shaft and western bypass',
  'group4_aft_midship_boarding_lift_001 and G4_AFT_MIDSHIP stop identities',
  'original tram, bridge, boarding safety and operating controllers',
  'D09/D10 grand-volume openings, watercourse, Living Gifts doors and original programmes',
  'Aft Midship public core, stairs and landing guards; D11 protected cover'],
 'guest_completion':{'required':True,'visual_acceptance':False,
  'arrival':'Supported inhabited balcony with an unobstructed boarding lane, original lift access and a genuine public stair connection.',
  'rest':'Conversation and quiet-view seating pockets outside boarding, cart-turning and through-circulation envelopes; use retained upholstered and timber furniture.',
  'planting':'Integrated canopy, shrub and groundcover beds framing water views and refuge pockets, using retained painterly botanical assets and shared mesh/material resources. No token pot substitution.',
  'materials':'Retained aquatic ivory enamel, warm walnut, terracotta enamel, champagne metal, wet/grip tile and intentional hospitality glass; metre-scaled UVs and modeled plinth/reveal transitions.',
  'lighting':'Reuse authored fixture/lens sources and unchanged light budget, bind real receiving surfaces; no unbounded added lights.',
  'style_authority':['Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',
   'Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json chapters 5,21,30,32,33',
   'DesignArchive/References/Uploaded_46/07/image(3).png',
   'User 2026-10-26 1970s futurism and greenery/relaxation requirements']},
 'remaining':['Exact original lift pit/shaft/gate/landing swept envelope, not just slab samples',
  'Continuous supports, bearings and lower access around retained openings',
  'Complete vehicle/cart/door component sweep against final receiving geometry',
  'Native and runtime geometry/material/UV equivalence',
  'Installed boarding and actual rider views; artistic review',
  'Moving RID failure, actual hardware frame-time/resource lifecycle, matching Windows export'],
 'source_pins':pins}
D.mkdir(parents=True)
(D/'RECEIVING_PLAN.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode())
print(json.dumps({'selected_for_development':chosen,'reserved_sweeps':c['queries'],
 'source_floor_witnesses':len(coverage),'all_on_retained_floor':True,
 'installed_source_changed':False}))
