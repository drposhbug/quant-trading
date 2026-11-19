"""What else to hold? Universe + diversifying-sleeve study. Writes reports/universe_results.md. Math: see MATH.md.

Every variant runs through the SHIPPED engine (model.target_weights / backtest_returns, params model.P untouched) and is
compared with the shipped model on the same days with a paired stationary bootstrap + split-sample check.

Selection-bias guard: stock candidates come from point-in-time rules (largest US market caps at end-2014), not from what
we now know went up. The number of variants is fixed below (VARIANTS) so the multiple-testing count is exact.

Run: python universe_study.py   (uses data/prices.csv from backtest.py for the shipped universe; downloads the rest)
"""
import numpy as np
import pandas as pd
import yfinance as yf

from backtest import prices, sharpe_rows, stationary_bootstrap_idx, stats
from model import BENCH, P, backtest_returns, target_weights

# Largest US-listed companies by market cap at 2014-12-31 (as known in early 2015; e.g. FT Global 500 / S&P Dow Jones
# year-end 2014 rankings): Apple ~$647B, Exxon ~$390B, Microsoft ~$382B, Berkshire ~$357B, Google ~$360B, J&J ~$292B,
# Wells Fargo ~$284B, Walmart ~$277B, GE ~$254B, P&G ~$246B, JPMorgan ~$232B, Chevron ~$211B. Ranking is approximate;
# membership is what matters and it uses no post-2014 information.
TOP12_2014 = ["AAPL", "XOM", "MSFT", "BRK-B", "GOOGL", "JNJ", "WFC", "WMT", "GE", "PG", "JPM", "CVX"]
# Ten largest US tech/internet names by market cap at 2014-12-31 (same sources): the current universe's *sector* bet
# made without knowing which names would win. FB is META today; IBM/INTC/CSCO/QCOM are the 2015 giants that lagged.
TECH10_2014 = ["AAPL", "MSFT", "GOOGL", "META", "ORCL", "INTC", "AMZN", "CSCO", "IBM", "QCOM"]
SLEEVES = ["TLT", "IEF", "GLD", "DBC", "USMV", "XLV", "XLP", "DBMF", "KMLM"]

# Numbers quoted from the 2026-11-19 run (20% vol target, drift-inclusive costs). Re-check if the table moves.
CONCLUSIONS = """## Findings

**Hindsight in the current universe.** The same engine on the 10 largest US tech names as of end-2014 (A2) earns
Sharpe 0.98 / CAGR 15% vs the shipped 1.26 / 23%, and the paired bootstrap says the current list is better with
P = 0.98. That gap (~0.3 Sharpe, ~8 pp CAGR) is name selection made knowing NVDA/AVGO/AMD/TSLA won: treat it as
hindsight, not edge. A no-hindsight forward expectation for this engine is the rule-based range, Sharpe ~1.0, not 1.3.
Adding the broad 2014 mega-caps (A3) lifts Sharpe slightly (1.34, P = 0.32) only by diluting into lower-vol names; it
loses in H1 (-0.34) and wins in H2 (+0.54), costs 5 pp CAGR, and is not significant. No stock additions recommended.

**Sleeves.** Assets with low correlation to the book raise Sharpe inside the same engine. Gold (B3) is the best single
sleeve: Sharpe 1.35 vs 1.26, P = 0.024, better in both halves and since 2022, MaxDD -22% vs -22.5%, CAGR -0.3 pp.
IEF + GLD (B8, pre-specified before the run) is best overall: Sharpe 1.42, P = 0.029, positive in H1, H2 and 2022+,
MaxDD -21%, but CAGR falls 23% -> 18% because the no-leverage cap stops the vol target re-levering (vol 12%).
Neither clears the Bonferroni bar (P < 0.0042 for 12 tries), so these are risk-preference choices, not proven edge.
Long bonds (TLT) stopped helping when the stock-bond correlation flipped (-0.19 to +0.05 after 2022; dSharpe 2022+
-0.03); IEF held up better. USMV/XLV/XLP/DBC: small, inconsistent gains. Managed futures (DBMF/KMLM): +0.13 Sharpe on
their own 2021+ window, but only ~5 years of data.

**Idle cash.** Holding un-invested cash in T-bills (BIL/SGOV) adds ~0.5%/yr and trims MaxDD with zero added risk.
Its "P = 0.000" is mechanical (it adds a positive return every day); in excess-of-T-bill terms it is just not
throwing away the risk-free rate. Do it: it is the only change here that needs no statistical argument.

**Recommendation.** Keep the stock universe as is (TSLA, SPCX, AAPL, MSFT, NVDA, GOOGL, AMZN, META, AVGO, TSM, AMD,
ORCL, + ANT), sweep idle cash into SGOV/BIL, and add GLD as a sleeve (cost ~0.3 pp CAGR for +0.09 Sharpe and a
slightly shallower drawdown). Add IEF too only if lower vol (12%) is preferred over return (18% vs 23% CAGR).

**Caveats.** 12 variants; best P = 0.024 > Bonferroni 0.0042. Gold's 2024-26 rally helps B3/B8 in-sample. The regime
filter also halves the sleeves in risk-off, the opposite of what a hedge should do; exempting them is an untested
13th variant. ^IRX is a proxy for BIL/SGOV (ignores ~0.1% fees). Survivorship: XOM/GE etc. still trade, so the
2014 lists have no delisting gap. Sharpe here is raw mean/std as in backtest.py; the excess column subtracts T-bills.
"""


