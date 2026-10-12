import pathlib,zipfile,json,hashlib,stat,re,datetime
R=pathlib.Path('/workspace/astraea-protected-integration-20261012');O=pathlib.Path(__file__).parent;G=R/'Game';original=O/'Astraea_Runtime_3210f55.zip';target=O/'Astraea_Windows_Preview_3210f55_20261012.zip';sha=lambda b:hashlib.sha256(b).hexdigest()
def file_sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert not target.exists();export_sha=file_sha(original);original.rename(target);c=json.loads((R/'CHECKPOINT.json').read_text());proof=json.loads((G/'data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json').read_text());paths={p for p in c['projects']['Godot']['files']if p.startswith(('assets/','data/','scripts/','scenes/','shaders/','tests/'))and not p.endswith(('.blend','.zip','.7z','.rar'))};paths.update(proof['current_sha256']);paths.add('project.godot');added=[];replaced=[]
with zipfile.ZipFile(target,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
 for name in sorted(paths):
  p=G/name;assert p.is_file(),name;expected=c['projects']['Godot']['files'].get(name)
  b=p.read_bytes();assert not expected or sha(b)==expected,name
  if name in z.NameToInfo:
   if sha(z.read(name))==sha(b):continue
   z.filelist=[i for i in z.filelist if i.filename!=name];z.NameToInfo.pop(name);replaced.append(name)
  else:added.append(name)
  z.writestr(name,b)
 z.writestr('Astraea.exe',(O/'windows_release_x86_64.exe').read_bytes())
 launch='@echo off\r\ncd /d "%~dp0"\r\n"%~dp0Astraea.exe" --path "%~dp0"\r\nif errorlevel 1 (echo Startup failed. Read README_FIRST.txt for limitations.& pause)\r\n'
 z.writestr('START_ASTRAEA.cmd',launch)
 launch_pack='@echo off\r\ncd /d "%~dp0"\r\nif exist "%~dp0Astraea_Windows_Preview_3210f55_20261012.zip" (\r\n "%~dp0Astraea.exe" --main-pack "%~dp0Astraea_Windows_Preview_3210f55_20261012.zip"\r\n) else (\r\n "%~dp0Astraea.exe" --main-pack "%~dp0..\\Astraea_Windows_Preview_3210f55_20261012.zip"\r\n)\r\nif errorlevel 1 pause\r\n'
 z.writestr('START_PACKED_ASTRAEA.cmd',launch_pack)
 readme='''ASTRAEA — WINDOWS X64 PREVIEW — SOURCE3210f55

This is an exported runtime/source preview,not a verified graphical Windows
working build. Cloud normal-render startup exceeded available16GiB memory.
Windows navigation,GPU/draw-call performance,60FPS and full completed-package
integration remain unaccepted. Read INTEGRATION_INVENTORY.json and BUILD_NOTES.md.

START: Extract the complete ZIP to one folder,then double-click START_ASTRAEA.cmd.
Keep all resource directories,including .godot. No Godot editor is required.
If the loose-file launch fails,keep the original ZIP beside the extracted folder
(or inside it) and use START_PACKED_ASTRAEA.cmd. The ZIP itself is a Godot resource
pack;it must keep its original filename. The executable is official Godot4.6.3
Windows x64 release,using the existing GL Compatibility renderer.

CONTROLS: WASD walk;mouse look;Space jump;hold RMB to focus,then E to interact;
Esc releases mouse;click recaptures it;M opens the existing express directory;
F4 toggles existing presentation effects;F9 shows live performance measurements.
Physical stairs/lifts/doors and express travel remain distinct;blocked or
uninstalled routes are not opened by this preview.

The original player script is byte-identical. Three local dining service kits
passed51,590 checks,49 local legs,720 preserved chairs and unload/light lifetime.
Cold Library arrival and original W connector walking passed. These are bounded
headless checks,not whole-ship traversal or hardware performance certification.

Thread's current design is visually rejected and its photograph is withheld.
The rejected thermal recovery successor is inactive. Existing technical fixtures
remain. Other inactive owner packages and exact receiving/support/proof/route
exceptions are listed in the inventory. Editable Blender and inactive archives
remain in private Git;they are not bundled as runtime data.

VERSION:3210f55b0906a1fe01e2e95953d90b1b7914a49f
Godot4.6.3.stable.official.7d41c59c4;source checkpoint SHA256
39ff40719f76545270f061646772fc8a96a75bef60e43cba96b1b5ffe67962b5.

When reporting a failure,include the startup error and your CPU,GPU,RAM and
Windows version. No exact minimum hardware requirement has been established.

Private preview. Godot engine license is included in GODOT_LICENSE.txt.
'''
 z.writestr('README_FIRST.txt',readme);z.writestr('GODOT_LICENSE.txt',(O/'GODOT_LICENSE.txt').read_bytes());z.writestr('INTEGRATION_INVENTORY.json',(R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json').read_bytes());z.writestr('BUILD_NOTES.md',(G/'docs/NAVIGABLE_BUILD_20261012.md').read_bytes())
 version={'commit':'3210f55b0906a1fe01e2e95953d90b1b7914a49f','engine':'4.6.3.stable.official.7d41c59c4','renderer':'GL Compatibility','checkpoint_sha256':'39ff40719f76545270f061646772fc8a96a75bef60e43cba96b1b5ffe67962b5','fully_integrated':False,'Windows_graphical_navigation_verified':False,'target60FPS_verified':False};z.writestr('VERSION.json',json.dumps(version,indent=2))
 for name in ['DINING_INTEGRATED_TOTALS001.json','NORMAL_WORKERS2_RESULT001.json','HEADLESS_STARTUP001.json','WINDOWS_TEMPLATE_RECEIPT.json']:
  z.writestr('TEST_EVIDENCE/'+name,(O/name).read_bytes())
 z.writestr('TEST_EVIDENCE/STREAMING_ARRIVALS001.json',(G/'artifacts/build_streaming_arrivals001.json').read_bytes())
with zipfile.ZipFile(target)as z:
 infos=z.infolist();names=[i.filename for i in infos];assert len(set(names))==len(names);assert len({n.casefold()for n in names})==len(names),'Windows case collision'
 for i in infos:
  p=pathlib.PurePosixPath(i.filename);assert not p.is_absolute()and '..'not in p.parts and '\\'not in i.filename and ':'not in i.filename;assert not stat.S_ISLNK(i.external_attr>>16)
 assert z.testzip()is None
 for path in proof['current_sha256']:assert sha(z.read(path))==sha((G/path).read_bytes()),path
 assert sha(z.read('Astraea.exe'))=='91724f15024a3a545e28ccd83134403d31ce2323a38e51c95e4dfa282f732ab6'
 size_unpacked=sum(i.file_size for i in infos)
report={'path':str(target),'bytes':target.stat().st_size,'sha256':file_sha(target),'members':len(infos),'uncompressed_bytes':size_unpacked,'safe_unique_case_insensitive_paths':True,'no_declared_symlinks':True,'all_members_CRC_verified':True,'original_export_sha256':export_sha,'raw_dependency_paths_added':added,'raw_dependency_paths_replaced_in_central_index':replaced,'158_current_auth_inputs_exact_source_bytes':True,'source_commit':version['commit'],'fully_integrated':False,'Windows_graphical_navigation_verified':False,'normal_renderer_memory_blocked':True,'cache_bytes_preserved_in_this_archive':True};(O/'WINDOWS_PREVIEW_ARCHIVE_RECEIPT.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k not in ['raw_dependency_paths_added','raw_dependency_paths_replaced_in_central_index']})
