# Chart-to-source matrix — beta working draft
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
