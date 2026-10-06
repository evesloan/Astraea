"""Original vector programme design; uses installed Inkscape only for rasterization.
All outputs remain beside this script. No borrowed logos, photos, or art assets.
"""
from pathlib import Path
import json, hashlib, subprocess, os
R=Path(__file__).resolve().parent
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=C/'assets/auditorium_arrival/AST-CUL-001.manifest.json'
retained=json.loads(manifest.read_text())
assert retained['details']['programme']=='A Thousand Small Worlds'
# Geometric mark, paired drapes, orbit and sun are drawn here from primitives.
# The companion cover only gains lateral breathing room; motifs/type do not stretch.
body='''
  <g id="publisher" fill="#eee3c8" font-family="DejaVu Sans, sans-serif">
    <text x="94" y="108" font-size="23" letter-spacing="5">SUNCORP CULTURE</text>
    <g id="original-sun-mark" fill="none" stroke="#c99d57" stroke-width="2">
      <circle cx="1120" cy="94" r="16"/><circle cx="1120" cy="94" r="25"/>
      <path d="M1082 94h76M1120 56v76"/>
    </g>
  </g>
  <text id="theatre" x="625" y="206" text-anchor="middle" fill="#eee3c8"
    font-family="DejaVu Serif, serif" font-size=" sixty">GRAND LANTERN</text>
  <path d="M95 248H1155" fill="none" stroke="#c99d57" stroke-width="1.5"/>
  <g id="original-curtain-sun-orbit-motif">
    <path d="M139 618V294H354C341 410 276 549 139 618Z" fill="#80534a"/>
    <path d="M139 618V294H239C233 410 199 532 139 618Z" fill="#a86f57"/>
    <path d="M1111 618V294H896C909 410 974 549 1111 618Z" fill="#80534a"/>
    <path d="M1111 618V294H1011C1017 410 1051 532 1111 618Z" fill="#a86f57"/>
    <path d="M282 597C318 401 412 309 625 309C838 309 932 401 968 597"
      fill="none" stroke="#365c59" stroke-width="2"/>
    <circle cx="625" cy="442" r="115" fill="#c99d57"/>
    <path d="M510 442A115 115 0 0 0 740 442Z" fill="#b98152"/>
    <ellipse cx="625" cy="460" rx="362" ry="77" fill="none" stroke="#ddc9a0" stroke-width="2"
      transform="rotate(-12 625 460)"/>
    <circle cx="961" cy="403" r="9" fill="#eee3c8"/>
    <circle cx="407" cy="550" r="5" fill="#c99d57"/>
    <path d="M239 601H1011M337 614H913" fill="none" stroke="#c99d57" stroke-width="1.5"/>
  </g>
  <g id="retained-fictional-title" text-anchor="middle" fill="#eee3c8" font-family="DejaVu Serif, serif">
    <text x="625" y="733" font-size="53" letter-spacing="2">A THOUSAND</text>
    <text x="625" y="807" font-size="62" letter-spacing="1.5">SMALL WORLDS</text>
  </g>
  <path d="M568 865H682" fill="none" stroke="#c99d57" stroke-width="1.5"/>
  <text id="programme-line" x="625" y="922" text-anchor="middle" fill="#d7c6a7"
    font-family="DejaVu Sans, sans-serif" font-size="18" letter-spacing="5">EVENING PROGRAMME</text>
'''.replace('font-size=" sixty"','font-size="60"')

def svg(w,h,dx,dy):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <title>SunCorp Culture — Grand Lantern evening programme</title>
  <desc>Original geometric sun, orbital ellipse and paired stage curtains. Retained fictional show title: A Thousand Small Worlds. No times, prices or schedule claims.</desc>
  <rect id="navy-paper-ground" width="{w}" height="{h}" fill="#142e34"/>
  <rect id="keyline" x="37" y="37" width="{w-74}" height="{h-74}" fill="none" stroke="#a68d60" stroke-width="1.5"/>
  <g id="editable-programme-composition" transform="translate({dx} {dy})">{body}</g>
</svg>\n'''
rows=[]
for stem,w,h,dx,dy in [('SUNCORP_GRAND_LANTERN_PROGRAMME',1250,990,0,0),('SUNCORP_GRAND_LANTERN_COVER',1400,1000,75,5)]:
 path=R/(stem+'.svg');path.write_text(svg(w,h,dx,dy))
 png=R/(stem+'.png')
 env=dict(os.environ,HOME=str(R/'.renderer_home'),XDG_CACHE_HOME=str(R/'.renderer_cache'),XDG_CONFIG_HOME=str(R/'.renderer_config'))
 for k in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME']:Path(env[k]).mkdir(exist_ok=True)
 subprocess.run(['inkscape',str(path),'--export-type=png','--export-filename='+str(png),'--export-width='+str(w),'--export-height='+str(h)],check=True,env=env,capture_output=True)
 rows.append({'svg':path.name,'svg_sha256':sha(path),'png':png.name,'png_sha256':sha(png),'dimensions_px':[w,h]})
receipt={'status':'ORIGINAL_EDITABLE_ART_CREATED_PIXEL_REVIEW_PENDING','art_originality':'New primitive SVG geometry and original SunCorp letter treatment; no external art, logo, photo or reference pixels used. System DejaVu typefaces.', 'render_method':'Installed Inkscape SVG renderer; no software installation','retained_title_evidence':{'path':str(manifest),'sha256':sha(manifest),'json_path':'details.programme','value':retained['details']['programme'],'supporting_source':str(C/'assets/auditorium_arrival/source/build_auditorium_arrival.py'),'supporting_source_sha256':sha(C/'assets/auditorium_arrival/source/build_auditorium_arrival.py')},'display_text':['SUNCORP CULTURE','GRAND LANTERN','A THOUSAND SMALL WORLDS','EVENING PROGRAMME'],'base_contract_text_override':{'PROGRAMME STUDY':'EVENING PROGRAMME'},'variants':rows,'source_native_acceptance':False}
(R/'ART_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
