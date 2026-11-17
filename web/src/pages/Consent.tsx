import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { post } from "../api";
import { useAuth } from "../auth";
import { safeNext } from "../format";

// A study participant can arrive with ?code=P04 in the link; App.tsx keeps it for this tab.
function codeFromLink(): string {
  try {
    return sessionStorage.getItem("cc_code") ?? "";
  } catch {
    return "";
  }
}

export function ConsentForm({ onSaved, initial }: {
  onSaved: () => void;
  initial?: { research: boolean | null; text: boolean; participant_code?: string };
}) {
  const [research, setResearch] = useState<boolean>(initial?.research ?? false);
  const [text, setText] = useState<boolean>(initial?.text ?? false);
  const [code, setCode] = useState<string>(initial?.participant_code || codeFromLink());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const { refreshMe } = useAuth();

  async function save() {
    setBusy(true);
    setError("");
    try {
      await post("/api/me/consent", { research, text: research && text, participant_code: research ? code.trim() : "" });
    } catch (e) {
      setBusy(false);
      return setError((e as Error).message);
    }
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
          <span className="muted">Keep a record of how you use the site: pages, checks and your answers on whether results are right. Anything we publish about it is anonymised.</span>
        </span>
      </label>
      <label className={`choice ${research ? "" : "disabled"}`}>
        <input type="checkbox" checked={research && text} disabled={!research} onChange={(e) => setText(e.target.checked)} />
        <span>
          <strong>Also keep the text I paste</strong>
          <span className="muted">Lets us study where CiteCheck gets it wrong. E-mail addresses and phone numbers are masked. Off by default.</span>
        </span>
      </label>
      <label className={`code-field ${research ? "" : "disabled"}`}>
        <span className="field-label">Study code <span className="muted">(only if the CiteCheck team gave you one)</span></span>
        <input type="text" value={code} onChange={(e) => setCode(e.target.value.toUpperCase().slice(0, 16))} disabled={!research}
               placeholder="e.g. P04" autoComplete="off" />
      </label>
      <p className="muted small">Either way, your checks are saved to your History, which only you can see on this site. The team can reach the database to keep the service running, and looks at individual checks only if you agreed above.</p>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="btn btn-primary" onClick={save} disabled={busy}>{busy ? "Saving…" : "Continue"}</button>
    </div>
  );
}

function takeDeletedNote(): string {
  try {
    const m = sessionStorage.getItem("cc_deleted") ?? "";
    sessionStorage.removeItem("cc_deleted");
    return m;
  } catch {
    return "";
  }
}

export default function Consent() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const [deleted] = useState(takeDeletedNote);
  return (
    <div className="page narrow">
      <section className="card">
        {deleted && <div className="banner">{deleted} You can keep using CiteCheck; choose again what we may keep.</div>}
        <h1>Welcome to CiteCheck</h1>
        <p className="lead small">Before you start, choose what we may keep. You can change this any time in Account.</p>
        <ConsentForm onSaved={() => nav(next === "/welcome" ? "/check" : next, { replace: true })} />
      </section>
    </div>
  );
}
