"""Create the local community sport beta. Sport statistics are synthetic."""
from pathlib import Path
import csv, io, json, random, urllib.request
ROOT=Path(__file__).resolve().parents[1]
def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding="utf-8",newline="\n")
def dump(path,obj):write(path,json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
def table(name,rows):
    for r in rows:r["data_status"]="Synthetic beta data"
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write("data/"+name+".csv",s.getvalue())
def download(url,path):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"FIT3179-beta/1.0"}),timeout=90) as r:p.write_bytes(r.read())
    return p
for package,filename in [
    ("vega@5.30.0/build/vega.min.js","vega.min.js"),
    ("vega-lite@5.20.1/build/vega-lite.min.js","vega-lite.min.js"),
    ("vega-embed@6.26.0/build/vega-embed.min.js","vega-embed.min.js"),
    ("purecss@3.0.0/build/pure-min.css","pure-min.css"),
    ("purecss@3.0.0/build/grids-responsive-min.css","grids-responsive-min.css")]:
    download("https://cdn.jsdelivr.net/npm/"+package,"vendor/"+filename)
for p in ["vega@5.30.0","vega-lite@5.20.1","vega-embed@6.26.0","purecss@3.0.0"]:
    download("https://cdn.jsdelivr.net/npm/"+p+"/LICENSE","vendor/"+p.split("@")[0]+"-LICENSE.txt")
write("vendor/README.md","""# Local browser libraries
Vega 5.30.0, Vega-Lite 5.20.1, Vega-Embed 6.26.0 and Pure.css 3.0.0.
Downloaded from jsDelivr's npm mirror. Original BSD licence texts included.
Projects: https://github.com/vega/vega , https://github.com/vega/vega-lite ,
https://github.com/vega/vega-embed , https://github.com/pure-css/pure .
""")
source=download("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson",".beta-tools/natural-earth-source.geojson")
world=json.loads(source.read_text(encoding="utf-8"))
codes={"New South Wales":"NSW","Victoria":"VIC","Queensland":"QLD","South Australia":"SA",
       "Western Australia":"WA","Tasmania":"TAS","Northern Territory":"NT","Australian Capital Territory":"ACT"}
def rounded(x):return [rounded(v) for v in x] if isinstance(x,list) else round(x,4) if isinstance(x,float) else x
features=[{"type":"Feature","properties":{"state":f["properties"]["name"],"code":codes[f["properties"]["name"]]},
 "geometry":{"type":f["geometry"]["type"],"coordinates":rounded(f["geometry"]["coordinates"])}}
 for f in world["features"] if f["properties"].get("admin")=="Australia" and f["properties"].get("name") in codes]
assert len(features)==8
victoria=[f for f in features if f["properties"]["code"]=="VIC"]
dump("data/australia_states.geojson",{"type":"FeatureCollection","features":features})
dump("data/victoria.geojson",{"type":"FeatureCollection","features":victoria})
write("data/GEOGRAPHY.md","""# Real geometry used in the beta
Natural Earth 1:50m Admin 1 states/provinces, public domain.
Source: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_1_states_provinces.geojson
Terms: https://www.naturalearthdata.com/about/terms-of-use/
Preparation: retain eight Australian jurisdictions, name/code only, round coordinates
to four decimal places. Jervis Bay and external territories are excluded. These are
cartographic outlines, not authoritative boundaries. Replace with appropriate simplified
ABS TopoJSON for the final plan. All associated sporting/facility/population data are synthetic.
""")
states=[
 ("New South Wales","NSW",8600000,6880000,21.4,24.2,18.7,11.0,147.1,-32.3),
 ("Victoria","VIC",7000000,5600000,24.1,27.1,21.2,12.8,144.2,-36.6),
 ("Queensland","QLD",5700000,4560000,20.8,23.6,18.1,11.2,144.6,-22.0),
 ("South Australia","SA",1900000,1520000,23.5,26.1,21.0,13.2,134.8,-30.0),
 ("Western Australia","WA",3000000,2400000,23.2,26.0,20.5,12.5,122.4,-25.0),
 ("Tasmania","TAS",580000,464000,22.8,25.3,20.4,13.5,146.7,-42.0),
 ("Northern Territory","NT",270000,216000,19.3,22.8,15.9,10.6,133.4,-19.6),
 ("Australian Capital Territory","ACT",490000,392000,26.2,28.6,23.9,14.8,149.1,-35.5)]
adult_total=sum(s[3] for s in states)
national_rate=round(sum(s[3]*s[4] for s in states)/adult_total,1)
national_volunteer=round(sum(s[3]*s[7] for s in states)/adult_total,1)
state_rows=[dict(state=a,code=b,population=c,adult_population=d,club_rate=e,male_rate=f,female_rate=g,
 estimated_participants=round(d*e/100),volunteer_rate=h,longitude=i,latitude=j,
 national_rate=national_rate,national_volunteer=national_volunteer) for a,b,c,d,e,f,g,h,i,j in states]
table("state_club_participation",state_rows)
table("participation_summary",[dict(cohort="Active adults",category=c,rate=r,order=i) for i,(c,r) in enumerate([
 ("Informal only",49),("Informal + organised",33),("Organised only",18)])])
table("organisation_types",[dict(organisation=n,rate=r) for n,r in [
 ("Sports club / association",national_rate),("Gym / fitness centre",19.6),("Private business",14.2),
 ("School / university",6.8),("Community group",5.5),("Workplace",2.3)]])
sports=["Football / soccer","Basketball","Tennis","Golf","Cricket","Australian football","Netball","Swimming","Rugby league","Volleyball"]
adult_rates=[3.8,3.0,2.7,2.6,2.1,2.0,1.8,1.6,0.9,0.8];child_rates=[13.2,9.6,7.5,0.8,5.9,8.4,6.7,12.1,2.9,1.9]
table("club_sports",[dict(sport=s,cohort=c,rate=r,estimated_participants=round(base*r/100))
 for c,rates,base in [("Adults (15+)",adult_rates,adult_total),("Children (0-14)",child_rates,5200000)]
 for s,r in zip(sports,rates)])
sport_state=[]
for si,sport in enumerate(sports):
 for st in state_rows:
    mod={"Australian football":{"VIC":2.1,"SA":1.9,"WA":1.7,"TAS":1.8,"NSW":.35,"QLD":.6},
      "Rugby league":{"NSW":2.1,"QLD":2.4,"VIC":.35,"SA":.2,"WA":.4,"TAS":.2},
      "Football / soccer":{"NSW":1.2,"VIC":1.12,"ACT":1.25},"Netball":{"VIC":1.3,"SA":1.35,"TAS":1.2}
    }.get(sport,{}).get(st["code"],1)
    rate=round(adult_rates[si]*mod*st["club_rate"]/national_rate,1)
    sport_state.append(dict(sport=sport,state=st["state"],code=st["code"],rate=rate,
     estimated_participants=round(st["adult_population"]*rate/100),longitude=st["longitude"],latitude=st["latitude"]))
table("sport_by_state",sport_state);max_sport_count=max(r["estimated_participants"] for r in sport_state)
ages=["15-24","25-34","35-44","45-54","55-64","65+"]
age_rates=[[9.2,6.7,4.5,2.8,1.6,.7],[8.6,5.0,3.3,2.1,1.0,.4],[4.8,4.1,4.5,4.2,3.7,3.1],
 [1.5,2.8,3.6,5.2,6.8,7.2],[5.8,4.4,3.3,2.1,1.3,.5],[6.2,4.0,2.6,1.4,.7,.2],
 [6.9,4.5,3.6,2.1,1.0,.3],[4.8,4.1,4.5,4.8,4.6,4.1],[3.5,2.6,1.7,.9,.4,.1],[3.8,2.6,1.8,1.3,.7,.3]]
table("age_sport",[dict(sport=s,age_group=a,age_order=j,rate=r) for s,rr in zip(sports,age_rates) for j,(a,r) in enumerate(zip(ages,rr))])
gender=[(6.4,2.7),(4.8,2.8),(3.8,3.5),(6.0,1.8),(4.9,.8),(4.8,1.6),(.4,6.8),(4.2,4.8),(3.0,.5),(2.4,2.1)]
table("gender_sport",[dict(sport=s,male=m,female=f,gap=round(abs(m-f),1)) for s,(m,f) in zip(sports,gender)])
roles=["Coach / instructor","Official / referee","Committee / administration","Team manager","General assistance","Driving participants","Fundraising","Medical / safety support"]
role_rates=[[1.8,3.5,5.6,4.9,2.8,1.5],[2.9,2.2,2.7,2.6,2.2,1.4],[.8,1.7,3.9,5.4,5.8,4.6],
 [.5,1.9,4.6,4.0,2.1,.9],[2.8,3.6,5.8,6.2,5.5,4.8],[.7,1.4,5.9,5.2,2.9,1.7],
 [1.4,2.3,4.0,4.5,4.1,3.0],[.4,.7,1.1,1.4,1.0,.7]]
