#!/usr/bin/env python3
"""Named section revision: preserve installed G7 edge with an outboard middle leg."""
from pathlib import Path
import importlib.util,sys,json,hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PREVIOUS=ROOT/'recovery/tram_section_successor_20261023'
spec=importlib.util.spec_from_file_location('retained_section_author',PREVIOUS/'author_section_r002.py');author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
original=author.screen.fillet

def receiving_route(corners,radius=4.):
    return original([[47.5 if x==44.5 else x,z]for x,z in corners],radius)

author.HERE=HERE;author.screen.fillet=receiving_route
out=HERE/'geometry_r001';assert not out.exists()
sys.argv=[str(Path(__file__)), '--output',str(out)];author.main()
p=out/'CANDIDATE.json';plan=json.loads(p.read_text())
plan.update(schema='astraea.tram.section.20261024.r001',protected_prerequisite='c2d7383311d3f52574a150c56bac6a9b6e3a0c3e',predecessor='tram_section_successor_20261023/r002',outboard_middle_leg_x=47.5)
plan['alignment_reason']='Preserve installed G7C6_D09_ComposedEdge metal fixture/tree/foliage; source024 body and first curved CENTRAL stop unchanged.'
plan['source_pins']['recovery/tram_section_successor_20261023/author_section_r002.py']={'bytes':(PREVIOUS/'author_section_r002.py').stat().st_size,'sha256':hashlib.sha256((PREVIOUS/'author_section_r002.py').read_bytes()).hexdigest()}
p.write_text(json.dumps(plan,separators=(',',':'))+'\n')
# Existing exact bridge is reused; no duplicate native or bridge generation.
sys.path.insert(0,str(PREVIOUS));from export_candidate import section
parts=json.loads((out/'MESHES.json').read_text());target=ROOT/'Game/tram_section_successor_20261024'
section(parts,ROOT/'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-014_central_source.glb',target/'section.glb')
for src,name in [(p,'section_plan.json'),(out/'POSE_KNOTS.json','POSE_KNOTS.json'),(PREVIOUS/'runtime_r002/AST-TRM-BRIDGE-20261023-r002.glb','bridge.glb')]:
    dest=target/name;assert not dest.exists();dest.write_bytes(src.read_bytes())
print(json.dumps({'status':'AUTHORED_UNADOPTED','route_x':47.5,'parts':len(parts),'unresolved_receivers':len(plan['unresolved_receivers']),'CENTRAL_unchanged':plan['central']==json.loads((PREVIOUS/'candidate_r002/CANDIDATE.json').read_text())['central']}))
