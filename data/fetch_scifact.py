"""Download SciFact and write a MANIFEST.json (hashes + counts) next to it.  Owner: Data & Evaluation (Sahil).

    python -m data.fetch_scifact                       # download from the official S3 release
    python -m data.fetch_scifact --tar C:\\path\\data.tar.gz   # you downloaded the tarball by hand
    python -m data.fetch_scifact --out data/scifact --force

Official release (allenai/scifact README):
    https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz

Only four whitelisted file names are extracted (no path traversal possible).  The .jsonl files are
git-ignored (see .gitignore); MANIFEST.json IS committed so anyone can check they hold the same data.
"""
from __future__ import annotations

import argparse
import json
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # allow `python data/fetch_scifact.py`

from src.data_io import label_distribution, load_claims, load_jsonl, sha256_file  # noqa: E402

URL = "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"
WANTED = ("corpus.jsonl", "claims_train.jsonl", "claims_dev.jsonl", "claims_test.jsonl")
LICENSE = {
    "claims_and_evidence_annotations": "CC BY 4.0",
    "abstracts (S2ORC)": "ODC-By 1.0",
    "source": "https://github.com/allenai/scifact/blob/master/LICENSE.md",
}


def download(url: str, dest: Path):
    import requests

    print(f"downloading {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done / 1e6:.1f} / {total / 1e6:.1f} MB", end="")
    print()


def extract(tar_path: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    found = set()
    with tarfile.open(tar_path) as tf:
        for member in tf.getmembers():
            base = Path(member.name).name
            if member.isfile() and base in WANTED and base not in found:
                src = tf.extractfile(member)
                (out / base).write_bytes(src.read())
                found.add(base)
    missing = set(WANTED) - found
    if missing:
        sys.exit(f"archive is missing {sorted(missing)}")


def write_manifest(out: Path, source: str):
    files = {}
    for name in WANTED:
        p = out / name
        files[name] = {"sha256": sha256_file(p), "n_rows": len(load_jsonl(p)), "bytes": p.stat().st_size}
    manifest = {
        "dataset": "SciFact (Wadden et al., EMNLP 2020)",
        "source": source,
        "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "license": LICENSE,
        "files": files,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/scifact")
    ap.add_argument("--url", default=URL)
    ap.add_argument("--tar", default=None, help="use a tarball you already downloaded")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)

    if (out / "corpus.jsonl").exists() and not a.force:
        print(f"{out} already has SciFact (use --force to re-download).")
    else:
        if a.tar:
            extract(Path(a.tar), out)
            source = f"local tarball {Path(a.tar).name}"
        else:
            with tempfile.TemporaryDirectory() as tmp:
                t = Path(tmp) / "data.tar.gz"
                download(a.url, t)
                extract(t, out)
            source = a.url
        write_manifest(out, source)

    m = json.loads((out / "MANIFEST.json").read_text(encoding="utf-8"))
    print("\nMANIFEST")
    for name, info in m["files"].items():
        print(f"  {name:20s} rows={info['n_rows']:6d}  sha256={info['sha256'][:12]}…")
    for split in ("train", "dev"):
        print(f"  {split} label distribution: {label_distribution(load_claims(out / f'claims_{split}.jsonl'))}")
    print("\nSanity: the SciFact paper describes 300 dev claims and a corpus of ~5.2k abstracts; "
          "if your counts differ a lot, re-download.")
    print("Reminder: claims_test.jsonl has NO labels. We never tune on it.")


if __name__ == "__main__":
    main()