table("volunteer_roles",[dict(role=role,age_group=a,age_order=j,rate=r) for role,rr in zip(roles,role_rates) for j,(a,r) in enumerate(zip(ages,rr))])
table("state_volunteering",[dict(state=r["state"],code=r["code"],club_rate=r["club_rate"],volunteer_rate=r["volunteer_rate"],population=r["population"]) for r in state_rows])
statements=[("Strengthens communities",[2,4,11,42,41]),("Supports wellbeing",[2,3,10,39,46]),
 ("Creates a sense of belonging",[3,5,14,43,35]),("Welcomes different backgrounds",[4,8,21,40,27]),("Values its volunteers",[4,7,23,40,26])]
responses=["Strongly disagree","Disagree","Neutral","Agree","Strongly agree"];likert=[]
for statement,values in statements:
 cursor=-(values[0]+values[1]+values[2]/2)
 for i,(response,value) in enumerate(zip(responses,values)):
    likert.append(dict(statement=statement,response=response,rate=value,order=i,start=cursor,end=cursor+value));cursor+=value
table("community_perceptions",likert)
rng=random.Random(3179)
def in_ring(x,y,ring):
 inside=False
 for i in range(len(ring)-1):
    x1,y1=ring[i];x2,y2=ring[i+1]
    if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:inside=not inside
 return inside
def in_victoria(x,y):
 g=victoria[0]["geometry"];pp=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
 return any(in_ring(x,y,p[0]) and not any(in_ring(x,y,h) for h in p[1:]) for p in pp)
centres=[("Melbourne",144.96,-37.81,.36),("Geelong",144.36,-38.15,.12),("Ballarat",143.85,-37.56,.18),
 ("Bendigo",144.28,-36.76,.18),("Shepparton",145.40,-36.38,.20),("Wangaratta",146.32,-36.36,.16),
 ("Traralgon",146.53,-38.19,.17),("Mildura",142.16,-34.19,.12)]
facility_sports=["Football / soccer","Australian football","Cricket","Netball","Tennis","Basketball"];facilities=[]
for i in range(84):
 name,lon,lat,spread=centres[i%len(centres)] if i>43 else centres[0]
 for attempt in range(10000):
    x=round(lon+rng.uniform(-spread,spread),4);y=round(lat+rng.uniform(-spread,spread)*.6,4)
    if in_victoria(x,y):break
 else:raise RuntimeError("Could not locate fictional facility within Victoria")
 facilities.append(dict(facility="Demo reserve "+str(i+1).zfill(2),locality=name,sport=facility_sports[i%6],
 longitude=x,latitude=y,surfaces=rng.randint(1,5),record_type="Fictional facility"))
table("victoria_facilities",facilities)
dump("data/headline_stats.json",dict(data_status="Synthetic beta data",adult_club_rate=national_rate,
 child_organised_rate=73.0,volunteer_rate=national_volunteer))


SCHEMA="https://vega.github.io/schema/vega-lite/v5.json"
GREEN="#216052";GOLD="#c38b32";PURPLE="#80618c";INK="#233c34"
def data(name):return {"url":"data/"+name+".csv","format":{"type":"csv"}}
def q(field,title=None,**extra):return dict(field=field,type="quantitative",title=title,**extra)
def n(field,title=None,**extra):return dict(field=field,type="nominal",title=title,**extra)
def tip(field,title,fmt=None,kind="quantitative"):
 d=dict(field=field,type=kind,title=title)
 if fmt:d["format"]=fmt
 return d
status_tip=tip("data_status","Status",kind="nominal");pctaxis={"labelExpr":"datum.label + '%'","tickCount":5}
def spec(name,body):
 base={"$schema":SCHEMA,"description":"BETA: synthetic demonstration sporting attributes; not survey findings.",
 "width":"container","height":300,"background":"transparent","autosize":{"type":"fit","contains":"padding"},
 "config":{"font":"DM Sans","view":{"stroke":None},
 "axis":{"labelFontSize":12,"titleFontSize":12,"titleFontWeight":500,"labelColor":"#56645d","titleColor":"#56645d",
 "domain":False,"tickColor":"#d9dfd7","gridColor":"#e5e8df","labelPadding":8,"titlePadding":14},
 "legend":{"labelFontSize":11,"title":None,"orient":"bottom","labelLimit":190},
 "range":{"category":[GREEN,GOLD,PURPLE,"#9fbc54","#6e98ac","#b37565"]}},
 "usermeta":{"data_status":"synthetic","beta":True}}
 base.update(body)
 if "vconcat" in body:
    for k in ["width","height","autosize"]:base.pop(k,None)
 dump("charts/"+name+".json",base)
spec("participation_structure",{"height":145,"data":data("participation_summary"),
 "layer":[{"mark":{"type":"bar","height":58,"cornerRadius":2},"encoding":{
 "y":n("cohort",axis=None),"x":q("rate","Share of active adults",stack="normalize",axis={"format":".0%","tickCount":5}),
 "color":n("category",scale={"domain":["Informal only","Informal + organised","Organised only"],"range":["#bfcbb8",GREEN,GOLD]}),
 "order":q("order"),"tooltip":[tip("category","Activity type",kind="nominal"),tip("rate","Share (%)",".0f"),status_tip]}},
 {"mark":{"type":"text","color":"white","fontWeight":"bold","fontSize":15},"encoding":{
 "y":n("cohort"),"x":q("rate",stack="normalize",bandPosition=.5),"detail":n("category"),"order":q("order"),
 "text":{"field":"rate","type":"quantitative","format":".0f"}}}]})
spec("organisation_types",{"height":290,"data":data("organisation_types"),
 "encoding":{"y":n("organisation",sort="-x",axis={"labelLimit":190,"ticks":False}),
 "x":q("rate","Adults participating (%)",axis=pctaxis,scale={"domain":[0,30]})},
 "layer":[{"mark":{"type":"rule","strokeWidth":2,"color":"#ccd6c7"},"encoding":{"x2":{"datum":0}}},
 {"mark":{"type":"circle","size":115,"opacity":1},"encoding":{
 "color":{"condition":{"test":"datum.organisation === 'Sports club / association'","value":GREEN},"value":"#a9b9a2"},
 "tooltip":[tip("organisation","Organiser",kind="nominal"),tip("rate","Adults (%)",".1f"),status_tip]}},
 {"mark":{"type":"text","align":"left","dx":10,"fontSize":12,"color":INK},"encoding":{"text":{"field":"rate","type":"quantitative","format":".1f"}}}]})
spec("club_sport_ranking",{"height":360,"data":data("club_sports"),
 "params":[{"name":"cohort","value":"Adults (15+)","bind":{"input":"select","options":["Adults (15+)","Children (0-14)"],"name":"Age group: "}}],
 "transform":[{"filter":"datum.cohort === cohort"}],"mark":{"type":"bar","cornerRadiusEnd":3,"color":GREEN,"height":{"band":.67}},
 "encoding":{"y":n("sport",sort="-x",axis={"labelLimit":160,"ticks":False}),
 "x":q("rate","Club-organised participation (%)",axis=pctaxis,scale={"domain":[0,15]}),
 "tooltip":[tip("sport","Sport",kind="nominal"),tip("cohort","Group",kind="nominal"),tip("rate","Participation (%)",".1f"),
 tip("estimated_participants","Demo participants",",.0f"),status_tip]}})
geo={"url":"data/australia_states.geojson","format":{"type":"json","property":"features"}}
projection={"type":"conicEqualArea","parallels":[-18,-36],"rotate":[-134,0,0],"center":[0,-28]}
demographic_rate="demographic === 'Male' ? datum.male_rate : demographic === 'Female' ? datum.female_rate : datum.club_rate"
spec("state_choropleth",{
 "params":[{"name":"demographic","value":"All adults","bind":{"input":"select","options":["All adults","Male","Female"],"name":"Show: "}}],
 "vconcat":[{"width":"container","height":430,"projection":projection,"data":geo,
 "transform":[{"calculate":"datum.properties.state","as":"state"},
 {"lookup":"state","from":{"data":data("state_club_participation"),"key":"state","fields":["club_rate","male_rate","female_rate","population","data_status"]}},
 {"calculate":demographic_rate,"as":"selected_rate"}],
 "params":[{"name":"stateSelect","select":{"type":"point","fields":["state"],"on":"click","clear":"dblclick"}}],
 "mark":{"type":"geoshape","stroke":"#fffdf6","strokeWidth":1.2},
 "encoding":{"color":q("selected_rate","Adults (%)",scale={"domain":[15,30],"range":["#e3ebd4","#175544"]},legend={"format":".0f"}),
 "opacity":{"condition":{"param":"stateSelect","value":1},"value":.35},
 "tooltip":[tip("state","State / territory",kind="nominal"),tip("selected_rate","Selected group (%)",".1f"),
 tip("population","Demo total population",",.0f"),status_tip]}},
 {"width":"container","height":190,"data":data("state_club_participation"),"transform":[{"calculate":demographic_rate,"as":"selected_rate"}],
 "mark":{"type":"circle","size":110,"color":GREEN},"encoding":{
 "x":q("selected_rate","Participation in selected adult group (%)",axis=pctaxis,scale={"domain":[15,30]}),
 "y":n("code",sort={"field":"selected_rate","order":"descending"},axis={"ticks":False}),
 "opacity":{"condition":{"param":"stateSelect","value":1},"value":.2},
 "tooltip":[tip("state","State / territory",kind="nominal"),tip("selected_rate","Participation (%)",".1f"),status_tip]}}
 ],"spacing":10,"resolve":{"scale":{"color":"independent"}}})
