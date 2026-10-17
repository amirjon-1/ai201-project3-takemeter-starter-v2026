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
> Carlsson also now has 11 goals since the NHL returned from the Four Nations Face-Off break and only five players in the league have more in that span.

**Example 2:**
> Starting from 07-08 when Hockey-Reference has data, his 5 on 5 CF% are 63.6, 60.4, 57.4, 55.7, 59.6, 57.5, 55.6, 59.8, 57.2. And that's ages 29-37. He's underrated offensively.

### `hot_take`

**Definition:** A confident claim about a player, team, or the sport with no supporting evidence offered.

**Example 1:**
> Not laughing he's an incredible player just entirely overrated by social media. He's routinely talked about in vague platitudes about his play.

**Example 2:**
> Bedard is going to be the #2 in the league in the coming years

### `reaction`

**Definition:** An immediate emotional response to something that just happened in hockey -- a game, a trade, or a play.

**Example 1:**
> It's only preseason and I am *hyped* Our young guys look super promising...I know we're not going to be good this year but I'm just excited to see some direction.

**Example 2:**
> Never in my life did I think I'd be cheering for Corey Perry

### The hardest boundary

**Which two labels:** `analysis` vs. `hot_take`

**The decision rule I used every time:**
If the post cites any specific, verifiable number or fact as support for a claim, it is `analysis`, even if the conclusion is stated with confidence. If it states only the conclusion with no cited evidence, it is `hot_take`. The fact must be load-bearing: the argument would collapse without it. A post that says "he's the best" is `hot_take`. A post that says "he leads the league in expected goals per 60 -- here's why that matters" is `analysis`.



---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**
All 195 rows are real r/hockey posts and comments collected programmatically from the Arctic Shift API (a free successor to Pushshift that provides historical Reddit data without authentication). The collection script (`scripts/build_labels.py`) pulled from two source files: `data/raw_posts.json` (163 unique posts with body text) and `data/raw_comments.json` (713 comments from game threads and discussion threads). No posts were written or invented. Every row of text in labels.csv was copied verbatim from the scraped Reddit data.

**How I labelled them:**
The first 20 rows were labeled cold, meaning I applied the decision rules entirely by hand to anchor the label definitions before running any automated step. The remaining rows were labeled in two passes: a manual list of 118 text snippets matched to their source posts and assigned labels by hand, then a keyword-based heuristic sweep over the remaining scraped data to fill out the dataset. The heuristics flagged posts as clearly one label and added them up to a per-label cap of 90. Every heuristic-labeled row was reviewed for plausibility. The note column on all non-cold rows reads "pre-labeled" to mark where heuristic assistance was used.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| analysis | 60 | 30.8% |
| hot_take | 57 | 29.2% |
| reaction | 78 | 40.0% |
| **Total** | **195** | 100% |

**Three hard cases**

**1.**
> *The post:* "Starting from 07-08 when Hockey-Reference has data, his 5 on 5 CF% are 63.6, 60.4, 57.4, 55.7, 59.6, 57.5, 55.6, 59.8, 57.2. And that's ages 29-37. He's underrated offensively."
>
> *Could have been:* `analysis` or `hot_take`
>
> *I chose `analysis`, because:* The string of CF% numbers is the load-bearing evidence. The claim "underrated offensively" is stated at the end, but it follows directly from the sustained Corsi numbers and collapses without them. A `hot_take` is the claim alone with no cited support. This post has the support.

**2.**
> *The post:* "Dude had a career high of 6 goals last season. Absolutely unreal."
>
> *Could have been:* `analysis` or `reaction`
>
> *I chose `analysis`, because:* The number 6 is being used as evidence, not just as a description of a live event. The post is citing a season-total stat to argue that the player underperformed, not reacting to a moment that just happened. "Absolutely unreal" is the conclusion, and the career-high stat is what makes the argument.

**3.**
> *The post:* "5 minutes in and we have 0 shots on goal lol. Oh boy"
>
> *Could have been:* `analysis` or `reaction`
>
> *I chose `reaction`, because:* Even though it contains two numbers, neither is being used as evidence for an argument. The post is live commentary from inside a game, expressing dismay about what is happening right now. A `analysis` post uses stats to build toward a conclusion. This post has no conclusion -- only an ongoing feeling about the game.

---

## The Training Run

**Device:** mps (Apple Silicon GPU, M-series Mac)

**Base model:** `distilbert-base-uncased`

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, seed 42, max token length 128

**Anything I changed from the defaults, and why:**
Nothing was changed from the notebook defaults. The dataset is small enough (195 rows) that 3 epochs at 2e-5 is a reasonable starting point, and the default max_length of 128 covers every post in the corpus since r/hockey posts are short.

**Split sizes:**
- Train: 135 posts (70%)
- Val: 30 posts (15%)
- Test: 30 posts (15%), stratified by label

Per-label counts in the test split:

| Label | Test count |
|---|---|
| analysis | 9 |
| hot_take | 9 |
| reaction | 12 |

Note: With only 9 examples each for analysis and hot_take in the test split, F1 scores for those labels move a lot between seeds. This is expected given the dataset size and is documented in criteria.md.

**Final test results (seed 42):**

| Metric | Value |
|---|---|
| Overall accuracy | 0.600 |
| Macro F1 | 0.470 |
| F1 -- analysis | 0.700 |
| F1 -- hot_take | 0.000 |
| F1 -- reaction | 0.710 |
| Precision -- analysis | 0.636 |
| Precision -- hot_take | 0.000 |
| Precision -- reaction | 0.579 |
| Confidence (most-sure third) | 1.000 |
| Confidence (least-sure third) | 0.100 |

The model predicted zero hot_take examples across all 30 test cases. Every hot_take test example was classified as either analysis (3) or reaction (6). This is the most important finding from this run and is documented further in the Unit 6 sections.



---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for:* Help writing a Python script to collect real r/hockey posts from the Arctic Shift API and build labels.csv from real scraped data.
- *What came back:* A script (`scripts/build_labels.py`) that reads `data/raw_posts.json` and `data/raw_comments.json`, matches text snippets to their source posts using substring search, and applies keyword-based heuristics to classify remaining posts.
- *What I changed:* The initial script failed on curly/smart apostrophes in the raw Reddit data (Unicode `’` vs ASCII `'`). Added a `normalize()` function that converts all smart quotes to straight ASCII before any string comparison. Also expanded the heuristic patterns after noticing that hot_take was underrepresented in early runs.

**Moment 2**

- *What I asked for:* Help writing the decision rule for the `analysis` vs. `hot_take` boundary in label_definitions.txt.
- *What came back:* A rule centered on whether the cited fact is "load-bearing" -- that is, whether removing the fact would collapse the argument into a pure opinion.
- *What I changed:* I kept the "load-bearing" framing because it gave me something concrete to apply. I added the clause that the fact must be specific and verifiable, not just any number, because I found cases where someone cited an approximate or vague figure and the post was still more `hot_take` than `analysis`.

**Pre-labelling disclosure:**
Rows 21-195 in labels.csv were labeled using a two-step process: a manually curated list of text snippets with hand-assigned labels, followed by a keyword heuristic sweep over the remaining scraped data. The heuristics were written by hand using patterns derived from the label definitions (e.g., stat words for analysis, evaluative language for hot_take, emotional exclamations for reaction). No model was used to assign labels. The note column on all non-cold rows reads "pre-labeled" to mark where heuristic assistance was used.

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
