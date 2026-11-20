@echo off
rem Daily betting pipeline: snapshot prices and injuries, then scan for signals.
rem Scheduled via Task Scheduler 3x/day; ~4 Odds API credits per run
rem (one per sport in log_prices DEFAULT_SPORTS: EPL, World Cup, MLS, NBA).
rem nba_injuries.py costs no API credits (ESPN is free) and must run daily:
rem ESPN publishes only the CURRENT report, so a run missed is history lost.
rem Output appends to daily_run.log next to this script.
cd /d "%~dp0"
echo ================ %date% %time% ================ >> daily_run.log
rem Preflight first: a collector that fails silently looks like "no
rem opportunities today" forever. This prints why, and exits 1 on a blocker.
py check_setup.py --quiet >> daily_run.log 2>&1
py log_prices.py >> daily_run.log 2>&1
py nba_injuries.py --snapshot >> daily_run.log 2>&1
rem News wire, all sports. Free (ESPN), so it costs no Odds API credits.
rem NOTE: 3x/day is enough to COLLECT but far too slow to trade on or to
rem measure feed latency -- an item can never be seen sooner than the polling
rem interval. For a speed edge, schedule news_watch.py separately every 5-15
rem minutes on game days: py news_watch.py --loop 10
py news_watch.py >> daily_run.log 2>&1
py analyze_prices.py --alert --paper-log >> daily_run.log 2>&1
rem One DRY trading pass: simulated fills against the live book, positions
rem logged to the positions table. Never live from here -- going live needs
rem --live AND POLYMARKET_LIVE=1 AND a key, deliberately. For the real
rem strategy cadence run it as its own loop: py trader.py --loop 60
py trader.py --once --quiet >> daily_run.log 2>&1
rem Pre-registered tennis favorites paper test (free: Gamma + CLOB only).
rem PM lists tennis ~1 day out, so 3x daily catches nearly every listing.
py tennis_favorites.py >> daily_run.log 2>&1
