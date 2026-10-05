# Upper Horizon view screening, 2026-10-05

## Result

The complete **above-horizon starboard cap and halo** and **above-horizon port crescent** fit the bounded close viewing stations below. This includes side boundaries, horizon endpoints, shader support/antialias extents, small X/Z moves and standing eye-height variation, rather than an apex-only ray.

This is source geometry/envelope screening, **not final006 stage acceptance**, an installed full-hull proof, a Godot test, a visual review, a body/route certificate, or a pressure/structural engineering certificate. No production files were edited and no engine/import/capture/backup process was launched by this worker.

## Current 0b892eb5 candidate: final aperture triangle PASS

The final metal sill top isY107.42 and upper seal underside isY111.03. The preserved005 walnut cap staysY107.40. The refreshed source contract was verified against those exact values before screening.

All12 screens and5,294,322 sampled eye/ray pairs pass. There are zero opaque continuous-cone candidates/hits, zero glass misses or missing exits, and exactly one intended LowBay glass assembly per target cone. At the lowest seated eyeY107.55 the positive target clears the new sill by0.13m; the complete local port antialias footprint retains0.058599m outer-reveal clearance.

- Final006 source SHA256:0b892eb5b59111bea434d4a3c3c1c886fd8995511641c6f2e6f89c997ac9ab34
- Final006 export SHA256:70fd0d75fba5a61f0f59dddc9a00e86fdb88828acf7379f7838e7e2db5fc1860
- Final optical results:actual_triangles/results.json
- Results SHA256:bfdacc802d3b634fd8bd046c39bf24c031ad6172253aec2825c31878a21397e9
- Reproduce:OPENBLAS_NUM_THREADS=1 python assets/upper_horizon_enclosure/qa/view_screen/screen_actual.py

All inputs, including005 and the aperture contract, remained unchanged during screening. Ordinary visual review, routes, collision/material behavior and full-stage acceptance remain separate gates. Earlier candidate passes below are explicitly superseded comparisons.

## Superseded ebc04596 candidate: actual-triangle PASS

The ebc04596 candidate has since been superseded by a small sill/seal depth change. Its record is preserved in actual_triangles_ebc04596_superseded. The refreshed0b892eb5 candidate is now covered by the current pass above.

The broader-glazing source rebuild was screened at its refreshed actual world vertices/oriented triangles. All12 optical screens and5,294,322 sampled eye/ray pairs pass, with zero opaque continuous-cone candidates/hits, zero glass misses and zero missing second glass-face intersections. Each target cone intersects exactly its one named LowBay glass assembly; the other26 logical panes do not add a second layer in either target cone.

- Superseded006 source SHA256:ebc04596d9edc69a1ccc45d31fb76a37e42a0294a1c4b04f63963202c7b0f8e9
- Superseded006 export SHA256:64a0b8b22e2d0f61b64ac27f9f4b0bd1e9dd4e3b0af093319a0550e8803a9fef
- Superseded result:actual_triangles_ebc04596_superseded/results.json
- Superseded result SHA256:a46a2239400144d0fdcbe1e4af2e17ecfa84c938181dd5e3c3f23194363ba6b8
- Reproduce:OPENBLAS_NUM_THREADS=1 python assets/upper_horizon_enclosure/qa/view_screen/screen_actual.py

This supersedes the c34b comparison for the current geometry. All current input hashes, including005, were checked before and after the screen. Future-roof/envelope limits, ordinary visual review, glass/material/collision behavior and physical routes remain separate gates.

## Superseded c34b source triangle comparison

The c34b source was superseded by the broader-glazing rebuild after this successful comparison. Retain this earlier record for comparison; use the current ebc04596 pass above for the rebuild.

After the earlier source build, actual Blender world-vertex/oriented-triangle records for revised005 and006 were screened. **All12 target/height screens pass**, with zero opaque continuous-cone candidates and zero opaque hits. Every one of5,294,322 sampled eye/ray pairs traverses the two physical faces of its single intended glass pane; zero glass misses or missing exits. Glass is deliberately treated as optically transmitting, not exempted from physical collision requirements.

The tests cover the complete above-horizon starboard cap/halo and port crescent at the standing eye boxes and all three seated heights, plus the complete local port antialias footprint. The future-roof limits below remain applicable to negative rays. Input hashes were rechecked after the screen and remained unchanged.

