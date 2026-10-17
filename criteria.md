# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1.

Overall accuracy >= 0.65 across all three seeds (42, 7, 2024).

**Why this target:**
A three-class random guesser reaches 0.33. Requiring 0.65 means the model must do at least twice as well as chance on every seed, not just the lucky one. If it cannot clear that bar consistently the fine-tuning added nothing durable.

---

## 2.

Per-label F1 >= 0.50 for every label on every seed.

**Why this target:**
A high macro average can hide one completely collapsed label. Requiring each label to reach 0.50 individually ensures the model learned all three distinctions. 0.50 rather than 0.60 acknowledges that reaction is the smallest group in the test split (about 10 examples) and genuine ambiguity exists at the analysis/hot_take boundary. A score computed on 10 examples swings a lot between seeds.

---

## 3.

Accuracy on the highest-confidence third of test predictions >= 0.80.

**Why this target:**
A well-calibrated classifier should be right most of the time when it is most certain. If it is wrong 30% of the time even on its most confident calls the probability scores cannot be trusted downstream. 0.80 on the top third is a reasonable bar given the label noise at the analysis/hot_take boundary.

---

## 4.

Cross-seed accuracy spread <= 0.10 (best seed minus worst seed across seeds 42, 7, 2024).

**Why this target:**
A spread wider than 0.10 means the result depends heavily on which examples land in the training set, which points to a dataset too small or labels too inconsistent to produce a reliable signal. Keeping the spread under 0.10 shows that the learned boundary is real and not a lucky split.

---

## 5.

Precision on the analysis label >= 0.60 on every seed.

**Why this target:**
Analysis is the label most likely to be confused with hot_take because both involve assertions about hockey. False positives on analysis are costly: they label an unsupported opinion as a reasoned argument, which is the core error TakeMeter exists to avoid. Requiring precision of at least 0.60 on analysis specifically ensures the model is not just assigning that label liberally to boost recall numbers.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
