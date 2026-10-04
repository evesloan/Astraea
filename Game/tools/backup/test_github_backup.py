import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import github_backup as b

class GitHubBackupTests(unittest.TestCase):
    def test_secret_names_and_text_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/'safe.md';p.write_text('Astraea construction notes')
            b.eligible(p,'docs/safe.md')
            with self.assertRaises(RuntimeError):b.eligible(p,'.env')
            p.write_text('ghp_'+'a'*36)
            with self.assertRaises(RuntimeError):b.eligible(p,'docs/safe.md')

    def test_private_destination_required(self):
        config={'auth_directory':'/unused','mirror':'/unused','repository':'owner/Astraea'}
        for data in [{'full_name':'owner/Astraea','private':False},{'full_name':'other/Astraea','private':True}]:
            with patch.object(b,'command',return_value=json.dumps(data)):
                with self.assertRaises(RuntimeError):b.verify_private(config)

    def test_mirror_copy_and_prune_never_change_source(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);src=root/'source';src.mkdir();(src/'a.txt').write_text('new')
            mirror=root/'mirror';(mirror/'Game').mkdir(parents=True);(mirror/'Game'/'old.txt').write_text('old')
            info={'entries':[('a.txt',3,0)],'signature':'stable'}
            with patch.object(b,'inventory',return_value=info):
                hashes=b.sync_project({'root':str(src),'prefix':'Game'},info,mirror)
            self.assertEqual((src/'a.txt').read_text(),'new');self.assertEqual((mirror/'Game/a.txt').read_text(),'new')
            self.assertFalse((mirror/'Game/old.txt').exists());self.assertEqual(hashes['a.txt'],b.digest(src/'a.txt'))

    def test_unstable_source_does_not_publish(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);src=root/'source';src.mkdir();(src/'a.txt').write_text('new');mirror=root/'mirror';mirror.mkdir()
            info={'entries':[('a.txt',3,0)],'signature':'old'}
            with patch.object(b,'inventory',return_value={'signature':'new'}):
                with self.assertRaises(b.SnapshotChanged):b.sync_project({'root':str(src),'prefix':'Game'},info,mirror)

    def test_remote_divergence_stops_before_copy(self):
        with tempfile.TemporaryDirectory() as t:
            state=Path(t)/'state.json';state.write_text(json.dumps({'remote_commit':'old','projects':{},'last_verified_epoch':0}))
            c={'state':str(state),'mirror':t,'projects':[{'name':'Godot','root':t,'prefix':'Game'}]}
            with patch.object(b,'inventory',return_value={'signature':'x','head':'h'}),patch.object(b,'verify_private'),patch.object(b,'remote_head',return_value='unexpected'),patch.object(b,'sync_project')as sync:
                with self.assertRaises(RuntimeError):b.run_once(c)
                sync.assert_not_called()

    def test_unchanged_source_does_not_contact_remote(self):
        with tempfile.TemporaryDirectory() as t:
            state=Path(t)/'state.json';state.write_text(json.dumps({'remote_commit':'old','projects':{'Godot':{'signature':'x','head':'h'}}}))
            c={'state':str(state),'projects':[{'name':'Godot'}]}
            with patch.object(b,'inventory',return_value={'signature':'x','head':'h'}),patch.object(b,'remote_head')as remote:
                self.assertFalse(b.run_once(c));remote.assert_not_called()

    def test_wip_waits_fifteen_minutes_but_new_commit_does_not(self):
        with tempfile.TemporaryDirectory() as t:
            state=Path(t)/'state.json';state.write_text(json.dumps({'remote_commit':'old','projects':{'Godot':{'signature':'before','head':'h'}},'last_verified_epoch':1000}))
            c={'state':str(state),'mirror':t,'projects':[{'name':'Godot'}],'wip_interval_seconds':900}
            with patch.object(b.time,'time',return_value=1899),patch.object(b,'inventory',return_value={'signature':'after','head':'h'}),patch.object(b,'verify_private')as remote:
                self.assertFalse(b.run_once(c));remote.assert_not_called()
            for clock,head in [(1900,'h'),(1001,'new_commit')]:
                with patch.object(b.time,'time',return_value=clock),patch.object(b,'inventory',return_value={'signature':'after','head':head}),patch.object(b,'verify_private',side_effect=RuntimeError('Reached remote validation'))as remote:
                    with self.assertRaisesRegex(RuntimeError,'Reached remote validation'):b.run_once(c)
                    remote.assert_called_once()

if __name__=='__main__':unittest.main()
