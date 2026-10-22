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
| hot_take | 61 | 31.3% |
| reaction | 74 | 37.9% |
| **Total** | **195** | 100% |

Note: Four posts were relabeled from reaction to hot_take as part of the Unit 6 improvement. The original counts were analysis=60, hot_take=57, reaction=78.

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
| Overall accuracy | 0.333 | 0.600 | +0.267 |
| Macro F1 | 0.260 | 0.470 | +0.210 |
| F1 — `analysis` | 0.444 | 0.700 | +0.256 |
| F1 — `hot_take` | 0.182 | 0.000 | -0.182 |
| F1 — `reaction` | 0.154 | 0.710 | +0.556 |

Both models were evaluated on the same 30 held-out hockey posts (`test_split.csv`). Trained numbers are from seed 42.

**What I predicted before I looked:**
The zero-shot baseline (BART-MNLI) has never seen r/hockey text and relies entirely on how well the label names match the NLI framing. I expected fine-tuning to beat it on overall accuracy, possibly by 20 or 30 points, because the training examples teach the model the specific vocabulary patterns of each class. I also expected reaction to improve the most since game-thread language is distinctive and easy to pick up from examples. Hot_take was the label I was least confident about because the boundary with reaction is subtle and depends on whether a post is tied to an immediate event, which is contextual and hard to learn from 195 examples.

**What the gap actually means:**
Fine-tuning clearly helped on reaction (+0.556 in F1) and analysis (+0.256), which tells us those two classes have learnable signal in the text itself. The trained model lost ground on hot_take (-0.182), dropping from an F1 of 0.182 to 0.000. This is not noise: the fine-tuned model predicts zero hot_takes while the zero-shot baseline at least recovers one. The cause is label noise at the hot_take/reaction boundary: the training data contains reaction-labeled posts that express general claims (not immediate events), which taught the model that general evaluative language means "reaction." The zero-shot model bypasses this because it never looked at the training labels.



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | >= 0.65 | 0.600 | 0.667 | 0.700 | MISSED |
| 2. Per-label F1 | >= 0.50 each label | 0.000 (hot_take) | 0.200 (hot_take) | 0.000 (hot_take) | MISSED |
| 3. Top-third accuracy | >= 0.80 | 1.000 | 0.900 | 0.900 | MET |
| 4. Accuracy spread | <= 0.10 | -- | -- | spread = 0.100 | MET |
| 5. Analysis precision | >= 0.60 | 0.636 | 0.778 | 0.692 | MET |

### Confusion matrix

Seed 42 (before improvement):

| true \ predicted | analysis | hot_take | reaction |
|---|---|---|---|
| **analysis** | 7 | 0 | 2 |
| **hot_take** | 3 | 0 | 6 |
| **reaction** | 1 | 0 | 11 |

**My biggest off-diagonal number, and what it means:**
The largest off-diagonal entry is 6: six real hot_take posts were predicted as reaction, and zero reaction posts were predicted as hot_take in the opposite direction. The asymmetry is total. The model learned to treat hot_take and reaction as the same class and collapsed them into the more frequent label. This is not confusion in both directions -- it is a one-way failure where the model never fires the hot_take prediction at all. The hot_take/reaction boundary (general claim vs. immediate event reaction) was not learned from the training data.



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy >= 0.65 | all seeds | MISSED | Seed 42 accuracy = 0.600, below 0.65. Seeds 7 and 2024 pass, but the criterion requires all three. |
| 2 | Per-label F1 >= 0.50 | all labels, all seeds | MISSED | hot_take F1 = 0.000 on seeds 42 and 2024, and 0.200 on seed 7. No seed cleared 0.50 for hot_take. |
| 3 | Top-third accuracy >= 0.80 | all seeds | MET | 1.000 / 0.900 / 0.900 across all three seeds. |
| 4 | Accuracy spread <= 0.10 | across seeds | MET | Spread = 0.100 (0.700 - 0.600). Exactly at the limit. |
| 5 | Analysis precision >= 0.60 | all seeds | MET | 0.636 / 0.778 / 0.692. All three seeds clear the target. |

**Diagnoses**

**Criterion 1 miss (accuracy < 0.65 on seed 42):**
Seed 42 accuracy = 0.600 because the model predicts zero hot_takes. All 9 hot_take test posts are misclassified (3 as analysis, 6 as reaction), which alone accounts for 9 of the 12 wrong predictions. If the hot_take label were removed from the test set, the model would have passed criterion 1. The cause is the same as criterion 2: the model never learned to fire the hot_take prediction.

**Criterion 2 miss (hot_take F1 = 0.000 on seeds 42 and 2024):**
The model collapsed hot_take into reaction across all three seeds. The evidence from the confusion matrix is directional: 6 of 9 hot_take posts are called "reaction," not the other way around. Two explanations are possible: inconsistent labeling in my training data, or a genuinely hard boundary.

The agreement report rules out the first explanation. My labels on the 30 staff posts matched the staff at 100%, which means I applied the decision rules consistently. A labeler who applies rules inconsistently would expect to disagree with a second labeler on ambiguous cases. Since there were no disagreements across 30 posts covering all three classes including hot_take, the consistency problem is not in how I applied the rules -- it is in the training data itself.

