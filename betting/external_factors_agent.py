"""
External Factors Research Agent
================================================================================
On-demand research agent for any two-team matchup — team names are always
passed in as arguments, nothing is hardcoded. Stats-based predictors
(pretournament_predictor.py etc.) only see numeric team strength — they can't
know that a given team has beaten its opponent the last 4 times they've met,
or that a match in Mexico City is played at ~7,000ft altitude. This script
fills that gap for one matchup at a time:

  1. Grok (via xAI's live web/X search) researches the matchup: head-to-head
     history, recent form, injuries, travel/altitude/venue conditions,
     storylines.
  2. Gemini cross-checks Grok's findings and turns them into a bounded,
     structured win-probability adjustment — a second model acting as a
     skeptic guards against over-weighting a vivid but minor anecdote.

Usage:
    py external_factors_agent.py "Norway" "Brazil" --context "2026 World Cup"
    py external_factors_agent.py "Mexico" "Poland" --round "Round of 32"

Pass --as-of-date (or --round, which maps to a date via ROUND_CUTOFFS below)
to restrict research to information published before that date — otherwise
Grok's live search will happily cite the actual final score, which defeats
the point of a genuine pre-match prediction test.

Requires XAI_API_KEY and GOOGLE_API_KEY (see .env.example). Reports are
saved to external_factors_reports/ and can be picked up automatically by
predictors via load_adjustment(team_a, team_b).
"""

import argparse
import json
import os
import re
import time
import requests
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "external_factors_reports")
ADJUSTMENT_CAP_PCT = 15.0  # max magnitude of a win-probability nudge, in percentage points

# Day before each round's matches begin (2026 World Cup schedule). Used as a
# search cutoff so research for a round can't see that round's own results or
# any later round — e.g. Round of 16 research can see Round of 32 results
# (already happened) but not Round of 16 or Quarterfinal results.
ROUND_CUTOFFS = {
    "Round of 32": "2026-06-27",
    "Round of 16": "2026-07-03",
    "Quarterfinals": "2026-07-08",
    "Semifinals": "2026-07-13",
    "Final": "2026-07-18",
}


def _safe_name(team):
    return re.sub(r"[^A-Za-z0-9]+", "_", team).strip("_")


def _report_path(team_a, team_b, fixture_id=None):
    """
    fixture_id disambiguates repeat meetings between the same two teams
    (club leagues play home-and-away every season, unlike a single-
    elimination bracket where a pairing happens at most once). Defaults to
    None so existing World Cup-style callers keep using the original
    team-pair-only filename, unaffected.
    """
    base = f"{_safe_name(team_a)}_vs_{_safe_name(team_b)}"
    if fixture_id:
        base += f"_{_safe_name(str(fixture_id))}"
    return os.path.join(REPORTS_DIR, f"{base}.json")


# Grok's web_search tool has no verified native date cutoff — the prompt-level
# "only use info before X" instruction reduces but doesn't reliably prevent
# result-revealing pages from being fetched and cited. This is a second,
# deterministic filter: drop any source or sentence whose text matches these
# outcome-revealing patterns, applied regardless of what the prompt asked for.
SPOILER_KEYWORDS = [
    "eliminated", "eliminate", "upset", "shock win", "shocks ", "stun ",
    "stuns ", "stunned", "advance to", "advances to", "advanced to",
    "progress to", "progresses to", "knocked out", "crash out", "crashed out",
    "sent home", "book their place", "through to the", "reach the",
    "reached the", "wins on penalties", "win on penalties",
    "penalty shootout win", "final score", "the result was", "won the match",
    "lost the match", "defeat ", "defeated", "victory over", "beat ",
    "beats ", "review and highlights", "match report and highlights",
]


def _contains_spoiler(text):
    # normalize URL/title separators (-, _, /) to spaces so hyphenated slugs
    # like "stun-germany-advance-round-of-16" match the same as prose text
    lowered = re.sub(r"[-_/]+", " ", text.lower())
    return any(kw in lowered for kw in SPOILER_KEYWORDS)


def _filter_spoiler_sources(sources):
    kept, dropped = [], []
    for s in sources:
        haystack = f"{s.get('title') or ''} {s.get('url') or ''}"
        (dropped if _contains_spoiler(haystack) else kept).append(s)
    return kept, dropped


def _filter_spoiler_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept = [s for s in sentences if not _contains_spoiler(s)]
    return " ".join(kept), len(sentences) - len(kept)


