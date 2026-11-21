# Engine patch — five new project types (prepared 21 Nov 2026, not yet applied)

The engine (Supabase Edge Function `swift-actionwacc`, v1.4) is not in this repo. This note is the change to make
there BEFORE the `project-types` branch is merged: the form on that branch sends five new `sector` values.

## 1. Sector map — add these entries next to ports / logistics / zones / marine

| `sector` value | Label | Damodaran industries (exact "Industry Name") |
| --- | --- | --- |
| `efficiency` | Energy efficiency | `Engineering/Construction`, `Electrical Equipment` |
| `energy` | Energy production | `Power`, `Green & Renewable Energy` |
| `oilgas` | Oil & gas services | `Oilfield Svcs/Equip.` |
| `mining` | Mining | `Metals & Mining`, `Precious Metals` |
| `agrifood` | Agrifood | `Farming/Agriculture`, `Food Processing` |

Names were read on 21 Nov 2026 from Damodaran's US and global beta pages (Betas.html, BetasGlobal.html, data as of
January 2026) and are spelled the same in both. Mind the trailing period in `Oilfield Svcs/Equip.`, the spaces
around `&` and no spaces around `/`.

Global unlevered betas corrected for cash, as read that day (firms): Engineering/Construction 0.76 (1390),
Electrical Equipment 1.34 (1158), Power 0.46 (486), Green & Renewable Energy 0.57 (258), Oilfield Svcs/Equip. 0.80
(431), Metals & Mining 1.13 (1874), Precious Metals 1.37 (777), Farming/Agriculture 0.49 (428), Food Processing 0.56
(1450). Use them only to sanity-check the first live run — the engine reads the live file.

## 2. Other places in the engine to check
- Any list of allowed `sector` values (input validation) — add the five keys.
- The agent prompt: wherever it names the four project types or asks for a "sector tax regime", make sure it also
  covers the new ones (mining and oil & gas often have their own tax codes and royalties; agrifood often has a
  reduced rate; energy production often has tax holidays). Shown, not applied — same rule as today.
- How two industries are combined for a sector (keep the existing rule used for logistics and zones).

## 3. Caveats
- Energy efficiency has no listed peer group of its own; the two industries are a proxy and give a high beta
  (0.76 and 1.34). Consider a sector note in the result saying so.
- Energy production mixes conventional and renewable power; could be split into two types later.
- Mining leaves out `Coal & Related Energy` (global 1.13).

## 4. Order of deployment
1. Patch and deploy the engine. 2. Run one estimate per new type. 3. Merge `project-types` into main.
