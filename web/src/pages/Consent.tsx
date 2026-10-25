import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { post } from "../api";
import { useAuth } from "../auth";
import { safeNext } from "../format";

export function ConsentForm({ onSaved, initial }: { onSaved: () => void; initial?: { research: boolean | null; text: boolean } }) {
  const [research, setResearch] = useState<boolean>(initial?.research ?? false);
  const [text, setText] = useState<boolean>(initial?.text ?? false);
  const [busy, setBusy] = useState(false);
  const { refreshMe } = useAuth();

  async function save() {
    setBusy(true);
    await post("/api/me/consent", { research, text: research && text }).catch(() => undefined);
    await refreshMe();
    setBusy(false);
    onSaved();
  }

  return (
    <div className="consent">
      <label className="choice">
        <input type="checkbox" checked={research} onChange={(e) => setResearch(e.target.checked)} />
        <span>
          <strong>Help us improve CiteCheck</strong>
          <span className="muted">Keep a record of how you use the site: pages, checks and your 👍/👎. Anything we publish about it is anonymised.</span>
        </span>
      </label>
      <label className={`choice ${research ? "" : "disabled"}`}>
        <input type="checkbox" checked={research && text} disabled={!research} onChange={(e) => setText(e.target.checked)} />
        <span>
          <strong>Also keep the text I paste</strong>
          <span className="muted">Lets us study where CiteCheck gets it wrong. E-mail addresses and phone numbers are masked. Off by default.</span>
        </span>
      </label>
      <p className="muted small">Either way, your checks are saved to your own History, which only you can see.</p>
      <button className="btn btn-primary" onClick={save} disabled={busy}>{busy ? "Saving…" : "Continue"}</button>
    </div>
  );
}

export default function Consent() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  return (
    <div className="page narrow">
      <section className="card">
        <h1>Welcome to CiteCheck</h1>
        <p className="lead small">Before you start, choose what we may keep. You can change this any time in Account.</p>
        <ConsentForm onSaved={() => nav(next === "/welcome" ? "/check" : next, { replace: true })} />
      </section>
    </div>
  );
}
