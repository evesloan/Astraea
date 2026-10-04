# Forward-commons arrival source audit

Read-only audit of surviving 1 October 2026 atlas and document snapshots. Only this derivative evidence folder was written. No original, catalogue, room registry, or runtime was changed.

## Useful result

An upper-deck horizontal arrival trace is recoverable from actual PDF vectors on D13–D17:

1. Plotted Townline forward-stop symbol center: **X 0, Z −432**
2. **Unverified boarding/egress connection** to port-sidewalk centerline **X −5.5, Z −432**
3. Authored sidewalk ribbon to **X −5.5, Z −370**
4. Authored transverse ribbon through the residential-lane crossing **X −44, Z −370**, to the commons door marker **X −63, Z −370**

The two ribbon-centerline legs after sidewalk arrival measure 62 + 57.5 = **119.5 m**. This is diagram-route length, not a verified gameplay journey or accessibility clearance. The nominal 5.5 m stop-center/sidewalk offset is not an authored vestibule route. No shaft or internal room geometry is needed to draw the recoverable horizontal portion; no new vertical shaft is established by it.

## Reproducible vector evidence

`extract_arrival_evidence.py` reads the PDF and existing allocation JSON, writing `atlas_forward_arrival_vectors.json`, `candidate_core_screen.json`, and `R3_candidate_core_screen.json`. All PDF drawing indices below are zero-based PyMuPDF `get_drawings()` indices. The JSON also preserves PDF sequence numbers, colors, widths, items, and calibration. Widths are drawing ribbon widths transformed into metres, not measured built clear widths.

PDF: `sources/Astraea-current-layout-atlas.pdf`, upper plans pp15–19 (D13–D17):

- Drawing 14: port sidewalk, **X −5.5, Z −541..−80**, width **4.6 m**
- Drawing 15: matching starboard sidewalk, X +5.5
- Drawing 18: port residential lane, **X −44, Z −541..−80**, width **4 m**
- Drawing 30: upper transverse ribbon, **Z −370, X −110..+110**, width **8 m**, full band **Z −374..−366**
- Drawing 32: separate outboard link at **Z −432, X −55..−95**, width **5 m**. This is not a surviving continuous stop-to-commons route and must not be extended through missing geometry
- Forward-commons allocation/door drawing indices: D13 **364/365**; D14 **521/522**; D15 **400/401**; D16 **440/441**; D17 **240/241**
- Allocation is **X −97..−63, Z −384..−356** on all five decks; door symbol is centered **X −63, Z −370**. Symbol dimensions are not door-aperture dimensions
- Tram route/forward-stop drawing indices: D13 **396/397**; D14 **553/554**; D15 **432/433**; D16 **472/473**; D17 **272/273**. Forward route centerline is X0 between Z−432 and −72. The 1.3 m line weight and 3 m stop-symbol radius are graphic conventions, not track or platform clearances

### Allocation-source line references

In `planning-package-v2/inputs/atlas_allocations.json`:

- D13 forward commons: lines **2222–2237**
- D14 forward commons: **4718–4733**
- D15 forward commons: **8414–8429**
- D16 forward commons: **11210–11225**
- D17 forward commons: **14306–14321**

These records intentionally have no mapped stable ID; do not invent one from the anonymous atlas footprint.

## Lower-deck routes differ

PDF pp11–14 (D09–D12):

- Drawing 14 remains the port sidewalk X−5.5, width4.6
- Drawing18 is a longitudinal **service/staff-colored ribbon**, **X−57, width5 m**, Z−541..541; full band X−59.5..−54.5. RGB **(0.654902,0.694118,0.729412)** matches the service/staff legend. The surviving text does not separately label this exact line; service-route meaning remains an interpretation, while its vector geometry is explicit
- Port guest transverse ribbons (drawings20–25) are at **Z−510,−324,−108,+108,+324,+510**, X−8..−54, width3.5
- **No Z−370 transverse ribbon exists on these lower decks**. Do not project the upper residential connector through them
- Some route primitives are painted before room shells and become covered. A underlying ribbon is not proof of a navigable route through the covering allocation

### Relevant lower public allocations and actual atlas door markers

D09: Orchard market, X−54..−8/Z−466..−398, door (−8,−432); Copper kettle, X8..54/same Z, door (8,−432). Atlas p11; allocation JSON lines2–33; directory `atlas.txt:928–931`.