# ---------------------------------------------------------------
# 1. Grok research pass (xAI live web/X search)
# ---------------------------------------------------------------
def research_with_grok(team_a, team_b, context=None, as_of_date=None, model=None):
    model = model or os.getenv("GROK_MODEL", "grok-4")
    api_key = os.environ["XAI_API_KEY"]

    context_line = f" Context: {context}." if context else ""
    cutoff_line = ""
    if as_of_date:
        cutoff_line = (
            f" IMPORTANT: This is a pre-match prediction test as of {as_of_date}. "
            f"Only use information published before {as_of_date}. Do not use, "
            f"state, or hint at the actual result of this match or of any match "
            f"played on or after {as_of_date} — if your search turns up the "
            f"outcome, ignore it and rely only on information that was known "
            f"before that date."
        )
    prompt = (
        f"Research the soccer match between {team_a} and {team_b}."
        f"{context_line}{cutoff_line} Search the web for factors beyond raw "
        "team strength that could affect the outcome: head-to-head history "
        "(especially in major tournaments), recent form/results, injuries or "
        "suspensions to key players, travel distance/fatigue, venue "
        "conditions (altitude, climate, pitch), crowd/home advantage, and "
        "any other notable storylines. Be specific with numbers and dates "
        "where you find them, and note where each fact comes from."
    )

    # xAI's older `search_parameters` chat-completions field was deprecated in
    # favor of the Agent Tools API (POST /v1/responses with a `tools` array).
    payload = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search"}, {"type": "x_search"}],
    }

    response = requests.post(
        "https://api.x.ai/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()

    raw_text_parts = []
    sources = []
    seen_urls = set()
    for item in data.get("output", []):
        for block in item.get("content", []) or []:
            if block.get("type") == "output_text":
                raw_text_parts.append(block.get("text", ""))
        for src in (item.get("action", {}) or {}).get("sources", []) or []:
            url = src.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({"url": url, "title": src.get("title")})

    raw_text = "".join(raw_text_parts).strip()
    clean_sources, dropped_sources = _filter_spoiler_sources(sources)
    clean_text, dropped_sentences = _filter_spoiler_sentences(raw_text)

    if dropped_sources or dropped_sentences:
        print(f"  [spoiler filter] dropped {len(dropped_sources)} result-revealing "
              f"source(s) and {dropped_sentences} sentence(s) for {team_a} vs {team_b}")

    return {
        "raw_text": clean_text,
        "sources": clean_sources,
        "spoiler_sources_dropped": [s["url"] for s in dropped_sources],
    }


# ---------------------------------------------------------------
# 2. Gemini cross-check / structuring pass
# ---------------------------------------------------------------
def analyze_with_gemini(raw_findings, team_a, team_b, as_of_date=None, model=None):
    from google import genai

    model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    cutoff_line = (
        f"\nThis is a pre-match prediction test as of {as_of_date}. If the "
        f"notes below leak the actual result of this match (or of any match "
        f"on/after {as_of_date}), ignore that specific fact entirely — do not "
        f"let it influence adjustment_pct, favors, or reasoning. Base your "
        f"analysis only on information that would have been known before "
        f"{as_of_date}.\n"
        if as_of_date else ""
    )

    prompt = f"""You are a skeptical sports analyst cross-checking a colleague's
research notes before they get used to adjust a statistical model's prediction.

Matchup: {team_a} vs {team_b}
{cutoff_line}
Research notes:
\"\"\"
{raw_findings}
\"\"\"

Return ONLY valid JSON (no markdown fences, no commentary) with this exact shape:
{{
  "adjustment_pct": <float between -{ADJUSTMENT_CAP_PCT:.0f} and {ADJUSTMENT_CAP_PCT:.0f}, positive favors {team_a}, negative favors {team_b}>,
  "favors": "<'{team_a}', '{team_b}', or 'neutral'>",
  "confidence": "<low|medium|high>",
  "factors": [{{"factor": "...", "impact": "..."}}],
  "reasoning": "..."
}}

Be conservative: most matchups should get a small adjustment (0-5). Only go
beyond 10 for strong, well-documented patterns (e.g. a team that has
genuinely dominated a head-to-head series across multiple meetings, or a
well-established extreme-altitude/travel effect). Do not invent facts that
aren't in the notes above. If the notes are thin or inconclusive, return a
small adjustment and "confidence": "low"."""

    response = None
    for attempt in range(4):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            break
        except Exception as e:
            if attempt == 3:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"  [gemini retry] {type(e).__name__} — retrying in {wait}s (attempt {attempt + 1}/4)...")
            time.sleep(wait)

    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())

    data = json.loads(text)
    adj = float(data.get("adjustment_pct", 0.0))
    data["adjustment_pct"] = max(-ADJUSTMENT_CAP_PCT, min(ADJUSTMENT_CAP_PCT, adj))
    return data


