export default function About() {
  return (
    <div className="page narrow prose">
      <h1>How CiteCheck works</h1>
      <p className="lead">CiteCheck is a course project at the University of Maryland (DATA/MSML 641, Natural Language Processing).</p>

      <h2>What happens when you check a draft</h2>
      <ol>
        <li><strong>Find the citations.</strong> Every sentence with a marker like [3] or (Smith et al., 2020) is matched to its entry in your reference list.</li>
        <li><strong>Find the paper.</strong> If the entry has a DOI or arXiv id we use it; otherwise we ask Crossref and accept its answer only when the titles match.</li>
        <li><strong>Read it.</strong> A language model trained to judge whether one text supports another compares your sentence with the paper's abstract.</li>
        <li><strong>Read more when unsure.</strong> If the abstract isn't enough, CiteCheck looks for a legal open-access copy (arXiv, Europe PMC, Unpaywall) and reads that.</li>
        <li><strong>Suggest, don't replace.</strong> If a citation doesn't hold up, it searches for a paper that does support the sentence, and shows it only when the model is very sure. It's a paper to read, not a citation to paste.</li>
      </ol>

      <h2>How well it does</h2>
      <p>On SciFact, a benchmark of 300 expert-written biomedical claims, the model scores a macro-F1 of 0.60 (95% CI 0.55–0.66) and wrongly says “supported” for 11% of claims that aren't supported. In a test where each claim cites a wrong but plausible paper, CiteCheck flagged 91% of the wrong citations.</p>
      <p>It is cautious: it would rather say “not enough evidence” than guess. With today's model, it also raises a concern about roughly half of the citations that are in fact correct. We are working on that.</p>

      <h2>Your data</h2>
      <ul>
        <li>We keep your account (e-mail) so you can sign in and see your history.</li>
        <li>With your permission, we record how you use the site and your feedback, for our course research. Published results are anonymised.</li>
        <li>The text you paste is stored only if you allow it, with e-mail addresses and phone numbers masked.</li>
        <li>You can change these choices any time in Account.</li>
      </ul>

      <h2>Data and models</h2>
      <p>Evaluation data: SciFact (claims CC BY 4.0, abstracts ODC-By 1.0). Paper metadata: OpenAlex, Semantic Scholar, arXiv, Crossref, Europe PMC and Unpaywall. Verifier: an open-source DeBERTa natural-language-inference model.</p>
    </div>
  );
}
