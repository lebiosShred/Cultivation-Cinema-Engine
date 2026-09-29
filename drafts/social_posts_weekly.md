# Weekly Social Media Campaign (Octane Solutions)

Author: Amiel Lebios  
Portal ID: 2926400  
HubSpot Social Tool: https://app.hubspot.com/social/2926400  

All posts are written to eliminate AI slop, pass the Tavern Test, and target senior finance leaders, TM1 developers, and FP&A architects.

================================================================================
POST 1: TUESDAY - ENGINE 12 MIGRATION
Scheduled Time: Tuesday, September 15, 2026 at 8:45 AM AEST
Blog Link: https://blog.octanesolutions.com.au/planning-analytics-engine-12-migration-checklist
================================================================================

### LinkedIn Post Copy:
If your enterprise is preparing to move to IBM Planning Analytics Engine 12, here is a technical reality check:

You cannot just copy over your old tm1s.cfg and expect Monday morning to run smoothly.

In Engine 12, TM1 is no longer a monolithic Windows service. It runs inside isolated Linux containers on cloud object storage.

That means:
1. Every ExecuteCommand TI script calling Windows .bat or PowerShell will abort immediately with error code 0x80004005.
2. Mapped drive paths (\\fileserver\actuals.csv) will throw file-not-found exceptions.
3. Giant .feeders files stored in S3 can create network startup bottlenecks instead of speeding up boots.

We put together a comprehensive, hour-by-hour pre-cutover checklist based on real migrations. It covers REST API orchestration, alternate hierarchy consolidation, and the exact rollback safety rules you need before cutover weekend.

Read the full technical migration guide:
https://blog.octanesolutions.com.au/planning-analytics-engine-12-migration-checklist

#IBMPlanningAnalytics #TM1 #FinanceTransformation #CloudMigration #CFO #FPandA

---

### Twitter / X Post Copy:
Planning your IBM Planning Analytics Engine 12 migration?

Watch out for container lockouts: legacy ExecuteCommand batch scripts will fail immediately with 0x80004005.

Here is our pre-cutover architecture guide and weekend checklist:
https://blog.octanesolutions.com.au/planning-analytics-engine-12-migration-checklist

#TM1 #IBMCloud #FPandA


================================================================================
POST 2: WEDNESDAY - TM1 OUT OF MEMORY FIX
Scheduled Time: Wednesday, September 16, 2026 at 1:15 PM AEST
Blog Link: https://blog.octanesolutions.com.au/tm1-out-of-memory-fix
================================================================================

### LinkedIn Post Copy:
Nothing causes more panic during budget season than a TM1 server crashing with Out of Memory errors right before board review.

Adding more RAM only treats the symptom.

Here is a number from a recent client audit:
A 64 GB TM1 server was constantly crashing. When we opened }StatsByCube, the fed-to-populated ratio in their sales forecast cube was 185:1.

That single cube was wasting 38 GB of physical RAM holding empty memory flags.

10 million numbers only take roughly 80 MB of physical memory. The crash comes from overfeeding, unconstrained view caches, and heap fragmentation.

In our latest guide, we break down:
- The exact crash signature in tm1server.log
- A copy-pasteable TurboIntegrator audit script to detect overfed cubes automatically
- The 3 feeder traps that kill server performance (and how to fix them)
- Key tm1s.cfg settings like MaximumMemoryFromCPUAddressSpacePercentage to prevent rogue queries from killing your instance

Read the complete diagnostic playbook:
https://blog.octanesolutions.com.au/tm1-out-of-memory-fix

#TM1 #IBMPlanningAnalytics #ModelOptimization #FPandA #FinanceSystems

---

### Twitter / X Post Copy:
Is your TM1 server running out of RAM during budget season?

10M numbers only take 80 MB of RAM. But bad feeders can bloat that to 40 GB+.

Here is our practical guide to fix runaway feeders, plus an automated TI audit script:
https://blog.octanesolutions.com.au/tm1-out-of-memory-fix

