"""Survivorship-bias-free S&P 500 daily dataset: point-in-time membership + adjusted prices, 2010 -> today.

Sources (all free):
  membership  fja05680/sp500 "Historical Components & Changes (Updated).csv" (ticker-as-of-date lists, to
              2026-08-18) + TAIL below (later changes, from Wikipedia edit summaries), cross-checked against
              Wikipedia "List of S&P 500 companies": the current table and the "Selected changes" table
              (revision 1368675864, 2026-08-10, the last one that still had it).
  identity    a company keeps one id (its latest ticker) across renames: Alpaca corporate-action name
              changes (FB->META, ...) and fja same-day swaps that Wikipedia does not explain and Alpaca
              prices show to be one continuous listing.
  prices      Alpaca SIP daily bars, adjustment=all (history starts 2016-01-04; delisted names included).
              yfinance fills pre-2016 only for symbols whose yfinance series matches Alpaca in Q1 2016.

  python universe_data.py     # download (cached in data/universe/), build, write reports/universe_data_quality.md
  from universe_data import load_universe; prices, member = load_universe()

Pickles in data/universe/ are this script's own local caches (not untrusted input).
"""
import io
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).parent
D = ROOT / 'data' / 'universe'
START = '2010-01-01'
ALP0 = pd.Timestamp('2016-01-04')  # first Alpaca daily bar (checked: start=2010 returns nothing earlier)
LOOKBACK = pd.Timedelta(days=400)  # price history kept before a company's first membership day
FJA = 'https://raw.githubusercontent.com/fja05680/sp500/master/S%26P%20500%20Historical%20Components%20%26%20Changes%20(Updated).csv'
WIKI = 'https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies'
WIKI_OLDID = 1368675864  # last revision with the "Selected changes" table
UA = {'User-Agent': 'Mozilla/5.0 (research script)'}
ALP = 'https://data.alpaca.markets'
# Index changes after fja's last row (2026-08-18), from Wikipedia edit summaries 2026-09-20..11-04.
# build() asserts the result equals Wikipedia's current table; extend this when it fails.
TAIL = [('2026-09-21', {'BE', 'P', 'ILMN'}, {'TAP', 'TTD', 'BLDR'}),
        ('2026-10-01', {'VYLR'}, set()),
        ('2026-10-06', {'TWLO', 'SKYD'}, {'CTVA', 'WBD', 'PSKY'}),  # PSKY->SKYD is a rename
        ('2026-11-04', {'OKTA'}, {'KVUE'})]
# fja ticker -> [(Alpaca symbol, from, to)]: bars to use for part of a spell. fja labels these companies with
# a later ticker for the whole spell while Alpaca keeps the earlier bars under the old symbol (renames before
# 2017-04, where Alpaca's name-change feed starts), or the symbol passed to a spun-off company.
OVERRIDES = {'AABA': [('YHOO', None, '2017-06-16')],   # Yahoo -> Altaba
             'ANDV': [('TSO', None, '2017-07-31')],    # Tesoro -> Andeavor
             'APTV': [('DLPH', None, '2017-12-04')],   # Delphi Automotive -> Aptiv (DLPH reused by the spin-off)
             'BHGE': [('BHI', None, '2017-07-03')],    # Baker Hughes Inc -> BHGE (bars from 2017-07 under BKR)
             'UAA': [('UA', None, '2016-04-07')],      # Under Armour class split (UA became class C)
             'ARNC': [('HWM', '2020-04-01', None)],
             # Paramount's 2022-02..2025-08 bars are not in Alpaca: its PARA series is the later PARA (ex-BNZI)
             'PARA': [('yf:SKYD', None, None)]}    # Arconic Inc -> Howmet; ARNC passed to spun-off Arconic Corp


def _cached(name, url, params=None):
    p = D / name
    if not p.exists():
        D.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, params=params, headers=UA, timeout=60)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def _alpaca_headers():
    env = dict(l.strip().split('=', 1) for l in open(ROOT / '.env') if '=' in l)
    return {'APCA-API-KEY-ID': env['ALPACA_API_KEY'], 'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY']}


def _alpaca_get(path, params, H):
    for attempt in range(5):
        time.sleep(0.4)  # <= 150 req/min, under the 200/min limit
        r = requests.get(ALP + path, headers=H, params=params, timeout=60)
        if r.status_code == 429:
            time.sleep(10 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f'Alpaca {path} kept returning 429')


# ---------------------------------------------------------------- sources
def fja_rows():
    """date -> set of tickers (ticker as of that date), from fja05680/sp500."""
    f = pd.read_csv(_cached('fja_hist.csv', FJA), parse_dates=['date'])
    return {d: set(t.split(',')) for d, t in zip(f.date, f.tickers)}


def wiki_tables():
    cur = pd.read_html(io.StringIO(_cached('wiki_current.html', WIKI).read_text('utf-8')))[0]
    old = pd.read_html(io.StringIO(_cached('wiki_20260810.html', WIKI, {'oldid': WIKI_OLDID}).read_text('utf-8')))[1]
    old.columns = ['date', 'add', 'add_name', 'rem', 'rem_name', 'reason']
    old['date'] = pd.to_datetime(old['date'], format='mixed', errors='coerce')
    return cur, old.dropna(subset=['date'])


def alpaca_name_changes():
    p = D / 'alpaca_name_changes.csv'
    if not p.exists():
        H, rows = _alpaca_headers(), []
        for y in range(2016, pd.Timestamp.today().year + 1):
            for a, b in [('01-01', '06-30'), ('07-01', '12-31')]:
                tok = None
                while True:
                    q = dict(types='name_change', start=f'{y}-{a}', end=f'{y}-{b}', limit=1000)
                    if tok:
                        q['page_token'] = tok
                    j = _alpaca_get('/v1/corporate-actions', q, H)
                    rows += j['corporate_actions'].get('name_changes', [])
                    tok = j.get('next_page_token')
                    if not tok:
                        break
        pd.DataFrame(rows).to_csv(p, index=False)
    nc = pd.read_csv(p, parse_dates=['process_date'])
    return nc[['old_symbol', 'new_symbol', 'process_date']].dropna()


