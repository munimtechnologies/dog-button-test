# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""dog-button-test: is the "non-random" network structure of soundboard-trained dogs' two-button
combinations (Bastos, Houghton, Naranjo & Rossano 2024, Sci Rep 14:28771) more than what each
button concept's popularity produces on its own? See DOGBUTTON-PREREG.md.

The authors' Randomness Index (RI) is the Pearson correlation, over degree values k, between k and
the mean local clustering coefficient of nodes with degree k, in each dog's network of button
pairs seen more than once. They compared it with Erdos-Renyi G(n, p) graphs of the same size and
density. Here the same RI is also compared with a popularity-only null: the dog's own pair events
re-paired at random (stub matching) so that every concept keeps exactly its number of pairings.

The authors' public tables (github.com/znhoughton/Modeling, no licence file) are fetched at a
pinned commit at run time and never copied into this repository.

Run:  python dogbutton_test.py --out-dir /out
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request

import numpy as np

AUTHORS_SHA = "23b3d2c933d9b72ca7f57cbe66ef247551d0b9fd"
RAW = ("https://raw.githubusercontent.com/znhoughton/Modeling/" + AUTHORS_SHA +
       "/Methods/Button%20Combinations/Data/")
FILES = {"q2": "question2_data.csv", "q3": "question3_data.csv", "concepts": "concept%20list.csv"}
SEED = 20261121
R_PRIMARY = 1000
R_SECONDARY = 300
THRESH = 2              # the authors keep pairs seen more than once (weight > 1)
MIN_EDGES = 4           # the authors' index returns NA below 4 edges
MIN_FINITE_SHARE = 0.5
MIN_DOGS = 20
ER_GAP_MIN = 0.2
SHARE_OK = 0.75
ALPHA = 0.05
AUTHOR_MARGIN = 0.2     # the authors' per-dog criterion: real RI below the null mean by >= 0.2


def nan():
    return float("nan")


def safe_mean(v):
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    return float(v.mean()) if v.size else nan()


def canon(s):
    """Upper-case letters and digits only: 'PLAY-ALL', 'PLAY_ALL' and 'play all' all -> 'PLAYALL'."""
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def parse_combo(cid, concepts):
    """'A_B' combination id -> (canon A, canon B, how) using the concept list to place the split;
    a single underscore with no listed match falls back to that split; else None."""
    cid = (cid or "").strip()
    valid = []
    for i, ch in enumerate(cid):
        if ch != "_":
            continue
        a, b = canon(cid[:i]), canon(cid[i + 1:])
        if a in concepts and b in concepts:
            valid.append((a, b))
    if len(valid) == 1:
        return valid[0][0], valid[0][1], "unique"
    if not valid and cid.count("_") == 1:
        a, b = (canon(x) for x in cid.split("_"))
        if a and b:
            return a, b, "fallback"
    return None


def read_rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def build_counts(rows, concepts):
    """{subject: {(a, b): pair events}} with a < b; self pairs and unparsed ids are counted."""
    counts = {}
    stats = {"rows": 0, "unique": 0, "fallback": 0, "unparsed": 0, "self": 0, "bad_freq": 0}
    for r in rows:
        stats["rows"] += 1
        try:
            f = int(round(float(r.get("combination_freq", ""))))
        except (TypeError, ValueError):
            stats["bad_freq"] += 1
            continue
        got = parse_combo(r.get("combination_id"), concepts)
        if got is None:
            stats["unparsed"] += 1
            continue
        a, b, how = got
        stats[how] += 1
        if a == b:
            stats["self"] += 1
            continue
        if f <= 0:
            stats["bad_freq"] += 1
            continue
        key = (a, b) if a < b else (b, a)
        d = counts.setdefault(str(r.get("subject", "")).strip(), {})
        d[key] = d.get(key, 0) + f
    return counts, stats


def graph_from_counts(pairs, thresh=THRESH):
    """Simple undirected graph of the pairs with at least thresh events; nodes = their concepts."""
    edges = [k for k, w in pairs.items() if w >= thresh]
    nodes = sorted({x for e in edges for x in e})
    ix = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=bool)
    for a, b in edges:
        A[ix[a], ix[b]] = True
        A[ix[b], ix[a]] = True
    return nodes, A


def local_clustering(A):
    """Degrees and igraph-style local transitivity (NaN for degree < 2)."""
    A = np.asarray(A, dtype=float)
    deg = A.sum(axis=1)
    tri = np.einsum("ij,jk,ki->i", A, A, A) / 2.0
    with np.errstate(divide="ignore", invalid="ignore"):
        C = tri / (deg * (deg - 1.0) / 2.0)
    C[deg < 2] = np.nan
    return deg, C


