from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).parent;C=P.parent;R=Path('/workspace/astraea-protected-integration-20261012');q=R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json';d=json.loads(q.read_text());check=json.loads((P/'CENTRAL_RECEIVING_RUNTIME.json').read_text());assert check['status']=='PASS_CURRENT_PORTCENTRAL_ADJUNCT_CARE_RECEIVING'
for row in d['group2_cumulative_nine_packages']:
 if row['package']in['group2_completion_20261011','group2_care_programmes_20261012']:
  assert 'port_central_upper_house'not in row['installed_source_keys'];row['installed_source_keys'].append('port_central_upper_house')
  row['reason']='Four of six adjunct/care pairs physically received; both aft pairs remain uninstalled. All care/service/private admission/engineering acceptance held.'
 if row['package']=='group2_completion_20261011':row['uninstalled_adjuncts']=2
 if row['package']=='group2_care_programmes_20261012':row['uninstalled_care_kits']=2
counts=d['group2_remaining_physical_counts'];counts.update(completion_adjuncts_uninstalled=2,care_kits_uninstalled=2)
for g in d['groups']:
 if g['group']==2:
  g['live_installed_and_checked']+='; Port-central adjunct/care pair received on six retained lower-stub slab bearings and four shallow court-slab joints: 80 m² source floor plus 30.06 m² missing approach to the installed west vestibule. Original door, walls, beams, slabs, model bytes and runtime identities retained. A finite 1.8 m guard opening preserves original nodes, bodies and outside faces. Two source fixture lights. Twelve original-controller return-route legs; capacity and operational acceptance held.'
  g['not_installed_or_unaccepted']='Completion/care partially installed: 4 of 6 pairs; 80 homes, 2 aft adjuncts and 2 care kits uninstalled. Three wholly source-only packages and two partial packages remain: five incomplete. Private 5 cabins/15 gates, pit 5 terraces/550 translations, wet 2 UNPLACED kits/952 m² roofs each and 790 remain held. All operational, clean/used/fluid, consent, egress, lower-room and structural-capacity acceptance held.'
  g['current_remaining_receiver_survey']='Both aft source footprints remain at z326–344; D17 courts start z356. Retained D16 floors do not underlie sampled adjunct footprints. Exact lower-bearing survey retained; no unsupported frame adopted.'
  g['next_action']='Resolve verified structural bearing/lower-room fit for both aft adjuncts and twelve-metre connections before authoring or admitting them.'
  g['physical_missing_or_conditional']=[x for x in g['physical_missing_or_conditional']if not x.startswith(('group2_completion:','group2_care_programmes:'))]+['group2_completion: 80 homes and 2 aft adjuncts uninstalled; 4 source adjuncts physically received.','group2_care_programmes: 2 aft kits uninstalled; all six operational clean/used/fluid/staff/care admission joins held.']
d.update(local_progress_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),local_progress_protection='PORTCENTRAL_ADJUNCT_CARE_REMOTE_READBACK_PENDING',fully_integrated=False,whole_ship_completed=False,build_ready=False);q.write_text(json.dumps(d,indent=2)+'\n')
audit=json.loads((C/'g2_remaining_five_pairs_20261013/ALL_EIGHT_INCLUSION_RECONCILIATION.json').read_text());audit.update(base_commit='9fe069e0b8af42869dbf49b4b97d69d95b2ab63d',ship_sha256=hashlib.sha256((R/'Game/scripts/ship.gd').read_bytes()).hexdigest(),G2_remaining_physical_counts=counts,new_admitted_physical_package={'package':'group2_portcentral_receiving_20261013','completion_adjuncts':1,'care_kits':1,'source_floor_m2':80.,'connector_m2':30.06,'lower_stub_bearings':6,'upper_slab_joints':4,'primary_models_changed':0,'operational_or_engineering_acceptance':False})
for row in audit['groups']:
 if row['group']==2:
  row['physical_missing_or_conditional']=next(g for g in d['groups']if g['group']==2)['physical_missing_or_conditional'];row['runtime_entry_source_pins']['scripts/group2_portcentral_receiving_20261013/package.gd']=hashlib.sha256((R/'Game/scripts/group2_portcentral_receiving_20261013/package.gd').read_bytes()).hexdigest()
assert audit['G3_missing_physical_factories']==0;(P/'ALL_EIGHT_INCLUSION_RECONCILIATION.json').write_text(json.dumps(audit,indent=2)+'\n');print('G2_REMAINING_80_HOMES_2_ADJUNCTS_2_CARE_KITS')