def load_extra(tickers):
    px = yf.download(tickers + ["^IRX"], start="2014-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    return px


def run(px):
    return backtest_returns(px, target_weights(px))


def cash_yield(px, irx):
    """Shipped model + T-bill yield on the un-invested fraction. ^IRX = 13-week bill yield in %, a conservative proxy for
    BIL/SGOV (ignores their ~0.1% fee, close enough). Idle fraction uses yesterday's weights, like backtest_returns."""
    w = target_weights(px)
    idle = (1 - w.shift(1).fillna(0).sum(axis=1)).clip(lower=0)
    rf = (irx.reindex(px.index).ffill().fillna(0) / 100 / 252)
    return backtest_returns(px, w) + idle * rf, idle


def main():
    base = prices()  # shipped universe + QQQ, same cache as backtest.py
    cur = [c for c in base.columns if c != BENCH]
    extra = load_extra(sorted(set(TOP12_2014 + TECH10_2014 + SLEEVES) - set(base.columns)))
    allpx = base.join(extra.drop(columns="^IRX"), how="left")
    irx = extra["^IRX"]
    mk = lambda names: allpx[list(dict.fromkeys(names)) + [BENCH]]

    adds12 = [t for t in TOP12_2014 if t not in cur]
    # Exactly these 12 variants are tested (plus the shipped baseline). Do not add rows without updating the count.
    VARIANTS = {
        "A1 Rule-only: top-12 US mkt cap 2014": mk(TOP12_2014),
        "A2 Rule-only: top-10 US tech 2014": mk(TECH10_2014),
        "A3 Current + top-12-2014 additions": mk(cur + adds12),
        "B1 Current + TLT": mk(cur + ["TLT"]),
        "B2 Current + IEF": mk(cur + ["IEF"]),
        "B3 Current + GLD": mk(cur + ["GLD"]),
        "B4 Current + DBC": mk(cur + ["DBC"]),
        "B5 Current + USMV": mk(cur + ["USMV"]),
        "B6 Current + XLV + XLP": mk(cur + ["XLV", "XLP"]),
        "B7 Current + DBMF + KMLM (2019+/2020+)": mk(cur + ["DBMF", "KMLM"]),
        "B8 Current + IEF + GLD": mk(cur + ["IEF", "GLD"]),
    }
    start = base.index[P["trend_long"] + P["vol_win"]]  # same window as backtest.py
    sl = lambda r: r.loc[start:]
    shipped = sl(run(base))
    rets = {"Shipped model (current universe)": shipped}
    weights = {}
    for k, px in VARIANTS.items():
        w = target_weights(px)
        weights[k] = sl(w)
        rets[k] = sl(backtest_returns(px, w))
    cy, idle = cash_yield(base, irx)
    rets["C1 Shipped + T-bill yield on idle cash"] = sl(cy)
    n_var = len(rets) - 1
    R = pd.DataFrame(rets).fillna(0)

    # --- battery: paired stationary bootstrap vs shipped, split-sample, 2022+ (stock-bond corr flipped positive) ---
    B = 2000
    idx = stationary_bootstrap_idx(len(R), B)
    S0 = sharpe_rows(R.iloc[:, 0].values[idx])
    half = R.index[len(R) // 2]
    sr = lambda r: r.mean() / r.std() * np.sqrt(252)
    excess_rf = sl(irx.reindex(base.index).ffill().fillna(0) / 100 / 252)
    rows = []
    for k in R:
        r = R[k]
        st = stats(r)
        p = np.nan if k == R.columns[0] else ((sharpe_rows(r.values[idx]) - S0) <= 0).mean()
        rows.append({
            "Variant": k, "CAGR": st["CAGR"], "Vol": st["Vol"], "Sharpe": st["Sharpe"], "MaxDD": st["MaxDD"],
            "Excess Sharpe (vs T-bill)": sr(r - excess_rf),
            "P(Sharpe <= shipped)": p,
            "dSharpe H1": sr(r[:half]) - sr(R.iloc[:, 0][:half]),
            "dSharpe H2": sr(r[half:]) - sr(R.iloc[:, 0][half:]),
            "dSharpe 2022+": sr(r["2022":]) - sr(R.iloc[:, 0]["2022":]),
        })
    T = pd.DataFrame(rows).set_index("Variant")

    # Managed futures only exist from 2019/2020: judge them on their own window too.
    mf_start = allpx["KMLM"].first_valid_index() + pd.Timedelta(days=120)
    mf = R.loc[mf_start:]
    mf_line = (f"From {mf_start.date()} (KMLM live + ~60d warm-up): shipped Sharpe {sr(mf.iloc[:, 0]):.2f}, "
               f"B7 Sharpe {sr(mf['B7 Current + DBMF + KMLM (2019+/2020+)']):.2f}.")

    # Sleeve correlations with the shipped model, by period (why bonds helped then stopped helping)
    lr = allpx.pct_change()
    corr = pd.DataFrame({
        per: {s: shipped.loc[a:b].corr(lr[s].loc[a:b]) for s in ["TLT", "IEF", "GLD", "DBC", "USMV", "XLV", "XLP", "DBMF", "KMLM"]}
        for per, (a, b) in {"2015-2021": ("2015", "2021"), "2022+": ("2022", None)}.items()
    })
    avg_w = pd.DataFrame({k: weights[k][[c for c in weights[k].columns if c not in cur]].mean()
                          for k in VARIANTS if k.startswith("B")}).T.round(3)

    out = [
        "# Universe & sleeve study\n",
        f"Period {R.index[0].date()} to {R.index[-1].date()} ({len(R)} days), same window and engine as backtest.py "
        f"(model.P unchanged: inv-vol, {P['cap']:.0%} cap, {P['vol_target']:.0%} vol target, no leverage, half gross when QQQ < 200d MA). "
        f"Generated by universe_study.py. **{n_var} variants tested** against the shipped model; with that many "
        f"tries, a one-sided P < 0.05 is expected ~{n_var * 0.05:.1f} times by luck, so the Bonferroni bar is "
        f"P < {0.05 / n_var:.4f}.\n",
        "## Results\n",
        "P = paired stationary bootstrap (L=20, B=2000) probability the variant's Sharpe is <= shipped (small = variant "
        "better). dSharpe = variant minus shipped in each half / since 2022. Excess Sharpe subtracts the T-bill rate.\n",
        T.to_markdown(floatfmt=".3f"), "\n",
        "## Sleeve weights and correlations\n",
        "Average weight the engine gave each added asset (weights include vol-target and regime scaling):\n",
        avg_w.to_markdown(), "\n",
        "Daily-return correlation of each sleeve with the shipped model:\n",
        corr.to_markdown(floatfmt=".2f"), "\n",
        f"Managed-futures window: {mf_line}\n",
        f"Idle cash: shipped model averages {sl(idle).mean():.0%} un-invested (risk-off days: "
        f"{sl(idle)[sl(idle) > 0.4].mean():.0%}). Mean T-bill yield over the period {sl(irx.reindex(base.index).ffill()).mean():.2f}%.\n",
        CONCLUSIONS,
    ]
    with open("reports/universe_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
