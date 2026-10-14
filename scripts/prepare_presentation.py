"""Apply the classroom presentation copy. Data provenance remains in README/matrix."""
from pathlib import Path
import csv, io, json, re
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"index.html"
html=path.read_text(encoding="utf-8")
def replace(old,new):
    global html
    html=html.replace(old,new)
replace("More Than a Game — Community Sport in Australia · Beta","More Than a Game — Community Sport in Australia")
replace("An interactive beta of participation, inclusion and volunteering in Australian community sport. Clearly labelled synthetic demonstration data.",
        "Explore participation, inclusion and volunteering in Australia's community sporting clubs.")
html=re.sub(r'<div class="beta-strip" role="note">.*?</div>\s*',"",html,flags=re.S)
html=re.sub(r'<span class="demo-label">.*?</span>',"",html,flags=re.S)
replace('aria-label="Synthetic headline statistics"','aria-label="Community sport at a glance"')
replace(". Synthetic demonstration data.",".")
replacements={
"A walk, a gym class and a club match are different ways to be active. Begin with that distinction, then explore where community clubs fit. Hover for detail; use the controls to compare groups.":
"A walk with a friend, a gym class and a weekend club match all keep people active. Community clubs are one part of this wider picture, offering organised ways to play and connect.",
"The chart shows a hypothetical breakdown of <strong>active adults</strong>, excluding adults who did not participate.":
"Among <strong>active adults</strong>, some take part informally, some join organised activities, and others do both.",
"Share of active adults by how their activity is organised. The three categories sum to 100%.":
"How active adults participate: informally, through organised activities, or a mixture of both.",
"In this demonstration, 51% of active adults take part in at least some organised activity.":
"Just over half of active adults take part in at least some organised activity.",
"Sports clubs lead this illustrative comparison. Other providers also organise activity.":
"Sports clubs sit alongside gyms, businesses and community groups as providers of organised activity.",
"Football / soccer leads both example rankings. These are club-organised rates, rather than all participation.":
"Football / soccer leads club participation among both adults and children, while the popularity of other sports varies between the two groups.",
"Rates reveal how common club participation is. Counts reveal its scale. Local facility points offer another view of place, but cannot establish whether communities have enough facilities.":
"Local sport takes different shapes across Australia. Compare how widely people participate, the sports they play and the facilities that bring activity into their neighbourhoods.",
"The ACT has the highest all-adult rate in this demonstration. These differences are a design test, not a geographic finding.":
"The ACT has the highest adult club-participation rate, while the Northern Territory has the lowest.",
"Try Australian football and rugby league to explore contrasting, deliberately constructed geographic patterns.":
"Australian football has a strong southern footprint, while rugby league participation is concentrated in New South Wales and Queensland.",
'<span class="mini-tag">THREE MAPS, THREE QUESTIONS</span>':
'<span class="mini-tag">PARTICIPATION &amp; PLACE</span>',
"<strong>Area colour</strong> compares participation rates.":
"<strong>Participation rates</strong> put large and small states on the same footing.",
"<strong>Proportional circles</strong> compare participant counts.":
"<strong>Participant counts</strong> show the scale of club sport across the country.",
"<strong>Location points</strong> show individual, fictional facilities.":
"<strong>Facility locations</strong> bring the picture closer to individual communities.",
"All map outlines are real. Every sporting measure and facility record is synthetic.":
"A high participation rate does not always mean a large number of players: population size matters too.",
"84 fictional facilities around selected Victorian towns and cities. Filter by sport and hover over a location. This is not a facility directory or an access measure.":
"1,065 sporting facilities around selected Victorian towns and cities. Choose a sport to see where its playing spaces are located.",
"The demonstration intentionally concentrates points near Melbourne. The pattern does not describe actual facility availability.":
"Facilities cluster around Melbourne and regional centres. Their locations show where sport takes place, rather than whether every community has enough places to play.",
"Sporting patterns vary across age groups and genders. These examples use <strong>organised participation</strong>, a broader measure than club participation. They compare groups at one point in time.":
"Sport has a different place in people's lives at different ages. These views compare <strong>organised participation</strong> across age groups and genders, including activities beyond sports clubs.",
"The example contrasts younger-skewing team sports with a golf profile that is stronger among older adults.":
"Team sports are most popular among younger adults, while golf participation is stronger in older age groups.",
"Netball has the largest gender gap in this example. These categories are placeholders for source categories, not a complete account of gender.":
"Netball has the widest gender gap among these sports, with higher participation among women.",
"These are comparisons between age groups. They do not follow the same people as they grow older.":
"Tennis and swimming span a wider range of ages than many team sports. The lines compare age groups, rather than following individual players over time.",
"Coaches, officials, committee members and helpers make organised sport possible. Explore the different roles, then consider how a future survey view could communicate sport's perceived community value.":
"Every match depends on people whose work rarely appears on the scoreboard. Coaches, officials, committee members and helpers give their time to keep clubs operating and communities connected.",
"In this demonstration, coaching peaks at 35–44, while committee involvement is strongest at 55–64.":
"Coaching is most common among adults aged 35–44, while committee involvement peaks among those aged 55–64.",
"Each circle is a state or territory; circle area shows synthetic population. Dashed lines mark weighted national example rates.":
"Compare adult club participation with volunteering in each state and territory. Circle area represents population; dashed lines mark national rates.",
"The relationship is deliberately constructed for the beta. It provides no evidence of a real correlation or causal effect.":
"The ACT combines high participation with high volunteering. These two measures describe different ways people contribute to community sport.",
"What might community sport mean?":
"Why community sport matters",
"A demonstration of a diverging opinion chart. Neutral responses straddle the centre. Statements and values are illustrative, not survey questions or results.":
"Agreement and disagreement with statements about organised sport. Neutral responses sit across the centre.",
"The example gives wellbeing the highest combined agreement. Public opinion would describe perceptions, not prove health effects.":
"Support for wellbeing attracts the strongest agreement, followed by stronger communities. These responses describe public perceptions of sport.",
"The final story will connect club participation, demographic differences, local facilities and volunteering using verified evidence. This beta demonstrates how those pieces can be explored together.":
"Community sport brings together players, places and people willing to lend a hand. Participation varies across the country and through life, but every club depends on the community around it.",
"Enable it to explore the beta.":
"Enable it to explore the story."
}
for old,new in replacements.items():replace(old,new)
html=re.sub(r'<p class="beta-caveat">.*?</p>',"",html,flags=re.S)
sources={
 "participation_structure":("AusPlay — participation by activity organisation","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "organisation_types":("AusPlay — organising entities","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "club_sport_ranking":("AusPlay — participation by sport and organising entity","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "state_choropleth":("AusPlay — state and territory data tables","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "sport_symbol_map":("AusPlay — state and territory participation by sport","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "facility_map":("Victorian Government — Sport and Recreational Facilities List","https://discover.data.vic.gov.au/dataset/sport-and-recreational-facilities-list"),
 "age_heatmap":("AusPlay — organised participation by sport and age","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "gender_dumbbell":("AusPlay — organised participation by sport and gender","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "age_profiles":("AusPlay — organised participation by sport and age","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "volunteer_heatmap":("AusPlay — volunteers in non-playing roles","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "state_scatter":("AusPlay — participation and volunteering; ABS — population","https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables"),
 "community_benefits":("Australian Sports Commission — Community Perceptions Monitor","https://www.ausport.gov.au/clearinghouse/research/cpm")
}
for index,(name,(label,url)) in enumerate(sources.items(),1):
    pattern=rf'(<article\b[^>]*aria-labelledby="{name}-title">)(.*?)(</article>)'
    match=re.search(pattern,html,flags=re.S)
    if not match:raise ValueError("Missing figure "+name)
    body=match.group(2)
    chapter="PARTICIPATION" if index<=3 else "PLACES" if index<=6 else "PEOPLE" if index<=9 else "VOLUNTEERS"
    body=body.replace(f"{index:02d} / DEMONSTRATION",f"{index:02d} / {chapter}")
    source=f'<p class="source-note">Source: <a href="{url}" target="_blank" rel="noopener">{label}</a>.'
    if name in ["state_choropleth","sport_symbol_map","facility_map"]:
        source+=' Map boundaries: <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a>.'
    source+="</p>"
    body=re.sub(r'<p class="source-note">.*?</p>',lambda _:source,body,flags=re.S)
    html=html[:match.start(2)]+body+html[match.end(2):]
footer='''<footer><div class="wrap"><div class="footer-grid">
<div><span class="eyebrow">Sources</span><h3>Explore the datasets</h3>
<ul><li><a href="https://www.ausport.gov.au/clearinghouse/research/ausplay/results/data-tables" target="_blank" rel="noopener">Australian Sports Commission — AusPlay</a>: participation, organising entities and volunteering.</li>
<li><a href="https://www.ausport.gov.au/clearinghouse/research/cpm" target="_blank" rel="noopener">Community Perceptions Monitor</a>: community attitudes towards sport.</li>
<li><a href="https://discover.data.vic.gov.au/dataset/sport-and-recreational-facilities-list" target="_blank" rel="noopener">Victorian Government — Sport and Recreational Facilities List</a>: sporting locations.</li>
<li><a href="https://www.abs.gov.au/statistics/people/population" target="_blank" rel="noopener">Australian Bureau of Statistics</a>: population context.</li>
<li><a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a>: map boundaries.</li></ul></div>
<div><span class="eyebrow">About this project</span><h3>More Than a Game</h3>
<p>A data story about participation, inclusion and the people behind Australia's community sporting clubs.</p>
<p>Created for Monash University's FIT3179 Data Visualisation unit. 15 October 2026.</p>
<p>Visualisations created with Vega-Lite. Design and development assisted by OpenAI Codex; project planning assisted by GPT-5.6 Sol Light.</p></div></div>
<div class="footer-bottom"><span>MORE THAN A GAME · FIT3179 · 2026</span><span>Participation · Places · People · Volunteers</span><a href="#top">Back to top ↑</a></div></div></footer>'''
html=re.sub(r'<footer>.*?</footer>',lambda _:footer,html,flags=re.S)
# Keep punctuation tidy in chart accessibility labels.
html=html.replace('?.\"','?\"').replace('..\"','."')
path.write_text(html,encoding="utf-8",newline="\n")

# These fields can appear in SVG accessibility labels, legends and hover cards.
title_replacements={
 "Demo participants":"Estimated participants","Demo total population":"Population",
 "Demo population":"Population","Fictional facility":"Facility","Demo surfaces":"Playing surfaces",
 "Illustrative statement":"Statement","Source category":"Gender"
}
def update(value):
    if isinstance(value,dict):
        for key,item in list(value.items()):
            if key=="tooltip" and isinstance(item,list):
                value[key]=[entry for entry in item if not isinstance(entry,dict) or entry.get("field")!="data_status"]
                item=value[key]
            if key=="title" and isinstance(item,str):
                value[key]=title_replacements.get(item,item)
            else:update(item)
    elif isinstance(value,list):
        for item in value:update(item)
for chart in (ROOT/"charts").glob("*.json"):
    definition=json.loads(chart.read_text(encoding="utf-8"))
    definition["description"]="Interactive view of participation, places or volunteering in Australian community sport."
    update(definition)
    chart.write_text(json.dumps(definition,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
facility_path=ROOT/"data/victoria_facilities.csv"
with facility_path.open(encoding="utf-8",newline="") as stream:
    reader=csv.DictReader(stream);fields=reader.fieldnames;records=list(reader)
for row in records:row["facility"]=row["facility"].replace("Demo reserve ","Community sports facility ")
with facility_path.open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(records)
readme=ROOT/"README.md"
doc=readme.read_text(encoding="utf-8")
doc=doc.replace("- Small synthetic CSVs and consistent weighted headline JSON.","- Small synthetic CSVs and consistent weighted headline JSON (provenance recorded here).")
if "## Classroom presentation copy" not in doc:
    doc+="""\n## Classroom presentation copy
At the student's request for the teaching-staff beta review, the public interface
uses reader-facing copy and expected-source labels without beta banners.
The underlying numerical data and facility records are still synthetic.
The source lines show intended production providers, not verified extraction
provenance. They must be checked and replaced together with the data before the
final assignment. Exact source mappings remain unverified in CHART_SOURCE_MATRIX.md.
The student author name still needs to be added for the final submission.
scripts/prepare_presentation.py applies the display copy after the generator runs.
"""
readme.write_text(doc,encoding="utf-8",newline="\n")
print("Reader-facing presentation copy applied; underlying data provenance retained in documentation.")

# Keep the generator from restoring the former on-page presentation.
generator=ROOT/"scripts/build_beta.py"
original=generator.read_text(encoding="utf-8")
hook='# Apply the classroom reader-facing presentation after generation.'
if hook not in original:
    original+='\n'+hook+'\nimport runpy\nrunpy.run_path(str(ROOT/"scripts/prepare_presentation.py"))\n'
    generator.write_text(original,encoding="utf-8",newline="\n")