def alpaca_bars(symbols, adjustment='all', cache='alpaca_bars.pkl'):
    """symbol -> DataFrame[close, volume] of SIP daily bars since START. Cached per symbol."""
    p = D / cache
    have = pd.read_pickle(p) if p.exists() else {}
    todo = sorted(set(symbols) - set(have))
    H = _alpaca_headers() if todo else None
    for i in range(0, len(todo), 50):
        chunk, tok, got = todo[i:i + 50], None, {}
        while True:
            q = dict(symbols=','.join(chunk), timeframe='1Day', start=START, feed='sip', adjustment=adjustment,
                     limit=10000)
            if tok:
                q['page_token'] = tok
            j = _alpaca_get('/v2/stocks/bars', q, H)
            for s, b in (j.get('bars') or {}).items():
                got.setdefault(s, []).extend(b)
            tok = j.get('next_page_token')
            if not tok:
                break
        for s in chunk:
            b = pd.DataFrame(got.get(s, []), columns=['t', 'c', 'v'])
            b.index = pd.to_datetime(b.t.str[:10])
            have[s] = b[['c', 'v']].rename(columns={'c': 'close', 'v': 'volume'})
        pd.to_pickle(have, p)
        print(f'  alpaca {min(i + 50, len(todo))}/{len(todo)}')
    return {s: have[s] for s in symbols}


def yf_closes(symbols, start=START, end='2016-03-31', cache='yf_closes.pkl'):
    """yfinance auto-adjusted closes (default 2010 .. 2016-03-31: pre-Alpaca fill + validation overlap)."""
    p = D / cache
    have = pd.read_pickle(p) if p.exists() else pd.DataFrame()
    todo = sorted(set(symbols) - set(have.columns))
    if todo:
        import yfinance as yf
        for i in range(0, len(todo), 100):
            chunk = todo[i:i + 100]
            x = yf.download([s.replace('.', '-') for s in chunk], start=start, end=end, auto_adjust=True,
                            progress=False, threads=True)['Close']
            x = x.reindex(columns=[s.replace('.', '-') for s in chunk])
            x.columns = chunk
            have = pd.concat([have, x], axis=1)
        pd.to_pickle(have, p)
    return have[list(symbols)]


# ---------------------------------------------------------------- helpers
def _spells(rows):
    """ticker -> list of [start, end) membership spells; end = first row date without it (None = still in)."""
    dates = sorted(rows)
    out, open_ = {}, {}
    for k, d in enumerate(dates):
        prev = rows[dates[k - 1]] if k else set()
        for t in rows[d] - prev:
            open_[t] = d
        for t in prev - rows[d]:
            out.setdefault(t, []).append((open_.pop(t), d))
    for t, s in open_.items():
        out.setdefault(t, []).append((s, None))
    return out


def _same_series(a, b, lo, hi, n=40):
    """True if two adjusted close series move together on [lo, hi] (same company, compatible adjustment)."""
    ov = a.index.intersection(b.index)
    ov = ov[(ov >= lo) & (ov <= hi)]
    if len(ov) < n:
        return None
    ra, rb = np.log(a[ov]).diff().dropna(), np.log(b[ov]).diff().dropna()
    return bool(ra.corr(rb) > 0.97 and (ra - rb).abs().quantile(0.95) < 0.005)


def _stitch(pieces):
    """Concatenate series pieces in time order, rescaling earlier pieces so levels join. If both pieces have a
    bar on the junction day the ratio there is exact; otherwise the junction return is taken as 0%."""
    pieces = [p for p in pieces if len(p)]
    if not pieces:
        return pd.Series(dtype=float)
    out = pieces[-1]
    for p in reversed(pieces[:-1]):
        j = out.index[0]
        f = out.iloc[0] / p[j] if j in p.index else out.iloc[0] / p[p.index < j].iloc[-1] if (p.index < j).any() else 1
        p = p[p.index < j]
        if len(p):
            out = pd.concat([p * f, out])
    return out


