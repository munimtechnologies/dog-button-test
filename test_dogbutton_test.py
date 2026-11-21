# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Unit tests for dogbutton_test.py (numpy only; synthetic data, no network)."""
import unittest

import numpy as np

import dogbutton_test as db


def triangle_pendant():
    A = np.zeros((4, 4), dtype=bool)
    for a, b in [(0, 1), (0, 2), (1, 2), (0, 3)]:
        A[a, b] = A[b, a] = True
    return A


class TestParsing(unittest.TestCase):
    def test_canon(self):
        self.assertEqual(db.canon("PLAY-ALL"), "PLAYALL")
        self.assertEqual(db.canon("go outside"), "GOOUTSIDE")
        self.assertEqual(db.canon(None), "")

    def test_parse_combo(self):
        c = {"ALLDONE", "GOOUTSIDE", "FOOD", "PLAYALL", "PERSONPARENT"}
        self.assertEqual(db.parse_combo("ALLDONE_GOOUTSIDE", c), ("ALLDONE", "GOOUTSIDE", "unique"))
        self.assertEqual(db.parse_combo("FOOD_PLAY_ALL", c), ("FOOD", "PLAYALL", "unique"))
        self.assertEqual(db.parse_combo("PERSON_PARENT_PLAY_ALL", c),
                         ("PERSONPARENT", "PLAYALL", "unique"))
        self.assertEqual(db.parse_combo("XX_YY", c), ("XX", "YY", "fallback"))
        self.assertIsNone(db.parse_combo("Q_R_S", c))
        self.assertIsNone(db.parse_combo("A_B_C", {"A", "AB", "BC", "C"}))

    def test_build_counts(self):
        rows = [{"subject": "7", "combination_id": "FOOD_WALK", "combination_freq": "3"},
                {"subject": "7", "combination_id": "WALK_FOOD", "combination_freq": "2"},
                {"subject": "7", "combination_id": "FOOD_FOOD", "combination_freq": "4"},
                {"subject": "8", "combination_id": "FOOD_WALK", "combination_freq": "x"},
                {"subject": "8", "combination_id": "A_B_C", "combination_freq": "1"}]
        counts, stats = db.build_counts(rows, {"FOOD", "WALK"})
        self.assertEqual(counts, {"7": {("FOOD", "WALK"): 5}})
        self.assertEqual(stats["self"], 1)
        self.assertEqual(stats["bad_freq"], 1)
        self.assertEqual(stats["unparsed"], 1)
        self.assertEqual(stats["unique"], 3)


class TestNetwork(unittest.TestCase):
    def test_graph_from_counts(self):
        nodes, A = db.graph_from_counts({("A", "B"): 3, ("B", "C"): 1, ("A", "C"): 2}, 2)
        self.assertEqual(nodes, ["A", "B", "C"])
        self.assertEqual(A.astype(int).tolist(), [[0, 1, 1], [1, 0, 0], [1, 0, 0]])
        nodes, A = db.graph_from_counts({("A", "B"): 1}, 2)
        self.assertEqual(nodes, [])
        self.assertEqual(A.shape, (0, 0))

    def test_clustering_and_ri(self):
        deg, C = db.local_clustering(triangle_pendant())
        self.assertEqual(deg.tolist(), [3.0, 2.0, 2.0, 1.0])
        self.assertAlmostEqual(C[0], 1.0 / 3.0)
        self.assertAlmostEqual(C[1], 1.0)
        self.assertTrue(np.isnan(C[3]))
        self.assertAlmostEqual(db.randomness_index(triangle_pendant()), -1.0)

    def test_ri_undefined(self):
        path = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=bool)
        self.assertTrue(np.isnan(db.randomness_index(path)))
        self.assertTrue(np.isnan(db.randomness_index(np.zeros((0, 0), dtype=bool))))

    def test_er_graph_extremes(self):
        rng = np.random.default_rng(0)
        full = db.er_graph(5, 1.0, rng)
        self.assertEqual(int(full.sum()), 20)
        self.assertFalse(full.diagonal().any())
        self.assertTrue((full == full.T).all())
        self.assertEqual(int(db.er_graph(5, 0.0, rng).sum()), 0)

    def test_stub_pairs_keep_strength(self):
        rng = np.random.default_rng(1)
        s = np.array([5, 3, 2, 0, 4])
        for _ in range(5):
            pr = db.stub_pairs(s, rng)
            self.assertEqual(pr.shape, (7, 2))
            self.assertEqual(np.bincount(pr.ravel(), minlength=5).tolist(), s.tolist())
        with self.assertRaises(ValueError):
            db.stub_pairs(np.array([1, 2]), rng)

    def test_pop_graph_is_simple(self):
        rng = np.random.default_rng(2)
        A = db.pop_graph(np.array([10, 8, 6, 4, 2]), rng, 1)
        self.assertTrue((A == A.T).all())
        self.assertFalse(A.diagonal().any())
        self.assertTrue(A.any(axis=1).all())

    def test_strengths(self):
        labels, s = db.strengths({("A", "B"): 3, ("A", "C"): 2})
        self.assertEqual(labels, ["A", "B", "C"])
        self.assertEqual(s.tolist(), [5, 3, 2])


class TestGroupAndVerdict(unittest.TestCase):
    def test_group_test_table(self):
        g = db.group_test(np.array([-0.5, -0.5]), [np.zeros(4), np.zeros(4)])
        self.assertEqual(g["n_dogs"], 2)
        self.assertAlmostEqual(g["T"], -0.5)
        self.assertAlmostEqual(g["p_low"], 0.2)
        self.assertAlmostEqual(g["p_high"], 1.0)

    def test_group_test_empty(self):
        g = db.group_test(np.array([float("nan")]), [np.zeros(4)])
        self.assertEqual(g["n_dogs"], 0)
        self.assertTrue(np.isnan(g["p_low"]))

    def test_verdicts(self):
        self.assertEqual(db.verdict(10, 0.8, 0.1, 0.01), "UNTESTABLE")
        self.assertEqual(db.verdict(50, float("nan"), 0.1, 0.01), "UNTESTABLE")
        self.assertEqual(db.verdict(50, 0.1, 0.0, 0.01), "ER_GAP_ABSENT")
        self.assertEqual(db.verdict(50, 0.8, 0.1, 0.01), "POPULARITY_EXPLAINS_MOST_OF_GAP")
        self.assertEqual(db.verdict(50, 0.8, 0.4, 0.01), "STRUCTURE_BEYOND_POPULARITY")
        self.assertEqual(db.verdict(50, 0.8, 0.4, 0.3), "INCONCLUSIVE")

    def test_analyse_structure(self):
        counts = {"1": {("A", "B"): 3, ("A", "C"): 3, ("B", "C"): 3, ("A", "D"): 3},
                  "2": {("A", "B"): 5}}
        res, per = db.analyse(counts, np.random.default_rng(3), 20, 2)
        self.assertEqual(res["n_subjects"], 2)
        self.assertEqual(res["n_eligible"], 1)
        self.assertFalse(per["2"]["eligible"])
        self.assertTrue(per["1"]["eligible"])
        self.assertEqual(per["1"]["n_edges"], 4)
        self.assertAlmostEqual(per["1"]["ri_real"], -1.0)
        self.assertEqual(res["verdict"], "UNTESTABLE")


if __name__ == "__main__":
    unittest.main()
