from pathlib import Path
import json
P=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');x=json.loads((R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json').read_text());q=R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.md';old=q.read_text();(P/'READABLE_INVENTORY_PREIMAGE.md.txt').write_text(old)
lines=['# Current construction inventory','','Generated from CONSOLIDATED_CONSTRUCTION_INVENTORY.json at the central adjunct/care physical checkpoint. JSON remains authoritative. Source retention, physical installation, operational acceptance and release acceptance remain distinct. All eight groups remain unfinished; the whole-ship build is unaccepted.','','G3 missing physical factory callers: 0. G2 wholly source-only packages: 3; partially installed packages: 2; incompletely installed packages: 5. Remaining: 80 completion homes, five adjuncts and five care kits; private/wet/pit packages remain uninstalled. Original 13 G3 network criteria and 184 joins remain held; G5 retains 84 unresolved address joins. Clinical operational, streaming and pool/RoyaltyPier support-span holds remain unchanged. Original movement and all 53 retained payloads are preserved. Tram redesign remains unapproved and disabled.','']
for g in x['groups']:
 lines += [f"## Group {g['group']}",'',f"Retained source: `{g['retained_source_commit']}`.",'','Installed and checked: '+g['live_installed_and_checked'],'','Uninstalled or unaccepted: '+g['not_installed_or_unaccepted'],'']
 for key,label in [('physical_missing_or_conditional','Physical omissions or conditions'),('controls_or_acceptance_held','Controls and acceptance holds')]:
  if g.get(key):lines+=[label+':','']+['- '+v for v in g[key]]+['']
 lines+=['Owner: '+str(g['blocker_owner']),'','Next: '+g['next_action'],'']
lines+=['## All nine Group2 retained packages','']
for row in x['group2_cumulative_nine_packages']:lines+=['- `'+row['package']+'`: '+row['status']+'. '+row['reason']]
lines+=['','## Earlier inventory snapshot','','The following content is preserved historical evidence. Use the current sections above and authoritative JSON for installation status.','',old]
q.write_text('\n'.join(lines)+'\n');print('Refreshed readable inventory for all8groups/all9G2packages;prior snapshot preserved')
