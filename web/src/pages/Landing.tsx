import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Landing() {
  const { signedIn } = useAuth();
  const start = signedIn ? "/check" : "/signin?next=/check";
  return (
    <div className="landing">
      <section className="hero">
        <div>
          <h1>Does the paper you cite really say that?</h1>
          <p className="lead">
            Paste your draft with its references. CiteCheck reads each cited paper and shows you the lines that back your
            sentence up, or contradict it.
          </p>
          <div className="hero-cta">
            <Link to={start} className="btn btn-primary btn-big">Check a draft</Link>
            <Link to={signedIn ? "/papers" : "/signin?next=/papers"} className="btn btn-ghost btn-big">Find papers for a topic</Link>
          </div>
        </div>

        <figure className="specimen" aria-label="Example: a cited sentence and the passage that decides it">
          <div className="spec-part">
            <div className="spec-label">
              <span>Your draft</span>
              <span className="pill bad">Contradicted</span>
            </div>
            <p className="spec-sentence">
              Attention-only models are always slower to train than recurrent ones <mark className="marker">[1]</mark>.
            </p>
          </div>
          <div className="spec-part">
            <div className="spec-label"><span>[1] Attention Is All You Need (2017), abstract</span></div>
            <p className="spec-abstract">
              …We propose a new simple network architecture, the Transformer, based solely on attention mechanisms,
              dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these
              models to be superior in quality{" "}
              <span className="decides">while being more parallelizable and requiring significantly less time to train.</span>
            </p>
          </div>
        </figure>
      </section>

      <section className="steps-strip" aria-label="How it works">
        <div className="step">
          <span className="step-n">1</span>
          <h3>Paste your draft</h3>
          <p>A paragraph, a section or a text-based PDF, with its reference list.</p>
        </div>
        <div className="step">
          <span className="step-n">2</span>
          <h3>CiteCheck reads each paper</h3>
          <p>It finds every reference, reads the abstract, and opens the free full text when the abstract isn't enough.</p>
        </div>
        <div className="step">
          <span className="step-n">3</span>
          <h3>See the deciding lines</h3>
          <p>Each citation is marked supported, contradicted or not enough evidence, with the sentences that decided it.</p>
        </div>
      </section>

      <section className="honest">
        <h2>Before you rely on it</h2>
        <div>
          <ul>
            <li>For paywalled papers it can only read the abstract, and it tells you when that happens.</li>
            <li>Scanned PDFs can't be read. Paste the text instead.</li>
            <li>It's a second pair of eyes, not proof. You decide what to cite.</li>
          </ul>
          <p><Link to="/about">How it works and how well it does</Link></p>
        </div>
      </section>
    </div>
  );
}