def randomness_index(A):
    """The authors' RI: Pearson correlation between each degree value k and the plain mean of
    the clustering of nodes with degree k (a class containing NaN is NaN and is skipped)."""
    deg, C = local_clustering(A)
    if deg.size == 0:
        return nan()
    ks, means = [], []
    for k in np.unique(deg):
        m = float(np.mean(C[deg == k]))
        if np.isfinite(m):
            ks.append(float(k))
            means.append(m)
    if len(ks) < 2:
        return nan()
    ks = np.array(ks)
    means = np.array(means)
    if ks.std() == 0 or means.std() == 0:
        return nan()
    return float(np.corrcoef(ks, means)[0, 1])


def er_graph(n, p, rng):
    U = np.triu(rng.random((n, n)) < p, k=1)
    return U | U.T


def stub_pairs(strength, rng):
    """Random perfect matching of stubs: node i has strength[i] stubs. Returns (M, 2) node pairs."""
    s = np.asarray(strength, dtype=int)
    stubs = np.repeat(np.arange(s.size), s)
    if stubs.size % 2:
        raise ValueError("odd number of stubs")
    stubs = stubs[rng.permutation(stubs.size)]
    return stubs.reshape(-1, 2)


def pop_graph(strength, rng, thresh=THRESH):
    """Popularity-only network: re-pair the dog's pair events at random keeping every concept's
    number of pairings, drop self pairs, keep pairs with >= thresh events."""
    pr = stub_pairs(strength, rng)
    pr = pr[pr[:, 0] != pr[:, 1]]
    n = len(strength)
    W = np.zeros((n, n), dtype=int)
    np.add.at(W, (pr[:, 0], pr[:, 1]), 1)
    W = W + W.T
    A = W >= thresh
    keep = A.any(axis=1)
    return A[np.ix_(keep, keep)]


def strengths(pairs):
    labels = sorted({x for k in pairs for x in k})
    ix = {v: i for i, v in enumerate(labels)}
    s = np.zeros(len(labels), dtype=int)
    for (a, b), w in pairs.items():
        s[ix[a]] += w
        s[ix[b]] += w
    return labels, s


def analyse_dog(pairs, rng, R, thresh=THRESH):
    nodes, A = graph_from_counts(pairs, thresh)
    n = len(nodes)
    m = int(np.triu(A, 1).sum())
    out = {"n_nodes": n, "n_edges": m, "pair_events": int(sum(pairs.values())),
           "n_concepts": len({x for k in pairs for x in k})}
    out["ri_real"] = randomness_index(A) if n else nan()
    out["eligible"] = bool(m >= MIN_EDGES and np.isfinite(out["ri_real"]))
    if not out["eligible"]:
        return out, None, None
    p = 2.0 * m / (n * (n - 1.0))
    er = np.array([randomness_index(er_graph(n, p, rng)) for _ in range(R)])
    _, s = strengths(pairs)
    pop = np.array([randomness_index(pop_graph(s, rng, thresh)) for _ in range(R)])
    fpop = pop[np.isfinite(pop)]
    out["ri_er_mean"] = safe_mean(er)
    out["ri_pop_mean"] = safe_mean(pop)
    out["er_finite"] = int(np.isfinite(er).sum())
    out["pop_finite"] = int(fpop.size)
    out["p_dog_pop"] = (float((1.0 + np.sum(fpop <= out["ri_real"])) / (1.0 + fpop.size))
                        if fpop.size else nan())
    return out, er, pop


def group_test(real, sims, B=None):
    """T = mean over dogs of (real RI - mean null RI). Null distribution: T* with one null draw
    per dog standing in for the real network. p_low: real more negative than the null."""
    keep = [i for i, s in enumerate(sims)
            if s is not None and np.isfinite(real[i])
            and np.isfinite(s).sum() >= MIN_FINITE_SHARE * s.size and np.isfinite(s).sum() > 0]
    if not keep:
        return {"n_dogs": 0, "T": nan(), "p_low": nan(), "p_high": nan(), "B": 0}
    fs = [sims[i][np.isfinite(sims[i])] for i in keep]
    mus = [float(f.mean()) for f in fs]
    r = np.array([real[i] for i in keep], dtype=float)
    T = float(np.mean(r - np.array(mus)))
    if B is None:
        B = max(f.size for f in fs)
    Tn = np.array([np.mean([f[b % f.size] - mu for f, mu in zip(fs, mus)]) for b in range(B)])
    return {"n_dogs": len(keep), "T": T,
            "p_low": float((1.0 + np.sum(Tn <= T)) / (B + 1.0)),
            "p_high": float((1.0 + np.sum(Tn >= T)) / (B + 1.0)),
            "T_null_sd": float(Tn.std()), "B": int(B), "kept": keep}


