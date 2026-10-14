"""Browser QA. Uses Playwright and installed Chrome (no browser download).
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