# ---------------------------------------------------------------- build
def build():
    rows = fja_rows()
    cur, chg = wiki_tables()
    log = {}

    # --- 1. extend fja with TAIL; must reproduce Wikipedia's current table
    last = max(rows)
    log['fja_last_row'] = str(last.date())
    s = set(rows[last])
    for d, add, rem in TAIL:
        if pd.Timestamp(d) > last:
            s = (s | add) - rem
            rows[pd.Timestamp(d)] = set(s)
    wiki_now = set(cur.Symbol)
    assert rows[max(rows)] == wiki_now, f'update TAIL: +{wiki_now - rows[max(rows)]} -{rows[max(rows)] - wiki_now}'
    dates = sorted(rows)

    def member_at(t, d):
        k = np.searchsorted(dates, d, 'right') - 1
        return k >= 0 and t in rows[dates[k]]

    # --- 2. cross-check against Wikipedia "Selected changes" since 2010
    all_t = set().union(*rows.values())
    chk = []
    for _, r in chg[chg.date >= START].iterrows():
        for kind, t in (('add', r['add']), ('rem', r['rem'])):
            if not isinstance(t, str):
                continue
            res = {}
            for k in (0, 7, 31):
                b, a = member_at(t, r.date - pd.Timedelta(days=k + 1)), member_at(t, r.date + pd.Timedelta(days=k))
                res[k] = (not b and a) if kind == 'add' else (b and not a)
            chk.append(dict(date=str(r.date.date()), kind=kind, ticker=t, exact=res[0], d7=res[7], d31=res[31],
                            in_fja=t in all_t))
    chk = pd.DataFrame(chk)
    log['wiki_check'] = dict(events=len(chk), exact=int(chk.exact.sum()), d7=int(chk.d7.sum()),
                             d31=int(chk.d31.sum()), ticker_not_in_fja=int((~chk.in_fja).sum()))
    log['wiki_mismatch'] = chk[~chk.d7].to_dict('records')

    # --- 3. identity links between consecutive spells (old ticker spell -> new ticker spell)
    sp = {t: [x for x in v if x[1] is None or x[1] > pd.Timestamp(START)] for t, v in _spells(rows).items()}
    sp = {t: v for t, v in sp.items() if v}
    nc = alpaca_name_changes()
    log['alpaca_name_change_first'] = str(nc.process_date.min().date())
    nc = nc[nc.old_symbol.isin(sp) & (nc.old_symbol != nc.new_symbol)]
    ren_all = {}
    for _, r in nc.iterrows():
        ren_all.setdefault(r.old_symbol, []).append((r.new_symbol, r.process_date))
    # a rename o->n while fja keeps o in the index (the symbol passed to a new member, e.g. IR->TT and
    # Gardner Denver took IR): split o's spell where n starts, so the old company continues as n
    log['spell_splits'] = []
    for o, v in ren_all.items():
        for n, r in v:
            ns = [aa for aa, _ in sp.get(n, []) if abs((aa - r).days) <= 10]
            for k, (a, c) in enumerate(sp[o]):
                if ns and a < ns[0] - pd.Timedelta(days=10) and (c is None or c > ns[0] + pd.Timedelta(days=10)):
                    sp[o][k:k + 1] = [(a, ns[0]), (ns[0], c)]
                    log['spell_splits'].append((o, n, str(ns[0].date())))
                    break
    starts = {}
    for t, v in sp.items():
        for a, c in v:
            starts.setdefault(a, []).append(t)
    # renames of a ticker while it was in the index (else the old symbol was a different, reused company)
    ren = {}
    for _, r in nc.iterrows():
        if any(a - pd.Timedelta(days=90) <= r.process_date <= (c or r.process_date) + pd.Timedelta(days=90)
               for a, c in sp[r.old_symbol]):
            ren.setdefault(r.old_symbol, []).append((r.new_symbol, r.process_date))
    wiki_d = {}
    for _, r in chg.iterrows():
        for t in (r['add'], r['rem']):
            if isinstance(t, str):
                wiki_d.setdefault(t, []).append(r.date)
    explained = lambda t, d: any(abs((x - d).days) <= 7 for x in wiki_d.get(t, []))

    syms = sorted(set(sp) | {n for v in ren_all.values() for n, _ in v} | {o[0] for v in OVERRIDES.values() for o in v if ':' not in o[0]}
                  | {'SPY'})
    valid = {k: b.loc[b.volume > 0, 'close'] for k, b in alpaca_bars(syms).items()}  # volume 0 = stale bar

    links, cand = {}, []
    for o, v in sp.items():
        for a, c in v:
            if c is None:
                continue
            news = [n for n in starts.get(c, []) if n != o]
            hit = [n for n, r in ren.get(o, []) if n in news and abs((r - c).days) <= 90]
            if hit:
                links[(o, a)] = (hit[0], c, 'alpaca rename')
                continue
            outs = [t for t, vv in sp.items() if any(cc == c for _, cc in vv) and not explained(t, c)]
            ins = [t for t in news if not explained(t, c)]
            if len(outs) == 1 and len(ins) == 1 and outs[0] == o:
                n = ins[0]
                vo, vn = valid.get(o, pd.Series(dtype=float)), valid.get(n, pd.Series(dtype=float))
                # successor listing: old symbol trades up to the swap, new symbol starts trading at it
                ok = (len(vo) and len(vn) and vo.index[-1] >= c - pd.Timedelta(days=10)
                      and vn.index[0] >= c - pd.Timedelta(days=10) and vn.index[0] <= c + pd.Timedelta(days=10))
                # or (2016+): old symbol has no bars at all, new symbol's bars cover the old spell (history moved)
                ok = ok or (c > ALP0 + pd.Timedelta(days=30) and not len(vo) and len(vn)
                            and vn.index[0] < c - pd.Timedelta(days=30))
                cand.append((o, n, str(c.date()), 'linked' if ok else 'not linked'))
                if ok:
                    links[(o, a)] = (n, c, 'fja swap + Alpaca continuity')
    log['swap_candidates'] = cand
    log['links'] = [(o, n, str(c.date()), how) for (o, a), (n, c, how) in sorted(links.items(), key=lambda x: x[1][1])]

    # chains of spells = companies
    targets = {(n, c) for n, c, _ in links.values()}
    chains = []
    for t, v in sp.items():
        for a, c in v:
            if (t, a) in targets:
                continue
            ch = [(t, a, c)]
            while (ch[-1][0], ch[-1][1]) in links:
                n, cc, _ = links[(ch[-1][0], ch[-1][1])]
                ch.append(next((n, aa, c2) for aa, c2 in sp[n] if aa == cc))
            chains.append(ch)
    chains.sort(key=lambda ch: ch[0][1])
    ids = {}
    for ch in chains:
        ids.setdefault(ch[-1][0], []).append(ch)
    named = {}
    for t, chs in ids.items():  # same final ticker on unlinked chains: earlier ones get "@<end year>"
        for k, ch in enumerate(chs):
            named[t if k == len(chs) - 1 else f'{t}@{ch[-1][2].year}'] = ch
    log['id_tickers'] = {i: [x[0] for x in ch] for i, ch in named.items() if len(ch) > 1}
    log['reused_ids'] = {i: [str(ch[0][1].date()), str(ch[-1][2].date()) if ch[-1][2] else None]
                         for i, ch in named.items() if '@' in i}

    # --- 4. trading calendar and membership [date x id]
    spy_yf = yf_closes(['SPY']).SPY.dropna()
    cal = spy_yf.index[spy_yf.index < ALP0].union(valid['SPY'].index)
    cal = cal[cal >= START]
    member = pd.DataFrame(False, index=cal, columns=sorted(named))
    for i, ch in named.items():
        for t, a, c in ch:
            member.loc[(cal >= a) & ((cal < c) if c is not None else True), i] = True

    # --- 5. prices [date x id]
    used = {}  # raw symbol -> [(id, a, c)] to keep a lookback from borrowing another member's history
    for i, ch in named.items():
        for t, a, c in ch:
            used.setdefault(t, []).append((i, a, c))
    yf_ = yf_closes(sorted({t for ch in named.values() for t, a, c in ch} | {i.split('@')[0] for i in named}))
    yf_ok = {}

    def yf_valid(sym):
        if sym not in yf_ok:
            y, a = yf_[sym].dropna() if sym in yf_ else pd.Series(dtype=float), valid.get(sym)
            yf_ok[sym] = 'no yfinance data' if y.empty else 'no Alpaca overlap' if a is None or a.empty else (
                {True: 'ok', False: 'mismatch', None: 'no Alpaca overlap'}[_same_series(a, y, ALP0, ALP0 + pd.Timedelta(days=90))])
        return yf_ok[sym] == 'ok'

    cur_ids = sorted(set(member.columns) & wiki_now)
    yr = yf_closes(cur_ids, start=str((ALP0 - LOOKBACK).date()), end=None, cache='yf_recent.pkl').reindex(cal)
    px = pd.DataFrame(index=cal, columns=member.columns, dtype=float)
    src = pd.DataFrame('', index=cal, columns=member.columns)
    log['jumps'], log['overrides'], log['pieces'], log['junctions'], log['yf_pick'] = [], [], {}, [], []
    for i, ch in named.items():
        base = i.split('@')[0]
        pieces = []
        for k, (t, a, c) in enumerate(ch):
            lo = a - LOOKBACK if k == 0 else a - pd.Timedelta(days=5)  # 1 overlapping bar for an exact junction
            hi = ch[k + 1][1] if k + 1 < len(ch) else (c or cal[-1]) + pd.Timedelta(days=10)
            if k == 0:  # lookback must not overlap another company's membership under the same symbol
                for j, aa, cc in used.get(t, []):
                    if j != i and (cc or cal[-1]) <= a and (cc or cal[-1]) > lo:
                        lo = cc
            # the symbol with the most bars in the window: own ticker, a later name, or the id's ticker
            # (Alpaca files a renamed company's history under its newest symbol, e.g. FB bars live under META)
            win = lambda o: valid[o][(valid[o].index >= lo) & (valid[o].index < hi)] if o in valid else pd.Series(dtype=float)
            opts = list(dict.fromkeys([base] + [t] + [n for n, r in ren_all.get(t, []) if r >= a]))
            sym = max(opts, key=lambda o: len(win(o)))
            if len(win(t)) >= 0.8 * len(win(sym)):  # own ticker wins unless clearly worse (symbol reused later)
                sym = t
            if base in yr.columns:  # current company: pick the candidate that matches yfinance's history of it
                def fit(o):
                    w, y = win(o), yr[base].dropna()
                    ov = w.index.intersection(y.index)
                    return np.log(w[ov]).diff().corr(np.log(y[ov]).diff()) if len(ov) > 60 else np.nan
                fits = {o: fit(o) for o in opts}
                best = max(fits, key=lambda o: -1 if np.isnan(fits[o]) else fits[o])
                if fits[best] > 0.97 and not fits.get(sym, 0) > 0.97:
                    log['yf_pick'].append((i, t, sym, best, round(float(fits[best]), 3)))
                    sym = best
            x = win(sym)
            tag = pd.Series('alpaca', index=x.index)
            for al, f, u in OVERRIDES.get(t, []):
                f, u = pd.Timestamp(f or lo), pd.Timestamp(u or hi)
                y = yr[al[3:]].dropna() if al.startswith('yf:') else win(al)
                y = y[(y.index >= max(f, lo)) & (y.index <= u) & (y.index < hi)]
                log['overrides'].append((i, al, str(y.index[0].date()) if len(y) else None,
                                         str(y.index[-1].date()) if len(y) else None))
                x = _stitch([x[x.index < f], y, x[x.index > u]])
                tag = pd.concat([tag[tag.index < f], pd.Series('yfinance' if al.startswith('yf:') else 'alpaca',
                                                               index=y.index), tag[tag.index > u]])
            log['pieces'].setdefault(i, []).append((t, sym, len(x)))
            if lo < ALP0:
                ysym = next((o for o in dict.fromkeys([t, sym, base]) if o and yf_valid(o)), None)
                if ysym:
                    y = yf_[ysym].dropna()
                    y = y[(y.index >= lo) & (y.index < min(hi, x.index[0] if len(x) else hi, ALP0))]
                    x = _stitch([y, x])
                    tag = pd.concat([pd.Series('yfinance', index=y.index), tag])
            if pieces and len(pieces[-1]) and len(x):  # level break at a segment junction (pre-rescale)
                log['junctions'].append((i, t, str(x.index[0].date()), round(float(np.log(x.iloc[0] / pieces[-1].iloc[-1])), 3)))
            pieces.append(x)
            src.loc[tag.index.intersection(cal), i] = tag[tag.index.isin(cal)]
        s = _stitch(pieces)
        s = s[~s.index.duplicated()].reindex(cal)
        # long hole + big jump inside the window = probably a different company on the same symbol
        v = s.dropna()
        g = v.index.to_series().diff().dt.days
        for d in g[g > 30].index:
            jump = float(np.log(v[d] / v[v.index < d].iloc[-1]))
            if abs(jump) > 0.25:
                first_m = member[i].idxmax()
                log['jumps'].append((i, str(d.date()), round(jump, 2), 'cut pre-gap lookback' if d <= first_m else 'kept'))
                if d <= first_m:
                    s[s.index < d] = np.nan
        px[i] = s
    # --- 6. cross-vendor check vs yfinance (current constituents; yfinance has no delisted names) and
    #        yfinance fill for current constituents with no Alpaca bars at all after 2016
    log['yf_gap_fill'], log['vendor_check'] = [], {}
    for i in cur_ids:
        if px.loc[ALP0:, i].isna().all() and yr[i].notna().any():
            y = yr[i].where(cal >= member[i].idxmax() - LOOKBACK)
            px[i], src[i] = y, np.where(y.notna(), 'yfinance', '')
            log['yf_gap_fill'].append((i, str(y.first_valid_index().date())))
            continue
        a_, y_ = px[i].where(src[i] == 'alpaca').dropna(), yr[i].dropna()
        ov = a_.index.intersection(y_.index)
        if len(ov) > 60:
            ra, ry = np.log(a_[ov]).diff().dropna(), np.log(y_[ov]).diff().dropna()
            log['vendor_check'][i] = (round(float(ra.corr(ry)), 4), round(float(((ra - ry).abs() > 0.01).mean()), 4), len(ov))
    # spin-offs: Alpaca's adjustment=all leaves most of them unadjusted (a fake -10..-45% day for the parent).
    # Where yfinance (which adjusts them) has the same company, replace the return on a day with a persistent
    # level shift: |diff| > 4%, no offsetting diff the day before/after (that is a one-day bad print in one
    # vendor), vendors agree (median |diff| < 0.3%) for 20 days around, and yfinance's return is the one closer
    # to the median member's return that day.
    log['spin_patch'] = []
    mkt = np.log(px).diff().where(member).median(axis=1)
    for i in cur_ids:
        a_ = px[i].where(src[i] == 'alpaca')
        ra, ry = np.log(a_).diff(), np.log(yr[i]).diff()
        d = ra - ry
        for t in d.index[(d.abs() > 0.04) & member[i]]:
            k = d.index.get_loc(t)
            around = pd.concat([d.iloc[max(k - 20, 0):k], d.iloc[k + 1:k + 21]]).abs()
            mk = mkt[t]
            if (abs(d.iloc[k + 1] if k + 1 < len(d) else 0) < 0.01 and abs(d.iloc[k - 1]) < 0.01
                    and around.count() > 30 and around.median() < 0.003 and abs(ry[t] - mk) < abs(ra[t] - mk)):
                lr = np.log(px[i]).diff()
                lr[t] = ry[t]
                v = px[i].notna()
                px[i] = np.exp(lr.fillna(0).cumsum()).where(v) * (px[i][v].iloc[-1] / np.exp(lr.fillna(0).cumsum())[v].iloc[-1])
                log['spin_patch'].append((i, str(t.date()), round(float(ra[t]), 3), round(float(ry[t]), 3)))
    src = src.where(px.notna(), '')
    log['yf_status'] = {k: v for k, v in yf_ok.items()}

    px.to_pickle(D / 'prices.pkl')
    member.to_pickle(D / 'membership.pkl')
    src.to_pickle(D / 'source.pkl')
    pd.to_pickle({i: [(t, a, c) for t, a, c in ch] for i, ch in named.items()}, D / 'chains.pkl')
    (D / 'build_log.json').write_text(json.dumps(log, indent=1, default=str))
    return px, member, src, log


