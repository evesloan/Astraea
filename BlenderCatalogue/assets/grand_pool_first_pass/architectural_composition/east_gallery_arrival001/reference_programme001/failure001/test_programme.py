"""Pure frame, arrow, and surface/solid regression tests. Never imports bpy."""
import sys,math,unittest,random,ast
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import programme_common as c
import check_programme as q
class ProgrammeChecks(unittest.TestCase):
    def setUp(self):self.plan=c.read(c.CORE)
    def test_display_frame_is_unmirrored(self):
        old,new=c.display_frames(self.plan)
        self.assertGreater(c.dot(c.cross(new['right_xyz'],new['up_xyz']),new['normal_xyz']),.999999999)
        self.assertGreater(new['right_xyz'][0],0);self.assertLess(new['right_xyz'][2],0)
        rng=random.Random(42)
        for _ in range(100):
            v=[rng.uniform(-2,2)for _ in range(3)];actual=c.to_local(c.reframe(c.from_local(v,old),old,new),new)
            self.assertLess(max(abs(a-b)for a,b in zip(v,actual)),1e-12)
    def test_ordinary_blender_plant_yaw(self):
        r=self.plan['plant_reservations'][0];v=[.35,-.215,1.2];angle=r['yaw_radians'];cs,sn=math.cos(angle),math.sin(angle)
        rb=[cs*v[0]-sn*v[1],sn*v[0]+cs*v[1],v[2]];expected=c.add(c.G(rb),r['position_xyz'])
        self.assertLess(c.length(c.sub(expected,c.plant_point(v,r))),1e-12)
    def test_exact_seven_programme_instances(self):
        plants=c.source_inventory(self.plan);self.assertEqual(len(plants),4);self.assertEqual({p['source_root']for p in plants},{'AST-BOT-002_pool_loggia_mass_00','AST-BOT-002_pool_loggia_mass_03','AST-BOT-003_pool_basal_00','AST-BOT-003_pool_basal_03'})
        self.assertEqual(len(c.sign_frames(self.plan)),2)
        self.assertTrue(all(p['reservation']['scale_xyz']==[1,1,1]for p in plants))
    def test_sign_arrow_and_actual_pad_back(self):
        signs=c.sign_frames(self.plan);a=c.arrow_spec(signs[0]);self.assertGreater(a['glyph_edge_gap_m'],.025);self.assertEqual(a['unit_arrow_uv'],[1,0]);self.assertEqual(a['depth_d'][0],signs[0]['backing_front_local_d']);self.assertGreater(a['depth_d'][1]-a['depth_d'][0],.0049)
        for s in signs:
            for p in s['meshes']:
                if 'FixedPad_'not in p['name']:continue
                v=[c.reframe(v,s['old_frame'],s['new_frame'])for v in p['vertices']];self.assertAlmostEqual(min(vv[2]for vv in v),s['mount_surface_z'],places=10)
    def test_no_launch_save_export_render_code(self):
        t=ast.parse((c.S/'append_retained_programme.py').read_text())
        forbidden={'save_as_mainfile','open_mainfile','read_factory_settings','render','export_scene','system','Popen','run'}
        names=[x.attr for x in ast.walk(t)if isinstance(x,ast.Attribute)]
        self.assertFalse(set(names)&forbidden)
    def test_open_plane_not_false_closed_solid(self):
        # A point/solid behind a quad has no 'inside quad'. Real intersection
        # through an open surface still fails the receiver test.
        def box(z0,z1):
            v=[[x,y,z]for z in [z0,z1]for y in [-.2,.2]for x in [-.2,.2]];fs=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]]
            p=q.record('receiver',v,[t for f in fs for t in q.triang_face(v,f)]);return q.cache([p])[0]
        vertices=[[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0]];p=q.cache([q.record('open_quad',vertices,[[vertices[i]for i in ids]for ids in [[0,1,2],[0,2,3]]],open_surface=True)])[0]
        self.assertFalse(q.actual_contact(p,box(-.2,-.1))['penetration'])
        self.assertTrue(q.actual_contact(p,box(-.1,.1))['penetration'])
if __name__=='__main__':unittest.main()
