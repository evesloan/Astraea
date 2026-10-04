from pathlib import Path
p=Path(__file__).parent/'build_planning_package.py'
s=p.read_text();needle='PDF.save()\n'
insert='''# 8 - one connected assembly proposal, independent of recovered adoption
p=Page(8,'One connected assembly to test first','An adjustable threshold-to-room proposal for the salon kit. The chain joins arrival, low reading edge and planted return; it is not six isolated decorations.')
p.text(62,166,'Plan   proposed joint test inside the historical allocation',23,INK,True)
xx=lambda x:86+(x-45)*17
zz=lambda z:422+z*17
# precise known door/axis; all proposed strips and modules are dashed
p.line(xx(48),zz(0),xx(72),zz(0),TEAL,3)
p.rect(xx(48),zz(-2),24*17,4*17,'#E2EBE5',TEAL,1,'6,4')
p.text(xx(60),zz(0)+5,'4 m STUDY CLEAR STRIP',14,TEAL,True,'middle')
p.line(xx(52),zz(-12),xx(52),zz(12),INK,2)
p.circle(xx(52),zz(0),6,BG,INK,2)
p.text(xx(52),zz(0)+27,'X52 guest door',13,MUT,'middle')
p.rect(xx(60),zz(-7.4),7.2*17,5.4*17,BLUE,INK,1.5,'7,4')
p.text(xx(63.6),zz(-5.4),'Quiet bay',15,INK,True,'middle')
p.text(xx(63.6),zz(-3.8),'7.2 x 5.4 m max',12,MUT,False,'middle')
p.rect(xx(60),zz(2),7.2*17,2.5*17,GREEN,INK,1.5,'7,4')
p.text(xx(63.6),zz(3.6),'Planted return',13,INK,True,'middle')
p.line(xx(52),zz(-2),xx(60),zz(-2),TEAL,5,'7,4')
p.text(xx(56),zz(-3),'portal / cove chain',12,MUT,False,'middle')
p.text(xx(48),zz(13.7),'Terrace',14,MUT)
p.text(xx(63),zz(13.7),'Room-side study',14,MUT)
p.para(62,713,'New study coordinates: quiet bay X60..67.2 / Z-7.4..-2; planted return X60..67.2 / Z+2..+4.5. The final 825.8 m2 room contour is missing, so these are candidate positions only.',610,17,MUT)
p.text(773,166,'Section   across the arrival route',23,INK,True)
sx=lambda v:800+(v+9)*33
sy=lambda h:551-h*34
p.line(sx(-9),sy(0),sx(8),sy(0),INK,2)
p.line(sx(-9),sy(8.25),sx(8),sy(8.25),MUT,1.2,'5,4')
p.text(sx(-9),sy(8.25)-12,'8.25 m historical usable-height budget',15,MUT)
p.line(sx(-7.4),sy(0),sx(-7.4),sy(3.8),INK,3,'7,4')
p.line(sx(-7.4),sy(3.8),sx(-2),sy(3.8),INK,3,'7,4')
p.rect(sx(-7.4),sy(.55),1.4*33,.55*34,BLUE,INK,1,'7,4')
p.rect(sx(2),sy(1.1),2.5*33,1.1*34,GREEN,INK,1,'7,4')
p.text(sx(-7.4),sy(3.8)-15,'Joined shelf / seat / cove',15,INK)
p.text(sx(0),sy(1.5),'CLEAR',14,TEAL,True,'middle')
p.text(sx(0),sy(.8),'4 m study',13,MUT,False,'middle')
p.text(sx(-9),sy(0)+28,'D09 +52.5 m   |   Z cross-section at proposed X64',14,MUT)
p.para(773,616,'The low bay uses the later 3.8 m maximum booth brief. Its ceiling must terminate into the enclosing return, with a joined light channel. The wider room ceiling remains unresolved.',605,17,INK)
p.para(773,723,'Preserve the actual door aperture, turn landings, Z0 route, X35..45 tram reserve and both service/public doors. The 4 m strip is a proposed QA allowance, not a proven body/cart clearance result.',605,17,RUST)
p.finish('Historical baseline + later component brief; all colored assembly locations and 4 m study strip are NEW proposals requiring fit review.')
'''
# fix one call that needs explicit bold/anchor
insert=insert.replace("p.text(xx(52),zz(0)+27,'X52 guest door',13,MUT,'middle')", "p.text(xx(52),zz(0)+27,'X52 guest door',13,MUT,False,'middle')")
s=s.replace(needle,insert+needle)
s=s.replace('seven compact vector sheets','eight compact vector sheets').replace('editable/01..07_planning_sheet.svg','editable/01..08_planning_sheet.svg').replace('Created PDF, 7 SVGs','Created PDF, 8 SVGs')
p.write_text(s)
