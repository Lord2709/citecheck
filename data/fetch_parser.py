"""
Pulls a small sample of papers from arXiv to use as a starting corpus.
"""
import arxiv
import json

def fetch_sample(query="natural language processing", max_results=30):
    search = arxiv.Search(query=query, max_results=max_results)
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "abstract": result.summary,
            "id": result.entry_id,
        })
    return papers

if __name__ == "__main__":
    papers = fetch_sample()
    with open("data/sample_papers.json", "w") as f:
        json.dump(papers, f, indent=2)
    print(f"Saved {len(papers)} papers to data/sample_papers.json")