def verdict(n_dogs, g_er, g_pop, p_low):
    if n_dogs < MIN_DOGS or not np.isfinite(g_er) or not np.isfinite(g_pop):
        return "UNTESTABLE"
    if g_er < ER_GAP_MIN:
        return "ER_GAP_ABSENT"
    share = 1.0 - g_pop / g_er
    if share >= SHARE_OK:
        return "POPULARITY_EXPLAINS_MOST_OF_GAP"
    if np.isfinite(p_low) and p_low <= ALPHA:
        return "STRUCTURE_BEYOND_POPULARITY"
    return "INCONCLUSIVE"


def analyse(counts, rng, R, thresh=THRESH):
    """Every dog, then the group comparison on dogs with enough finite null draws in both nulls."""
    per = {}
    er_s, pop_s, real = [], [], []
    subjects = sorted(counts, key=lambda x: (len(x), x))
    for subj in subjects:
        out, er, pop = analyse_dog(counts[subj], rng, R, thresh)
        per[subj] = out
        if out["eligible"]:
            ok = (out["er_finite"] >= MIN_FINITE_SHARE * R and out["pop_finite"] >= MIN_FINITE_SHARE * R)
            out["in_group"] = bool(ok)
            if ok:
                real.append(out["ri_real"])
                er_s.append(er)
                pop_s.append(pop)
    res = {"n_subjects": len(subjects), "n_eligible": int(sum(v["eligible"] for v in per.values())),
           "n_group": len(real), "R": R, "thresh": thresh}
    if real:
        r = np.array(real)
        er_m = np.array([safe_mean(e) for e in er_s])
        pop_m = np.array([safe_mean(p) for p in pop_s])
        res["ri_real_mean"] = float(r.mean())
        res["ri_real_median"] = float(np.median(r))
        res["ri_er_mean"] = float(er_m.mean())
        res["ri_pop_mean"] = float(pop_m.mean())
        res["g_er"] = float(np.mean(er_m - r))
        res["g_pop"] = float(np.mean(pop_m - r))
        res["share_explained"] = (1.0 - res["g_pop"] / res["g_er"]) if res["g_er"] > 0 else nan()
        res["n_author_criterion_er"] = int(np.sum(r < er_m - AUTHOR_MARGIN))
        res["n_author_criterion_pop"] = int(np.sum(r < pop_m - AUTHOR_MARGIN))
        pd = np.array([per[s]["p_dog_pop"] for s in subjects if per[s].get("in_group")])
        res["n_dog_p05_pop"] = int(np.sum(pd <= ALPHA))
        gt = group_test(r, pop_s)
        gt.pop("kept", None)
        res["group_pop"] = gt
        res["hist_bins"] = [-2.0, -1.0, -0.6, -0.2, 0.2, 0.6, 1.0, 2.0]
        res["hist_real"] = np.histogram(r, bins=res["hist_bins"])[0].tolist()
        res["hist_er_mean"] = np.histogram(er_m, bins=res["hist_bins"])[0].tolist()
        res["hist_pop_mean"] = np.histogram(pop_m, bins=res["hist_bins"])[0].tolist()
    else:
        res.update({"g_er": nan(), "g_pop": nan(), "share_explained": nan(),
                    "group_pop": {"n_dogs": 0, "T": nan(), "p_low": nan(), "p_high": nan(), "B": 0}})
    res["verdict"] = verdict(res["n_group"], res["g_er"], res["g_pop"], res["group_pop"]["p_low"])
    return res, per


def fetch(name, tries=3):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(RAW + name, timeout=120) as r:
                return r.read().decode("utf-8-sig")
        except Exception as exc:  # noqa: BLE001
            print("fetch %s attempt %d failed: %s" % (name, attempt + 1, exc), flush=True)
            time.sleep(20)
    raise SystemExit("could not fetch %s; nothing computed" % name)


def describe_table(rows):
    fr = []
    for r in rows:
        try:
            fr.append(int(round(float(r.get("combination_freq", "")))))
        except (TypeError, ValueError):
            pass
    subj = {str(r.get("subject", "")).strip() for r in rows}
    return {"rows": len(rows), "subjects": len(subj), "min_freq": min(fr) if fr else None,
            "max_freq": max(fr) if fr else None, "pair_events": int(sum(fr))}


def fmt(v, nd=3):
    if isinstance(v, float):
        return "nan" if v != v else ("%." + str(nd) + "f") % v
    return str(v)


