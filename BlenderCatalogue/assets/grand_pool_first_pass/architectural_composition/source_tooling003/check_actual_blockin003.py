"""Apply the same independent retained-geometry screen to reopened actual vertices."""
from pathlib import Path
S=Path(__file__).resolve().parent
text=(S/'check_blockin003.py').read_text()
assert text.count("plan=json.loads((S/'BLOCKIN_PLAN_003.json').read_text())")==1
text=text.replace("plan=json.loads((S/'BLOCKIN_PLAN_003.json').read_text())","plan=json.loads((S/'BLOCKIN_ACTUAL_PLAN_003.json').read_text())")
text=text.replace("'BLOCKIN_PREFLIGHT_003.json'","'BLOCKIN_ACTUAL_PREFLIGHT_003.json'")
exec(compile(text,str(S/'check_blockin003.py'),'exec'),{'__name__':'__main__','__file__':str(S/'check_blockin003.py')})
