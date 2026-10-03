import hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
from checkpoint_source import verify_archive

class ArchiveIntegrity(unittest.TestCase):
    def make(self,root,body=b'fixture',expected=None,extra=False):
        path=Path(root)/'test.zip'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('astraea-godot-production/project.godot',body)
            z.writestr('MANIFEST.json',json.dumps({'files':{'astraea-godot-production/project.godot':expected or hashlib.sha256(body).hexdigest()}}))
            z.writestr('READ_ME.txt','test')
            if extra:z.writestr('unexpected','test')
        return path
    def test_verified_source(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(len(verify_archive(self.make(d))['files']),1)
    def test_changed_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):verify_archive(self.make(d,expected='0'*64))
    def test_unlisted_entry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):verify_archive(self.make(d,extra=True))

if __name__=='__main__':unittest.main()
