"""Expand synthetic Victorian facilities to the requested classroom-beta counts."""
from pathlib import Path
from collections import Counter
import csv,json,random,re
ROOT=Path(__file__).resolve().parents[1]
TARGETS={"Football / soccer":210,"Australian football":275,"Cricket":140,"Netball":150,"Tennis":100,"Basketball":190}
source=ROOT/"data/victoria_facilities.csv"
with source.open(encoding="utf-8",newline="") as stream:
    reader=csv.DictReader(stream);fields=reader.fieldnames;rows=list(reader)
counts=Counter(row["sport"] for row in rows)
assert not (set(counts)-set(TARGETS)), "Unexpected sport in facilities"
assert all(counts[s]<=limit for s,limit in TARGETS.items()), "Existing facilities exceed requested targets"
geometry=json.loads((ROOT/"data/victoria.geojson").read_text(encoding="utf-8"))["features"][0]["geometry"]
polygons=geometry["coordinates"] if geometry["type"]=="MultiPolygon" else [geometry["coordinates"]]
def inside_ring(x,y,ring):
    inside=False
    for i in range(len(ring)-1):
        x1,y1=ring[i];x2,y2=ring[i+1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:
            inside=not inside
    return inside
def in_victoria(x,y):
    return any(inside_ring(x,y,p[0]) and not any(inside_ring(x,y,h) for h in p[1:]) for p in polygons)
# Nearby towns are location context; these are not actual facility records.
towns=[
 ("Geelong",144.36,-38.15),("Ballarat",143.85,-37.56),("Bendigo",144.28,-36.76),
 ("Shepparton",145.40,-36.38),("Wangaratta",146.32,-36.36),("Traralgon",146.53,-38.19),
 ("Mildura",142.16,-34.19),("Wodonga",146.89,-36.12),("Warrnambool",142.48,-38.38),
 ("Horsham",142.20,-36.71),("Echuca",144.75,-36.13),("Swan Hill",143.56,-35.34),
 ("Bairnsdale",147.63,-37.83),("Sale",147.07,-38.11),("Hamilton",142.02,-37.74),
 ("Portland",141.61,-38.35),("Colac",143.59,-38.34),("Ararat",142.93,-37.28),
 ("Stawell",142.78,-37.06),("Castlemaine",144.22,-37.06),("Benalla",145.98,-36.55),
 ("Seymour",145.13,-37.03),("Wonthaggi",145.59,-38.61),("Warragul",145.93,-38.16),
 ("Bacchus Marsh",144.44,-37.68),("Yarrawonga",146.00,-36.01)]
town_weights=[10,8,8,5,4,5,4,4,4,3,3,2,3,3,2,2,2,2,2,2,2,2,2,3,3,2]
melbourne=("Melbourne",144.96,-37.81)
rng=random.Random(317906)
coordinates={(float(r["longitude"]),float(r["latitude"])) for r in rows}
next_id=max(int(re.search(r"(\d+)$",r["facility"]).group(1)) for r in rows)+1
added=0
for sport,target in TARGETS.items():
    metro_share={"Football / soccer":.55,"Australian football":.43,"Cricket":.44,
                 "Netball":.46,"Tennis":.53,"Basketball":.64}[sport]
    for _ in range(target-counts[sport]):
        for attempt in range(10000):
            mode=rng.random()
            if mode<metro_share:
                locality,cx,cy=melbourne
                lon=rng.gauss(cx,.37);lat=rng.gauss(cy,.19)
            elif mode<.91:
                locality,cx,cy=rng.choices(towns,weights=town_weights,k=1)[0]
                lon=rng.gauss(cx,.14);lat=rng.gauss(cy,.085)
            else:
                lon=rng.uniform(140.98,149.98);lat=rng.uniform(-39.14,-34.0)
                locality,_,_=min([melbourne]+towns,key=lambda t:((t[1]-lon)*.8)**2+(t[2]-lat)**2)
            lon,lat=round(lon,5),round(lat,5)
            if (lon,lat) not in coordinates and in_victoria(lon,lat):break
        else:raise RuntimeError("Could not place facility within Victoria")
        coordinates.add((lon,lat))
        rows.append(dict(facility=f"Community sports facility {next_id:04d}",locality=locality,
                         sport=sport,longitude=lon,latitude=lat,surfaces=rng.randint(1,5),
                         record_type="Fictional facility",data_status="Synthetic beta data"))
        next_id+=1;added+=1
if added:rng.shuffle(rows)
actual=Counter(row["sport"] for row in rows)
assert actual==Counter(TARGETS)
assert len({r["facility"] for r in rows})==len(rows)
assert all(in_victoria(float(r["longitude"]),float(r["latitude"])) for r in rows)
with source.open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
# Smaller marks keep the enlarged statewide layer readable.
chart=ROOT/"charts/facility_map.json"
spec=json.loads(chart.read_text(encoding="utf-8"))
spec["layer"][1]["mark"].update(size=30,opacity=.65,strokeWidth=.5)
chart.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
readme=ROOT/"README.md"
doc=readme.read_text(encoding="utf-8")
summary="\n## Expanded facility layer\nThe synthetic Victorian facility layer has 1,065 records: soccer 210, Australian\nfootball 275, cricket 140, netball 150, tennis 100 and basketball 190. The original\n84 records are retained; added points are checked against the Victoria polygon,\nincluding coastline and holes. Most added points cluster around Melbourne and\nregional towns, with some rural locations. These are not real facility records.\nRegenerate using scripts/expand_facilities.py; build_beta.py also invokes it.\n"
if "## Expanded facility layer" not in doc:
    readme.write_text(doc+summary,encoding="utf-8",newline="\n")
print(json.dumps({"total":len(rows),"added":added,"counts":dict(actual),"all_points_within_victoria":True},indent=2))