D10: Shared table and Sunward dining have the same port/starboard allocation bounds and door coordinates, each 240 reserved places. Atlas p12; JSON **1662–1693**; directory `atlas.txt:1083–1086`.

D11: Cinema1 is starboard, X11..61/Z−468..−396, door **(11,−407)** (not at Z−432). The Music room is port, X−54..−8/Z−384..−316, door **(−8,−350)**. Atlas p13, door drawings985 and2003; JSON **1838–1853**, **1934–1949**; directory `atlas.txt:1159,1177`.

D12: Horizon room and Long library have port/starboard X−54..−8 / X8..54, both Z−466..−398, doors **(−8,−432)** / **(8,−432)**. Listening salon is X−54..−8/Z−358..−290, door **(−8,−324)**. Atlas p14, door drawings42/45/48; JSON **2030–2077**; directory `atlas.txt:1235–1241`.

The lower station doors are destinations reached on their own deck. A stacked station number does not establish a physical lift shaft there.

## Candidate screens

### Original lateral test (recorded in `candidate_core_screen.json`)

Guest core X−62..−56/Z−386..−378; service core X−62..−56/Z−362..−354; landings X−63..−54/Z−378..−374 and Z−366..−362.

- No positive-area room-allocation intersections on D09–D17
- On each D09–D12, each core intersects historical X−57 gray ribbon by **28 m²**; each landing by **20 m²**
- On D13–D17, no positive-area intersections with extracted room allocations or main diagram ribbons
- D09 nearby shop footprints include X−78..−66 and X−106..−94 at Z−398..−386 and Z−372..−360. No anonymous shop ID was invented

### Revised R3 test (`R3_candidate_core_screen.json`)

New test reservations: guest core **X−40..−34/Z−386..−378**; service core **X−54..−48/same Z**; separate same-X landings **Z−378..−374**. Vertical scope D12–D17 only. Proposed D12 guest spur **X−40..−5.5/Z−374..−366** and proposed service link **X−54.5..−54/Z−378..−374**.

- On D12–D17, both cores and both landings have **zero positive-area room or main-ribbon intersections**
- D13–D17 landings touch the historical transverse-ribbon boundary at Z−374. The X−46..−42 residential-lane ribbon remains untouched
- Proposed D12 guest spur has no room hits, and overlaps the port sidewalk ribbon by **18.4 m²** at the intended connection
- Proposed D12 service link has no positive-area room or ribbon hits and touches the X−54.5 edge of the gray ribbon
- If extended to D11, each core intersects the Music room by **36 m²**, and each landing by **24 m²**. This separately recorded diagnostic supports rejecting extension below D12
- This is only a historical 2D room/ribbon screen. It does not establish free real space, current runtime geometry, core sizing, wall thicknesses, slabs/structure, headroom, fire strategy, accessibility, moving-cabin mechanics or capacity

## Text evidence and limits

- `atlas.txt:80–112`: atlas is a spatial snapshot, not a construction drawing; minor objects/wall thicknesses omitted; ribbons indicate authored ground markings/access links, not independent navigation certification; transit meanings and excluded certifications
- `atlas.txt:2128–2138`: central starboard bypass coordinates; five stop Z coordinates; central express arrival X+5.5/Z−72; panoramic lift architecture differs from usable express interface
- `atlas.txt:2147–2151`: known central side portals X±52/Z0 and cross-street portals X±52/Z±42 only; these do not establish a forward-commons core
- `extracted/project_docs/SHIP_DESIGN.md:53–59`: canonical floor heights, separated public sidewalks/service-tram lane, residential branches, cart landings, explicit abstract passenger transit
- `extracted/project_docs/GUEST_SIMULATION.md:17–19,86`: route/landing/boarding API expectations and abstract transfer behavior; no surviving numeric boarding-anchor payload for the forward stop in the supplied snapshot
- `extracted/project_docs/architecture/WHOLE_SHIP_COVERAGE.md:47`: circulation is separately tracked and is not a registered room; lines122,136 distinguish later midship cupboard coordinates X±59/Z±20 and their bounded checks, not forward cupboards or a new forward service landing
- `extracted/Governing_Architecture_Brief.txt:29–33,50–66`: historical baseline must be reconciled to live branch; envelopes are allocations; protect stops, swept clearance, privacy/access and occupied deck slabs

No exact forward-stop vestibule geometry, forward-commons internal room layout, core mechanism, shaft envelope, shaft structure, or certified door clear width was recovered. Existing history/status pass claims cannot substitute for a fresh affected-route test after a new structural design.
