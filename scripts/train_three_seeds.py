#!/usr/bin/env python3
"""Run three-seed training and write results_three_seeds_{before|after}.json.

Uses torch.utils.data.Dataset (not datasets.Dataset.from_pandas) to avoid
the Python 3.14/dill incompatibility.

Usage:
    python scripts/train_three_seeds.py
    python scripts/train_three_seeds.py --label after
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset as TorchDataset
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

ROOT = Path(__file__).resolve().parent.parent

LABELS = ["analysis", "hot_take", "reaction"]
BASE_MODEL = "distilbert-base-uncased"
EPOCHS = 3
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 128
SEEDS = [42, 7, 2024]


def pick_device():
    if torch.cuda.is_available():
        return "cuda", torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", "Apple Silicon GPU (MPS)"
    return "cpu", "CPU"


class TextDataset(TorchDataset):
    def __init__(self, texts, label_ids, tokenizer):
        enc = tokenizer(
            list(texts),
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.tensor(list(label_ids), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.labels[idx],
        }


def to_ids(df):
    lookup = {label: i for i, label in enumerate(LABELS)}
    return df["label"].astype(str).str.strip().map(lookup)


def split_dataset(df, seed):
    def stratify_on(frame):
        counts = frame["label"].value_counts()
        return frame["label"] if counts.min() >= 2 else None

    rest, test = train_test_split(
        df, test_size=0.15, random_state=seed, stratify=stratify_on(df)
    )
    val_share = 0.15 / 0.85
    train, val = train_test_split(
        rest, test_size=val_share, random_state=seed, stratify=stratify_on(rest)
    )
    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def compute_metrics(eval_pred):
    logits, gold = eval_pred
    predicted = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(gold, predicted),
        "f1_macro": f1_score(gold, predicted, average="macro", zero_division=0),
    }


def train_model(train_df, val_df, seed):
    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(LABELS),
        id2label={i: l for i, l in enumerate(LABELS)},
        label2id={l: i for i, l in enumerate(LABELS)},
    )
    train_ds = TextDataset(train_df["text"], to_ids(train_df), tokenizer)
    val_ds = TextDataset(val_df["text"], to_ids(val_df), tokenizer)

    args = TrainingArguments(
        output_dir=str(ROOT / "takemeter_out"),
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=10,
        seed=seed,
        report_to="none",
        disable_tqdm=True,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    return trainer, tokenizer


def evaluate(trainer, tokenizer, test_df, seed):
    test_ds = TextDataset(test_df["text"], to_ids(test_df), tokenizer)
    output = trainer.predict(test_ds)

    predicted = np.argmax(output.predictions, axis=-1)
    gold = np.array(output.label_ids)

    scores = output.predictions
    exp = np.exp(scores - scores.max(axis=-1, keepdims=True))
    confidence = (exp / exp.sum(axis=-1, keepdims=True)).max(axis=-1)

    precision, recall, f1, support = precision_recall_fscore_support(
        gold, predicted, labels=list(range(len(LABELS))), zero_division=0
    )

    right = gold == predicted
    ranked = np.argsort(confidence)
    third = max(1, len(confidence) // 3)
    least, most = ranked[:third], ranked[-third:]

    confusion = {t: {p: 0 for p in LABELS} for t in LABELS}
    for g, p in zip(gold, predicted):
        confusion[LABELS[int(g)]][LABELS[int(p)]] += 1

    return {
        "seed": seed,
        "n_test": int(len(gold)),
        "accuracy": float(accuracy_score(gold, predicted)),
        "f1_macro": float(f1_score(gold, predicted, average="macro", zero_division=0)),
        "per_label": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(LABELS)
        },
        "confusion": confusion,
        "confidence": {
            "mean_when_right": float(confidence[right].mean()) if right.any() else None,
            "mean_when_wrong": float(confidence[~right].mean()) if (~right).any() else None,
            "accuracy_most_confident_third": float(right[most].mean()),
            "accuracy_least_confident_third": float(right[least].mean()),
            "n_per_third": int(third),
        },
    }


def spread_table(all_results):
    seeds = [r["seed"] for r in all_results]
    header = f"| Measure | {' | '.join(f'Seed {s}' for s in seeds)} | Spread |"
    divider = "|---|" + "|".join(["---"] * (len(seeds) + 1)) + "|"

    def row(name, values):
        spread = max(values) - min(values)
        cells = " | ".join(f"{v:.3f}" for v in values)
        return f"| {name} | {cells} | {spread:.3f} |"

    rows = [header, divider]
    rows.append(row("Overall accuracy", [r["accuracy"] for r in all_results]))
    rows.append(row("Macro F1", [r["f1_macro"] for r in all_results]))
    for label in LABELS:
        rows.append(row(f"F1 — `{label}`",
                        [r["per_label"][label]["f1"] for r in all_results]))
    return "\n".join(rows)


def matrix_markdown(confusion):
    header = f"| true \\ predicted | {' | '.join(LABELS)} |"
    divider = "|---|" + "|".join(["---"] * len(LABELS)) + "|"
    rows = [header, divider]
    for true_label in LABELS:
        cells = " | ".join(str(confusion[true_label][p]) for p in LABELS)
        rows.append(f"| **{true_label}** | {cells} |")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="before", choices=["before", "after"])
    args = parser.parse_args()

    device, device_name = pick_device()
    print(f"device: {device}  ({device_name})\n")

    df = pd.read_csv(ROOT / "labels.csv")
    print(f"Loaded labels.csv: {len(df)} rows")
    print(df["label"].value_counts().to_string())
    print()

    all_results = []
    for i, seed in enumerate(SEEDS, 1):
        print(f"{'=' * 60}\nSeed {seed}  ({i}/{len(SEEDS)})\n{'=' * 60}")
        tr, va, te = split_dataset(df, seed)
        print(f"  train={len(tr)}  val={len(va)}  test={len(te)}")
        t, tok = train_model(tr, va, seed)
        r = evaluate(t, tok, te, seed)
        r["device"] = device
        r["device_name"] = device_name
        r["torch_version"] = torch.__version__
        r["max_length"] = MAX_LENGTH
        all_results.append(r)
        print(f"  accuracy={r['accuracy']:.3f}   macro_F1={r['f1_macro']:.3f}")
        for label, s in r["per_label"].items():
            print(f"    {label:<16} F1={s['f1']:.3f}  P={s['precision']:.3f}  R={s['recall']:.3f}")
        print()

    out = ROOT / f"results_three_seeds_{args.label}.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Wrote {out}")
    print(f"{'=' * 60}\n")

    print("SPREAD TABLE:\n")
    print(spread_table(all_results))
    print()

    for r in all_results:
        print(f"CONFUSION MATRIX — seed {r['seed']}:\n")
        print(matrix_markdown(r["confusion"]))
        print()

    accs = [r["accuracy"] for r in all_results]
    spread = max(accs) - min(accs)
    print(f"Accuracy spread: {spread:.3f}")
    if spread > 0.10:
        print("WARNING: spread > 0.10")


if __name__ == "__main__":
    main()
