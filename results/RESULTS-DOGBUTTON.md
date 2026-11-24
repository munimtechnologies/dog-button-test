# RESULTS-DOGBUTTON: is the dogs' 'non-random' button network more than button popularity?

Rendered by dogbutton_test.py (pre-registration: DOGBUTTON-PREREG.md). Made with AI agents
working in MV2's name; no human expert has checked it yet.

Primary table: q2 (threshold: pairs seen >= 2 times). Primary verdict: **POPULARITY_EXPLAINS_MOST_OF_GAP**

| quantity | primary | q3_thresh2 | q2_thresh1 |
|---|---|---|---|
| dogs in group test | 133 | 96 | 161 |
| mean real RI | -0.564 | -0.748 | -0.498 |
| median real RI | -0.796 | -0.934 | -0.656 |
| mean Erdos-Renyi null RI | -0.209 | -0.386 | -0.202 |
| mean popularity null RI | -0.766 | -0.823 | -0.659 |
| gap to Erdos-Renyi (null - real) | 0.356 | 0.362 | 0.296 |
| gap to popularity null (null - real) | -0.201 | -0.075 | -0.160 |
| share of ER gap explained by popularity | 1.566 | 1.208 | 1.542 |
| dogs passing the authors' -0.2 criterion vs ER | 93 | 69 | 115 |
| dogs passing the -0.2 criterion vs popularity | 24 | 10 | 40 |
| dogs with per-dog p <= 0.05 vs popularity | 7 | 7 | 5 |
| group p (real more negative than popularity null) | 1.0000 | 0.9801 | 1.0000 |
| verdict | POPULARITY_EXPLAINS_MOST_OF_GAP | POPULARITY_EXPLAINS_MOST_OF_GAP | POPULARITY_EXPLAINS_MOST_OF_GAP |

Tables: {"q2": {"rows": 15981, "subjects": 176, "min_freq": 1, "max_freq": 400, "pair_events": 81357}, "q3": {"rows": 3709, "subjects": 169, "min_freq": 1, "max_freq": 313, "pair_events": 23603}}

Parsing: {"q2": {"rows": 15981, "unique": 15981, "fallback": 0, "unparsed": 0, "self": 0, "bad_freq": 0}, "q3": {"rows": 3709, "unique": 3709, "fallback": 0, "unparsed": 0, "self": 0, "bad_freq": 0}}

Histogram of per-dog RI (bins [-2.0, -1.0, -0.6, -0.2, 0.2, 0.6, 1.0, 2.0]): real [0, 85, 20, 12, 14, 2, 0], ER-null mean [0, 9, 37, 87, 0, 0, 0], popularity-null mean [0, 111, 21, 1, 0, 0, 0]