def render(out):
    P = out["primary"]
    L = ["# RESULTS-DOGBUTTON: is the dogs' 'non-random' button network more than button popularity?",
         "", "Rendered by dogbutton_test.py (pre-registration: DOGBUTTON-PREREG.md). Made with AI agents",
         "working in MV2's name; no human expert has checked it yet.", "",
         "Primary table: %s (threshold: pairs seen >= %d times). Primary verdict: **%s**" % (
             out["primary_table"], P["thresh"], P["verdict"]), "",
         "| quantity | primary | %s |" % " | ".join(k for k in out["secondary"]),
         "|---|---|" + "---|" * len(out["secondary"])]
    rowsdef = [("dogs in group test", "n_group", 0), ("mean real RI", "ri_real_mean", 3),
               ("median real RI", "ri_real_median", 3),
               ("mean Erdos-Renyi null RI", "ri_er_mean", 3), ("mean popularity null RI", "ri_pop_mean", 3),
               ("gap to Erdos-Renyi (null - real)", "g_er", 3),
               ("gap to popularity null (null - real)", "g_pop", 3),
               ("share of ER gap explained by popularity", "share_explained", 3),
               ("dogs passing the authors' -0.2 criterion vs ER", "n_author_criterion_er", 0),
               ("dogs passing the -0.2 criterion vs popularity", "n_author_criterion_pop", 0),
               ("dogs with per-dog p <= 0.05 vs popularity", "n_dog_p05_pop", 0)]
    for label, key, nd in rowsdef:
        vals = [P.get(key)] + [v.get(key) for v in out["secondary"].values()]
        L.append("| %s | %s |" % (label, " | ".join(fmt(v, nd) for v in vals)))
    gl = [P["group_pop"]] + [v["group_pop"] for v in out["secondary"].values()]
    L.append("| group p (real more negative than popularity null) | %s |" % " | ".join(
        fmt(g.get("p_low"), 4) for g in gl))
    L.append("| verdict | %s |" % " | ".join([P["verdict"]] + [v["verdict"] for v in out["secondary"].values()]))
    L += ["", "Tables: %s" % json.dumps(out["tables"]), "",
          "Parsing: %s" % json.dumps(out["parse"]), "",
          "Histogram of per-dog RI (bins %s): real %s, ER-null mean %s, popularity-null mean %s" % (
              P.get("hist_bins"), P.get("hist_real"), P.get("hist_er_mean"), P.get("hist_pop_mean")), ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    text = {k: fetch(v) for k, v in FILES.items()}
    concepts = {canon(r.get("concept")) for r in read_rows(text["concepts"])} - {""}
    rows = {k: read_rows(text[k]) for k in ("q2", "q3")}
    tables = {k: describe_table(v) for k, v in rows.items()}
    print("tables: %s" % json.dumps(tables), flush=True)
    if tables["q2"]["min_freq"] == 1:
        primary = "q2"
    elif tables["q3"]["min_freq"] == 1:
        primary = "q3"
    else:
        primary = "q2"
    other = "q3" if primary == "q2" else "q2"
    counts, parse = {}, {}
    for k in ("q2", "q3"):
        counts[k], parse[k] = build_counts(rows[k], concepts)
    print("parsing: %s" % json.dumps(parse), flush=True)
    rng = np.random.default_rng(SEED)
    prim, per = analyse(counts[primary], rng, R_PRIMARY, THRESH)
    print("primary %s: %s" % (primary, json.dumps({k: v for k, v in prim.items() if not k.startswith("hist")})),
          flush=True)
    sec = {}
    sec["%s_thresh2" % other], _ = analyse(counts[other], rng, R_SECONDARY, THRESH)
    sec["%s_thresh1" % primary], _ = analyse(counts[primary], rng, R_SECONDARY, 1)
    out = {"primary_table": primary, "primary": prim, "secondary": sec, "tables": tables,
           "parse": parse, "n_concepts_listed": len(concepts), "authors_sha": AUTHORS_SHA,
           "seed": SEED, "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(a.out_dir, "dogbutton_results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    with open(os.path.join(a.out_dir, "per_dog.csv"), "w", newline="", encoding="utf-8") as fh:
        cols = ["subject", "n_concepts", "pair_events", "n_nodes", "n_edges", "eligible", "ri_real",
                "ri_er_mean", "ri_pop_mean", "p_dog_pop"]
        w = csv.writer(fh)
        w.writerow(cols)
        for s, v in per.items():
            w.writerow([s] + [v.get(c, "") for c in cols[1:]])
    with open(os.path.join(a.out_dir, "RESULTS-DOGBUTTON.md"), "w", encoding="utf-8") as fh:
        fh.write(render(out))
    print(json.dumps({"verdict": prim["verdict"], "g_er": prim.get("g_er"), "g_pop": prim.get("g_pop"),
                      "share": prim.get("share_explained"), "p_low": prim["group_pop"]["p_low"],
                      "seconds": out["seconds"]}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
