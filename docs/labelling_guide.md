# Labelling guide: the real-world citation set (experiment E4)

Owner: Users & Research, reviewed by Data & Evaluation.  Tooling: `tools/realworld_set.py`.

## What you label

Each item is one **real citing sentence** from a published paper (the claim, with its citation markers removed) and the
**abstract of the paper it cites**. You answer one question:

> Judging only from this abstract, does the cited paper support the claim the sentence makes about it?

| label | use it when |
|---|---|
| `SUPPORT` | the abstract states or directly reports what the claim says it does (same finding, same direction, compatible population or setting) |
| `CONTRADICT` | the abstract reports the opposite, a null result for what the claim says was found, or a clearly different population/condition presented as the same |
| `NEI` | the abstract neither supports nor contradicts it: the claim may be supported in the paper's body, the claim is too general, or you are unsure |
| `SKIP` | the item is unusable: not a claim (e.g. "as described in [3]"), garbled text, or the abstract is missing or in another language |

## Rules

1. **Abstract only.** Do not open the paper or search the web. The product reads the abstract first; we need to know what
   the abstract alone allows.
2. **Unsure means `NEI`.** Do not guess `SUPPORT`.
3. **Partial support** (the abstract supports part of the claim, the rest is not mentioned): `NEI`, and write `partial`
   in `note`.
4. **Overstatement** (claim says "cures", abstract says "associated with"; claim says "in humans", abstract is in mice):
   `CONTRADICT` if the abstract clearly limits the finding, otherwise `NEI`; write `overstated` in `note`.
5. **Label alone.** The two labellers do not discuss items until both sheets are done and `kappa` has been run.
6. Keep a note for every `CONTRADICT` and `SKIP`, in a few words.

## Procedure

1. Seeds: `data/realworld/seeds.csv`, about half biomedical and half computer science papers (field, DOI or arXiv id).
2. `python -m tools.realworld_set candidates --seeds data/realworld/seeds.csv --per-paper 6` writes
   `data/cache/realworld/items_A.csv` and `items_B.csv` (git-ignored: they contain text from Semantic Scholar).
3. Labeller A fills `items_A.csv`, labeller B fills `items_B.csv` (Excel is fine; keep the columns; save as CSV UTF-8).
4. `python -m tools.realworld_set kappa data/cache/realworld/items_A.csv data/cache/realworld/items_B.csv --json evidence/realworld_kappa_v1.json`
5. Target (`docs/north_star.md`): Cohen's kappa at least 0.6. Below that, discuss the disagreements, sharpen this guide,
   and relabel a fresh batch. Report kappa either way.
6. Adjudicate: for each disagreement, agree a label together and write it in a `final_label` column of sheet A.
7. `python -m tools.realworld_set merge data/cache/realworld/items_A.csv` writes the gold file for the evaluation
   (`data/cache/realworld/gold_v1.jsonl`, with text, not committed) and `data/realworld/labels_v1.csv` (ids and labels
   only: commit it).

## Examples (invented, to calibrate; not from the set)

| claim | abstract says | label |
|---|---|---|
| Zorvex increases bone density in adult mice. | "Zorvex supplementation significantly increased femoral bone density compared with controls." (mice) | `SUPPORT` |
| Zorvex increases bone density in humans. | the same mouse study | `NEI`, note `overstated` (`CONTRADICT` only if the abstract says it did not work in humans) |
| Zorvex has no effect on bone density. | the same mouse study | `CONTRADICT` |
| Zorvex is widely used in clinics. | the same mouse study | `NEI` |
| As described in [12], we used the standard protocol. | any | `SKIP` |
