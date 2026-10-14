"""Read-only structural and synthetic-data integrity checks."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"index.html").read_text(encoding="utf-8")
charts=sorted((ROOT/"charts").glob("*.json"));assert len(charts)==12
paths=set()
def visit(value):
 if isinstance(value,dict):
    if isinstance(value.get("url"),str) and not value["url"].startswith("http"):paths.add(value["url"])
    for v in value.values():visit(v)
 elif isinstance(value,list):
    for v in value:visit(v)
for path in charts:
 obj=json.loads(path.read_text(encoding="utf-8"));assert obj["usermeta"]["data_status"]=="synthetic"
 assert f'id="{path.stem}"' in html;visit(obj)
for path in paths:assert (ROOT/path).is_file(),path
for path in (ROOT/"data").glob("*.csv"):
 assert b'\r\r\n' not in path.read_bytes(), "Duplicate CSV line endings"
 rows=list(csv.DictReader(path.open(encoding="utf-8",newline="")))
 assert rows and all(r["data_status"]=="Synthetic beta data" for r in rows),path
 for row in rows:
    for field in ["rate","club_rate","volunteer_rate","male_rate","female_rate"]:
     if field in row:assert 0<=float(row[field])<=100,(path,field)
rows=list(csv.DictReader((ROOT/"data/community_perceptions.csv").open(encoding="utf-8",newline="")))
for statement in set(r["statement"] for r in rows):
 group=[r for r in rows if r["statement"]==statement]
 assert len(group)==5 and sum(float(r["rate"]) for r in group)==100
 assert abs(float(group[-1]["end"])-float(group[0]["start"])-100)<.001
 assert float(group[2]["start"])==-float(group[2]["rate"])/2
states=list(csv.DictReader((ROOT/"data/state_club_participation.csv").open(encoding="utf-8",newline="")))
geo=json.loads((ROOT/"data/australia_states.geojson").read_text(encoding="utf-8"))
assert {r["state"] for r in states}=={f["properties"]["state"] for f in geo["features"]}
stats=json.loads((ROOT/"data/headline_stats.json").read_text(encoding="utf-8"));den=sum(int(s["adult_population"]) for s in states)
for field,key in [("club_rate","adult_club_rate"),("volunteer_rate","volunteer_rate")]:
 assert round(sum(int(s["adult_population"])*float(s[field]) for s in states)/den,1)==stats[key]
for path in re.findall(r'(?:src|href)="([^"#?]+)"',html):
 if not path.startswith(("http:","https:")):assert (ROOT/path).exists(),path
size=sum(p.stat().st_size for folder in ["charts","data"] for p in (ROOT/folder).rglob("*") if p.is_file())
assert size<3000000
print(f"PASS: 12 specs, {len(paths)} data paths, exact state joins, synthetic labels,")
print(f"      Likert totals, consistent weighted headlines and local page assets.")
print(f"      Charts + data: {size/1024:.1f} KiB")
