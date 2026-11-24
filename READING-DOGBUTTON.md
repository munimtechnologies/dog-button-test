# dog-button-test: graded reading of job dogbutton-test-v1 (2026-11-24)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert
has checked this reading yet. Text CC BY 4.0. Every number below is copied from
[results/dogbutton_results.json](results/dogbutton_results.json),
[results/RESULTS-DOGBUTTON.md](results/RESULTS-DOGBUTTON.md) and
[results/per_dog.csv](results/per_dog.csv), written by the job that ran the code in this repository
on 2026-11-24 (14:01-14:22 UTC) after `gate.py` confirmed that DOGBUTTON-PREREG.md and the code on
GitHub were identical to the job's own copies. The authors' tables were fetched at their commit
23b3d2c933d9b72ca7f57cbe66ef247551d0b9fd; all 15,981 rows of question2_data.csv and 3,709 rows of
question3_data.csv parsed (0 fallback splits, 0 unparsed, 0 same-concept pairs).

## The claim tested

Bastos, Houghton, Naranjo and Rossano (2024), [Scientific Reports 14:28771](https://www.nature.com/articles/s41598-024-79517-6),
called soundboard-trained dogs' two-button combinations "non-random" partly because each dog's
network of button pairs had a strongly negative Randomness Index (RI, the correlation between a
node's degree and its mean local clustering; Meghanathan 2017), while Erdos-Renyi random graphs of the
same size and density had an RI near 0. An Erdos-Renyi graph gives every button the same chance of
being used. We asked whether unequal button use alone, with no preference for any particular pairing,
already produces the negative RI.

## Registered verdict: POPULARITY_EXPLAINS_MOST_OF_GAP

The rule fixed in DOGBUTTON-PREREG.md section 5: at least 20 dogs, an Erdos-Renyi gap of at least 0.2,
then a share explained by popularity of at least 0.75 gives POPULARITY_EXPLAINS_MOST_OF_GAP. The
primary table (question2, smallest count 1, so complete counts) gave 133 dogs in the group test, an
Erdos-Renyi gap of 0.356 and a share explained of 1.566.

## What the job found

| quantity (primary: question2, pairs seen at least twice) | value |
|---|---|
| dogs in the tables / with an eligible network / in the group test | 176 / 139 / 133 |
| mean real RI (median) | -0.564 (-0.796) |
| mean Erdos-Renyi null RI | -0.209 |
| mean popularity-only null RI | -0.766 |
| gap to Erdos-Renyi (null minus real) | 0.356 |
| gap to popularity-only null (null minus real) | -0.201 |
| share of the Erdos-Renyi gap explained by popularity | 1.566 |
| dogs passing the authors' -0.2 criterion against Erdos-Renyi | 93 of 133 |
| dogs passing the same criterion against popularity | 24 of 133 |
| dogs with per-dog p <= 0.05 against popularity | 7 of 133 |
| group p, real more negative than popularity (registered tail) | 1.0000 |

1. **The paper's gap is reproduced on the public concept networks.** The dogs' networks sit 0.356
   below Erdos-Renyi graphs of the same size and density on average, and 93 of 133 dogs pass the
   authors' own per-dog criterion (real RI at least 0.2 below the random mean).
2. **Popularity alone over-produces it.** When each dog's own pair events are re-paired at random so
   that every concept keeps exactly its number of pairings, the resulting networks have a mean RI of
   -0.766, more negative than the real -0.564. Popularity explains 157% of the Erdos-Renyi gap.
3. **The authors' criterion fires on popularity-only networks.** Applied to the average of 1,000
   popularity-only re-pairings of each eligible dog, the criterion "RI at least 0.2 below the
   Erdos-Renyi mean" fires for 127 of 139 dogs (0.914; counted from results/per_dog.csv by
   `test_reading_counts.py`). Ten of the 12 exceptions are networks of at most 6 concepts whose
   Erdos-Renyi RI is already -0.58 or lower.
4. **Robust to the registered variants.** The question3 table (96 dogs; share 1.208) and the
   question2 table with every pair kept (161 dogs; share 1.542) give the same verdict.

Seen in the registered code's output but not a registered test direction: the dogs' networks are
*less* hub-and-spoke than the popularity-only null (group p 0.001 in that tail on the primary table,
0.0033 with every pair kept, 0.023 on question3), and 16 of 133 real networks have an RI of 0.2 or more
while no dog's average null network (in either null) does. One mechanism consistent with it is the paper's own
"non-accidental" result: if a dog repeats particular pairs, a popular concept's events concentrate on
fewer partners than random re-pairing gives it, so fewer spokes pass the two-event threshold and the
network is less star-like. Features the null does not keep (press order, which interaction each
pairing came from) could also contribute. It is not evidence for the hub-and-spoke reading the RI was given, and it was not
registered, so we do not grade it.

## Predictions (priors from DOGBUTTON-PREREG.md section 6) and Brier score

| id | prediction | prior | outcome | Brier |
|---|---|---|---|---|
| P1 | Erdos-Renyi gap >= 0.2 on the primary table | 0.80 | yes (0.356) | 0.0400 |
| P2 | verdict POPULARITY_EXPLAINS_MOST_OF_GAP | 0.55 | yes | 0.2025 |
| P3 | fewer than half as many dogs pass the -0.2 criterion against popularity as against Erdos-Renyi | 0.75 | yes (24 against 93) | 0.0625 |
| P4 | at most 15% of group dogs have per-dog p <= 0.05 against popularity | 0.60 | yes (7 of 133, 5.3%) | 0.1600 |
| P5 | threshold-1 secondary gives the same verdict | 0.60 | yes | 0.1600 |

Mean Brier score 0.1250 (P2 scored on the realised verdict; over all five registered verdict
probabilities, 0.55 / 0.20 / 0.15 / 0.05 / 0.05, its multi-class Brier is 0.2700). We gave 0.20 to
structure beyond popularity in the registered direction; there was none.

## What this does and does not say

The network evidence for "non-random" combinations is what unequal button use produces on its own.
It says nothing against the paper's other two results: the population-level model in which some
concept pairs occur more often than their buttons' popularity predicts, and the comparison with
owners' presses (non-imitative). Those are not tested here.

## Limits

- **Concept level, not button level.** The authors' press log (export_08_23_2022.csv) is not public.
  Their RI was computed on button-label networks; the public tables give per-dog counts of concept
  pairs (up to 59 concepts per dog in results/per_dog.csv). Their code (network_analysis2.Rmd at the same commit) builds pairs
  from consecutive presses after removing repeated buttons; we assume the concept tables were built
  the same way, which the tables do not state.
- **Dog counts differ.** The paper reports 152 dogs; the public question2 table has 176 subjects, of
  which 139 have a network with at least 4 edges.
- **What the null keeps.** It keeps each concept's number of pairings and nothing else: not which
  interaction a pairing came from, not press order, not time.
- Owners log presses through the app (possible reporting bias, as the authors note). Two authors
  consulted for the app company and one works there; their data are used exactly as published.
- The work was carried out with AI agents working in MV2's name; no human expert has checked it.

## Prior work

Searched 2026-11-24 (web search for reanalyses or critiques of Bastos et al. 2024; for "randomness
index" with null models; Europe PMC for soundboard dog papers 2025-2026; the two published comments).
We found no reanalysis of the Randomness Index result. Kuhlmeier 2025 (Learning & Behavior,
doi:10.3758/s13420-025-00679-y; full text not read, summaries only) is reported to accept the
non-random result and question communicative intent;
Wayenberg 2026 (Frontiers in Animal Science, doi:10.3389/fanim.2026.1907975) questions semantics and
proposes event-level coding, and does not discuss the network null. The general point that falling
clustering with degree can come from degree structure rather than hierarchy is Soffer and Vazquez 2005
(Phys Rev E 71:057101); what is new here is the measurement for this claim, on the authors' data.
