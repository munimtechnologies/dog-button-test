# dog-button-test

An open, pre-registered test of whether the "non-random" network structure of soundboard-trained
dogs' two-button combinations (Bastos et al. 2024, Scientific Reports 14:28771) is more than what
unequal button popularity produces by itself. It reproduces the paper's Randomness Index and
Erdos-Renyi comparison on the authors' public concept-pair tables, then adds a popularity-only null
model that keeps every concept's number of pairings.

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human
expert has checked it yet. Code: Apache-2.0. Text and derived tables: CC BY 4.0.

## Status

| step | what | state |
|---|---|---|
| 1 | RI vs Erdos-Renyi null vs popularity null, per dog and pooled | registered 2026-11-21 ([DOGBUTTON-PREREG.md](DOGBUTTON-PREREG.md)); job queued |

## Files

- `DOGBUTTON-PREREG.md`: question, data, method, verdict rule and predictions, fixed before any result.
- `dogbutton_test.py`: the analysis (numpy only). `python dogbutton_test.py --out-dir OUT`. It fetches
  the authors' tables at a pinned commit; they are not copied here (their repository has no licence).
- `test_dogbutton_test.py`: unit tests (`python -m unittest -v test_dogbutton_test`).
- `gate.py`: the job computes nothing until these files on GitHub equal the job's copies.

## Credit

Data and the original analysis: Amalia P. M. Bastos, Zachary N. Houghton, Lucas Naranjo and Federico
Rossano; data collected through the FluentPet app (CleverPet). Their code and tables:
github.com/znhoughton/Modeling. This project only re-examines their public tables; any error here is ours.