spec("sport_symbol_map",{"height":460,"projection":projection,
 "params":[{"name":"selectedSport","value":"Australian football","bind":{"input":"select","options":sports,"name":"Sport: "}}],
 "layer":[{"data":geo,"mark":{"type":"geoshape","fill":"#e6eadf","stroke":"white","strokeWidth":1.2}},
 {"data":data("sport_by_state"),"transform":[{"filter":"datum.sport === selectedSport"}],
 "mark":{"type":"circle","color":GREEN,"stroke":"#fffdf6","strokeWidth":1.4,"opacity":.7},
 "encoding":{"longitude":q("longitude"),"latitude":q("latitude"),
 "size":q("estimated_participants","Demo participants",scale={"domain":[0,max_sport_count],"range":[0,4000]},
 legend={"format":"~s","values":[10000,100000,250000]}),
 "tooltip":[tip("state","State / territory",kind="nominal"),tip("sport","Sport",kind="nominal"),
 tip("estimated_participants","Demo participants",",.0f"),tip("rate","Adult club rate (%)",".1f"),status_tip]}},
 {"data":data("state_club_participation"),"mark":{"type":"text","dy":-5,"fontSize":10,"color":INK},
 "encoding":{"longitude":q("longitude"),"latitude":q("latitude"),"text":n("code")}}]})
spec("facility_map",{"height":430,"projection":{"type":"mercator"},
 "params":[{"name":"facilitySport","value":"All sports","bind":{"input":"select","options":["All sports"]+facility_sports,"name":"Sport: "}}],
 "layer":[{"data":{"url":"data/victoria.geojson","format":{"type":"json","property":"features"}},
 "mark":{"type":"geoshape","fill":"#e6eadf","stroke":"#cdd7c7","strokeWidth":1}},
 {"data":data("victoria_facilities"),"transform":[{"filter":"facilitySport === 'All sports' || datum.sport === facilitySport"}],
 "mark":{"type":"circle","size":60,"opacity":.75,"stroke":"white","strokeWidth":.8},"encoding":{
 "longitude":q("longitude"),"latitude":q("latitude"),
 "color":n("sport",scale={"domain":facility_sports,"range":[GREEN,GOLD,PURPLE,"#9aaf50","#6c92a2","#b36c5d"]},legend={"columns":2,"symbolSize":75}),
 "tooltip":[tip("facility","Fictional facility",kind="nominal"),tip("locality","Nearby town / city",kind="nominal"),
 tip("sport","Sport",kind="nominal"),tip("surfaces","Demo surfaces",".0f"),status_tip]}},
 {"data":{"values":[dict(name=c[0],longitude=c[1],latitude=c[2]) for c in centres]},
 "mark":{"type":"text","dy":-10,"fontSize":10,"color":"#56645d"},
 "encoding":{"longitude":q("longitude"),"latitude":q("latitude"),"text":n("name")}}]})
age_param={"name":"ageSport","value":"All sports"}
spec("age_heatmap",{"height":350,"data":data("age_sport"),"params":[age_param],
 "mark":{"type":"rect","stroke":"#fffdf6","strokeWidth":2,"cornerRadius":2},"encoding":{
 "x":{"field":"age_group","type":"ordinal","sort":ages,"title":"Age group (years)","axis":{"labelAngle":0}},
 "y":n("sport",sort=sports,axis={"labelLimit":155,"ticks":False}),
 "color":q("rate","Organised participation (%)",scale={"domain":[0,10],"range":["#edf0df",GREEN]}),
 "opacity":{"condition":{"test":"ageSport === 'All sports' || datum.sport === ageSport","value":1},"value":.25},
 "tooltip":[tip("sport","Sport",kind="nominal"),tip("age_group","Age group",kind="nominal"),tip("rate","Participation (%)",".1f"),status_tip]}})
spec("gender_dumbbell",{"height":370,"data":data("gender_sport"),
 "encoding":{"y":n("sport",sort={"field":"gap","order":"descending"},axis={"labelLimit":150,"ticks":False}),
 "x":q("male","Organised participation (%)",scale={"domain":[0,8]},axis=pctaxis)},
 "layer":[{"mark":{"type":"rule","strokeWidth":2,"color":"#cfd6ca"},"encoding":{"x2":{"field":"female"}}},
 {"transform":[{"fold":["male","female"],"as":["gender","rate"]},{"calculate":"datum.gender === 'male' ? 'Male' : 'Female'","as":"gender_label"}],
 "params":[{"name":"genderHighlight","select":{"type":"point","fields":["gender_label"]},"bind":"legend"}],
 "mark":{"type":"circle","size":110},"encoding":{"x":q("rate","Organised participation (%)"),
 "color":n("gender_label",scale={"domain":["Male","Female"],"range":[GREEN,PURPLE]}),
 "opacity":{"condition":{"param":"genderHighlight","value":1},"value":.2},
 "tooltip":[tip("sport","Sport",kind="nominal"),tip("gender_label","Source category",kind="nominal"),tip("rate","Participation (%)",".1f"),status_tip]}}]})
spec("age_profiles",{"height":350,"data":data("age_sport"),"params":[age_param],
 "transform":[{"filter":"ageSport === 'All sports' ? indexof(['Football / soccer','Tennis','Netball','Golf'], datum.sport) >= 0 : datum.sport === ageSport"}],
 "mark":{"type":"line","point":{"filled":True,"size":65},"strokeWidth":2.5},"encoding":{
 "x":{"field":"age_group","type":"ordinal","sort":ages,"title":"Age group (years)","axis":{"labelAngle":0}},
 "y":q("rate","Organised participation (%)",scale={"domain":[0,10]},axis=pctaxis),
 "color":n("sport",scale={"domain":sports,"range":[GREEN,GOLD,PURPLE,"#779343","#b56e54","#5a91a7","#8b647c","#888b52","#ae9054","#628c86"]},
 legend={"columns":2,"labelLimit":145}),
 "tooltip":[tip("sport","Sport",kind="nominal"),tip("age_group","Age group",kind="nominal"),tip("rate","Participation (%)",".1f"),status_tip]}})
spec("volunteer_heatmap",{"height":330,"data":data("volunteer_roles"),
 "mark":{"type":"rect","stroke":"#fffdf6","strokeWidth":2,"cornerRadius":2},"encoding":{
 "x":{"field":"age_group","type":"ordinal","sort":ages,"title":"Age group (years)","axis":{"labelAngle":0}},
 "y":n("role",sort=roles,axis={"labelLimit":190,"ticks":False}),
 "color":q("rate","Adults volunteering (%)",scale={"domain":[0,7],"range":["#f6edda","#ba8029"]}),
 "tooltip":[tip("role","Volunteer role",kind="nominal"),tip("age_group","Age group",kind="nominal"),tip("rate","Adults in age group (%)",".1f"),status_tip]}})
spec("state_scatter",{"height":340,"layer":[
 {"data":{"values":[{"national_rate":national_rate}]},"mark":{"type":"rule","strokeDash":[5,4],"color":"#9aa598"},"encoding":{"x":q("national_rate")}},
 {"data":{"values":[{"national_volunteer":national_volunteer}]},"mark":{"type":"rule","strokeDash":[5,4],"color":"#9aa598"},"encoding":{"y":q("national_volunteer")}},
 {"data":data("state_volunteering"),"params":[{"name":"scatterPick","select":{"type":"point","fields":["state"]}}],
 "mark":{"type":"circle","color":GOLD,"stroke":"white","strokeWidth":1.5},"encoding":{
 "x":q("club_rate","Adults in club sport (%)",scale={"domain":[18,28]},axis=pctaxis),
 "y":q("volunteer_rate","Adults volunteering (%)",scale={"domain":[9,16]},axis=pctaxis),
 "size":q("population",scale={"range":[90,1400]},legend=None),
 "opacity":{"condition":{"param":"scatterPick","value":.9},"value":.25},
 "tooltip":[tip("state","State / territory",kind="nominal"),tip("club_rate","Club participation (%)",".1f"),
 tip("volunteer_rate","Volunteering (%)",".1f"),tip("population","Demo population",",.0f"),status_tip]}},
 {"data":data("state_volunteering"),"mark":{"type":"text","dy":-19,"fontSize":11,"color":INK},
 "encoding":{"x":q("club_rate"),"y":q("volunteer_rate"),"text":n("code")}}]})
