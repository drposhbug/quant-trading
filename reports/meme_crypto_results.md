# Meme stocks, crypto stocks and candles

Rules written in meme_crypto_study.py before the run. Meme list (33): GME, AMC, BB, NOK, KOSS, BBBY, EXPR, PLTR, HOOD, SOFI, RIVN, LCID, NKLA, SPCE, CVNA, AFRM, UPST, DJT, RDDT, TLRY, SNDL, CLOV, WISH, MULN, FFIE, NIO, PLUG, DKNG, OPEN, BYND, PTON, SNAP, RBLX. Crypto list (17): COIN, MSTR, MARA, RIOT, CLSK, HUT, BITF, CIFR, HIVE, BTBT, WULF, IREN, CORZ, GLXY, SI, BKKT, CAN. Not found or too short: none. 2016-01-04 to 2026-11-23. bp = hundredths of a percent.

## 1. Night against day

|                                       |    days |   mean, bp |     t |   1st half, bp |   2nd half, bp |   share of days up |
|:--------------------------------------|--------:|-----------:|------:|---------------:|---------------:|-------------------:|
| meme: overnight (close to open)       | 2738.00 |      15.77 |  5.23 |          24.74 |           6.81 |               0.57 |
| meme: overnight after 10 bp a night   | 2738.00 |       5.77 |  1.91 |          14.74 |          -3.19 |               0.52 |
| meme: daytime (open to close)         | 2739.00 |     -10.60 | -2.46 |          -5.48 |         -15.72 |               0.47 |
| crypto: overnight (close to open)     | 2738.00 |      49.95 |  2.69 |          34.70 |          65.20 |               0.53 |
| crypto: overnight after 10 bp a night | 2738.00 |      39.95 |  2.15 |          24.70 |          55.20 |               0.51 |
| crypto: daytime (open to close)       | 2739.00 |     -10.43 | -1.44 |          -5.20 |         -15.66 |               0.46 |

- Verdict (meme list, overnight): **real**.

## 2. After a spike (up more than 15% on more than 3 times normal volume)

491 spikes. In at the next open, 5 sessions, against the list's average: -89 bp a day, t -3.2 (halves -74 and -104), 1137 days. Per spike over the 5 sessions: -0.8%; it lagged the list 67% of the time.

- Verdict: **real: spikes fade**.

## 3. Crypto stocks and Bitcoin

- They move together: the crypto list's daily move against Bitcoin's (16:00 to 16:00) has a correlation of 0.39; for each 1% in Bitcoin the list moves 1.02%.
- Bitcoin's overnight move is in the opening price: for each 1% Bitcoin moves between the close and 09:00, the list opens 0.92% higher (correlation 0.20).
- **The deciding number:** for each 1% Bitcoin moved overnight, the list then moved -0.04% from its open to its close, t -1.1, 1479 days (halves +0.02 and -0.18). After weekends only: -0.06, t -0.9.

- Verdict: **no pattern**.

## 4. Candles

39 tries (13 patterns, holding 1, 5, 10 sessions), from the next open, both lists together. The strongest five by t:

| Pattern                |   h |    n |   excess_bp |   hit |     t |   pre2021_bp |   post2021_bp |      p |   p_holm | stable   |
|:-----------------------|----:|-----:|------------:|------:|------:|-------------:|--------------:|-------:|---------:|:---------|
| Hammer (after down 5d) |  10 | 1231 |        -268 |  0.41 | -3.64 |         -119 |          -339 | 0.0003 |    0.011 | True     |
| Outside bar            |   5 | 7380 |         -66 |  0.43 | -2.8  |          -15 |           -84 | 0.005  |    0.192 | True     |
| Gap down > 1%          |  10 | 6025 |        -154 |  0.42 | -2.61 |          -42 |          -182 | 0.0091 |    0.336 | True     |
| Bullish engulfing      |  10 | 3412 |        -152 |  0.41 | -2.5  |           11 |          -205 | 0.0124 |    0.447 | False    |
| Bear marubozu          |   5 | 2298 |         -65 |  0.43 | -2.37 |           29 |          -114 | 0.0178 |    0.623 | False    |

- Verdict: **1 of 39 candle patterns survive**: Hammer (after down 5d) (10 sessions).