# ---------------------------------------------------------------
# 3. Orchestration + persistence
# ---------------------------------------------------------------
def get_matchup_report(team_a, team_b, context=None, as_of_date=None, fixture_id=None):
    research = research_with_grok(team_a, team_b, context=context, as_of_date=as_of_date)
    analysis = analyze_with_gemini(research["raw_text"], team_a, team_b, as_of_date=as_of_date)

    report = {
        "team_a": team_a,
        "team_b": team_b,
        "context": context,
        "as_of_date": as_of_date,
        "fixture_id": fixture_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research": research,
        "analysis": analysis,
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(_report_path(team_a, team_b, fixture_id), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def has_report(team_a, team_b, fixture_id=None):
    return (os.path.exists(_report_path(team_a, team_b, fixture_id))
            or os.path.exists(_report_path(team_b, team_a, fixture_id)))


def clean_existing_reports():
    """
    Re-applies the spoiler filter to every already-saved report's sources and
    raw_text, in place, with no new API calls. Useful after tightening
    SPOILER_KEYWORDS, or for reports generated before the filter existed.
    """
    if not os.path.isdir(REPORTS_DIR):
        print("No reports directory found.")
        return
    for fname in sorted(os.listdir(REPORTS_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(REPORTS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)
        research = report.get("research", {})
        sources = research.get("sources", [])
        raw_text = research.get("raw_text", "")

        clean_sources, dropped_sources = _filter_spoiler_sources(sources)
        clean_text, dropped_sentences = _filter_spoiler_sentences(raw_text)

        if not dropped_sources and not dropped_sentences:
            print(f"  {fname}: clean")
            continue

        research["sources"] = clean_sources
        research["raw_text"] = clean_text
        research["spoiler_sources_dropped"] = (
            research.get("spoiler_sources_dropped", []) + [s["url"] for s in dropped_sources]
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"  {fname}: dropped {len(dropped_sources)} source(s), {dropped_sentences} sentence(s)")


def load_adjustment(team_a, team_b, fixture_id=None):
    """
    Returns a win-probability adjustment for team_a (as a fraction, e.g. 0.05
    means +5 percentage points for team_a), or 0.0 if no saved report exists
    for this pairing/fixture. Order-independent — flips sign if the saved
    report was generated with the teams in the opposite order.
    """
    for path, flip in ((_report_path(team_a, team_b, fixture_id), False),
                        (_report_path(team_b, team_a, fixture_id), True)):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                report = json.load(f)
            adj_pct = report.get("analysis", {}).get("adjustment_pct", 0.0)
            adj = adj_pct / 100.0
            return -adj if flip else adj
    return 0.0


def print_report(report):
    team_a, team_b = report["team_a"], report["team_b"]
    analysis = report["analysis"]
    print("\n" + "=" * 70)
    print(f"EXTERNAL FACTORS REPORT — {team_a} vs {team_b}")
    if report.get("context"):
        print(f"Context: {report['context']}")
    if report.get("as_of_date"):
        print(f"As-of date (pre-match cutoff): {report['as_of_date']}")
    print("=" * 70)

    print(f"\nFavors: {analysis.get('favors')}  |  Confidence: {analysis.get('confidence')}")
    print(f"Suggested adjustment: {analysis.get('adjustment_pct'):+.1f} percentage points "
          f"(positive favors {team_a})")

    print("\nKey factors:")
    for f in analysis.get("factors", []):
        print(f"  - {f.get('factor')}: {f.get('impact')}")

    print(f"\nReasoning: {analysis.get('reasoning')}")

    sources = report.get("research", {}).get("sources", [])
    if sources:
        print("\nSources:")
        for s in sources:
            title = s.get("title") or s.get("url")
            print(f"  - {title} ({s.get('url')})")

    print(f"\nSaved to: {_report_path(team_a, team_b, report.get('fixture_id'))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Research external factors for a single matchup.")
    parser.add_argument("team_a", nargs="?")
    parser.add_argument("team_b", nargs="?")
    parser.add_argument("--context", default=None, help="e.g. '2026 World Cup Round of 32'")
    parser.add_argument("--round", dest="round_name", default=None, choices=list(ROUND_CUTOFFS),
                         help="Auto-fills --as-of-date from ROUND_CUTOFFS for this round.")
    parser.add_argument("--as-of-date", dest="as_of_date", default=None,
                         help="YYYY-MM-DD. Restrict research to info published before this date "
                              "(prevents the agent from seeing the actual result). Overrides --round.")
    parser.add_argument("--clean", action="store_true",
                         help="Re-apply the spoiler filter to all saved reports in place (no API calls) and exit.")
    args = parser.parse_args()

    if args.clean:
        clean_existing_reports()
        raise SystemExit(0)

    if not args.team_a or not args.team_b:
        parser.error("team_a and team_b are required unless --clean is used.")

    as_of_date = args.as_of_date or (ROUND_CUTOFFS.get(args.round_name) if args.round_name else None)
    context = args.context or args.round_name

    for var in ("XAI_API_KEY", "GOOGLE_API_KEY"):
        if not os.getenv(var):
            raise SystemExit(f"Missing {var}. Copy .env.example to .env and fill it in.")

    report = get_matchup_report(args.team_a, args.team_b, context=context, as_of_date=as_of_date)
    print_report(report)
