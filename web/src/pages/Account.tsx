import { useState } from "react";
import { get } from "../api";
import { useAuth } from "../auth";
import { ConsentForm } from "./Consent";

export default function Account() {
  const { me, devMode } = useAuth();
  const [saved, setSaved] = useState(false);
  const [exportMsg, setExportMsg] = useState("");

  async function exportData() {
    setExportMsg("");
    try {
      const data = await get<Record<string, unknown>>("/api/admin/export");
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `citecheck_research_export_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      setExportMsg("Downloaded. User ids are anonymised and no pasted text is included.");
    } catch (e) {
      setExportMsg((e as Error).message);
    }
  }

  return (
    <div className="page narrow">
      <section className="card">
        <h1>Account</h1>
        <p className="muted">{devMode ? "Development mode (no sign-in)." : `Signed in as ${me?.email}`}</p>
        <h2>What we may keep</h2>
        <ConsentForm initial={me?.consent} onSaved={() => setSaved(true)} />
        {saved && <p className="ok-text">Saved.</p>}
      </section>
      {me?.is_admin && (
        <section className="card">
          <h2>Research export</h2>
          <p className="muted small">Usage, outcomes and feedback from people who agreed to research use, with anonymised ids and no free text. Only admins see this.</p>
          <button className="btn" onClick={exportData}>Download the export (JSON)</button>
          {exportMsg && <p className="muted small">{exportMsg}</p>}
        </section>
      )}
    </div>
  );
}
