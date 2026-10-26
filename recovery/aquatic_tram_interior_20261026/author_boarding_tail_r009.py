"""Extend the same inhabited balcony past the retained bearing; lift stays exact."""
from pathlib import Path
import json,importlib.util,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r009'
spec=importlib.util.spec_from_file_location('a',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
floors=[r for r in json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions'] if r['floor_y']==61]
a.prism('BoardingTailSlab',[[21.1,198],[26.1,198],[26.1,225],[20.7,225],[20.7,216.5],[21.1,216.5]],55.82,56.1,'warm_stone')
# Replace only the superseded portion of the old south guard. Retain refuge edge.
for name,x0,x1,z in [('RefugeSouthGuard',26.1,28.5,197.95),('TailSouthGuard',20.7,26.1,224.95)]:
 a.beam(name,[x0,57.23,z],[x1,57.23,z],.1,.1)
 a.box(name+'Glass',[(x0+x1)/2,56.71,z],[x1-x0,1.1,.035],'AquaticGuardGlass')
a.beam('TailEastGuard',[26.05,57.23,198],[26.05,57.23,225],.1,.1)
a.box('TailEastGuardGlass',[26.05,56.71,211.5],[.035,1.1,27],'AquaticGuardGlass')
for lo,hi in [(190.89,193.11),(198,216.5),(216.5,219.89),(222.11,225)]:
 x=21.16 if lo==198 else 20.76
 a.beam('TailTrackGuard_'+str(lo),[x,57.23,lo],[x,57.23,hi],.1,.1)
 a.box('TailTrackGuardGlass_'+str(lo),[x,56.71,(lo+hi)/2],[.035,1.1,hi-lo],'AquaticGuardGlass')
a.box('TailWalnutFasciaEast',[26,55.94,211.5],[.12,.24,27],'warm_walnut')
a.box('TailWalnutFasciaWestNorth',[21.2,55.94,207.25],[.12,.24,18.5],'warm_walnut')
a.box('TailWalnutFasciaWestSouth',[20.8,55.94,220.75],[.12,.24,8.5],'warm_walnut')
a.box('TailTerracottaEnd',[23.4,55.88,224.9],[5.4,.28,.12],'AquaticTerracottaEnamel')
receivers=[]
for i,(x,z) in enumerate([(21.1,223.9),(25.7,223.9),(21.1,198.5),(25.7,198.5),(21.1,205.5),(25.7,205.5),(21.1,212.5),(25.7,212.5)]):
 pad=[x,z];owners=a.screen.footprint_owners(pad,floors)
 if len(owners)!=1 or abs(owners[0]['overlap_m2']-.0864)>1e-6:pad=[21.1,z];owners=a.screen.footprint_owners(pad,floors)
 assert len(owners)==1 and abs(owners[0]['overlap_m2']-.0864)<1e-6,(pad,owners)
 a.box('BoardingTailHanger_'+str(i),[x,58.1,z],[.12,4.48,.12])
 a.box('BoardingTailBearing_'+str(i),[pad[0],60.79,pad[1]],[.24,.08,.36])
 if abs(x-pad[0])>1e-6:a.beam('BoardingTailOverarm_'+str(i),[x,60.34,z],[pad[0],60.34,z],.18,.32)
 a.beam('BoardingTailStub_'+str(i),[pad[0],60.34,z],[pad[0],60.79,z],.12,.12)
 receivers.append({'part':'BoardingTailHanger_'+str(i),'leg':[x,z],'pad':pad,'owner':owners[0]})
for z in [198.5,205.5,212.5,223.9]:a.beam('TailUnderbeam_'+str(z),[20.7,55.74,z],[26.1,55.74,z],.2,.24)
for z in [190.89,198.,216.5]:
 a.beam('GuardSetbackJoin_'+str(z),[20.76,57.23,z],[21.16,57.23,z],.1,.1)
 a.box('GuardSetbackJoinGlass_'+str(z),[20.96,56.71,z],[.4,1.1,.035],'AquaticGuardGlass')
out=D/'BOARDING_TAIL.json';assert not out.exists()
out.write_bytes((json.dumps({'parts':a.parts,'receivers':receivers,'remove_exact':['SouthGuard','SouthGuardGlass'],'portal_translation_xyz':[0,0,29],'added_floor_m2':138.4,'preserved':'Original shaft, lift, pit, stair, planting, benches and two fixtures'},separators=(',',':'))+'\n').encode())
print('Authored supported balcony tail:',len(a.parts),'members',len(receivers),'source bearings')
