"""Build a tiny, randomly initialised BERT NLI classifier ON DISK so the real transformer code paths
(tokenisation, batching, softmax, label mapping, training loop) can be tested with no download.
Its predictions are meaningless: tests only check plumbing.  Owner: Data & Evaluation."""
import re
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mini_scifact"


def make_tiny_nli(path, id2label=None, seed=0, num_labels=3):
    import torch
    from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    text = " ".join(p.read_text(encoding="utf-8") for p in FIXTURE.glob("*.jsonl")).lower()
    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + sorted(set(re.findall(r"[a-z0-9]+", text)))
    (path / "vocab.txt").write_text("\n".join(vocab), encoding="utf-8")
    tok = BertTokenizerFast(vocab_file=str(path / "vocab.txt"), do_lower_case=True)
    id2label = id2label or ({0: "entailment", 1: "neutral", 2: "contradiction"} if num_labels == 3 else {0: "LABEL_0"})
    cfg = BertConfig(
        vocab_size=len(vocab), hidden_size=32, num_hidden_layers=2, num_attention_heads=2, intermediate_size=64,
        max_position_embeddings=512, num_labels=num_labels, id2label=id2label, label2id={v: k for k, v in id2label.items()},
    )
    torch.manual_seed(seed)
    BertForSequenceClassification(cfg).save_pretrained(path)
    tok.save_pretrained(path)
    return str(path)


def make_tiny_sentence_transformer(path, seed=0):
    """A real SentenceTransformer (tiny BERT + mean pooling) saved to disk, for testing our dense-retrieval code path."""
    from sentence_transformers import SentenceTransformer, models

    base = make_tiny_nli(Path(path) / "base", seed=seed)
    st = SentenceTransformer(modules=[models.Transformer(base, max_seq_length=64), models.Pooling(32)])
    out = str(Path(path) / "st")
    st.save(out)
    return out
