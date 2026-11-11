# Harbourline WACC — weekly reference-data update (for the scheduled task)

Goal: refresh the stored inputs of the WACC app (https://wacc.harbourlineatlas.com) so every estimate uses data
checked within the week. The file you push is imported into the Supabase table `market_snapshots` by the repo's
GitHub Action.

1. Clone github.com/telfarouki/harbourline-wacc (add_repo with push access, then git clone). Read research/SCHEMA.md
   and countries.js. Find the newest file in weekly/ (ignore README.md) — that is LAST WEEK's file, the starting point.
   If there is none, this is the first (seed) run: every country must be researched in full.
2. Global block: WebFetch https://fred.stlouisfed.org/series/DGS10 for the latest US 10-year yield and its date;
   WebFetch Damodaran's ctryprem.html for the update date and the mature-market implied ERP.
3. Run 7 research agents in parallel, one per group:
   (g1) North & West Africa I: DZA EGY LBY MAR MRT TUN BEN BFA CPV CIV GMB GHA GIN GNB
   (g2) West & Central Africa: LBR MLI NER NGA SEN SLE TGO CMR CAF TCD COG COD GNQ GAB
   (g3) East Africa & Horn: BDI COM DJI ERI ETH KEN MDG MUS RWA SYC SOM SSD SDN TZA
   (g4) Southern Africa and others: UGA AGO BWA SWZ LSO MWI MOZ NAM ZAF ZMB ZWE STP
   (g5) Middle East: BHR IRN IRQ ISR JOR KWT LBN OMN PSE QAT SAU SYR TUR ARE YEM
   (g6) Central & South Asia, Caucasus: AFG ARM AZE BGD GEO IND KAZ KGZ PAK LKA TJK TKM UZB
   (g7) Other markets: AUS BRA CAN CHL DOM ECU IDN KOR PER PHL ROU SRB GBR VNM
   Each agent receives last week's entries for its countries and research/SCHEMA.md, and must:
   - seed run: fill every field for every country;
   - later runs: search for sovereign rating actions (Moody's, S&P, Fitch) and corporate-tax changes in the last
     10 days, refresh the Eurobond yield, and re-verify in full any country whose `checked` date is older than
     90 days (oldest first, at least 3 countries per group each week). Unchanged countries keep last week's values.
   - write its countries as a JSON object {ISO3: entry} to a temp file, plus a list of changes.
4. Merge into weekly/<ISO year>-W<ISO week>.json (ISO week of today, Dubai date). Overwrite if it exists.
   Run `python3 scripts/validate.py weekly/<file>` and fix everything it reports until it prints OK.
5. git add weekly/<file>; commit "Weekly data <week>"; git push origin main. The "Import weekly data" Action then
   loads it into Supabase. Wait ~60 s and check `gh run list --repo telfarouki/harbourline-wacc --limit 1`;
   if it failed, read the log and report the error (a missing SUPABASE_URL / SUPABASE_SERVICE_KEY secret or a missing
   market_snapshots table are the likely causes — say which).
6. Final report (under 15 lines): countries covered, the changes list (rating/outlook moves, tax changes), US 10-year
   and the move since last week, countries with missing data. Send it with SendUserMessage.
If the push is refused: send the JSON file to the user and say it can be uploaded to the weekly/ folder of the repo.
