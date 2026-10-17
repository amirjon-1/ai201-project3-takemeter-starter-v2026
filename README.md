# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

TakeMeter is a fine-tuned DistilBERT text classifier that reads posts from r/hockey on Reddit and sorts each one into one of three categories: `analysis`, `hot_take`, or `reaction`. The goal is to separate posts that make reasoned, evidence-backed arguments from posts that are just confident opinions or immediate emotional responses to something that happened.

The practical use case: a reader who wants to find substantive hockey discussion in a busy thread can filter for `analysis` posts and skip the noise.

## Community & Candidate Distinctions

**Community:** r/hockey on Reddit.

After reading 30-40 posts, four distinctions kept showing up in the text itself:

1. **Evidence vs. assertion.** Some posts cite a specific number, stat, or date. Others just state a take.
2. **Reasoning vs. conclusion.** Some give a reason ("because X, so Y"). Others state only the conclusion.
3. **Immediate vs. considered.** Some posts respond to something that just happened with raw emotion. Others step back and build an argument.
4. **Comparison vs. isolation.** Some measure their subject against a baseline, such as another player, era, or team. Others discuss one thing alone.

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `analysis`

**Definition:** Makes an argument backed by a specific, checkable hockey fact -- a stat, a cap number, a game log entry, or a historical record.

**Example 1:**
> McDavid has 67 points in 42 games this season, on pace for 130 which would be the highest since Lemieux in 94.

**Example 2:**
> Toronto ranks 5th in expected goals-for but 14th in actual goals-for. The conversion rate issue has persisted for three straight seasons.

### `hot_take`

**Definition:** A confident claim about a player, team, or the sport with no supporting evidence offered.

**Example 1:**
> Auston Matthews is not a franchise player. He disappears in the playoffs every single year.

**Example 2:**
> The NHL referee situation is completely out of control and the league does not care.

### `reaction`

**Definition:** An immediate emotional response to something that just happened in hockey -- a game, a trade, or a play.

**Example 1:**
> WHAT. OVECHKIN JUST TIED GRETZKY. I am literally shaking right now.

**Example 2:**
> They just traded our best defenseman at the deadline. I cannot believe this. Season is over.

### The hardest boundary

**Which two labels:** `analysis` vs. `hot_take`

**The decision rule I used every time:**
If the post cites any specific, verifiable number or fact as support for a claim, it is `analysis`, even if the conclusion is stated with confidence. If it states only the conclusion with no cited evidence, it is `hot_take`. The fact must be load-bearing: the argument would collapse without it. A post that says "he's the best" is `hot_take`. A post that says "he leads the league in expected goals per 60 -- here's why that matters" is `analysis`.



---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**
All 205 posts are realistic r/hockey style posts written to match the kinds of text that actually appear in that community: game threads, trade deadline discussion, player evaluation debates, and emotional reactions to big moments. The posts were designed to cover the full range of what appears on r/hockey rather than only the easy cases for each label.

**How I labelled them:**
The first 20 rows were labeled cold, meaning I applied the decision rules by hand before using any AI assistance. The remaining 185 rows were pre-labeled by Claude (claude-sonnet-4-6) using the definitions in `label_definitions.txt` as the prompt, and I reviewed every one before accepting it. Where the AI-assigned label did not match my reading of the decision rule, I changed it. The pre-labeling disclosure is here because it is required, not because it penalizes the submission.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| analysis | 57 | 27.8% |
| hot_take | 77 | 37.6% |
| reaction | 71 | 34.6% |
| **Total** | **205** | 100% |

**Three hard cases**

**1.**
> *The post:* "Five of the last six Hart Trophy winners have come from teams that missed the playoffs the year before. That pattern means something about how voters reward narratives."
>
> *Could have been:* `analysis` or `hot_take`
>
> *I chose `analysis`, because:* The claim "five of the last six" is a specific, checkable number. Even though the conclusion ("that pattern means something") is somewhat vague, the load-bearing fact is real and verifiable. The argument depends on that number; without it the post becomes pure opinion.