The real cause is signal overlap in the text. Posts labeled "reaction" in my training set often contain general evaluative language ("that was incredible," "this guy is the real deal") that is identical in surface form to hot_take language. The model saw those posts labeled "reaction" and learned that evaluative language equals "reaction." It did not learn the actual distinction (immediate event vs. general claim) because that distinction is contextual and not always visible in the post text alone. With only 57 hot_take training examples and a noisy boundary, the model took the safe route and collapsed both classes into the more frequent label.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** 30 / 30 = 100%

Agreement was checked by running `python agreement.py`, which compared `my_staff_labels.csv` against the staff ground-truth file row by row. Output: `{"compared": 30, "agreed": 30, "agreement_rate": 1.0, "disagreements": []}`.

**Disagreements**

None. Every post matched the staff label exactly.

**What the pattern in my disagreements tells me:**
100% agreement means there are no individual cases to adjudicate. What it does tell me is something useful for the diagnosis: the staff taxonomy is specific enough that two labelers applying the same rules converge completely on 30 posts drawn to include ambiguous cases. This means my labels are not the source of the hot_take/reaction failure. The failure is not that I applied the rules differently across 200 posts -- it is that the boundary itself is difficult for the model to learn from surface text features alone, because "general claim" vs. "immediate event reaction" is not always visible in the post text without knowing the thread context it came from.



---

## The Improvement

**What I changed:**
I relabeled four posts in `labels.csv` from `reaction` to `hot_take`. The four posts are:

- "Josh Anderson just can't not score against the Leafs." -- a general claim about a player's pattern against one team, not a reaction to a specific goal
- "It's not even the regular season and we already have the leading contender for worst reffing decision of the season lol" -- a comparative evaluative claim about reffing quality, elevated beyond a simple event reaction
- "He was okay. He had spurts of good games and spurts of games where I forgot he was on the team." -- a retrospective general player evaluation with no event anchor
- "On Mcdavids better games, EVERY TIME he gets the puck he looks dangerous." -- a general pattern observation about McDavid, not tied to any specific game or play

All four were pre-labeled via the keyword heuristic and had no event anchor in the text. They were training the model to associate general-claim language with the "reaction" label, which was the direct cause of the hot_take collapse. After relabeling: hot_take = 61, reaction = 74, analysis = 60.

**Which diagnosis pointed at it:**
The confusion matrix for seeds 42 and 2024 showed that every hot_take test post was predicted as either analysis or reaction, with 6 of 9 going to reaction. The diagnosis identified that training data contained reaction-labeled posts with general evaluative language, which overlapped with the surface features of hot_take posts. The 100% agreement rate ruled out a consistency problem in how I applied the rules, pointing instead at training data noise. Relabeling the clearest reaction-to-hot_take boundary cases was the most direct fix available without adding new data.

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | >= 0.65 | 0.700 | 0.733 | 0.667 | MET |
| 2. Per-label F1 | >= 0.50 each label | 0.533 (hot_take) | 0.632 (hot_take) | 0.000 (hot_take) | MISSED |
| 3. Top-third accuracy | >= 0.80 | 1.000 | 1.000 | 0.900 | MET |
| 4. Accuracy spread | <= 0.10 | -- | -- | spread = 0.067 | MET |
| 5. Analysis precision | >= 0.60 | 0.667 | 0.857 | 0.643 | MET |

**Did it help, and how do I know:**
Yes, partially. Criterion 1 flipped from MISSED to MET: seed 42 accuracy went from 0.600 to 0.700, crossing the 0.65 threshold. Hot_take F1 improved from 0.000 to 0.533 on seed 42 and from 0.000 to 0.632 on seed 7, which means the model now predicts hot_takes in two of three seeds. The accuracy spread also tightened from 0.100 to 0.067.

The improvement did not fix criterion 2. Seed 2024 still predicts zero hot_takes (F1 = 0.000). Four relabeled posts are not enough to resolve the full boundary problem when the model also depends on which examples land in the training split. Seed 2024 happened to draw a training split where the surviving noise outweighed the signal from the corrected examples.



---

## What's Still Broken

**Criterion 2 is still missed:** Seed 2024 produces hot_take F1 = 0.000 after the relabeling fix. The model in that seed predicts zero hot_takes: 5 hot_take test posts are called analysis, 5 are called reaction. The split is different from seeds 42 and 7 because seed 2024 draws a different training set, and the remaining noisy boundary cases dominate.

To fix criterion 2 fully, I would need to audit the remaining reaction posts systematically and relabel every post that expresses a general evaluative claim without an event anchor. That is a larger labeling pass, not a targeted four-post fix. I stopped at four posts because the assignment allows only one improvement and four was the set I could defend clearly without guessing.

A second issue is dataset size. With 61 hot_take training examples and a three-way stratified split, each seed puts roughly 44 hot_take posts in train, 8 in val, and 9 in test. That is thin enough that one bad training split can wipe out everything the model learned about the label. The F1 spread across seeds for hot_take is 0.632 (from 0.000 to 0.632), which is much larger than the spread for analysis (0.033) or reaction (0.065). This is a data-size problem that relabeling four posts cannot solve.

**The gap between what I meant my labels to capture and what the model learned:**
I defined hot_take as a general confident claim with no supporting evidence and reaction as an immediate emotional response to a specific event. The model learned to predict reaction for any post with evaluative or excited language, whether or not that language was anchored to a live event. The confusion matrix shows the evidence: before the fix, 6 of 9 hot_take test posts were predicted as reaction and zero reaction posts were predicted as hot_take, which means the model treated the two classes as one and defaulted to the more frequent label.



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