def load_universe(start=START, yf_fill=True, build_if_missing=True):
    """(prices [date x id] adjusted close, membership [date x id] bool). id = latest ticker of the company
    ("X@2013" = an earlier, different company that used ticker X).

    Prices are NaN outside [first membership - ~400d, last membership + 10d] and wherever no trusted data
    exists. yf_fill=False keeps Alpaca bars only (i.e. nothing before 2016-01-04)."""
    if not (D / 'prices.pkl').exists() and build_if_missing:
        build()
    px, mem = pd.read_pickle(D / 'prices.pkl'), pd.read_pickle(D / 'membership.pkl')
    if not yf_fill:
        px = px.where(pd.read_pickle(D / 'source.pkl') == 'alpaca')
    return px.loc[start:], mem.loc[start:]


# ---------------------------------------------------------------- quality report
MISSING_WHY = {  # verified by hand while building (see build_log.json)
    'STI': 'SunTrust (merged into Truist 2019-12). No Alpaca bars under STI (symbol later reused); not in yfinance.',
    'DOW@2017': 'Dow Chemical before the 2017-09 DowDuPont merger. No bars in Alpaca or yfinance.',
    'FTI': 'FMC Technologies before the 2017-01-17 Technip merger; Alpaca FTI starts with TechnipFMC.',
    'ARNC': 'Alcoa Inc. before its 2016-11-01 split; Alpaca ARNC starts 2016-11-01 (old Alcoa bars missing).',
    'TE': 'TECO Energy (acquired 2016-07). Alpaca TE bars belong to a later issuer (2020+).',
    'CCE': 'Coca-Cola Enterprises (became CCEP 2016-05). No bars.',
    'SNDK@2016': 'SanDisk (acquired by WDC 2016-05). SNDK reused in 2025 by the new SanDisk.',
    'AMCR': 'Added 2019-06-07; Amcor plc first traded on NYSE 2019-06-11.',
}
SUSPECT = {  # one-day member returns |log r| > 0.4 that look like data artefacts, not market moves
    ('SW', '2016-05-16'): 'artefact: WestRock (WRK) bars before this day are at a wrong level in Alpaca',
    ('TGNA', '2017-06-01'): 'artefact: Cars.com spin-off unadjusted; TGNA left the index, no yfinance patch',
    ('EVHC', '2016-12-02'): 'artefact: Envision/AmSurg merger, symbol switch inside the series',
    ('UA', '2016-04-08'): 'artefact: class-C first day; lookback bars are the pre-split class A',
}