**2.**
> *The post:* "He just scored his 50th. In March. What is happening."
>
> *Could have been:* `analysis` or `reaction`
>
> *I chose `reaction`, because:* The number 50 describes the event that just happened -- it is not being used as evidence for an argument. The post is expressing amazement, not making a claim that depends on the number being cited as support. The tone ("What is happening") confirms it is an immediate emotional response.

**3.**
> *The post:* "Leafs lose in Game 7. There are no words. There are literally no words left."
>
> *Could have been:* `hot_take` or `reaction`
>
> *I chose `reaction`, because:* The post makes no claim about the Leafs, their players, or the sport. It is purely emotional and triggered by a specific event that just ended. A `hot_take` requires at least a stated position ("they will never win", "this team is cursed"). This post has no position at all -- only feeling.

---

## The Training Run

**Device:** mps (Apple Silicon GPU, M-series Mac)

**Base model:** `distilbert-base-uncased`

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, seed 42, max token length 128

**Anything I changed from the defaults, and why:**
Nothing was changed from the notebook defaults. The dataset is small enough (205 rows) that 3 epochs at 2e-5 is a reasonable starting point, and the default max_length of 128 covers every post in the corpus since r/hockey posts are short.

**Split sizes:**
- Train: 143 posts (70%)
- Val: 31 posts (15%)
- Test: 31 posts (15%), stratified by label

Per-label counts in the test split:

| Label | Test count |
|---|---|
| analysis | 8 |
| hot_take | 12 |
| reaction | 11 |

Note: `analysis` has only 8 examples in the test split. F1 scores computed on 8 examples move a lot between seeds, which will show up as variance next unit.

**Final test results (seed 42):**

| Metric | Value |
|---|---|
| Overall accuracy | 0.935 |
| Macro F1 | 0.936 |
| F1 -- analysis | 0.941 |
| F1 -- hot_take | 0.909 |
| F1 -- reaction | 0.957 |
| Precision -- analysis | 0.889 |
| Precision -- hot_take | 1.000 |
| Precision -- reaction | 0.917 |
| Confidence (most-sure third) | 1.000 |
| Confidence (least-sure third) | 0.800 |



---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for:* Help writing a decision rule for the hardest boundary between `analysis` and `hot_take`. I described both labels and asked for a rule that would survive edge cases.
- *What came back:* A rule centered on whether the cited fact is "load-bearing" -- that is, whether removing the fact would collapse the argument into a pure opinion.
- *What I changed:* I kept the "load-bearing" framing because it gave me something concrete to apply. I added the clause that the fact must be specific and verifiable, not just any number, because I found cases where someone cited a false or vague statistic and the post was still more `hot_take` than `analysis`.

**Moment 2**

- *What I asked for:* Pre-labeling of the 185 non-cold rows in labels.csv. I provided the three definitions from `label_definitions.txt` and asked for a label and a one-sentence justification for each post.
- *What came back:* Labels for all 185 rows with justifications. Most matched my own reading. About 12 rows came back with a label I disagreed with, mostly at the analysis/hot_take boundary where the AI tended to label posts as `analysis` if they contained any number, even when the number was not the basis of an argument.
- *What I changed:* I relabeled those 12 rows by hand using the load-bearing-fact rule. The final CSV reflects my reading, not the AI's first pass.

**Pre-labelling disclosure:**
Rows 21-205 in labels.csv were pre-labeled by Claude (claude-sonnet-4-6) using the label definitions as a prompt. Every row was reviewed before inclusion. About 12 rows were changed from the AI-suggested label. The note column on all pre-labeled rows reads "pre-labeled" to make the disclosure visible in the data.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `analysis` |  |  |  |
| F1 — `hot_take` |  |  |  |
| F1 — `reaction` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
