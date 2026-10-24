#!/usr/bin/env python3
"""Author the unadopted lateral section and curved CENTRAL boarding connection.

No engine, production writes, changed admission, passenger movement or acceptance.
Run once into a NEW output directory; native/runtime readers share these vertices.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("section_screen", HERE / "screen_section.py")
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)
parts = []


def mesh(name, vertices, faces, material="champagne_metal", purpose="fixed receiving geometry"):
    parts.append({"name": name, "vertices": [[float(v) for v in p] for p in vertices],
                  "faces": [list(f) for f in faces], "material": material, "purpose": purpose,
                  "collision_policy": "static_trimesh_candidate"})


def beam(name, a, b, width, height, material="champagne_metal", purpose="fixed receiving geometry"):
    a, b = np.array(a, float), np.array(b, float)
    delta = b-a
    tangent = delta/np.linalg.norm(delta)
    side = np.array([tangent[2], 0, -tangent[0]])
    if np.linalg.norm(side) < 1e-8:
        side = np.array([1., 0, 0])
    else:
        side /= np.linalg.norm(side)
    up = np.cross(tangent, side)
    vertices = [p+side*w+up*h for p in (a, b) for w, h in [(-width/2, -height/2), (width/2, -height/2), (-width/2, height/2), (width/2, height/2)]]
    mesh(name, vertices, [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)], material, purpose)


def box(name, center, size, material="champagne_metal", purpose="fixed receiving geometry"):
    c = np.array(center, float); x, y, z = np.array(size, float)/2
    vertices = [c+np.array(p) for p in [(-x,-y,-z),(x,-y,-z),(-x,y,-z),(x,y,-z),(-x,-y,z),(x,-y,z),(-x,y,z),(x,y,z)]]
    mesh(name, vertices, [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)], material, purpose)


def ribbon(name, points, offset, width, lower, upper):
    vertices = []
    for i, p in enumerate(points):
        delta = points[min(len(points)-1, i+1)]-points[max(0, i-1)]
        delta = delta/np.linalg.norm(delta); normal = np.array([delta[1], -delta[0]])
        for y, w in [(lower, offset-width/2), (lower, offset+width/2), (upper, offset-width/2), (upper, offset+width/2)]:
            q = p+normal*w; vertices.append([q[0], y, q[1]])
    faces = [(0,2,3,1)]
    for i in range(len(points)-1):
        a, b = 4*i, 4*i+4
        faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
    a = 4*(len(points)-1); faces.append((a,a+1,a+3,a+2))
    mesh(name, vertices, faces, purpose="source gauge/datum retained; complete named route ribbon")


def prism(name, poly, bottom, top, material):
    count = len(poly)
    vertices = [[x, y, z] for y in [bottom, top] for x, z in poly]
    faces = [tuple(reversed(range(count))), tuple(range(count, count*2))]
    faces += [(i, (i+1)%count, (i+1)%count+count, i+count) for i in range(count)]
    mesh(name, vertices, faces, material, "CENTRAL upper platform extension; original slab/pit retained")


class PathFit:
    def __init__(self, points):
        self.p = np.asarray(points)
        self.v = self.p[1:]-self.p[:-1]
        self.length = np.linalg.norm(self.v, axis=1)
        assert np.all(self.length > 1e-8)
        self.s = np.r_[0, np.cumsum(self.length)]
        self.t = np.zeros_like(self.p); self.t[0] = self.v[0]; self.t[-1] = self.v[-1]; self.t[1:-1] = self.p[2:]-self.p[:-2]
        self.t /= np.linalg.norm(self.t, axis=1)[:,None]

    def sample(self, at):
        i = min(len(self.length)-1, max(0, int(np.searchsorted(self.s, at, side="right")-1)))
        fraction = (at-self.s[i])/self.length[i]
        tangent = self.t[i]*(1-fraction)+self.t[i+1]*fraction
        return self.p[i]+self.v[i]*fraction, tangent/np.linalg.norm(tangent)

    def nearest(self, point):
        fraction = np.clip(np.sum((point-self.p[:-1])*self.v, axis=1)/(self.length*self.length), 0, 1)
        positions = self.p[:-1]+self.v*fraction[:,None]
        i = int(np.argmin(np.linalg.norm(positions-point, axis=1)))
        return float(self.s[i]+fraction[i]*self.length[i])

    def fit(self, at):
        low, high = 1.5, 2.8
        for _ in range(25):
            h = (low+high)/2; a = self.sample(at-h)[0]; b = self.sample(at+h)[0]
            if np.linalg.norm(b-a) < 3: low = h
            else: high = h
        h = (low+high)/2; a = self.sample(at-h)[0]; b = self.sample(at+h)[0]
        position = (a+b)/2; forward = (b-a)/np.linalg.norm(b-a)
        yaw = math.atan2(forward[0], forward[1]); right = np.array([math.cos(yaw), -math.sin(yaw)])
        bogies = []
        for local_z, near in [(-1.5, at-h), (1.5, at+h)]:
            target = position+forward*local_z; projection = (self.p-target)@forward; candidates = []
            for i in np.flatnonzero(projection[:-1]*projection[1:] <= 0):
                denominator = projection[i]-projection[i+1]
                if abs(denominator) < 1e-9: continue
                fraction = projection[i]/denominator; rail_at = self.s[i]+fraction*self.length[i]
                if abs(rail_at-near) > 4: continue
                p, tangent = self.sample(rail_at)
                slide = float((p-target)@right); angle = math.atan2(tangent[0], tangent[1])-yaw
                angle = math.atan2(math.sin(angle), math.cos(angle))
                candidates.append((abs(rail_at-near), slide, angle, float(rail_at), p))
            assert candidates, (at, local_z)
            _, slide, angle, rail_at, p = min(candidates, key=lambda row: row[0])
            assert np.linalg.norm(position+forward*local_z+right*slide-p) < 1e-6
            bogies.extend([slide, angle, rail_at])
        return [float(at), float(position[0]), float(position[1]), yaw, *bogies]


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", required=True, type=Path); args = parser.parse_args()
    out = args.output.resolve(); assert out.parent == HERE and not out.exists()
    interface = json.loads(screen.read(ROOT / "BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/SUCCESSOR_INTERFACE.json"))
    old = np.array(interface["guideway"]["route_points_xz"], float)
    a = int(np.argmin(np.linalg.norm(old-[-5.6,-85.3], axis=1))); b = int(np.argmin(np.linalg.norm(old-[-5.6,92], axis=1)))
    assert np.linalg.norm(old[a]-[-5.6,-85.3]) < 1e-6 and np.linalg.norm(old[b]-[-5.6,92]) < 1e-6 and a < b
    central = screen.fillet([[-5.6,-85.3],[-5.6,-78],[44.5,-78],[44.5,78],[-5.6,78],[-5.6,92]])
    route = np.vstack([old[:a], central, old[b+1:]])
    fit = PathFit(route)
    central_begin = float(fit.s[a]); central_end = float(fit.s[a+len(central)-1])
    # The selected point is on the first curve. Body/chord fitting is never forced
    # onto that point or into yaw zero. All bridge measurements use the real body.
    central_at = float(fit.s[a+24]); pose = fit.fit(central_at)
    body = np.array(pose[1:3]); forward = np.array([math.sin(pose[3]),math.cos(pose[3])]); right = np.array([math.cos(pose[3]),-math.sin(pose[3])])
    track_point = fit.sample(central_at)[0]; edge = track_point-right*2.2
    source_plan = json.loads(screen.read(ROOT / "Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
    central_station = next(row for row in source_plan["stations"] if row["label"] == "CENTRAL")
    source_reach = float(central_station["bridge_reach_m"])
    source_sill = 2.2-source_reach
    portal = body-right*source_sill
    reach = float((portal-edge)@right)
    assert abs(float((portal-edge)@forward)) < 1e-6
    assert 1.3 < reach < 1.5
    # A three-metre-wide apron fans into the unchanged platform's north edge.
    front_left, front_right = edge-forward*1.5, edge+forward*1.5
    outward = -right
    assert outward[1] > .8
    back_left = front_left+outward*((-75-front_left[1])/outward[1])
    back_right = front_right+outward*((-75-front_right[1])/outward[1])
    polygon = np.array([front_left,front_right,back_right,back_left])
    assert polygon[:,0].min() > -7.8 and polygon[:,0].max() < -2.2
    assert abs(back_left[1]+75) < 1e-8 and abs(back_right[1]+75) < 1e-8
    assert np.linalg.norm(back_right-back_left) > 2.18
    prism("TSC23_CentralForeApron",polygon,55.85,56.1,"warm_stone")
    # Preserve the old north guard outside the new opening using named segments.
    join = sorted([float(back_left[0]),float(back_right[0])])
    for n,(x0,x1) in enumerate([(-7.8,join[0]),(join[1],-2.2)]):
        beam(f"TSC23_NorthGuard_{n}",[x0,57.23,-75],[x1,57.23,-75],.11,.11)
        beam(f"TSC23_NorthInfill_{n}",[x0,56.75,-75],[x1,56.75,-75],.06,1.08,"ivory_enamel")
    for n,(front,back) in enumerate([(front_left,back_left),(front_right,back_right)]):
        beam(f"TSC23_ApronSideRail_{n}",[front[0],57.23,front[1]],[back[0],57.23,back[1]],.11,.11)
        beam(f"TSC23_ApronSideInfill_{n}",[front[0],56.75,front[1]],[back[0],56.75,back[1]],.06,1.08,"ivory_enamel")
    # Close the old east-side boarding opening; no duplicate active portal.
    beam("TSC23_OldPortalClosedRail",[-2.2,57.23,-73.2],[-2.2,57.23,-70.8],.11,.11)
    beam("TSC23_OldPortalClosedInfill",[-2.2,56.75,-73.2],[-2.2,56.75,-70.8],.06,1.08,"ivory_enamel")
    for n,sign in enumerate([-1,1]):
        p = edge+forward*(1.2*sign)-right*.05
        box(f"TSC23_NewPortalPost_{n}",[p[0],57.35,p[1]],[.12,2.5,.12],"ivory_enamel")
    left, right_edge = edge-forward*1.32-right*.1,edge+forward*1.32-right*.1
    beam("TSC23_NewPortalHeader",[left[0],58.60,left[1]],[right_edge[0],58.60,right_edge[1]],.18,.18,"ivory_enamel")

    for name,offset,width,lo,hi in [("TSC23_ContinuousWeb",0,3.2,55.55,55.68),("TSC23_RailPort",-.86,.09,55.68,55.74),("TSC23_RailStarboard",.86,.09,55.68,55.74)]:
        ribbon(name, route, offset,width,lo,hi)
    for offset in [-1.25,1.25]:
        ribbon("TSC23_CentralUnderweb_"+str(offset),central,offset,.20,55.55,55.71)

    layout = json.loads(screen.read(ROOT / "Game/data/generated/structural_meshes.json"))
    d10 = [r for r in layout["regions"] if r["floor_y"] == 61]
    receivers=[]; unresolved=[]
    # Same pad size and header section as retained receiving_module_003. Drops
    # move outside the full four-metre running envelope, not into its safety band.
    for nominal in np.arange(central_begin+2,central_end-7,8):
        chosen=None
        for shift in [0,.5,-.5,1,-1,1.5,-1.5,2,-2]:
            at=nominal+shift; q,tangent=fit.sample(at); normal=np.array([tangent[1],-tangent[0]])
            legs=[q+normal*side for side in [-2.25,2.25]]
            owners=[screen.footprint_owners(p,d10) for p in legs]
            if all(len(x)==1 and abs(x[0]["overlap_m2"]-.0864)<1e-6 and abs(x[0]["underside_y"]-60.76)<1e-6 for x in owners):
                chosen=(at,q,legs,owners);break
        if chosen is None:
            unresolved.append({"nominal_cursor_m":float(nominal),"reason":"no full unique D10 bearing within +/-2m"});continue
        at,q,legs,owners=chosen; i=len(receivers)
        aa,bb=legs;beam(f"TSC23_Header_{i}",[aa[0],60.34,aa[1]],[bb[0],60.34,bb[1]],.18,.32)
        for j,(point,owner) in enumerate(zip(legs,owners)):
            x,z=point;box(f"TSC23_Bearing_{i}_{j}",[x,60.79,z],[.24,.08,.36])
            beam(f"TSC23_Drop_{i}_{j}",[x,55.72,z],[x,60.78,z],.08,.08)
            direction=(point-q)/np.linalg.norm(point-q);shoe_a=q+direction*1.48;shoe_b=q+direction*2.29
            beam(f"TSC23_Shoe_{i}_{j}",[shoe_a[0],55.695,shoe_a[1]],[shoe_b[0],55.695,shoe_b[1]],.38,.19)
        receivers.append({"cursor_m":float(at),"center_xz":q.tolist(),"pads":[{"xz":p.tolist(),"owner":o[0]}for p,o in zip(legs,owners)]})
    # Directly supported fore apron: pads land on the actual D10 fore_apron.
    for n,p in enumerate([front_left-right*.12,front_right-right*.12,back_left,back_right]):
        owners=screen.footprint_owners(p,d10)
        assert len(owners)==1 and abs(owners[0]["overlap_m2"]-.0864)<1e-6
        box(f"TSC23_ApronBearing_{n}",[p[0],60.79,p[1]],[.24,.08,.36])
        beam(f"TSC23_ApronDrop_{n}",[p[0],55.90,p[1]],[p[0],60.78,p[1]],.08,.08)
        receivers.append({"station_apron_pad":p.tolist(),"owner":owners[0]})
    # Retained south axial receiver geometry follows the now-straight X-5.6 tie.
    d09=[r for r in layout["regions"] if r["floor_y"]==52.5]
    for n,z in enumerate([84.,92.]):
        for x in [-2.4,2.4]:
            owners=screen.footprint_owners([x,z],d09); assert len(owners)==1
            box(f"TSC23_SouthPad_{n}_{x}",[x,52.54,z],[.42,.08,.75])
            box(f"TSC23_SouthPier_{n}_{x}",[x,54.12,z],[.30,3.08,.40],"ivory_enamel")
            receivers.append({"south_pad":[x,z],"owner":owners[0]})
        beam(f"TSC23_SouthBeam_{n}",[-7.4,55.63,z],[2.8,55.63,z],.55,.16)
        box(f"TSC23_SouthSeat_{n}",[-5.6,55.675,z],[3.5,.10,.55])

    source_paths=["Game/scripts/group4_boarding_safety.gd","Game/scripts/group4_tram_source_actuator.gd","Game/scripts/group4_boarding_bridge.gd","Game/scripts/group4_completion.gd","Game/scripts/group4_integrated_receiving.gd",
                  "Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-014_central_source.glb","Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-019_boarding_bridge.glb",
                  "BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend",
                  "BlenderCatalogue/assets/group4_tram_connections_20261009/receiving_module_003/Group4_Receiving_Module_003.blend"]
    for path in source_paths:screen.read(ROOT/path)
    stops=[]
    for station in source_plan["stations"]:
        if station["label"]=="CENTRAL":cursor=central_at
        else:
            target=np.array([station["track_x"],station["physical_docking_z"]]);cursor=fit.nearest(target)
            assert np.linalg.norm(fit.sample(cursor)[0]-target)<1e-6
        pp=fit.fit(cursor)
        stops.append({"station":station["label"],"distance_m":cursor,"world_xyz":[pp[1],56.1,pp[2]],"body_yaw":pp[3],"catchment_z":station["catchment_z"]})
    knots=sorted(set([4.,float(fit.s[-1]-4)]+list(np.arange(4,fit.s[-1]-4,.1))+[r["distance_m"]for r in stops]))
    poses=[fit.fit(float(at))for at in knots]
    max_slide=max(abs(p[i])for p in poses for i in [4,7])
    assert max_slide<.20
    # Conservative retained low speed. Full motor/braking/dynamics remain untested.
    poses=[p+[.25]for p in poses]
    result={"schema":"astraea.tram.section_candidate.20261023.r001","status":"UNADOPTED_SOURCE_CANDIDATE",
            "active":False,"integration_motion_admitted":False,"integration_boarding_admitted":False,"integration_joint_admitted":False,
            "protected_source":"1091d34e; original geometry and source files remain unchanged",
            "route_points_xz":route.tolist(),"central_interval_m":[central_begin,central_end],"safe_body_cursor_range_m":[4.,float(fit.s[-1]-4)],
            "guideway":{"soffit_y":55.55,"rail_head_y":55.74,"boarding_y":56.1,"running_clearance_top_y":60.1,"running_width_m":4.,"radius_m":4.},
            "protected_route_xz":interface["protected_polyline_xz"],"protected_band_y":[52.55,56.55],
            "central":{"source_station":central_station,"new_pose":pose,"path_point_xz":track_point.tolist(),"body_to_path_m":float(np.linalg.norm(body-track_point)),
                       "bridge_origin_xyz":[float(edge[0]),56.1,float(edge[1])],"bridge_yaw":pose[3],"bridge_reach_m":reach,
                       "retained_bridge_reach_m":source_reach,"moving_panel_x_scale":reach/source_reach,"usable_width_m":2.18,
                       "platform_fore_polygon_xz":polygon.tolist(),"join_to_retained_floor_x":join,"join_z":-75.,
                       "docking_tolerance_m":.005,"docking_tolerance_rad":.001,"stationary_frames":15,"lower_lift_pit_and_cabin_unchanged":True},
            "stops":stops,"maximum_cross_slide_m":max_slide,"source_cross_slide_limit_m":.20,"receiver_bindings":receivers,"unresolved_receivers":unresolved,
            "source_pins":screen.PINS,"parts_count":len(parts),
            "remaining":["Exact triangle/receiver/old-owner compatibility gate","Native Blender recipe has not run","Focused connected Godot physical gate","Existing caster/joint hold","Passenger views and repeated-route performance","No main adoption or movement admission"]}
    out.mkdir()
    for name,data in [("CANDIDATE.json",result),("MESHES.json",parts),("POSE_KNOTS.json",poses)]:
        (out/name).write_text(json.dumps(data,separators=(",",":"))+"\n")
    print(json.dumps({"parts":len(parts),"receivers":len(receivers),"unresolved_receivers":len(unresolved),"central_body_pose":pose[:4],"bridge_reach_m":reach,"max_cross_slide_m":max_slide,"pose_knots":len(poses)}))


if __name__ == "__main__":main()
