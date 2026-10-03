from pathlib import Path
import importlib.util,json,subprocess,tempfile,unittest,zipfile,time,sys
from unittest.mock import patch
from types import SimpleNamespace
spec=importlib.util.spec_from_file_location('backup',Path(__file__).with_name('automatic_backup.py'));backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)

class Backups(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'project';self.root.mkdir()
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        (self.root/'project.godot').write_text('test source')
        subprocess.run(['git','-C',str(self.root),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Test','-c','user.email=test@localhost','commit','-qm','test'],check=True)
        self.project={'name':'Test','kind':'godot','root':str(self.root)}
        self.output=Path(self.temp.name)/'backups'
    def tearDown(self):self.temp.cleanup()
    def test_snapshot_roundtrip_and_wip(self):
        (self.root/'scripts').mkdir();(self.root/'scripts/new.gd').write_text('extends Node')
        (self.root/'.env').write_text('NEVER_UPLOAD=test')
        info=backup.inventory(self.project);self.assertTrue(info['dirty'])
        archives=backup.snapshot(self.project,info,self.output,{},part_limit=50)
        names=[]
        for a in archives:
            with zipfile.ZipFile(a['path'])as z:
                m=json.loads(z.read('MANIFEST.json'));names.extend(m['files'])
                for n,h in m['files'].items():self.assertEqual(backup.hashlib.sha256(z.read(n)).hexdigest(),h)
        self.assertIn('source/scripts/new.gd',names);self.assertNotIn('source/.env',names)
    def test_no_retry_after_uncertain_upload(self):
        config={'state':str(self.output/'state.json'),'output':str(self.output),'upload_helper':'missing','projects':[self.project]}
        with self.assertRaises(RuntimeError):backup.run_once(config)
        state=json.loads(Path(config['state']).read_text());self.assertTrue(state['blocked'])
        with patch.object(backup,'snapshot',side_effect=AssertionError('must not retry')):
            with self.assertRaises(RuntimeError):backup.run_once(config)
    def test_source_mutation_defers_without_upload(self):
        info=backup.inventory(self.project)
        with patch.object(backup,'inventory',return_value=dict(info,signature='different')):
            with self.assertRaises(backup.SnapshotChanged):backup.snapshot(self.project,info,self.output,{'head':info['head']})
    def test_skip_unchanged_independently_retained_state(self):
        info=backup.inventory(self.project);self.output.mkdir()
        config={'state':str(self.output/'state.json'),'output':str(self.output),'upload_helper':'missing','projects':[self.project]}
        Path(config['state']).write_text(json.dumps({'status':'healthy','projects':{'Test':{'signature':info['signature'],'verified_utc':'test'}}}))
        with patch.object(backup,'upload',side_effect=AssertionError('unchanged source must not upload')):self.assertEqual(backup.run_once(config)['status'],'healthy')
    def test_existing_hooks_preserved(self):
        hook=self.root/'.git/hooks/post-commit';hook.write_text('# owner hook')
        with self.assertRaises(RuntimeError):backup.install_hooks(Path('/tmp/config.json'),{'projects':[self.project]})
        self.assertEqual(hook.read_text(),'# owner hook')


    def test_live_hook_and_periodic_wip_trigger_with_fake_transport(self):
        helper=Path(self.temp.name)/'fake_helper.py'
        helper.write_text("import json,sys\nr=json.load(sys.stdin);print(json.dumps({'results':[{'local_path':x['local_path'],'status':'succeeded','library_file_id':'TEST_ONLY','local_metadata_applied':True} for x in r['uploads']]}))\n")
        config={'state':str(self.output/'state.json'),'output':str(self.output),'upload_helper':str(helper),'projects':[self.project],'wip_interval_seconds':.3,'poll_seconds':.05}
        config_path=Path(self.temp.name)/'config.json';config_path.write_text(json.dumps(config))
        backup.install_hooks(config_path,config)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Test','-c','user.email=test@localhost','commit','--allow-empty','-qm','hook trigger'],check=True)
        self.assertTrue((self.output/'checkpoint.request').exists())
        runner=subprocess.Popen([sys.executable,str(Path(backup.__file__)),'watch','--config',str(config_path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            deadline=time.monotonic()+5;first=None
            while time.monotonic()<deadline:
                if Path(config['state']).exists():
                    first=json.loads(Path(config['state']).read_text()).get('projects',{}).get('Test')
                    if first:break
                time.sleep(.05)
            self.assertIsNotNone(first,'Post-commit request must cause retention')
            self.assertEqual(first['head'],backup.inventory(self.project)['head'])
            (self.root/'project.godot').write_text('uncommitted edit')
            deadline=time.monotonic()+5;second=None
            while time.monotonic()<deadline:
                second=json.loads(Path(config['state']).read_text()).get('projects',{}).get('Test')
                if second and second['signature']!=first['signature']:break
                time.sleep(.05)
            self.assertNotEqual(first['signature'],second['signature'])
            self.assertTrue(second['work_in_progress'])
        finally:
            (self.output/'STOP').touch();runner.wait(timeout=3)
        self.assertEqual(runner.returncode,0)

    def test_partial_transport_is_not_success(self):
        archive={'path':'/test/archive.zip','sha256':'test','bytes':1}
        result=SimpleNamespace(returncode=0,stdout=json.dumps({'results':[{'local_path':archive['path'],'status':'failed'}]}),stderr='')
        with patch.object(backup.subprocess,'run',return_value=result):
            with self.assertRaises(RuntimeError):backup.upload(str(Path(backup.__file__)),[archive],Path(self.temp.name)/'log')
    def test_missing_project_records_blocker(self):
        bad=dict(self.project,root=str(self.root/'missing'))
        config={'state':str(self.output/'state.json'),'output':str(self.output),'upload_helper':'missing','projects':[bad]}
        with self.assertRaises(subprocess.CalledProcessError):backup.run_once(config)
        self.assertTrue(json.loads(Path(config['state']).read_text())['blocked'])

if __name__=='__main__':unittest.main()
