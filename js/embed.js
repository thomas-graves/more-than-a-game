
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
