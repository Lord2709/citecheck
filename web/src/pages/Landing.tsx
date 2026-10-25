import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Landing() {
  const { signedIn } = useAuth();
  const start = signedIn ? "/check" : "/signin?next=/check";
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-text">
          <p className="eyebrow">For students and researchers who cite papers</p>
          <h1>Does the paper you cite <span className="hl">really say that?</span></h1>
          <p className="lead">
            Paste your draft with its references. CiteCheck reads every cited paper and shows you which sentences
            back you up, which don't, and the exact lines that decide it.
          </p>
          <div className="hero-cta">
            <Link to={start} className="btn btn-primary btn-big">Check a draft</Link>
            <Link to={signedIn ? "/papers" : "/signin?next=/papers"} className="btn btn-ghost btn-big">Find papers for a topic</Link>
          </div>
          <p className="muted small">Free · sign in with your e-mail · nothing to install</p>
        </div>

        <div className="hero-demo" aria-label="Example result">
          <div className="demo-card">
            <div className="demo-line">
              <span className="pill ok">Supported</span>
              <span className="demo-claim">Transformers dispense with recurrence and convolutions <mark className="marker">[1]</mark></span>
            </div>
            <blockquote className="evidence small">“…based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.”</blockquote>
          </div>
          <div className="demo-card">
            <div className="demo-line">
              <span className="pill bad">Contradicted</span>
              <span className="demo-claim">Attention-only models are slower to train <mark className="marker">[1]</mark></span>
            </div>
            <blockquote className="evidence small">“…more parallelizable and requiring significantly less time to train.”</blockquote>
          </div>
          <div className="demo-card">
            <div className="demo-line">
              <span className="pill warn">Not enough evidence</span>
              <span className="demo-claim">The base model uses 8 attention heads <mark className="marker">[1]</mark></span>
            </div>
            <p className="muted small">Not in the abstract → CiteCheck reads the open-access PDF.</p>
          </div>
        </div>
      </section>

      <section className="steps-strip">
        <div className="step">
          <span className="step-n">1</span>
          <h3>Paste or upload</h3>
          <p>A paragraph, a section or a whole text-based PDF, with its reference list.</p>
        </div>
        <div className="step">
          <span className="step-n">2</span>
          <h3>CiteCheck reads the papers</h3>
          <p>It finds each reference, reads the abstract, and opens the free full text when the abstract isn't enough.</p>
        </div>
        <div className="step">
          <span className="step-n">3</span>
          <h3>You see the evidence</h3>
          <p>Each citation is marked supported, contradicted or unclear, with the deciding sentences and better papers to read.</p>
        </div>
      </section>

      <section className="honest">
        <h2>What it can and can't do</h2>
        <div className="honest-grid">
          <div>
            <h3>Good at</h3>
            <ul>
              <li>Catching citations that don't back up the sentence they're attached to</li>
              <li>Showing you exactly which lines of the paper decided it</li>
              <li>Papers with open abstracts on OpenAlex, Semantic Scholar or arXiv</li>
            </ul>
          </div>
          <div>
            <h3>Not good at (yet)</h3>
            <ul>
              <li>Paywalled papers: it can only read their abstract, and says so</li>
              <li>Scanned PDFs: they can't be read</li>
              <li>Being certain: it's a second pair of eyes. You decide what to cite</li>
            </ul>
          </div>
        </div>
        <p><Link to="/about">How it works and how well it does →</Link></p>
      </section>
    </div>
  );
}