spec("community_benefits",{"height":270,"data":data("community_perceptions"),"layer":[
 {"mark":{"type":"bar","height":{"band":.65}},"encoding":{
 "y":n("statement",sort=[s[0] for s in statements],axis={"labelLimit":195,"ticks":False}),
 "x":q("start","Share of responses (%)",scale={"domain":[-40,100]},
 axis={"values":[-40,-20,0,20,40,60,80,100],"labelExpr":"abs(datum.value) + '%'"}),"x2":{"field":"end"},
 "color":n("response",sort=responses,scale={"domain":responses,"range":["#80618c","#b8a3be","#e3e4da","#8daf86",GREEN]},
 legend={"columns":3,"labelLimit":135,"symbolType":"square"}),
 "order":q("order"),"tooltip":[tip("statement","Illustrative statement",kind="nominal"),
 tip("response","Response",kind="nominal"),tip("rate","Responses (%)",".0f"),status_tip]}},
 {"mark":{"type":"rule","color":"#8b9589","strokeWidth":1},"encoding":{"x":{"datum":0}}}]})


write("css/layout.css",r'''
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:100px}body{margin:0}
.wrap{width:min(1160px,calc(100% - 80px));margin-inline:auto}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:24px;min-height:72px}
.topbar nav{display:flex;gap:24px;align-items:center}
.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:60px;padding-block:72px 58px;align-items:center}
.hero-copy{max-width:690px}.hero-art{min-width:0}.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));padding-bottom:54px;gap:36px}
.stat{padding-top:22px;border-top:1px solid var(--line)}.chapter{padding-block:72px;scroll-margin-top:50px}
.chapter-heading{display:grid;grid-template-columns:1.05fr .95fr;gap:65px;align-items:end;margin-bottom:36px}
.chapter-heading p{margin-bottom:4px;max-width:500px}
.pure-g{display:flex;flex-wrap:wrap;row-gap:26px;margin-inline:-13px;letter-spacing:normal}
.pure-g>[class*="pure-u"]{padding-inline:13px;font-family:inherit;letter-spacing:normal}
.figure{padding:25px 26px 19px;border:1px solid var(--line);background:var(--paper);height:100%;min-width:0}
.figure.full{margin-top:26px}.figure-header{margin-bottom:15px}
.chart{width:100%;min-width:0;min-height:160px;position:relative}
.chart .vega-embed{width:100%;max-width:100%;display:block;padding:0!important}
.chart>svg,.chart>canvas,.chart .vega-embed>svg,.chart .vega-embed>canvas{display:block;max-width:100%;height:auto}
.chart .vega-bindings{padding-top:12px;display:flex;flex-wrap:wrap;gap:10px}
.chart .vega-bind{display:flex;align-items:center;gap:7px;max-width:100%}
.chart .vega-bind select{max-width:100%}
.source-note{margin:13px 0 0;padding-top:12px;border-top:1px solid var(--line)}
.insight{margin:15px 0 0;padding-left:12px;border-left:3px solid var(--accent)}
.chart-pair{margin-top:26px}.editorial-note{padding:27px 8px 14px 0;max-width:340px}
.shared-control{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:16px 0 24px}
.footer-grid{display:grid;grid-template-columns:1fr 1fr;gap:64px}
footer{padding:60px 0 30px}.footer-bottom{margin-top:32px;padding-top:22px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:20px}
@media(max-width:1000px){.hero{gap:30px}.topbar nav{gap:15px}.chapter-heading{gap:30px}.figure{padding:22px 16px}.wrap{width:calc(100% - 48px)}}
@media(max-width:767px){.wrap{width:calc(100% - 32px)}.topbar .wrap{min-height:64px;flex-wrap:wrap;padding-block:12px;gap:10px}
.topbar nav{gap:15px;width:100%;justify-content:space-between}.hero{grid-template-columns:1fr;padding-block:42px 35px;gap:30px}
.hero-art{max-width:380px;width:100%;margin-inline:auto}.stats{gap:16px;padding-bottom:32px}.stat{padding-top:15px}
.chapter{padding-block:43px}.chapter-heading{grid-template-columns:1fr;gap:10px;margin-bottom:25px}.figure{padding:20px 10px 16px}
.pure-g{margin-inline:-5px;row-gap:20px}.pure-g>[class*="pure-u"]{padding-inline:5px}.figure.full{margin-top:20px}
.editorial-note{max-width:none;padding-block:0}.footer-grid{grid-template-columns:1fr;gap:28px}.footer-bottom{flex-direction:column}
.shared-control{align-items:flex-start}.shared-control select{width:100%}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
''')
write("css/style.css",r'''
:root{--forest:#203e33;--green:#216052;--accent:#a6bd62;--gold:#c38b32;--purple:#80618c;--paper:#fffdf6;--cream:#f4f3e9;--ink:#233c34;--muted:#647166;--line:#dce1d4}
body{background:var(--cream);color:var(--ink);font-family:"DM Sans",Arial,sans-serif;font-size:15px;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:inherit;text-underline-offset:3px}a:hover{color:var(--green)}
a:focus-visible,button:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:4px}
.skip-link{position:fixed;left:16px;top:-80px;z-index:100;padding:10px 20px;background:var(--paper)}.skip-link:focus{top:10px}
.beta-strip{background:#e9dda6;color:#4b4222;padding:8px 16px;text-align:center;font-size:12px;letter-spacing:.01em}.beta-strip strong{font-weight:800}
.topbar{position:sticky;top:0;z-index:20;background:rgba(244,243,233,.97);border-bottom:1px solid var(--line)}
.wordmark{text-decoration:none;display:flex;align-items:center;gap:10px;font-weight:800;font-size:15px;letter-spacing:-.4px}
.brand-mark{width:25px;height:25px;border:1.8px solid var(--forest);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:13px}
.topbar nav a{text-decoration:none;font-size:12px;font-weight:600;color:#526253}.topbar nav a:hover{text-decoration:underline}
.eyebrow{text-transform:uppercase;font-size:11px;letter-spacing:2px;font-weight:800;color:var(--green);display:block;margin:0 0 20px}
.hero h1{font-family:"DM Serif Display",Georgia,serif;font-weight:400;font-size:clamp(68px,8.4vw,112px);line-height:.98;letter-spacing:-4px;margin:0 0 28px}
.hero h1 em{font-weight:400;color:var(--green)}.hero .subtitle{font-size:19px;line-height:1.55;max-width:570px;margin:0 0 20px}
.hero .intro{font-size:14px;color:var(--muted);max-width:520px}
.hero-link{display:inline-flex;gap:28px;text-decoration:none;font-size:12px;font-weight:800;margin-top:12px;padding:8px 0;border-bottom:1px solid var(--forest)}
.hero-art svg{width:100%;height:auto;display:block}
.art-caption{text-transform:uppercase;font-size:10px;letter-spacing:1.7px;text-align:center;color:var(--muted);margin-top:14px}
.stat-value{display:block;font-family:"DM Serif Display",Georgia,serif;font-size:clamp(35px,4vw,55px);line-height:1.15;color:var(--forest)}
.stat-label{display:block;font-size:13px;margin-top:8px;max-width:250px}.stat-label strong{font-weight:700}
.demo-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#87712f;margin-top:9px}
.section-tint{background:#eaf0e5;border-block:1px solid #dce5d7}.section-warm{background:#f0ecdf;border-block:1px solid #e5dfce}
.chapter-heading .eyebrow{margin-bottom:12px}.chapter h2{font-family:"DM Serif Display",Georgia,serif;font-size:clamp(34px,4vw,48px);font-weight:400;line-height:1.12;letter-spacing:-1.2px;margin:0}
.chapter-heading p{color:var(--muted);font-size:14px;line-height:1.8}
h3{font-size:18px;line-height:1.35;letter-spacing:-.4px;margin:0 0 8px;font-weight:700}
.figure-index{font-size:10px;font-weight:800;letter-spacing:1.5px;color:var(--green);display:block;margin-bottom:9px}
.figure-header p{font-size:12px;line-height:1.65;color:var(--muted);margin:0}
.source-note{font-size:10px;color:var(--muted);line-height:1.7}.insight{font-size:12px;line-height:1.7;color:#526253}
.editorial-note h3{font-family:"DM Serif Display",Georgia,serif;font-size:29px;font-weight:400;line-height:1.25}
.editorial-note p{color:var(--muted);font-size:14px}.mini-tag{display:inline-block;border:1px solid #b6c7ae;border-radius:30px;padding:4px 10px;font-size:10px;letter-spacing:.6px;margin-bottom:16px}
select{font-family:inherit;font-size:12px;line-height:1.4;background:var(--paper);color:var(--ink);border:1px solid #bcc9b7;border-radius:4px;padding:8px 28px 8px 10px}
label,.vega-bind-name{font-size:12px;font-weight:600}.shared-control .control-tip{font-size:12px;color:var(--muted)}
.reset-button{background:transparent;color:var(--green);border:1px solid #b7c7ae;padding:7px 12px;font:600 11px "DM Sans",Arial,sans-serif;border-radius:3px;cursor:pointer}
.reset-button:hover{background:#eaf0e5}.chart-error{padding:25px 18px;background:#f5e9df;color:#69442e;border-left:3px solid #bc824d;font-size:13px}
.chart-loading{font-size:12px;color:var(--muted);padding:36px 0}
.closing{background:var(--forest);color:#fffdf5;padding-block:58px}.closing .eyebrow{color:#b6ca7c}
.closing h2{font:400 clamp(32px,4vw,48px)/1.16 "DM Serif Display",Georgia,serif;max-width:780px;margin:0 0 20px;letter-spacing:-.7px}
.closing p{max-width:760px;color:#d3ddcd;font-size:14px}.closing .beta-caveat{font-size:11px;color:#bbcba8;border-top:1px solid #52684e;padding-top:17px;margin-top:24px}
footer h3{font-size:14px;margin-bottom:12px}footer p,footer li{font-size:12px;color:var(--muted)}footer ul{padding-left:18px}footer li{margin-bottom:7px}
footer details{padding:12px 0;border-top:1px solid var(--line)}footer summary{font-size:12px;font-weight:600;cursor:pointer}
.footer-bottom{font-size:10px;color:var(--muted)}.green{color:var(--green)}.gold{color:var(--gold)}.purple{color:var(--purple)}
@media(max-width:767px){body{font-size:14px}.hero h1{font-size:74px;letter-spacing:-2.5px}.hero .subtitle{font-size:17px}
.stat-label{font-size:11px}.demo-label{font-size:9px;letter-spacing:.4px}.stat-value{font-size:36px}.figure-header p{font-size:11px}.chapter h2{font-size:35px}.eyebrow{font-size:10px}}
@media(max-width:360px){.topbar nav{gap:6px}.topbar nav a{font-size:10px}.hero h1{font-size:64px}.stat-value{font-size:29px}.stat{min-width:0}}
@media print{.topbar{position:static}.beta-strip{display:block}.figure{break-inside:avoid}.chapter{padding-block:30px}.chart .vega-bindings,.reset-button{display:none}}
''')
note='<p class="source-note">Synthetic beta data · Illustrative values, not verified AusPlay or survey results.</p>'
def figure(i,title,description,name,insight="",extra=""):
 return f'''<article class="figure {extra}" aria-labelledby="{name}-title"><div class="figure-header">
<span class="figure-index">{i:02d} / DEMONSTRATION</span><h3 id="{name}-title">{title}</h3><p>{description}</p></div>
<div id="{name}" class="chart" role="group" aria-label="{title}. Synthetic demonstration data." aria-busy="true"><p class="chart-loading">Loading visualisation…</p></div>
{('<p class="insight">'+insight+'</p>') if insight else ''}{note}</article>'''
html='''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>More Than a Game — Community Sport in Australia · Beta</title>
<meta name="description" content="An interactive beta of participation, inclusion and volunteering in Australian community sport. Clearly labelled synthetic demonstration data.">
<meta name="theme-color" content="#203e33"><link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="stylesheet" href="vendor/pure-min.css"><link rel="stylesheet" href="vendor/grids-responsive-min.css">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/layout.css"><link rel="stylesheet" href="css/style.css">
<script defer src="vendor/vega.min.js"></script><script defer src="vendor/vega-lite.min.js"></script><script defer src="vendor/vega-embed.min.js"></script><script defer src="js/embed.js"></script></head>
<body><a class="skip-link" href="#participation">Skip to the data story</a>
<div class="beta-strip" role="note"><strong>BETA / DEMONSTRATION DATA</strong> — All statistics and facility records are synthetic. This page demonstrates the design and interactions.</div>
<header class="topbar"><div class="wrap"><a class="wordmark" href="#top"><span class="brand-mark" aria-hidden="true">↗</span> MORE THAN A GAME</a>
<nav aria-label="Story chapters"><a href="#participation">01 Participation</a><a href="#places">02 Places</a><a href="#people">03 People</a><a href="#volunteers">04 Volunteers</a></nav></div></header>
<main id="top"><div class="wrap"><section class="hero" aria-labelledby="main-title"><div class="hero-copy">
<span class="eyebrow">Australia / Community sport / A data story</span><h1 id="main-title">More than<br>a <em>game.</em></h1>
<p class="subtitle">Mapping participation, inclusion and the volunteers behind Australia's community sporting clubs.</p>
<p class="intro">A Saturday match begins long before the first whistle. Explore who takes part, where opportunities are found, and the people who make local sport possible.</p>
<a class="hero-link" href="#participation">EXPLORE THE STORY <span aria-hidden="true">↓</span></a></div><div class="hero-art">
<svg viewBox="0 0 440 455" role="img" aria-labelledby="field-title"><title id="field-title">An original illustration of a community sporting field</title>
<defs><pattern id="stripes" width="56" height="56" patternUnits="userSpaceOnUse"><rect width="28" height="56" fill="#ffffff" opacity=".035"/></pattern></defs>
<rect x="15" y="10" width="410" height="430" rx="205" fill="#244e3e"/><rect x="15" y="10" width="410" height="430" rx="205" fill="url(#stripes)"/>
<g fill="none" stroke="#a9bf85" stroke-width="1.4" opacity=".7"><rect x="62" y="61" width="316" height="328" rx="149"/><path d="M62 225h316"/>
<circle cx="220" cy="225" r="61"/><circle cx="220" cy="225" r="4" fill="#b9ca8e"/>
<path d="M151 76v53h138V76M182 63v33h76V63M151 374v-53h138v53M182 387v-33h76v33"/></g>
<g fill="#d9dfa4"><circle cx="143" cy="185" r="7"/><circle cx="286" cy="283" r="7"/><circle cx="265" cy="144" r="7"/></g>
<g fill="#e3b35f"><circle cx="178" cy="300" r="7"/><circle cx="305" cy="201" r="7"/><circle cx="145" cy="266" r="7"/></g>
<path d="M151 185c45-36 91-44 109-40" fill="none" stroke="#e9edcd" stroke-width="1.3" stroke-dasharray="4 5" opacity=".7"/>
<rect x="280" y="340" width="153" height="70" rx="3" fill="#e4b764" transform="rotate(-7 350 375)"/>
<text x="356" y="371" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" letter-spacing="1.2" fill="#294433" transform="rotate(-7 350 375)">LOCAL TEAMS.</text>
<text x="356" y="389" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" letter-spacing="1.2" fill="#294433" transform="rotate(-7 350 375)">SHARED PURPOSE.</text></svg>
<p class="art-caption">On the field. Behind the scenes. In the community.</p></div></section>
<div class="stats" aria-label="Synthetic headline statistics">
<div class="stat"><span class="stat-value" id="stat-club">—</span><span class="stat-label">of adults take part through a <strong>sports club or association</strong></span><span class="demo-label">Synthetic demonstration</span></div>
<div class="stat"><span class="stat-value" id="stat-child">—</span><span class="stat-label">of children participate in <strong>organised activity outside school</strong></span><span class="demo-label">Synthetic demonstration</span></div>
<div class="stat"><span class="stat-value" id="stat-volunteer">—</span><span class="stat-label">of adults give their time as <strong>volunteers in sport</strong></span><span class="demo-label">Synthetic demonstration</span></div></div></div>
<section class="chapter" id="participation"><div class="wrap"><div class="chapter-heading"><div><span class="eyebrow">01 / The starting line</span><h2>How Australians<br><span class="green">take part.</span></h2></div>
<p>A walk, a gym class and a club match are different ways to be active. Begin with that distinction, then explore where community clubs fit. Hover for detail; use the controls to compare groups.</p></div>
<div class="pure-g"><div class="pure-u-1 pure-u-md-1-3"><div class="editorial-note"><span class="mini-tag">ACTIVITY ≠ CLUB MEMBERSHIP</span><h3>Not every active Australian plays for a club.</h3><p>Informal and organised activities can overlap. Participation through a club is also different from registered membership.</p><p>The chart shows a hypothetical breakdown of <strong>active adults</strong>, excluding adults who did not participate.</p></div></div><div class="pure-u-1 pure-u-md-2-3">'''
html+=figure(1,"There is more than one way to move","Share of active adults by how their activity is organised. The three categories sum to 100%.","participation_structure","In this demonstration, 51% of active adults take part in at least some organised activity.")
html+='</div></div><div class="pure-g chart-pair"><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(2,"Who brings people together?","Organisers of adult activity. A person can use more than one organiser, so these rates should not be added.","organisation_types","Sports clubs lead this illustrative comparison. Other providers also organise activity.")
html+='</div><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(3,"Which sports bring people to clubs?","Switch between adults and children. Each rate uses the population of the selected age group.","club_sport_ranking","Football / soccer leads both example rankings. These are club-organised rates, rather than all participation.")
html+='''</div></div></div></section>
<section class="chapter section-tint" id="places"><div class="wrap"><div class="chapter-heading"><div><span class="eyebrow">02 / A place to play</span><h2>One country.<br><span class="green">Different sporting places.</span></h2></div><p>Rates reveal how common club participation is. Counts reveal its scale. Local facility points offer another view of place, but cannot establish whether communities have enough facilities.</p></div>'''
html+=figure(4,"A state-by-state picture","Colour represents participation rate, not population. Choose a group, then click a state to highlight it in both views. Double-click to clear.","state_choropleth","The ACT has the highest all-adult rate in this demonstration. These differences are a design test, not a geographic finding.")
html+='<div class="pure-g chart-pair"><div class="pure-u-1 pure-u-md-2-3">'
html+=figure(5,"The sporting footprint changes by code","Circle area represents estimated adult club participants. The size scale stays fixed when you change sports.","sport_symbol_map","Try Australian football and rugby league to explore contrasting, deliberately constructed geographic patterns.")
html+='''</div><div class="pure-u-1 pure-u-md-1-3"><aside class="editorial-note"><span class="mini-tag">THREE MAPS, THREE QUESTIONS</span><h3>How common?<br>How many?<br>Where?</h3><p><strong>Area colour</strong> compares participation rates.</p><p><strong>Proportional circles</strong> compare participant counts.</p><p><strong>Location points</strong> show individual, fictional facilities.</p><p>All map outlines are real. Every sporting measure and facility record is synthetic.</p></aside></div></div>'''
html+=figure(6,"A closer look at Victoria","84 fictional facilities around selected Victorian towns and cities. Filter by sport and hover over a location. This is not a facility directory or an access measure.","facility_map","The demonstration intentionally concentrates points near Melbourne. The pattern does not describe actual facility availability.","full")
html+='''</div></section><section class="chapter" id="people"><div class="wrap"><div class="chapter-heading"><div><span class="eyebrow">03 / Who gets in the game?</span><h2>Different ages.<br><span class="purple">Different opportunities.</span></h2></div><p>Sporting patterns vary across age groups and genders. These examples use <strong>organised participation</strong>, a broader measure than club participation. They compare groups at one point in time.</p></div>
<div class="shared-control"><label for="age-sport">Explore a sport</label><select id="age-sport"><option value="All sports">Overview — all sports</option>'''
html+="".join(f'<option value="{s}">{s}</option>' for s in sports)
html+='''</select><button type="button" id="reset-age" class="reset-button">Reset overview</button><span class="control-tip" id="age-selection-status" aria-live="polite">Click a heat-map cell to update the age profile below.</span></div>'''
html+=figure(7,"A different sporting mix at every age","Darker cells mean higher organised participation. Click a sport to highlight its row and show its age profile below.","age_heatmap","The example contrasts younger-skewing team sports with a golf profile that is stronger among older adults.")
html+='<div class="pure-g chart-pair"><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(8,"Gender gaps across sporting codes","Each line connects male and female rates for one sport. Click a legend label to highlight that category.","gender_dumbbell","Netball has the largest gender gap in this example. These categories are placeholders for source categories, not a complete account of gender.")
html+='</div><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(9,"Participation across life stages","The overview compares four contrasting sports. Use the selector above or click the heat map to inspect any sport.","age_profiles","These are comparisons between age groups. They do not follow the same people as they grow older.")
html+='''</div></div></div></section><section class="chapter section-warm" id="volunteers"><div class="wrap"><div class="chapter-heading"><div><span class="eyebrow">04 / Behind every game</span><h2>The people who<br><span class="gold">keep clubs running.</span></h2></div><p>Coaches, officials, committee members and helpers make organised sport possible. Explore the different roles, then consider how a future survey view could communicate sport's perceived community value.</p></div>'''
html+=figure(10,"Many roles. Many ways to contribute.","Share of adults in each age group undertaking each unpaid role. One person can contribute in several roles.","volunteer_heatmap","In this demonstration, coaching peaks at 35–44, while committee involvement is strongest at 55–64.")
html+='<div class="pure-g chart-pair"><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(11,"Playing and helping, side by side","Each circle is a state or territory; circle area shows synthetic population. Dashed lines mark weighted national example rates.","state_scatter","The relationship is deliberately constructed for the beta. It provides no evidence of a real correlation or causal effect.")
html+='</div><div class="pure-u-1 pure-u-md-1-2">'
html+=figure(12,"What might community sport mean?","A demonstration of a diverging opinion chart. Neutral responses straddle the centre. Statements and values are illustrative, not survey questions or results.","community_benefits","The example gives wellbeing the highest combined agreement. Public opinion would describe perceptions, not prove health effects.")
html+='''</div></div></div></section><section class="closing"><div class="wrap"><span class="eyebrow">Beyond the scoreboard</span><h2>Participation starts with a place to play.<br>Community starts with people.</h2><p>The final story will connect club participation, demographic differences, local facilities and volunteering using verified evidence. This beta demonstrates how those pieces can be explored together.</p><p class="beta-caveat">All numerical findings above are examples derived from synthetic data. Replace and check them against the original sources before assessment submission.</p></div></section>
</main><footer><div class="wrap"><div class="footer-grid"><div><span class="eyebrow">Sources &amp; transparency</span><h3>A working prototype with a clear data boundary.</h3><p>No AusPlay, ABS or Community Perceptions Monitor statistics have been extracted into this beta. These organisations are intended final sources; they did not supply the demonstration values.</p>
<ul><li><a href="https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables" target="_blank" rel="noopener">AusPlay data tables</a> — planned participation and volunteering source.</li>
<li><a href="https://www.ausport.gov.au/clearinghouse/research/cpm" target="_blank" rel="noopener">Community Perceptions Monitor</a> — planned perceptions source.</li>
<li><a href="https://discover.data.vic.gov.au/dataset/sport-and-recreational-facilities-list" target="_blank" rel="noopener">Victorian facilities data</a> — planned source, subject to date and coverage checks.</li>
<li><a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noopener">Natural Earth</a> — actual public-domain state outlines used in this beta.</li></ul></div>
<div><h3>How to read this beta</h3>
<details><summary>Demonstration data and denominators</summary><div><p>Sporting statistics, population values, response statements and facilities are invented for prototyping. Adult participation uses a 15+ example population; child participation uses 0–14. Chart 1 uses active adults only. Organisation, sport and role categories may overlap.</p><p>Headline adult club and volunteer rates are population-weighted from the same synthetic state table. Demographic subgroup rates are independent constructed examples; subgroup population weights are not modelled.</p></div></details>
<details><summary>Methods and final-version limitations</summary><div><p>Verify releases, denominators, uncertainty and reliability flags. AusPlay changed collection methodology in July 2023: do not draw a continuous trend across the break. Age comparisons do not describe individual change; opinion surveys do not establish causation.</p><p>The beta uses compact GeoJSON; the final plan calls for simplified ABS TopoJSON. Facility counts alone do not measure access. State volunteering remains conditional on reliable, comparable data.</p></div></details>
<details><summary>Code, authorship and AI acknowledgement</summary><div><p>FIT3179 Data Visualisation 2 · Student author: <strong>[Add your name]</strong> · Beta prepared 15 October 2026.</p><p>OpenAI Codex assisted with HTML, CSS, JavaScript, Vega-Lite specifications and synthetic data. The project brief was developed with GPT-5.6 Sol Light, as reported by the student. The student must verify the final data and analysis.</p><p>Original field illustration created in SVG for this page. Library licences are included in vendor/. Typography: DM Sans and DM Serif Display via Google Fonts, with local fallbacks.</p></div></details>
<p><a href="CHART_SOURCE_MATRIX.md">Chart-to-source working matrix</a> · <a href="README.md">Setup and beta notes</a></p></div></div>
<div class="footer-bottom"><span>MORE THAN A GAME · FIT3179 · 2026</span><span>12 visualisations / 3 map idioms / Synthetic beta</span><a href="#top">Back to top ↑</a></div></div></footer>
<noscript><p class="wrap">JavaScript is required to render the charts. Enable it to explore the beta.</p></noscript></body></html>'''
write("index.html",html)
write("js/embed.js",r'''
"use strict";
(() => {
  const names = ["participation_structure","organisation_types","club_sport_ranking","state_choropleth",
    "sport_symbol_map","facility_map","age_heatmap","gender_dumbbell","age_profiles","volunteer_heatmap","state_scatter","community_benefits"];
  const views = new Map(), specs = new Map(), widths = new Map();
  const tracked = {club_sport_ranking:["cohort"],state_choropleth:["demographic","stateSelect_store"],
    sport_symbol_map:["selectedSport"],facility_map:["facilitySport"],age_heatmap:["ageSport"],age_profiles:["ageSport"]};
  const ageSelect = document.getElementById("age-sport");
  let ageValue = ageSelect.value, queue = Promise.resolve();
  window.betaCharts = views; window.betaReady = false;
  function showError(container,error) {
    container.replaceChildren();
    const p = document.createElement("p"); p.className = "chart-error";
    p.textContent = location.protocol === "file:"
      ? "Open this page through a local web server (see README.md). Charts cannot load data when opened directly."
      : "This chart could not load. Check local chart/data files and refresh. Details are in the browser console.";
    container.append(p); container.setAttribute("aria-busy","false");
    console.error("Chart loading failed:",container.id,error);
  }
  function fit(original,width) {
    const result = structuredClone(original);
    if (result.vconcat) {
      result.vconcat.forEach(part => {part.width=width;part.autosize={type:"fit-x",contains:"padding"};});
      result.vconcat[0].height=Math.max(255,Math.min(430,width*.63));
    } else {
      result.width=width;
      if (["sport_symbol_map","facility_map"].includes(original.usermeta?.chart_name))
        result.height=Math.max(255,Math.min(original.height,width*.74));
    }
    if (width<420) {
      result.config.axis.labelFontSize=10; result.config.axis.titleFontSize=10;
      result.config.axis.titleLimit=width-20; result.config.legend.labelFontSize=10; result.config.legend.columns=2;
      const shorten = part => {
        if (part.encoding?.y?.axis) part.encoding.y.axis.labelLimit=112;
        if (part.encoding?.x?.axis) part.encoding.x.axis.titleLimit=width-20;
        part.layer?.forEach(shorten);
      };shorten(result);
    }
    return result;
  }
  async function chooseAge(sport) {
    ageValue=sport;ageSelect.value=sport;
    document.getElementById("age-selection-status").textContent=sport==="All sports"
      ? "Overview: four contrasting sports in the profile. Click a heat-map cell to explore."
      : "Selected: "+sport+". Age profile updated below.";
    await Promise.all(["age_heatmap","age_profiles"].map(async name => {
      const view=views.get(name);if(view) await view.signal("ageSport",sport).runAsync();
    }));
  }
  ageSelect.addEventListener("change",()=>chooseAge(ageSelect.value).catch(console.error));
  document.getElementById("reset-age").addEventListener("click",()=>chooseAge("All sports").catch(console.error));
  async function render(name,initial=false) {
    const container=document.getElementById(name), width=Math.floor(container.clientWidth);
    if (width<1 || (!initial && Math.abs((widths.get(name)??0)-width)<8)) return;
    const previous=views.get(name), retained={};
    for (const key of tracked[name]||[]) {
      try {
        if (previous) retained[key]=key.endsWith("_store") ? previous.data(key) : previous.signal(key);
      } catch (_error) { /* No saved state on an initial render. */ }
    }
    previous?.finalize();
    try {
      container.replaceChildren();
      const {view}=await vegaEmbed(container,fit(specs.get(name),width),{actions:false,renderer:"svg",tooltip:true});
      views.set(name,view);widths.set(name,width);
      for (const [key,value] of Object.entries(retained)) {
        if (value===undefined) continue;
        if (key.endsWith("_store")) view.change(key,vega.changeset().remove(()=>true).insert(value));
        else view.signal(key,value);
      }
      if (["age_heatmap","age_profiles"].includes(name)) view.signal("ageSport",ageValue);
      await view.runAsync();
      if(name==="age_heatmap") view.addEventListener("click",(_event,item)=>{
        if(item?.datum?.sport) chooseAge(item.datum.sport).catch(console.error);
      });
      container.setAttribute("aria-busy","false");container.dataset.ready="true";
    } catch(error) {container.dataset.ready="false";showError(container,error);}
  }
  async function loadStats() {
    try {
      const r=await fetch("data/headline_stats.json");if(!r.ok)throw new Error("Headline HTTP "+r.status);
      const s=await r.json();
      [["stat-club",s.adult_club_rate],["stat-child",s.child_organised_rate],["stat-volunteer",s.volunteer_rate]]
        .forEach(([id,value])=>{document.getElementById(id).textContent=value.toFixed(1)+"%";});
    } catch(error) {console.error("Headline loading failed:",error);}
  }
  async function start() {
    await Promise.all([loadStats(),...names.map(async name=>{
      const container=document.getElementById(name);
      try {
        if(typeof vegaEmbed!=="function")throw new Error("Missing local Vega libraries.");
        const response=await fetch("charts/"+name+".json");if(!response.ok)throw new Error("Chart HTTP "+response.status);
        const definition=await response.json();definition.usermeta.chart_name=name;specs.set(name,definition);
        await render(name,true);
      } catch(error) {showError(container,error);}
    })]);
    window.betaReady=true;document.body.dataset.chartsReady=String(views.size);await chooseAge(ageValue);
    let timer;
    const observer=new ResizeObserver(()=>{
      clearTimeout(timer);timer=setTimeout(()=>{
        queue=queue.then(async()=>{for(const name of names)if(specs.has(name))await render(name);}).catch(console.error);
      },180);
    });names.forEach(name=>observer.observe(document.getElementById(name)));
  }
  start().catch(console.error);
})();
''')


