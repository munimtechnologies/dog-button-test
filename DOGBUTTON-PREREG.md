# DOGBUTTON-PREREG: is the "non-random" button network of soundboard dogs more than button popularity?

dog-button-test, MV2, Munim, Inc. Made with AI agents working in MV2's name; no human expert has
checked it yet. Registered 2026-11-21, before any statistic was computed on the authors' tables by
us. Text: CC BY 4.0; code: Apache-2.0.

## 1. The claim

Bastos, Houghton, Naranjo & Rossano (2024), "Soundboard-trained dogs produce non-accidental,
non-random and non-imitative two-button combinations", Scientific Reports 14:28771
(doi 10.1038/s41598-024-79517-6). 152 dogs, 194,901 dog presses from the FluentPet app. The
"non-random" part: for each dog, a network of button labels linked when pressed next to each
other (pairs seen more than once), summarised by a Randomness Index (RI) = the Pearson correlation,
over degree values k, between k and the mean local clustering of nodes with degree k. Real
networks had strongly negative RI (mode about -0.84); Erdos-Renyi G(n, p) networks of the same
size and density had RI near 0; paired Bayesian t-test BF = 72.73.

## 2. Why test it

An Erdos-Renyi graph gives every button the same chance of being pressed. Real boards do not:
a few concepts (outside, food, play) are pressed far more than the rest. When pair events land
on concepts in proportion to their popularity, popular concepts link to many rare ones, rare
concepts link only to the popular hubs, and the hubs' neighbourhoods are sparse: mean clustering
falls with degree, so RI is negative with no sequential structure at all. The paper's other two
analyses (non-accidental: a model with a popularity offset; non-imitative) are not tested here.
A search on 2026-11-21 found no reanalysis of the RI result; the only methods critique
(Wayenberg 2026, Front. Anim. Sci., doi 10.3389/fanim.2026.1907975) does not discuss the null.

## 3. Data

The authors' public tables at github.com/znhoughton/Modeling, commit
23b3d2c933d9b72ca7f57cbe66ef247551d0b9fd (no licence file: fetched at run time, never copied
here): `question2_data.csv` and `question3_data.csv` (subject, combination_id,
combination_rel_probs, combination_freq: per-dog counts of concept pairs) and `concept list.csv`.
The raw press log (export_08_23_2022.csv) is not public, so the paper's button-label networks
cannot be rebuilt; we use the public concept-level pair counts. Primary table: question2 if its
smallest count is 1 (complete counts), else question3 if its smallest count is 1, else question2.
Combination ids are split into two concepts using the concept list (letters and digits only,
upper case); an id with a single underscore and no listed match is split there; others are
dropped and counted, as are same-concept pairs.

## 4. Method

Per dog: the network of concept pairs with >= 2 events (the authors' weight > 1), nodes = their
concepts. Eligible if it has >= 4 edges (the authors' NA rule) and a finite RI. RI computed as in
the authors' R code (igraph local transitivity, NaN below degree 2; plain mean per degree class,
so degree-1 classes drop out; Pearson over the remaining classes; NaN with < 2 classes).

- **ER null (the authors')**: G(n, p) with the real n and p = mean degree / (n - 1); 1000 draws;
  null RI = mean of finite draws.
- **Popularity null (new, primary)**: the dog's own pair events, all counts including singletons,
  re-paired by a random perfect matching of "stubs" (each concept keeps exactly its number of
  pairings), same-concept pairs dropped, then the same >= 2 threshold and RI; 1000 draws.
- Group set: eligible dogs with >= 50% finite draws in both nulls. g_er = mean(ER null RI - real
  RI); g_pop = mean(popularity null RI - real RI); share explained = 1 - g_pop / g_er.
- Calibrated group test: T = mean over dogs of (real RI - popularity-null mean); its null
  distribution uses one popularity draw per dog in place of the real network (B = 1000);
  p_low = (1 + #T* <= T) / (B + 1).
- Also reported: dogs passing the authors' per-dog criterion (real RI below the null mean by
  >= 0.2) against each null; dogs with per-dog p <= 0.05 against the popularity null.
- Secondary (300 draws each): the other table at threshold 2; the primary table at threshold 1.
- Seed 20261121.

## 5. Verdict (primary table, threshold 2), first that applies

1. UNTESTABLE: fewer than 20 dogs in the group set, or g_er / g_pop not finite.
2. ER_GAP_ABSENT: g_er < 0.2 (the paper's gap does not appear in the public concept networks).
3. POPULARITY_EXPLAINS_MOST_OF_GAP: share explained >= 0.75.
4. STRUCTURE_BEYOND_POPULARITY: p_low <= 0.05.
5. INCONCLUSIVE.

With about 100 dogs the group test can detect a tiny residual, so the verdict rests on the share
explained first; p_low is reported with every verdict.

Readings. POPULARITY_EXPLAINS_MOST_OF_GAP: the network evidence for "non-random" combinations is
what unequal button use produces by itself; it says nothing against the paper's other analyses.
STRUCTURE_BEYOND_POPULARITY: dogs' networks are more hub-and-spoke than popularity alone makes
them, which strengthens the claim with a stricter null than the paper used.

## 6. Predictions (graded in the reading)

P1 g_er >= 0.2 on the primary table: 0.80.
P2 primary verdict: POPULARITY_EXPLAINS_MOST_OF_GAP 0.55, STRUCTURE_BEYOND_POPULARITY 0.20,
ER_GAP_ABSENT 0.15, INCONCLUSIVE 0.05, UNTESTABLE 0.05.
P3 fewer than half as many dogs pass the -0.2 criterion against the popularity null as against
the ER null: 0.75.
P4 at most 15% of group dogs have per-dog p <= 0.05 against the popularity null: 0.60.
P5 the threshold-1 secondary gives the same verdict as the primary: 0.60.

## 7. Limits known now

Concept-level networks (up to about 68 nodes, owner-assigned concepts) are not the paper's
button-label networks; the public tables do not say whether a "combination" is an adjacent pair or
any pair within one interaction. The popularity null keeps each concept's pairing count but not
which interactions it occurred in or their order. Owners logged the presses (possible reporting
bias, as the authors note). Two authors consulted for the app company and one works there; their
data are used here exactly as published.

## 8. Rules

The job (`gate.py`) computes nothing until this file and the code on GitHub main equal its
copies. A published plan is never edited; changes go in a dated AMENDMENT file. Technical
failures are fixed and re-run under a new version name with an amendment. Results are published
whatever they say.
