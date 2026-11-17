import { useState } from "react";
import { get, post } from "../api";
import { useAuth } from "../auth";
import { ConsentForm } from "./Consent";

export default function Account() {
  const { me, devMode, refreshMe } = useAuth();
  const [saved, setSaved] = useState(false);
  const [exportMsg, setExportMsg] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteMsg, setDeleteMsg] = useState("");

  async function deleteData() {
    setDeleting(true);
    setDeleteMsg("");
    try {
      const r = await post<{ deleted: { checks: number; feedback: number; events: number } }>("/api/me/delete", {});
      const msg = `Deleted ${r.deleted.checks} check${r.deleted.checks === 1 ? "" : "s"}, ${r.deleted.feedback} answer${r.deleted.feedback === 1 ? "" : "s"} and ${r.deleted.events} activity record${r.deleted.events === 1 ? "" : "s"}.`;
      try {
        sessionStorage.setItem("cc_deleted", msg);   // shown on the consent screen, where the site takes you next
      } catch {
        /* storage blocked: the message is simply not repeated there */
      }
      setDeleteMsg(msg);
      setConfirmDelete(false);
      await refreshMe();
    } catch (e) {
      setDeleteMsg((e as Error).message);
    } finally {
      setDeleting(false);
    }
  }

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
        <ConsentForm initial={me ? { ...me.consent, participant_code: me.participant_code } : undefined} onSaved={() => setSaved(true)} />
        {saved && <p className="ok-text">Saved.</p>}
      </section>
      <section className="card">
        <h2>Delete my data</h2>
        <p className="muted small">Removes your checks, your answers and your activity from CiteCheck. Your e-mail stays with the sign-in service so you can sign in again; ask the team if you want that removed too.</p>
        {!confirmDelete ? (
          <button className="btn btn-danger" onClick={() => setConfirmDelete(true)}>Delete my data</button>
        ) : (
          <div className="row">
            <button className="btn btn-danger" onClick={deleteData} disabled={deleting}>{deleting ? "Deleting…" : "Yes, delete everything"}</button>
            <button className="btn btn-ghost" onClick={() => setConfirmDelete(false)} disabled={deleting}>Cancel</button>
          </div>
        )}
        {deleteMsg && <p className="muted small" role="status">{deleteMsg}</p>}
      </section>
      {me?.is_admin && (
        <section className="card">
          <h2>Research export</h2>
          <p className="muted small">Usage, outcomes and answers from people who agreed to research use, with anonymised ids, study codes and team accounts flagged, and no free text. Only admins see this.</p>
          <button className="btn" onClick={exportData}>Download the export (JSON)</button>
          {exportMsg && <p className="muted small">{exportMsg}</p>}
        </section>
      )}
    </div>
  );
}
