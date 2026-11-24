# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Checks that the counts quoted in READING-DOGBUTTON.md follow from the job's own output files
(results/per_dog.csv and results/dogbutton_results.json). Standard library only.

Run: python -m unittest -v test_reading_counts
"""
import csv
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PER_DOG = os.path.join(HERE, "results", "per_dog.csv")
RESULTS = os.path.join(HERE, "results", "dogbutton_results.json")
MARGIN = 0.2  # the authors' per-dog criterion: RI at least 0.2 below the Erdos-Renyi mean


def eligible_rows():
    with open(PER_DOG, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return rows, [r for r in rows if r["eligible"] == "True"]


class TestReadingCounts(unittest.TestCase):
    def test_eligible(self):
        rows, el = eligible_rows()
        self.assertEqual(len(rows), 176)
        self.assertEqual(len(el), 139)

    def test_criterion_on_popularity_networks(self):
        _, el = eligible_rows()
        fires = [r for r in el if float(r["ri_pop_mean"]) < float(r["ri_er_mean"]) - MARGIN]
        self.assertEqual(len(fires), 127)
        miss = [r for r in el if not float(r["ri_pop_mean"]) < float(r["ri_er_mean"]) - MARGIN]
        self.assertEqual(len(miss), 12)
        small = [r for r in miss if int(r["n_nodes"]) <= 6 and float(r["ri_er_mean"]) <= -0.58]
        self.assertEqual(len(small), 10)

    def test_quoted_primary_numbers(self):
        with open(RESULTS, encoding="utf-8") as fh:
            d = json.load(fh)
        p = d["primary"]
        self.assertEqual(d["primary_table"], "q2")
        self.assertEqual(p["verdict"], "POPULARITY_EXPLAINS_MOST_OF_GAP")
        self.assertEqual((p["n_subjects"], p["n_eligible"], p["n_group"]), (176, 139, 133))
        self.assertEqual(round(p["g_er"], 3), 0.356)
        self.assertEqual(round(p["share_explained"], 3), 1.566)
        self.assertEqual(round(p["ri_pop_mean"], 3), -0.766)
        self.assertEqual(round(p["ri_real_mean"], 3), -0.564)
        self.assertEqual((p["n_author_criterion_er"], p["n_author_criterion_pop"], p["n_dog_p05_pop"]),
                         (93, 24, 7))
        self.assertEqual(sum(p["hist_real"][4:]), 16)
        self.assertEqual(sum(p["hist_pop_mean"][4:]) + sum(p["hist_er_mean"][4:]), 0)


if __name__ == "__main__":
    unittest.main()
