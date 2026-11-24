# Grok: attack on the decision (2026-11-23)

Grok did not answer the long first-principles question put to Astra (it ran for over 25 minutes without output). It was then asked a shorter question: here are the findings and the plan, find what is wrong. The question is in `8b the shorter question put to Grok.md`. Unedited.

---

### 1. Artefact

**Finding 1.** The 55.2% hit rate is a sign test on 2,338 days (naive z ≈ 5). A 12-month book barely changes from day to day, and losses cluster, so this is one repeated bet. Mean +0.6 bp, **t = 0.25**, annualised Sharpe ≈ 0.08: **+14% of notional, uncompounded, over 9.3 years**. σ ≈ 0.6 bp × √2338 / 0.25 ≈ 116 bp, so ½σ² ≈ 0.67 bp/day of drag and compounded growth is ~0. Median +8.7 bp and skew −1.4 flatter that sign test. It was the best of 332 patterns.

**Check:** non-overlapping monthly hit rate (~110 months) and a block bootstrap with 21–63 day blocks, then a White/Hansen haircut for the 332-way search. A monthly hit rate that was still 55% would be only z ≈ 1. **Opinion: P(this kills the claim) ≈ 0.85.**

### 2. Neutralisation

**Remove market beta and sector. Keep style.**

N_eff ≈ 28 (1/0.19²) because residuals co-move. A constant market shock already drops out of rank IC. Residualize each pattern and the forward return on trailing beta and sector dummies estimated before the outcome window.

Over-neutralising deletes industry momentum and whatever style premium the live book still holds, and a fat in-sample projection shrinks true IC toward zero. **Opinion: P(effective N reaches several hundred) ≈ 0.2.** Market and sector together might reach ~100.

### 3. Overnight

+2.8 bp runs from the close that enters the signal. MOC cutoff is 15:50. The version an account can send: ranks as of t−1, MOC today, MOO tomorrow. **Opinion: a one-day lag costs ~10–20% of a 12-month rank.**

Gross +2.8 bp, σ ≈ 54 bp (2.8 × √2338 / 2.5), ~+7%/year, Sharpe ~0.8, −13% nights included. Four fills a night. Break-even is **2.8 bp all-in**: with ~0.5 bp borrow, about **0.6 bp per fill**. Auction fills in a tiny large-cap account can land under that. Open shortfall above ~0.6 bp, or opens and closes other than the official auction, takes the whole gross. The lagged book is unscored. Scored from the next open, the hit rate is already 48%. **Opinion: P(net profitable after lag, borrow, and crashes) ≈ 0.2.**

### 4. News

Own-stock direction after a shock is already t < 1 on 11,041 events, so a large average drift is unlikely. A rare concentrated reaction can still hide, and 13,731 unfiltered posts are mostly noise.

**Untested, on free daily fields:** industry lead-lag. After a residual move above 3σ on double volume, do same-sector stocks that did not jump drift over the next 1–5 sessions? Posts: freeze a sector lexicon, keep off-hours posts, buy that basket at the next open. **Opinion: P(this reaches an e-value of 20) ≈ 0.10.**

### 5. Plan

**Missing:** one lagged portfolio judged on net P&L after borrow and slippage, point-in-time constituents, delisting returns, and a written e-process before the next close. “Confirms at 20” binds only that pre-specified score. History through tonight is the mining set. Dead names without the exit return leave the hole in the short leg.

**Delete (d).** In-sample t-weights hand the job back to the winner of the 332-search and undo (f). **(e) is a position limit: t = 0.96 is still a null (opinion).**

### 6. Probability

**Opinion: P ≈ 0.12** that the finished plan produces a real after-cost edge, confirmed on new days, that beats vol-scaled momentum. Earnings dates are the only add-on with a real prior, and event days are sparse next to the 0.025 IC floor in Finding 4. Four separate passes at e-value 20 put a false confirmation near 0.2.