#TM1 #FPandA


================================================================================
POST 3: THURSDAY - POWER BI DATA DRIFT
Scheduled Time: Thursday, September 17, 2026 at 8:45 AM AEST
Blog Link: https://blog.octanesolutions.com.au/tm1-to-power-bi-eliminate-data-drift
================================================================================

### LinkedIn Post Copy:
Every CFO knows the uncomfortable feeling in a board meeting when the numbers on the Power BI dashboard do not match the numbers in TM1.

This is reporting drift.

In 9 out of 10 finance teams, it happens because of brittle intermediate CSV dumps:
- A late journal entry is posted in TM1 at 6:15 PM.
- The Power BI Gateway refreshed at 5:00 PM based on an afternoon file export.
- Or worse: the refresh fails completely because TM1 is still writing the CSV file when Power BI tries to read it.

You can eliminate this entirely by connecting Power BI directly to the TM1 REST API.

In this practical guide, we share:
1. The exact Power Query M script to query TM1 cubes over HTTPS without flat files.
2. A 3-tier incremental refresh partition strategy (history vs daily actuals vs dynamic rolling forecast).
3. Automated DAX measures to tie out balances dollar-for-dollar in real time.

Read the guide and grab the Power Query M script:
https://blog.octanesolutions.com.au/tm1-to-power-bi-eliminate-data-drift

#PowerBI #TM1 #IBMPlanningAnalytics #BusinessIntelligence #FPandA #DataGovernance

---

### Twitter / X Post Copy:
Tired of Power BI dashboards disagreeing with your TM1 cubes at month-end?

Stop relying on scheduled CSV exports to shared drives. Connect Power BI directly to TM1 via the REST API:
https://blog.octanesolutions.com.au/tm1-to-power-bi-eliminate-data-drift

#PowerBI #TM1 #FPandA


================================================================================
POST 4: FRIDAY - TM1 VS ANAPLAN COMPARISON
Scheduled Time: Friday, September 18, 2026 at 8:45 AM AEST
Blog Link: https://blog.octanesolutions.com.au/tm1-vs-anaplan-real-world-comparison
================================================================================

### LinkedIn Post Copy:
Choosing between IBM Planning Analytics (TM1) and Anaplan is one of the biggest software decisions a finance leader will make.

Both promise fast planning, but their underlying calculation engines are completely different.

Here is the unvarnished engineering comparison:

1. Sparse Arrays vs Hyperblock:
In a 10-dimension P&L model with 500 million potential intersections, TM1 only calculates and stores the 1.2 million non-zero cells. It uses roughly 110 MB of RAM. In Anaplan, deep list hierarchies can explode memory past the 100 GB workspace limit.

2. Complex Allocations:
In a benchmark stepped allocation test across 80 business units, TM1 TurboIntegrator completed the run in 42 seconds. An equivalent Anaplan model with 14 chained modules took 8 minutes of recalculation.

3. The Excel Reality:
Planning Analytics for Excel (PAfE) offers active, bi-directional formula modeling with DBRW. The Anaplan Excel Add-in is primarily an import/export connector.

We broke down real calculation benchmarks, Excel workflows, and a 3-year Total Cost of Ownership model for Australian enterprises.

Read the full comparison before your next steering committee meeting:
https://blog.octanesolutions.com.au/tm1-vs-anaplan-real-world-comparison

#IBMPlanningAnalytics #Anaplan #TM1 #FPandA #CFO #EnterpriseSoftware

---

### Twitter / X Post Copy:
Evaluating IBM Planning Analytics (TM1) vs Anaplan for enterprise finance?

We compared calculation engines, stepped allocation speeds, Excel workflows, and 3-year TCO.

Here is the unvarnished breakdown:
https://blog.octanesolutions.com.au/tm1-vs-anaplan-real-world-comparison

#TM1 #Anaplan #FPandA