-006 Blender source SHA256:c34b600ce42bdebe1c4a839c7934a335e2ae6a3f61cb0b4934401d41a4b99b5a
-006 GLB SHA256:3b9712b2c73e28af78a1ec22b02e9eefaa705bf4d4d2d794e5c84e32e1114ef1
-005 Blender source SHA256:4f96d43ec2d5c018451704168809592d9ca28269b07b7820421f482f4f5c92b9
- Superseded comparison results:actual_triangles_c34b_superseded/results.json
- Reproduce:OPENBLAS_NUM_THREADS=1 python assets/upper_horizon_enclosure/qa/view_screen/screen_actual.py

The separate source/export parity, contact and physical-route gates are owned by the parent. Ordinary normal/effects-off views and slow pans remain required; this result does not certify glass appearance or final art.

## Bounded station and aperture contract

- Standing |X|32.70..33.10, Y107.95..108.35, representing1.45..1.85m above floorY106.5
- Starboard standing/diagnostic eyeZ161.05..161.35; nominal eye(32.9,108.15,161.2)
- Port standing/diagnostic eyeZ162.10..162.60; nominal eye(-32.9,108.15,162.35)
- Seated diagnostic eyeY107.55,107.65,107.75 at the same X/Z station boxes; these are optical tests without furniture
- Glass centre |X|35.70, thickness0.06; glass faces35.67/35.73
- Reveal faces |X|35.52/35.88, clearZ160.10..163.90 and clearY107.42..111.03
- Preserved005 walnut cap topY107.40; new006 metal sill topY107.42 (0.92m above floor); no new element within target shoulder corridors belowY113.40; exterior top<=114.50

At outer reveal|X|35.88 the standing starboard target envelope is Y107.95..109.093808, Z160.321025..163.738588. Port positive target is Y107.95..109.106159, Z161.288427..162.617591. These are conservative envelopes for all eyes/rays, not just corners or a centre eye.

At |X|52 the worst standing target elevations are112.864306 starboard and112.939264 port. Clearances toY113.40 are0.535694m and0.460736m. Target-corridor shoulder envelopes from |X|35.7 to52 lie within starboardZ156.625721..175.846775 and portZ157.174412..162.706765. New fascia/brackets/trim must satisfy the same underside rule; the current actual-triangle screen above checks these authored triangles.

## Unchanged shader and exact angular boundaries

Actual runtime uses zero world sky rotation, default direction/radius uniforms and use_radiance_cache=false. Shader SHA256:08f0ec4c92b7de0c45afa539f8d9abdd65ec00c3d4af1831548f0ec24d485b2d.

- Starboard raw centre(0.9354072,-0.2923717,0.1988269), nominal radius29deg, halo support29.85deg
- Starboard positive halo horizon endpoints azimuth-12.9112521084deg and+36.9112476318deg
- Corresponding world directions(0.974717332121,0,-0.223441541488) and(0.799566775660,0,0.600577198418)
- Above-horizon halo q=dz/d|x| interval[-0.229237271283,0.751128256827]; p=dy/d|x| interval[0,0.233901864157]
- Max starboard halo-slope direction approximately(0.947788416,0.221689477,0.229239819); the maximum slope is not the same as the maximum-elevation direction
- Port raw centre(-0.9871089,0.1045285,-0.1212017), nominal radius7deg
- Port shader antialias support radius=acos(cos(7deg)-0.0006)=7.276646279255deg, rather than7deg
- Port full support p interval[-0.022453174763,0.237785706220], q interval[-0.255211787765,0.005531854752]
- Max port support-slope direction approximately(-0.965584523,0.229602198,-0.122185756)

The earlier eye|X|30,Y108.15 leaves only0.018714m belowY113.40 for the port antialias extent. It also cannot fit the whole above-horizon starboard halo: at glass35.7 the horizon span is5.588083m, exceeding the3.8m clear width. Its apex passes but its aft horizon endpoint hits glassZ166.281431 from eyeZ162, outside the bay. The close station solves this without changing the sky.

## Current frame and narrow005 comparison

The continuous conservative ray-cone AABB proof finds zero005 source-part candidates for either standing above-horizon composition, across the entire station boxes. Because the cone AABB encloses every exact target ray and each source AABB encloses every source triangle, disjointness proves exact source geometry cannot block those targets; this is stronger than merely sampling rays.

The original005 guard (opaque top107.82) crops the seated views. At nominal X32.9, its centre-azimuth cutoff is approximately:

