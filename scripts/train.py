"""
Train TakeMeter on labels.csv and write results.json + test_split.csv.

Usage:
    python scripts/train.py [--seed 42]

Writes results.json and test_split.csv to the project root.

Uses torch.utils.data.Dataset directly instead of datasets.Dataset to avoid
the dill/pickle incompatibility with Python 3.14.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
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


def pick_device():
    if torch.cuda.is_available():
        return "cuda", torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", "Apple Silicon GPU (MPS)"
    return "cpu", "CPU"


class TextDataset(Dataset):
    def __init__(self, texts, labels_ids, tokenizer):
        enc = tokenizer(
            list(texts),
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.tensor(list(labels_ids), dtype=torch.long)

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


def train_model(train_df, val_df, seed, quiet=False):
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
        disable_tqdm=quiet,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    DEVICE, DEVICE_NAME = pick_device()
    print(f"device: {DEVICE}  ({DEVICE_NAME})")
    print(f"torch:  {torch.__version__}\n")

    csv_path = ROOT / "labels.csv"
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path.name}")
    print(df["label"].value_counts().to_string())
    print()

    train_df, val_df, test_df = split_dataset(df, args.seed)
    print(f"train {len(train_df)}  val {len(val_df)}  test {len(test_df)}\n")

    print(f"Training seed={args.seed} ...")
    trainer, tokenizer = train_model(train_df, val_df, args.seed, quiet=args.quiet)
    print("Trained.\n")

    results = evaluate(trainer, tokenizer, test_df, args.seed)
    results["device"] = DEVICE
    results["device_name"] = DEVICE_NAME
    results["torch_version"] = torch.__version__
    results["max_length"] = MAX_LENGTH

    out_results = ROOT / "results.json"
    with open(out_results, "w") as f:
        json.dump(results, f, indent=2)

    out_split = ROOT / "test_split.csv"
    test_df.to_csv(out_split, index=False)

    print(f"accuracy  {results['accuracy']:.3f}")
    print(f"macro F1  {results['f1_macro']:.3f}\n")
    for label, s in results["per_label"].items():
        print(f"  {label:<16} F1 {s['f1']:.3f}   precision {s['precision']:.3f}   (n={s['support']})")
    c = results["confidence"]
    print(f"\nconfidence  most-sure third {c['accuracy_most_confident_third']:.3f}"
          f"  least-sure third {c['accuracy_least_confident_third']:.3f}")
    print(f"\nWrote {out_results.name} and {out_split.name}")


if __name__ == "__main__":
    main()
