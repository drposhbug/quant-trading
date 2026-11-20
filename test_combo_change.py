"""Checks for combo_change_study.py. Run: python test_combo_change.py"""
import numpy as np

import combo_change_study as S

# logistic fit recovers known coefficients
rng = np.random.default_rng(0)
x = rng.normal(size=(20000, 1))
y = (rng.random(20000) < 1 / (1 + np.exp(-(-1 + 2 * x[:, 0])))).astype(float)
b = S.fit_logistic(x, y)
assert abs(b[0] + 1) < 0.08 and abs(b[1] - 2) < 0.1
# decomposition is exact
r, pr, lu = S.decompose([0.1, 0.5], [0, 1], [0.08, 0.45])
assert np.allclose(r, pr + lu) and np.isclose(r[0], 0.1 / 0.9)
# bootstrap diff: clear effect -> small p; none -> large p
m, lo, hi, p = S.boot_diff(np.r_[np.ones(50), np.zeros(50)] + 1, np.arange(100))
assert m == 1.5 and p < 0.01 and lo < 1.5 < hi
assert S.boot_diff([1, -1] * 50, np.arange(100))[3] > 0.5
# Holm
assert np.allclose(S.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
# team side from tickers
assert S.team_of("KXNFLPASSYDS-26NOV15NEDET-DETJGOFF16-175", "KXNFLPASSYDS-26NOV15NEDET") == "H"
assert S.team_of("KXNFLPASSINT-26NOV15NEDET-NEDMAYE10-1", "KXNFLPASSINT-26NOV15NEDET") == "A"
assert S.team_of("KXNFL1QTOTAL-26NOV15NEDET-8", "KXNFL1QTOTAL-26NOV15NEDET") is None
assert S.team_of("KXNBASPREAD-26NOV05MIAGSW-GSW10", "KXNBASPREAD-26NOV05MIAGSW") == "H"
lg = lambda m, s="yes": {"market_ticker": m, "event_ticker": m.rsplit("-", 1)[0] if m.count("-") == 2 else "-".join(m.split("-")[:2]), "side": s}
a, b2 = lg("KXNFLGAME-26NOV15NEDET-DET"), lg("KXNFLPASSYDS-26NOV15NEDET-DETJGOFF16-175")
assert S.relation(a, b2) == "same" and S.relation(a, lg("KXNFLPASSINT-26NOV15NEDET-NEDMAYE10-1")) == "opp"
# same-event pairs only within a game
legs = [a, b2, lg("KXNBAGAME-26NOV15DALBOS-BOS")]
assert len(S.same_event_pairs(legs)) == 1
# lift: independence -> ~0; perfect co-occurrence -> positive; shrinks toward prior with few pairs
assert abs(S.shrunk_loglift(10000, 5000, 5000, 2500)) < 0.01
assert S.shrunk_loglift(10000, 5000, 5000, 5000) > 0.6
assert S.shrunk_loglift(0, 0, 0, 0, prior=0.3) > 0.25        # no data -> prior
# model fair and roi
assert np.allclose(S.model_fair([0.1], [np.log(2)], 1), [0.2]) and S.model_fair([0.9], [5], 1)[0] == 0.999
assert np.isclose(S.roi_yes(0.2, 1, 0), 4) and np.isclose(S.roi_yes(0.2, 0, 0), -1)
print("ok")