def report(px, member, src, log):
    big6 = ['SPY', 'AAPL', 'NVDA', 'TSLA', 'GOOGL', 'AMZN']
    raw = alpaca_bars(big6, adjustment='raw', cache='alpaca_raw.pkl')
    adj = alpaca_bars(big6)
    test = ['TWTR', 'ATVI', 'XLNX', 'CTXS', 'CELG', 'TWX', 'YHOO', 'PXD', 'FRC', 'SIVB', 'SBNY', 'MON']
    bars = alpaca_bars(test)
    has = px.notna() & member
    n = member.sum(axis=1)
    lr = np.log(px).diff()
    hist = px.notna().rolling(252, min_periods=1).sum() >= 240
    hist_a = px.where(src == 'alpaca').notna().rolling(252, min_periods=1).sum() >= 240
    yt = pd.DataFrame({
        'members/day': n,
        '% priced': 100 * has.sum(axis=1) / n,
        '% Alpaca': 100 * (member & (src == 'alpaca')).sum(axis=1) / n,
        '% yfinance': 100 * (member & (src == 'yfinance')).sum(axis=1) / n,
        '% 1y history': 100 * (member & hist).sum(axis=1) / n,
        '% 1y history, Alpaca only': 100 * (member & hist_a).sum(axis=1) / n,
    }).groupby(member.index.year).mean().round(1)
    g = member.index.year
    yt['ids member'] = member.groupby(g).any().sum(axis=1)
    yt['ids member, never priced that year'] = (member.groupby(g).any() & ~has.groupby(g).any()).sum(axis=1)
    yt.index.name = 'year'

    lastm = member[::-1].idxmax()
    miss = (member & px.isna()).loc[ALP0:].sum()
    miss = miss[miss > 0].sort_values(ascending=False)
    rows = []
    for i, k in miss.items():
        why = MISSING_WHY.get(i)
        lv = px[i].last_valid_index()
        if why is None and lv is not None and lv < lastm[i]:
            why = f'last bar {lv.date()}: stopped trading before the effective removal date'
        rows.append((i, int(k), str(member[i].idxmax().date()), str(lastm[i].date()),
                     why or 'isolated days with no Alpaca bar: ' + ', '.join(
                         str(d.date()) for d in member.index[member[i] & px[i].isna()][:5])))
    miss_tab = pd.DataFrame(rows, columns=['id', 'member-days unpriced (2016+)', 'first member day (2010+)',
                                           'last member day', 'why'])

    pre = member.loc[:ALP0 - pd.Timedelta(days=1)]
    pre_ids = pre.columns[pre.any()]
    pre_np = [i for i in pre_ids if not (pre[i] & px.loc[pre.index, i].notna()).any()]
    gone = [i for i in pre_np if lastm[i] < ALP0]
    yfst = pd.Series(log['yf_status']).value_counts()

    dl = []
    for t in test:
        b = bars[t]
        v = b[b.volume > 0]
        dl.append((t, str(v.index[0].date()), str(v.index[-1].date()), len(v), int((b.volume == 0).sum()),
                   str(lastm[t].date()) if t in lastm and member[t].any() else 'held under a later id'))

    sp_rows = []
    for t, d in [('AAPL', '2020-08-31'), ('TSLA', '2020-08-31'), ('TSLA', '2022-08-25'), ('AMZN', '2022-06-06'),
                 ('GOOGL', '2022-07-18'), ('NVDA', '2021-07-20'), ('NVDA', '2024-06-10')]:
        sp_rows.append((t, d, f'{raw[t].close.pct_change()[d]:+.1%}', f'{adj[t].close.pct_change()[d]:+.1%}'))
    s_r, s_a = raw['SPY'].close, adj['SPY'].close
    yrs = (s_r.index[-1] - s_r.index[0]).days / 365.25
    cg_r = (s_r.iloc[-1] / s_r.iloc[0]) ** (1 / yrs) - 1
    cg_a = (s_a.iloc[-1] / s_a.iloc[0]) ** (1 / yrs) - 1

    vc = pd.DataFrame(log['vendor_check'], index=['corr', 'frac_gt1pct', 'n']).T
    big = lr.where(member).loc[ALP0:].stack()
    big = big[big.abs() > 0.4].sort_values()
    big_tab = pd.DataFrame([(str(d.date()), i, f'{v:+.2f}', SUSPECT.get((i, str(d.date())), ''))
                            for (d, i), v in big.items()], columns=['date', 'id', 'log return', 'note'])
    fails = [(i, str(lastm[i].date()), str(px[i].last_valid_index().date())) for i in ('SIVB', 'SBNY', 'FRC')]
    wc = log['wiki_check']
    md = lambda df: df.to_markdown(index=False)
    pct = lambda k: 100 * wc[k] / wc['events']

    out = f"""# S&P 500 point-in-time dataset: data quality

Generated by `universe_data.py` on {pd.Timestamp.today().date()}. Data cached in `data/universe/` (gitignored).
`from universe_data import load_universe; prices, member = load_universe()` returns adjusted closes and a
membership mask, both [trading day x company id], {member.index[0].date()} .. {member.index[-1].date()},
{member.shape[1]} ids. The id is the company's latest ticker (Facebook's history is under `META`); `X@2013` is
an earlier spell under ticker X that is a different company or could not be proven to be the same one.
`load_universe(yf_fill=False)` keeps Alpaca bars only.

## Verdict

* **2016-01-04 onward is usable for a wide-universe backtest.** {yt.loc[2016:, '% priced'].min():.1f}-{yt.loc[2016:, '% priced'].max():.1f}% of
  point-in-time members have a price on an average day (Alpaca SIP bars, delisted and acquired names
  included). The gaps are the {len(MISSING_WHY)} companies listed below plus 1-5 day gaps between an acquired company's last
  trade and its index exit. Survivorship bias from missing delisted names is essentially gone in this window.
* **2010-2015 is NOT usable.** Alpaca has nothing before 2016-01-04 and yfinance has only companies that still
  trade, so {yt.loc[2010, '% priced']:.0f}% (2010) to {yt.loc[2015, '% priced']:.0f}% (2015) of members are priced, and the missing
  ones are the companies later acquired, merged or bankrupt. That is the survivorship bias this dataset exists
  to remove; any test that starts before 2016 inherits it.
* **12-month-lookback features start ~2017-01.** In 2016 {yt.loc[2016, '% 1y history']:.0f}% of members have >= 240 days of
  prior prices, but only {yt.loc[2016, '% 1y history, Alpaca only']:.0f}% without the survivor-only yfinance fill; from 2017 it is
  {yt.loc[2017, '% 1y history, Alpaca only']:.0f}%+. For an unbiased 12-month signal, start the backtest at 2017-01-03.
* Net: ~10 years (2016/17 .. 2026-11) of ~503 names a day, about 40x the 12-name universe in breadth. Good
  enough for a cross-sectional factor/ML backtest of daily-to-monthly signals, provided daily returns are
  winsorized (artefacts below) and failed companies get an explicit delisting return.

## Sources and method

| piece | source | notes |
|---|---|---|
| membership 1996 .. 2026-08-18 | [fja05680/sp500](https://github.com/fja05680/sp500) `S&P 500 Historical Components & Changes (Updated).csv` | one row per change date, tickers as of that date |
| membership 2026-08-18 .. today | `TAIL` in universe_data.py, from Wikipedia edit summaries | asserted equal to Wikipedia's current table ({int(member.iloc[-1].sum())} names) |
| cross-check | Wikipedia "Selected changes" table, revision {WIKI_OLDID} (the table was removed from the live page in 2026-08) | below |
| identity | Alpaca name changes (feed starts {log['alpaca_name_change_first']}), unexplained same-day fja swaps confirmed by Alpaca bars, 7 hand-verified `OVERRIDES` | {len(log['links'])} rename links |
| prices | Alpaca `/v2/stocks/bars` 1Day, feed=sip, adjustment=all | volume-0 bars dropped (stale prints after delisting) |
| pre-2016 prices | yfinance auto_adjust, only symbols whose yfinance returns match Alpaca in Q1 2016 (corr > 0.97, 95% of daily diffs < 0.5%) | {int(yfst.get('ok', 0))} symbols ok, {int(yfst.get('mismatch', 0))} mismatch, {int(yfst.get('no yfinance data', 0))} not in yfinance |
| gap fill, cross-vendor check, spin-off patch | yfinance 2014-12 .. today, current constituents only | {', '.join(i for i, _ in log['yf_gap_fill'])} filled entirely from yfinance (no Alpaca bars); Paramount 2022-02..2025-08 from yfinance SKYD |

Prices run from ~400 calendar days before a company's first membership day to 10 days after its last, so
lookback features exist at entry. A renamed company's series is stitched from the symbol it traded under at the
time; the level is rescaled at the join (exact when both symbols have a bar on the join day, else that day's
return is 0). Raw build diagnostics: `data/universe/build_log.json`.

## Membership cross-check (fja vs Wikipedia "Selected changes", 2010+)

{wc['events']} add/remove events. fja agrees on the exact effective date for {wc['exact']} ({pct('exact'):.0f}%), within 7 days
for {wc['d7']} ({pct('d7'):.0f}%), within 31 days for {wc['d31']} ({pct('d31'):.0f}%). {wc['ticker_not_in_fja']} events use a ticker that never appears in fja.
The disagreements are naming, not membership: Wikipedia writes a later ticker (BKR for BHGE, MDLZ for KFT, IQV
for Q, GOOGL in 2014, ARNC for AA), share-class swaps (FOX/FOXA, UA/UAA), or fja's date is a few days off. No
case was found of a constituent missing or a phantom one for more than a few weeks. Daily member count is
{int(n.loc['2016':].min())}-{int(n.loc['2016':].max())} since 2016 ({int(n.min())}-{int(n.max())} since 2010): ~500 companies plus second share classes.

Events not matched within 7 days: {', '.join(f"{r['ticker']} {r['kind']} {r['date']}" for r in log['wiki_mismatch'])}.

Rename links: {', '.join(f'{o}->{n2} ({d[:4]})' for o, n2, d, h in log['links'])}. IR is split at
2020-03-03 (Ingersoll-Rand plc became TT; Gardner Denver took the IR symbol). Tickers used by two different
member spells are separate ids: {', '.join(log['reused_ids'])}.

## Does Alpaca have delisted names?

Yes, from 2016-01-04. A request with start=2010-01-01 returns nothing earlier for any symbol (SPY, AAPL
included): that is Alpaca's first daily bar, so 2008-2015 failures and acquisitions are absent.

{md(pd.DataFrame(dl, columns=['symbol', 'first bar', 'last real bar', 'bars', 'volume-0 bars', 'last S&P member day']))}

After a delisting Alpaca can keep emitting volume-0 bars at the last price (MON: years of them, then the
symbol becomes a SPAC); they are dropped. Alpaca usually files a renamed company's history under its newest
symbol (FB->META, HCP/PEAK->DOC, ABC->COR, ANTM->ELV) but not always (YHOO/AABA, BHI/BKR, TSO/ANDV, DLPH/APTV
are split), and a reused symbol can carry the new issuer's bars back in time (Alpaca `PARA` is the ex-BNZI
company, not Paramount; `CTRA` before 2021-02 is Contura Energy; `BBT` disagrees with Truist's history, so
TFC's own bars are used). Each case found is handled in code; the cross-vendor check below is the safety net,
but it only covers current constituents.

## Coverage by year

`% priced`: point-in-time members with a price that day, averaged over the year. `% 1y history`: members with
>= 240 priced days in the trailing 252.

{yt.reset_index().to_markdown(index=False)}

### Members without prices, 2016+

{md(miss_tab)}

The 1-5 day gaps are acquisitions: the target stops trading at the deal close and S&P removes it a few days
later. Holding the last price (the deal price) to the exit is the right treatment.

### Members without prices, 2010-2015

{len(pre_ids)} ids were members at some point in 2010-2015; {len(pre_np)} have no price at all in that period:
{len(gone)} left the index before 2016 (in neither Alpaca nor yfinance) and {len(pre_np) - len(gone)} were still members in 2016 but
yfinance has no history under the symbol or it failed validation. Never priced pre-2016: {', '.join(sorted(pre_np))}.

## Corporate actions

**Splits** (Alpaca adjustment=all), one-day return on the split day:

{md(pd.DataFrame(sp_rows, columns=['symbol', 'split day', 'raw return', 'adjusted return']))}

**Dividends**: SPY {s_r.index[0].date()} .. {s_r.index[-1].date()}, raw price CAGR {cg_r:.2%} vs adjusted {cg_a:.2%}. The
{cg_a - cg_r:.2%}/yr gap is the dividend yield, so cash dividends are reinvested in the adjusted series.

**Spin-offs are mostly NOT adjusted by Alpaca.** On the ex-date the parent shows a fake loss equal to the
spun-off shares' value. Alpaca's spin-off feed starts ~2021 and misses events (IBM/Kyndryl, MRK/Organon). For
current constituents the build compares each day with yfinance and takes yfinance's return where the vendors
agree for 20 days around, disagree that day without reversal, and yfinance's return is closer to the median
member's ({len(log['spin_patch'])} patched): {', '.join(f'{i} {d} ({a:+.3f} -> {b:+.3f})' for i, d, a, b in log['spin_patch'])}.
Companies that have left the index cannot be checked this way, so some of their spin-off days remain as fake
drops (e.g. TGNA 2017-06-01).

**Cross-vendor check** (current constituents, Alpaca days, before the patch): median daily-return correlation
with yfinance {vc['corr'].median():.4f}; {int((vc['corr'] > 0.99).sum())} of {len(vc)} names above 0.99. Below 0.97:
{', '.join(f"{i} ({r['corr']:.2f})" for i, r in vc[vc['corr'] < 0.97].iterrows())}. SW is yfinance's problem (its SW
history before 2024-07 is not WestRock, the S&P member used here); RTX, YUM, PNR are spin-offs patched above;
DHR is a yfinance error on 2016-07-05 (Fortive spin-off), Alpaca kept. One-day print differences that reverse the
next day (mostly 2020-03-09..19) are left as Alpaca has them.

## Member daily returns beyond +/-40% (2016+)

Most are real (bank failures, the 2020-03-09 oil crash, earnings gaps). Known artefacts are annotated.

{md(big_tab)}

## Biases and limits that remain

1. **Window**: unbiased only from 2016-01-04 (2017-01 for 12-month lookbacks). 2010-2015 is survivor-biased.
2. **Delisting returns**: when trading stops before index removal, the last price is the last trade. For cash
   acquisitions that is about the deal price (fine). For failures it overstates the outcome:
   {', '.join(f'{i} (last bar {b}, removed {a})' for i, a, b in fails)} were near-total losses after the last bar
   here. Apply an explicit delisting return (e.g. -100% for seizures/bankruptcies) if a strategy can hold them.
3. **Spin-offs** of companies no longer in the index are unadjusted (fake one-day drops). Winsorize daily
   returns (e.g. at +/-40%) or drop flagged days.
4. **Join days**: when a rename's two symbols share no bar, the join-day return is 0.
5. **Membership timing**: fja matches Wikipedia to the day for {pct('exact'):.0f}% of events, within a week for {pct('d7'):.0f}%.
   Lag membership by a day (decide on day t-1's list) to avoid acting on a change before it is known.
6. **Not included**: point-in-time fundamentals, sectors, market caps, shares outstanding. Wikipedia GICS sectors
   are today's. Prices are back-adjusted with today's factors: fine for returns, wrong for price-level filters.
7. **Index selection**: survivorship is fixed; selection into the index is not. Additions follow strong past
   returns, so do not treat pre-entry lookback prices as investable returns.
8. **Provenance**: fja is one maintainer's file (seeded from Clenow's 1996-2019 list) and Alpaca is one vendor,
   cross-checked against yfinance only for current names. Assume residual errors on ~0.1-1% of member-days.
"""
    (ROOT / 'reports' / 'universe_data_quality.md').write_text(out, encoding='utf-8')
    return yt


if __name__ == '__main__':
    px, member, src, log = build()
    print(report(px, member, src, log).to_string())
