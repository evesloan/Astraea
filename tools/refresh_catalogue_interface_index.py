"""Promote current, hash-bound interface audit data to the consumer index.

This is metadata only. It executes no asset generators and never changes models.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--proposal',type=Path,default=ROOT/'qa/batch08/interface_normalized_index_proposed.json');p.add_argument('--output',type=Path,default=ROOT/'standards/catalogue_interfaces.json');args=p.parse_args()
 proposal=json.loads(args.proposal.read_text());catalogue=json.loads((ROOT/'catalogue_manifest.json').read_text());expected={r['catalogue_id']:r for r in catalogue['assets']};rows=proposal['assets'];assert len(rows)==len(expected)==45
 assert {r['catalogue_id'] for r in rows}==set(expected)
 checked=[]
 for row in rows:
  asset=expected[row['catalogue_id']]
  for key,record in row['source_export_manifest_bindings'].items():
   path=(ROOT/record['path']).resolve();assert path.is_relative_to(ROOT) and path.is_file(),record['path']
   assert sha(path)==record['sha256'],('Stale proposal binding; refresh audit first',record['path'])
   if key in ('source','export','manifest'):assert record['path']==asset[key]
   checked.append({'path':record['path'],'sha256':record['sha256']})
 proposal['revision']='astraea-catalogue-interfaces-01'
 proposal['status']='current_component_consumer_index_not_engine_acceptance'
 proposal['scope']='Explicit existing component declarations and bounded offline interface evidence. Actual native hierarchy governs geometry; no engine, installed-room, actor, controller or operating behavior is implemented by this index.'
 proposal['audit_source']={'path':str(args.proposal.resolve().relative_to(ROOT)),'sha256':sha(args.proposal),'report':'qa/batch08/interface_audit_report.md','correction_map':'qa/batch08/interface_proposed_corrections.json'}
 proposal['binding_validation']={'exact_asset_id_set':True,'current_bound_files_checked':len(checked),'all_files_current':True}
 output=args.output.resolve();assert output.is_relative_to(ROOT);output.write_text(json.dumps(proposal,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'output':str(output),'sha256':sha(output),'assets':len(rows),'current_file_bindings':len(checked),'runtime_acceptance':False},indent=2))
if __name__=='__main__':main()
