"""
Basic BM25 retrieval over the sample corpus.
"""
import json
from rank_bm25 import BM25Okapi

def load_corpus(path="data/sample_papers.json"):
    with open(path) as f:
        return json.load(f)

def build_index(papers):
    tokenized = [p["abstract"].lower().split() for p in papers]
    return BM25Okapi(tokenized), papers

def search(query, bm25, papers, top_k=5):
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(zip(scores, papers), key=lambda x: x[0], reverse=True)
    return ranked[:top_k]

if __name__ == "__main__":
    papers = load_corpus()
    bm25, papers = build_index(papers)
    results = search("citation entailment verification", bm25, papers)
    for score, paper in results:
        print(f"{score:.2f}  {paper['title']}")