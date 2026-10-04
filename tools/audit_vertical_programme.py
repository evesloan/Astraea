"""Source-derived adjacency/void audit. Never creates rooms or grants cut permission."""
from pathlib import Path
import hashlib, json
from shapely.geometry import Polygon, box

ROOT = Path(__file__).resolve().parents[1]

def rectangle(record):
    return box(record['x'][0], record['z'][0], record['x'][1], record['z'][1])

def opening_conflicts(guests, openings):
    result = []
    for opening in openings:
        polygon = Polygon(opening['boundary'])
        assert polygon.is_valid and polygon.area > 0, opening['id']
        for i, guest in enumerate(guests):
            if f"D{guest['deck']:02}" not in opening['decks']:
                continue
            area = rectangle(guest).intersection(polygon).area
            if area > 1e-6:
                result.append({'opening': opening['id'], 'historical_guest_index': i,
                               'deck': guest['deck'], 'overlap_m2': round(area, 4)})
    return result

def main():
    files = ['data/design_contract.json', 'data/programme_ledger.json',
             'data/reference/directory_allocations.json',
             'data/reference/historical_guest_census.json', 'data/spatial_layout.json',
             'data/aquatic_section.json']
    contract, ledger, allocations, census, layout, aquatic = [json.loads((ROOT/f).read_text()) for f in files]
    elevations = {d['deck_id']: d['floor_elevation_m'] for d in contract['deck_datums']}
    programmes = {r['programme_key']: r for r in ledger['destinations']}
    records = allocations['records']
    assert len(records) == len(programmes) == 161
    assert set(programmes) == {r['programme_key'] for r in records}
    assert len(census['guest_envelopes']) == contract['binding_scale']['guest_units'] == 1000
    by_deck = {n: [] for n in range(1, 19)}
    for r in records:
        by_deck[r['deck']].append(r)
    connections = []
    for r in records:
        for upper in by_deck.get(r['deck'] + 1, []):
            area = rectangle(r).intersection(rectangle(upper)).area
            if area <= 1e-6:
                continue
            connections.append({'lower': r['programme_key'], 'upper': upper['programme_key'],
                                'overlap_m2': round(area, 3),
                                'floor_datum_difference_m': elevations[f"D{upper['deck']:02}"]-elevations[f"D{r['deck']:02}"],
                                'meaning': 'Stacked allocation only; no opening, route, headroom or architectural approval implied'})
    # Every compiler-level cut must be checked, including district lift shafts.
    openings = list(layout['voids'])
    openings += [{'id': 'aquatic_'+deck, 'decks': [deck], 'boundary': boundary}
                 for deck, boundary in aquatic['openings'].items()]
    conflicts = opening_conflicts(census['guest_envelopes'], openings)
    report = {'schema': 1, 'scope': 'Whole-ship section coordination; source allocations are not constructed rooms or capacity acceptance',
              'source_sha256': {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
              'decks': 18, 'programme_records': len(records), 'historical_guest_envelopes': 1000,
              'physical_guest_beds': None, 'finished_guest_units': 0,
              'checked_opening_ids': [v['id'] for v in openings],
              'protected_opening_guest_conflicts': conflicts, 'stacked_programme_adjacencies': connections,
              'limitations': ['Unknown persistent IDs remain unknown', 'No new structural openings authorized',
                              'Luxury replacements and multistorey fit unresolved', 'Deck pitch is not finished ceiling height',
                              'Programme adjacency does not prove an accessible connection',
                              'Full hull, crew berth fit and environmental routing require separate review']}
    (ROOT/'docs/VERTICAL_PROGRAMME_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# Whole-ship section coordination', '',
             'Generated from the historical allocations and current protected openings. This is an adjacency inventory, not a replacement room registry or a final architectural plan.', '',
             'All 161 directory programmes and 1,000 historical guest envelopes remain accounted for. No guest allocation intersects the checked compiler-level and aquatic openings. This does not establish fitted beds, completed rooms, or permission for further openings.', '',
             '## Section-first construction order', '',
             '1. Establish district volumes and their neighbouring uses in plan and section, within the hull and protected accommodation allocations.',
             '2. Resolve guest/service arrivals, accessible vertical travel, privacy and environmental boundaries before closing ceilings or adding repeatable room interiors.',
             '3. Author the district-specific Blender kit alongside the space, including its transitions and supports.',
             '4. Validate clearances and review normal-height views before applying approved construction families more broadly.', '',
             '## Existing connected work', '',
             '- Central atrium: D02 garden through D17 galleries beneath the D18 opaque cap; four principal bands and twelve quieter levels. Edges still need destinations and inhabitation.',
             '- Aft starboard: D08 Gentle Waters, D09 Living Gifts and D10 Vesper share a verified allocation and authored openings. D07 Team lounge and the D11 programme remain protected. This is only part of the aquatic district.',
             '- Theatre: D11 performance volume with retained D12–D14 floor openings. Gallery entry rectangles describe entries, not the whole auditorium.',
             '- Residential houses and upper luxury: establish fitted volumes and local lobbies/lifts against the 1,000 existing envelopes; no unverified house scheme is promoted to approved design.', '',
             '## Deck programme and adjacent levels', '',
             'The vertical distances below are datum differences, not required ceiling heights. Programmes can share an authored multi-level volume only after its boundaries and affected uses are reconciled.', '']
    for deck in range(1, 19):
        key = f'D{deck:02}'
        pitch = f"; next datum +{elevations[f'D{deck+1:02}']-elevations[key]:g} m" if deck < 18 else '; roof/hull clearance not inferred'
        lines += [f'### {key}, floor {elevations[key]:g} m{pitch}', '']
        for r in by_deck[deck]:
            uppers = [programmes[c['upper']]['name'] for c in connections if c['lower']==r['programme_key']]
            lines.append(f"- {r['name']}: X {r['x'][0]:g}…{r['x'][1]:g}, Z {r['z'][0]:g}…{r['z'][1]:g}." + (' Allocation above: '+ '; '.join(uppers)+'.' if uppers else ' No adjacent-level directory allocation overlap identified; this is not proof of empty space.'))
        lines += ['']
    (ROOT/'docs/WHOLE_SHIP_SECTION_COORDINATION.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'programmes':len(records), 'guests':1000, 'stacked_adjacencies':len(connections), 'opening_conflicts':len(conflicts)}))
    if conflicts:
        raise SystemExit('Protected guest envelopes intersect openings; resolve before geometry propagation')

if __name__ == '__main__':
    main()