write(".gitignore",".beta-tools/\n__pycache__/\n*.pyc\n.DS_Store\n")
write("README.md","""# More Than a Game — local beta
FIT3179 Data Visualisation 2 · Prepared 15 October 2026.

**All sports, population, opinion and facility attributes are synthetic. This beta
demonstrates layout and interactions; it is not ready for final submission.**
The real state outlines come from Natural Earth.

## View locally
In a terminal in this assignment directory, run:

~~~powershell
python -m http.server 8000 --bind 127.0.0.1
~~~

Visit http://127.0.0.1:8000/ in your browser. Stop with Ctrl+C.
Do not open index.html directly using file://: browsers block CSV/JSON loading.
VS Code Live Server also works. No npm installation or build step is needed.
Vega and Pure.css are local; Google Fonts are optional, with system fallbacks.

## Included
- A responsive, single scrolling page with 12 Vega-Lite visualisations.
- State choropleth, proportional-symbol and facility point maps.
- Coordinated map/state dots and age heat-map/profile views.
- Dropdowns, tooltips, legend highlighting and visible narrative findings.
- Small synthetic CSVs and consistent weighted headline JSON.
- Local library distributions and their original licence files.
- Source matrix, methodology notes and AI acknowledgement.
- Existing brief and PDFs preserved.

## Interactions
1. Switch club ranking between adults and children.
2. Choose a demographic on the state choropleth; click a state to highlight its
   comparison dot. Double-click to clear.
3. Change the sport on the proportional-symbol map; its size scale stays fixed.
4. Filter fictional Victorian facilities by sport.
5. Click an age heat-map cell or choose a sport above it to update the profile.
6. Click a gender legend item to highlight that category.
7. Click a scatterplot point to highlight its state.

## Files
- index.html: semantic story structure, annotations, sources and AI acknowledgement.
- css/layout.css: layout and responsive rules.
- css/style.css: typography and palette.
- js/embed.js: embedding, error handling, coordinated views and resizing.
- charts/*.json: 12 readable Vega-Lite specifications.
- data/: synthetic attributes and real geometry; see GEOGRAPHY.md.
- CHART_SOURCE_MATRIX.md: beta fields and intended final sources.
- scripts/build_beta.py: deterministic generator. Rerunning overwrites generated
  beta files; it preserves the existing project brief and PDFs.
- scripts/check_beta.py: structural/data integrity checks.
- scripts/browser_check.py: browser rendering and interaction checks.
- .beta-tools/: ignored development dependencies, original geometry and QA screenshots.

## Replace before submission
1. Open the actual sources; verify releases, sheets, fields and denominators.
2. Replace CSVs, headline figures and illustrative findings together. Keep the
   field names where sensible, or update corresponding JSON specifications.
3. Check reliability, uncertainty, missing data and methodology breaks.
4. Replace fictional facilities with verified Victorian or Casey records.
5. Verify state volunteering comparability; use the brief's fallback if needed.
6. Replace beta geography with the appropriate ABS TopoJSON where required.
7. Add your name, source dates and exact citations; review AI acknowledgement.
8. Align with the hand-drawn sketch, publish and test GitHub Pages while logged out.

## Data definitions
Adult = 15+; child = 0–14. Chart 1 uses active adults only.
Headline adult club and volunteer rates are weighted by synthetic adult population.
Gender subgroup rates are independently constructed; subgroup weights are not modelled.
Age/gender views show organised participation, not strictly clubs. Organiser, sport
and role categories can overlap. Opinion categories sum to 100% per statement.
Fictional facilities are not evidence of access or an actual facility directory.

## Verification
~~~powershell
python scripts/check_beta.py
~~~
Browser QA uses Playwright with installed Chrome:
~~~powershell
python scripts/browser_check.py
~~~
The site itself does not depend on Playwright. See the script's docstring for setup.

## GitHub Pages
Upload index.html, css/, js/, charts/, data/ and vendor/ to the repository root and
configure Pages for that branch/root. Relative paths support repository subpaths.
Keep specifications public alongside the page. Exclude .beta-tools/.
Creating local files does not publish a website.
""")
write("CHART_SOURCE_MATRIX.md","""# Chart-to-source matrix — beta working draft
Every beta sporting attribute is synthetic. Source suggestions come from the
brief and are **not verified extraction mappings**. Record exact workbook filename,
release, sheet/table title, row/cell range, denominator and reliability after
opening the actual files.

| # | Specification | Beta CSV and key fields | Intended final source (unverified) | Required check |
|---|---|---|---|---|
| 1 | participation_structure.json | participation_summary.csv: cohort, category, rate, order | AusPlay national, suggested sheet 3 | Active-adult denominator; exclusive categories |
| 2 | organisation_types.json | organisation_types.csv: organisation, rate | AusPlay national, suggested sheet 5 | Adult rates; overlapping categories |
| 3 | club_sport_ranking.json | club_sports.csv: sport, cohort, rate, estimated_participants | AusPlay By Sport, suggested club/association field, sheet 4 | Separate adult/child denominators; club only |
| 4 | state_choropleth.json | state_club_participation.csv: state, code, club_rate, male_rate, female_rate, population | Eight AusPlay jurisdictions and ABS population | Exact joins; rate not count; subgroup reliability |
| 5 | sport_symbol_map.json | sport_by_state.csv: sport, state, rate, estimated_participants, longitude, latitude | Eight AusPlay jurisdiction workbooks | Size proportional to count; fixed scale |
| 6 | facility_map.json | victoria_facilities.csv: facility, locality, sport, longitude, latitude, surfaces | Victorian facilities or City of Casey | Observation date, coverage; facilities are not clubs |
| 7 | age_heatmap.json | age_sport.csv: sport, age_group, age_order, rate | AusPlay national sheet 19 or By Sport | Organised rates unless true club rates available |
| 8 | gender_dumbbell.json | gender_sport.csv: sport, male, female, gap | AusPlay national sheet 19 or By Sport | Denominator and exact source category labels |
| 9 | age_profiles.json | age_sport.csv: sport, age_group, age_order, rate | Same verified source as chart 7 | Cross-sectional, shared sport control |
| 10 | volunteer_heatmap.json | volunteer_roles.csv: role, age_group, age_order, rate | AusPlay national, suggested sheet 25 | Unpaid non-playing roles; overlapping categories |
| 11 | state_scatter.json | state_volunteering.csv: state, code, club_rate, volunteer_rate, population | Comparable state AusPlay volunteering, if reliable | Otherwise replace with national volunteer comparison |
| 12 | community_benefits.json | community_perceptions.csv: statement, response, rate, order, start, end | Community Perceptions Monitor report/table | Exact question, report page, categories; no causal claim |

Headline JSON uses the synthetic state table for adult club/volunteer rates and a
separate child placeholder. Real map context is Natural Earth: see data/GEOGRAPHY.md.
Production geography remains appropriate simplified ABS TopoJSON.

## Extraction record template
For each final dataset record:
- Provider, dataset title, source URL and authors.
- Release date and observation period.
- Exact downloaded filename, sheet and table title.
- Row/cell range and source fields.
- Population, denominator and category wording.
- Estimates, margins of error and reliability flags.
- Preparation steps, output fields and cross-check totals.

Every synthetic CSV row contains data_status. Change it only after verification,
together with the chart, narrative and footer labels.
""")
write("scripts/check_beta.py",r'''"""Read-only structural and synthetic-data integrity checks."""
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
''')
write("scripts/browser_check.py",r'''"""Browser QA. Uses Playwright and installed Chrome (no browser download).
Optional isolated setup:
python -m pip install --target .beta-tools/python playwright
The application itself requires no Python packages.
"""
from pathlib import Path
import functools,http.server,json,sys,threading
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/".beta-tools/python"))
from playwright.sync_api import sync_playwright
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
    if path.startswith("/assignment-beta/"):path=path[len("/assignment-beta"):]
    return super().translate_path(path)
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Handler,directory=str(ROOT)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
url=f"http://127.0.0.1:{server.server_port}/"
out=ROOT/".beta-tools";out.mkdir(exist_ok=True)
report={"errors":[],"warnings":[],"checks":[]}
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",headless=True)
    page=browser.new_page(viewport={"width":1366,"height":900},device_scale_factor=1)
    page.on("pageerror",lambda error:report["errors"].append(str(error)))
    page.on("console",lambda message:report["errors"].append(message.text) if message.type=="error" else report["warnings"].append(message.text) if message.type=="warning" else None)
    page.on("response",lambda r:report["errors"].append(f"HTTP {r.status}: {r.url}") if r.status>=400 and r.url.startswith(url) else None)
    page.goto(url,wait_until="networkidle",timeout=60000)
    page.wait_for_function("window.betaReady === true",timeout=60000)
    assert page.locator(".chart[data-ready='true']").count()==12,"Not all charts rendered"
    assert page.locator(".chart-error").count()==0
    assert page.locator("#stat-club").inner_text()!="—"
    for name in page.evaluate("Array.from(window.betaCharts.keys())"):
     assert page.locator("#"+name+" svg").count()==1,name
     assert page.locator("#"+name+" svg path").count()>0,name
    report["checks"].append("12 charts render with non-empty SVGs")
    page.screenshot(path=str(out/"beta-desktop.png"))
    page.screenshot(path=str(out/"beta-fullpage.png"),full_page=True)
    page.locator("#places").screenshot(path=str(out/"beta-places.png"))
    page.locator("#club_sport_ranking select").select_option("Children (0-14)")
    assert page.evaluate("window.betaCharts.get('club_sport_ranking').signal('cohort')")=="Children (0-14)"
    page.locator("#sport_symbol_map select").select_option("Rugby league")
    assert page.evaluate("window.betaCharts.get('sport_symbol_map').signal('selectedSport')")=="Rugby league"
    page.locator("#facility_map select").select_option("Tennis")
    assert page.evaluate("window.betaCharts.get('facility_map').signal('facilitySport')")=="Tennis"
    page.locator("#state_choropleth select").select_option("Female")
    assert page.evaluate("window.betaCharts.get('state_choropleth').signal('demographic')")=="Female"
    report["checks"].append("Four bound dropdowns update Vega signals")
    page.locator("#age-sport").select_option("Golf")
    page.wait_for_function("window.betaCharts.get('age_profiles').signal('ageSport') === 'Golf'")
    assert page.evaluate("window.betaCharts.get('age_heatmap').signal('ageSport')")=="Golf"
    page.locator("#reset-age").click()
    page.wait_for_function("window.betaCharts.get('age_profiles').signal('ageSport') === 'All sports'")
    cells=page.locator("#age_heatmap .mark-rect.role-mark path")
    assert cells.count()==60,f"Expected 60 heat-map cells, got {cells.count()}"
    cells.first.click()
    page.wait_for_function("document.getElementById('age-sport').value !== 'All sports'")
    assert page.evaluate("window.betaCharts.get('age_profiles').signal('ageSport') === document.getElementById('age-sport').value")
    report["checks"].append("Sport selector, reset and heat-map click coordinate both age views")
    shapes=page.locator("#state_choropleth .mark-shape.role-mark path")
    assert shapes.count()==8
    shapes.first.click()
    page.wait_for_function("window.betaCharts.get('state_choropleth').data('stateSelect_store').length === 1")
    shapes.first.dblclick()
    page.wait_for_function("window.betaCharts.get('state_choropleth').data('stateSelect_store').length === 0")
    report["checks"].append("Map click selects a shared state; double-click clears")
    page.locator("#gender_dumbbell .role-legend-label").get_by_text("Female",exact=True).click()
    page.wait_for_function("window.betaCharts.get('gender_dumbbell').data('genderHighlight_store').length === 1")
    report["checks"].append("Gender legend highlighting responds to clicks")
    # The exact click target is verified using the actual shape centre in subsequent QA if needed.
    for width in [1024,768,390,320]:
     page.set_viewport_size({"width":width,"height":900})
     page.wait_for_timeout(1800)
     assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth+1"),f"Horizontal overflow at {width}: " + str(page.evaluate("[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,cls:e.className.baseVal||e.className,right:e.getBoundingClientRect().right})).slice(0,8)"))
     assert page.locator(".chart[data-ready='true']").count()==12
     assert page.locator(".chart-error").count()==0
     if width==390:
      page.screenshot(path=str(out/"beta-mobile.png"),full_page=True)
     report["checks"].append(f"All charts fit at {width}px without horizontal page scrolling")
    assert page.evaluate("window.betaCharts.get('sport_symbol_map').signal('selectedSport')")=="Rugby league"
    assert page.evaluate("window.betaCharts.get('facility_map').signal('facilitySport')")=="Tennis"
    report["checks"].append("Dropdown state survives responsive resizing")
    page.set_viewport_size({"width":1366,"height":900})
    page.goto(url+"assignment-beta/",wait_until="networkidle",timeout=60000)
    page.wait_for_function("window.betaReady === true",timeout=60000)
    assert page.locator(".chart[data-ready='true']").count()==12
    report["checks"].append("All chart/data paths work from a repository-style URL subpath")
    browser.close()
 assert not report["errors"],report["errors"]
 print(json.dumps(report,indent=2))
finally:
 server.shutdown();server.server_close()
 (out/"browser-check.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
''')
print("Beta created:",ROOT)
print("All sporting attributes are synthetic demonstration data.")

write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#203e33"/><circle cx="32" cy="32" r="20" fill="none" stroke="#b6ca7c" stroke-width="2"/><path d="M12 32h40" stroke="#b6ca7c" stroke-width="2"/></svg>')

# Apply the classroom reader-facing presentation after generation.
import runpy
runpy.run_path(str(ROOT/"scripts/expand_facilities.py"))
runpy.run_path(str(ROOT/"scripts/prepare_presentation.py"))
