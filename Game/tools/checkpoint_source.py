"""Create a verified, ordinary ZIP of a clean committed source tree.

This creates a local artifact only. Independent retention and Workshop copying
are separate steps and must not be inferred from a successful ZIP check.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def verify_archive(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('ZIP CRC failure')
        manifest = json.loads(z.read('MANIFEST.json'))
        for name, expected in manifest['files'].items():
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise ValueError('Manifest mismatch: '+name)
        if set(z.namelist()) != set(manifest['files']) | {'MANIFEST.json', 'READ_ME.txt'}:
            raise ValueError('Unmanifested or missing archive entries')
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--since', help='Optional verified ancestor for incremental Git history; source files remain complete')
    parser.add_argument('--restore-check', action='store_true', help='Run Godot checks from a clean extracted source folder')
    args = parser.parse_args()
    target = args.output.resolve()
    if target.exists(): raise SystemExit('Refusing to overwrite an existing checkpoint')
    if target.suffix.lower() != '.zip': raise SystemExit('Use an ordinary .zip destination')
    if git('status', '--porcelain').strip(): raise SystemExit('Commit or preserve outstanding changes before making a source checkpoint')
    commit = git('rev-parse', 'HEAD').decode().strip()
    prerequisite = None
    if args.since:
        prerequisite = git('rev-parse', '--verify', args.since+'^{commit}').decode().strip()
        subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',prerequisite,commit],check=True)
        if prerequisite == commit: raise SystemExit('Incremental history would be empty')
    names = git('ls-files','-z').decode().rstrip('\0').split('\0')
    paths = {}
    for name in names:
        source = ROOT/name
        if source.is_symlink() or not source.is_file(): raise SystemExit('Unsupported tracked file: '+name)
        paths['astraea-godot-production/'+name] = source
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='astraea-checkpoint-',dir=target.parent) as temporary:
        temp = Path(temporary)
        bundle = temp/'source_history.bundle'
        revision = prerequisite+'..HEAD' if prerequisite else '--all'
        subprocess.run(['git','-C',str(ROOT),'bundle','create',str(bundle),revision],check=True)
        subprocess.run(['git','-C',str(ROOT),'bundle','verify',str(bundle)],check=True,capture_output=True)
        paths['source_history.bundle'] = bundle
        manifest = {'source_commit':commit,'history_prerequisite':prerequisite,
                    'source_snapshot':'complete tracked source','files':{name:digest(path) for name,path in paths.items()},
                    'scope':'Unfinished Godot ship source. Reference archives and editable Blender catalogue are backed up separately.'}
        staged = temp/'checkpoint.zip'
        with zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED) as z:
            for name,path in paths.items(): z.write(path,name)
            z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
            z.writestr('READ_ME.txt','Extract astraea-godot-production and open project.godot with Godot4.6.3 Compatibility. The folder is a complete source snapshot and does not require Git. Optional source_history.bundle contains full history unless MANIFEST names a prerequisite commit. This is unfinished reconstruction work, not a recovered original or finished game. ZIP verification is not an independent backup: retain a copy outside the execution workspace.\n')
        verify_archive(staged)
        restored = False
        if args.restore_check:
            # The archive was just created from validated relative paths above.
            with zipfile.ZipFile(staged) as z: z.extractall(temp/'restore')
            source = temp/'restore'/'astraea-godot-production'
            result = subprocess.run(['python3',str(source/'tools/validate.py')],cwd=source,capture_output=True,text=True)
            (target.parent/(target.stem+'.restore.log')).write_text(result.stdout+result.stderr)
            if result.returncode: raise SystemExit('Restore validation failed; no final checkpoint promoted')
            restored = True
        staged.rename(target)
    receipt = {'path':str(target),'bytes':target.stat().st_size,'sha256':digest(target),
               'source_commit':commit,'archive_integrity_verified':True,'clean_restore_tested':restored,
               'independent_retention_verified':False,'workshop_copy_verified':False}
    target.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
