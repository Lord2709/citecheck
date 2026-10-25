import { useEffect, useRef, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth";
import { safeNext } from "../format";

export default function SignIn() {
  const { signedIn, sendCode, verifyCode, ready } = useAuth();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"email" | "code">("email");
  const [digits, setDigits] = useState(["", "", "", "", "", ""]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [wait, setWait] = useState(0);
  const boxes = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (wait <= 0) return;
    const t = window.setTimeout(() => setWait(wait - 1), 1000);
    return () => window.clearTimeout(t);
  }, [wait]);

  if (ready && signedIn) return <Navigate to={next} replace />;

  async function send() {
    setError("");
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) return setError("Please enter a valid e-mail address.");
    setBusy(true);
    try {
      await sendCode(email.trim().toLowerCase());
      setStep("code");
      setWait(60);
      window.setTimeout(() => boxes.current[0]?.focus(), 50);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function verify(code: string) {
    setError("");
    setBusy(true);
    try {
      await verifyCode(email.trim().toLowerCase(), code);
    } catch (e) {
      setError((e as Error).message);
      setDigits(["", "", "", "", "", ""]);
      boxes.current[0]?.focus();
    } finally {
      setBusy(false);
    }
  }

  function setDigit(i: number, v: string) {
    const clean = v.replace(/\D/g, "");
    if (clean.length > 1) {                                  // pasted the whole code
      const all = clean.slice(0, 6).split("");
      const d = [...all, ...Array(6 - all.length).fill("")];
      setDigits(d);
      if (all.length === 6) verify(all.join(""));
      return;
    }
    const d = [...digits];
    d[i] = clean;
    setDigits(d);
    if (clean && i < 5) boxes.current[i + 1]?.focus();
    if (d.every((x) => x)) verify(d.join(""));
  }

  return (
    <div className="page narrow">
      <section className="card auth">
        <h1>Sign in</h1>
        {step === "email" ? (
          <>
            <p className="lead small">We'll e-mail you a 6-digit code. No password needed.</p>
            <label className="field-label" htmlFor="email">E-mail</label>
            <input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)}
                   onKeyDown={(e) => e.key === "Enter" && send()} placeholder="name@example.com" />
            {error && <p className="error" role="alert">{error}</p>}
            <button className="btn btn-primary wide" onClick={send} disabled={busy}>{busy ? "Sending…" : "Send me a code"}</button>
          </>
        ) : (
          <>
            <p className="lead small">Enter the 6-digit code we sent to <strong>{email}</strong>. It may take a minute; check your spam folder too.</p>
            <div className="otp" onPaste={(e) => { e.preventDefault(); setDigit(0, e.clipboardData.getData("text")); }}>
              {digits.map((d, i) => (
                <input key={i} ref={(el) => { boxes.current[i] = el; }} inputMode="numeric" autoComplete={i === 0 ? "one-time-code" : "off"}
                       maxLength={6} value={d} aria-label={`Digit ${i + 1}`} disabled={busy}
                       onChange={(e) => setDigit(i, e.target.value)}
                       onKeyDown={(e) => { if (e.key === "Backspace" && !digits[i] && i > 0) boxes.current[i - 1]?.focus(); }} />
              ))}
            </div>
            {error && <p className="error" role="alert">{error}</p>}
            <div className="row">
              <button className="link-btn" onClick={() => { setStep("email"); setError(""); }}>Use a different e-mail</button>
              <button className="link-btn" onClick={send} disabled={wait > 0 || busy}>{wait > 0 ? `Resend in ${wait}s` : "Resend the code"}</button>
            </div>
          </>
        )}
        <p className="muted small fine">By signing in you agree that we keep your account (e-mail) to let you sign in and see your history. You choose what else we may store on the next screen.</p>
      </section>
    </div>
  );
}