| EyeY | Starboard elevation cutoff | Port elevation cutoff |
|---|---:|---:|
|107.55|5.628026deg|5.710328deg|
|107.65|3.550461deg|3.602588deg|
|107.75|1.463510deg|1.485044deg|

Only the exact allowlisted Back/Cap objects in the central bay are candidates. Baseline test samples contain substantial blocked ray sets at each height; counts are retained as diagnostics, not projected image-area percentages.

The revised005 ledger hash e278b2faa8b98e91ffc49137d51c44fbdc4a4f5f1ac168453f3434792513e320 has **zero continuous-cone candidates at all three seated heights**, including the entire X/Z station boxes. Positive targets clear the preserved005 capY107.40 by0.15/0.25/0.35m and the new006 sillY107.42 by0.13/0.23/0.33m. Every target ray through the guard depth remains strictly insideZ160..164, so preserving the short forward stub and long aft stub does not crop the intended targets.

The full local port shader footprint, including its below-horizon antialias fringe, also clears revised005 and the aperture. At the lowest seated eyeY107.55 it has minimum outer-revealY107.478599,0.078599m above the preserved005 cap and0.058599m above the new006 sill. Future roof limitations still apply.

## Future massing and honest failures

- Both positive targets miss the conservative central pavilion boxes|X|94..118/Z22..54 and aft pavilion boxes|X|73..104/Z400..436, independent of height. The full target envelope between them is retained in results.json
- Court reservations are|X|63..100/Z250..491.123. At|X|100 the farthest starboard positive ray hasZ211.900932; there is no court view from this composition
- Positive target rays stay at or above the eye height, so they never meet the D17 roof planeY106.5
- Starboard centre ray from nominal eye hits glassY107.274830, below the new sill, and roofY106.5 at(38.178972,106.5,162.322080). A full planet is impossible
- A starboard-5deg ray clears current local guard and pane, then intersects future roof at(51.347459,106.5,165.121128). Opening the local window does not grant a full lower-body view
- A starboard-10deg ray hits the original guard cap, is eligible to be released locally by the lower sill, and then meets future roof at(42.053129,106.5,163.145558)
- A high sky ray from nominal starboard eye through glass(35.7,111.03,162) touches the new head seal at approximately(35.7000,111.0300,162.0000), then reaches unchanged ACP_RoofLong_X35.5_Flange.008 at(35.768054,111.099998,162.019444). High stars near the pane top are legitimately framed/clipped; full-window panoramic visibility is not claimed
- The finite historical hull plan is|X|120 at these Z. At standing nominal port eye the nominal-1deg limb meetsY106.5 at|X|126.723836, outside that plan, while the actual shader's lowest supported fringe meets it at|X|106.386267, inside. Thus “all negative rays are hidden by roof” is not a valid finite-envelope claim
- For the three seated eyes, even the nominal port-1deg limb meets future roof inside the hull plan, at|X|92.606077/98.292371/103.978664. Lowest antialias support meets it at|X|79.663988/84.117701/88.571415. Promise the evaluated above-horizon crescent; record the lower crop

The roof calculation uses a future horizontal reservation clipped to the historical hull plan, not actual finished roof geometry or a resolved per-height hull. Its assumptions are explicit in the machine-readable results.

## Reproduce and retained files

Run:

python assets/upper_horizon_enclosure/qa/view_screen/screen.py --source-dir assets/upper_horizon_enclosure/qa/view_screen/baseline_source --label baseline_62ecbc2 --output assets/upper_horizon_enclosure/qa/view_screen/baseline

python assets/upper_horizon_enclosure/qa/view_screen/screen.py --label revised005 --output assets/upper_horizon_enclosure/qa/view_screen/revised005

Use baseline/results.json and revised005/results.json as the paired records. The root-level results.json/rays.npz are preliminary output superseded by these paired directories. Each result records exact input hashes. baseline_source is an evidence extract from the approved62ecbc2 source commit, not a production rollback. Its geometry SHA256 is939a06fc142d194a4bf48e09472b6fbbef350cb5320679ed5261c895073fbfe0 and section SHA256 is3b23828f71a63b6175cff393e33a2ebbeaf0e353c67f5f2546f7086a2aa247f7.

Each rays.npz retains normalized full/positive direction arrays and27 standing test eyes. Exact formulas and continuous slope bounds are in the script/results. Source-derived witness rays use double-sided triangle intersections, and all failures include names/points. actual_triangles/eyes.npz adds the standing/seated grids used by the final supplied-source screen. Ordinary default/effects-off views, slow pans and real body/routes remain the next gates.
