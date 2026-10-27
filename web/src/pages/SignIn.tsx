import { useEffect, useRef, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth";
import { safeNext } from "../format";

// Supabase sends codes of 6 to 10 digits (Authentication → Email → "Email OTP Length"); accept any of them.
const MIN_CODE = 6;
const MAX_CODE = 10;

export default function SignIn() {
  const { signedIn, sendCode, verifyCode, ready } = useAuth();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"email" | "code">("email");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [wait, setWait] = useState(0);
  const codeBox = useRef<HTMLInputElement | null>(null);

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
      setCode("");
      setWait(60);
      window.setTimeout(() => codeBox.current?.focus(), 50);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function verify(value: string) {
    if (value.length < MIN_CODE) return setError(`Enter the full code from the e-mail (at least ${MIN_CODE} digits).`);
    setError("");
    setBusy(true);
    try {
      await verifyCode(email.trim().toLowerCase(), value);
    } catch (e) {
      setError((e as Error).message);
      setCode("");
      window.setTimeout(() => codeBox.current?.focus(), 50);
    } finally {
      setBusy(false);
    }
  }

  const digitsOnly = (v: string) => v.replace(/\D/g, "").slice(0, MAX_CODE);

  return (
    <div className="page narrow">
      <section className="card auth">
        <h1>Sign in</h1>
        {step === "email" ? (
          <>
            <p className="lead small">We'll e-mail you a sign-in code. No password needed.</p>
            <label className="field-label" htmlFor="email">E-mail</label>
            <input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)}
                   onKeyDown={(e) => e.key === "Enter" && send()} placeholder="name@example.com" />
            {error && <p className="error" role="alert">{error}</p>}
            <button className="btn btn-primary wide" onClick={send} disabled={busy}>{busy ? "Sending…" : "Send me a code"}</button>
          </>
        ) : (
          <>
            <p className="lead small">Enter the code we sent to <strong>{email}</strong>. It may take a minute; check your spam folder too.</p>
            <label className="field-label" htmlFor="code">Code</label>
            <input id="code" ref={codeBox} className="otp-input" inputMode="numeric" autoComplete="one-time-code"
                   maxLength={MAX_CODE} value={code} disabled={busy} aria-describedby="code-help"
                   onChange={(e) => setCode(digitsOnly(e.target.value))}
                   onPaste={(e) => {
                     e.preventDefault();
                     const pasted = digitsOnly(e.clipboardData.getData("text"));
                     setCode(pasted);
                     if (pasted.length >= MIN_CODE) verify(pasted);
                   }}
                   onKeyDown={(e) => e.key === "Enter" && verify(code)} />
            <span id="code-help" className="muted small">Digits only. Pasting the code signs you in straight away.</span>
            {error && <p className="error" role="alert">{error}</p>}
            <button className="btn btn-primary wide" onClick={() => verify(code)} disabled={busy || code.length < MIN_CODE}>
              {busy ? "Signing in…" : "Sign in"}
            </button>
            <div className="row auth-links">
              <button className="link-btn" onClick={() => { setStep("email"); setError(""); setCode(""); }}>Use a different e-mail</button>
              <button className="link-btn" onClick={send} disabled={wait > 0 || busy}>{wait > 0 ? `Resend in ${wait}s` : "Resend the code"}</button>
            </div>
          </>
        )}
        <p className="muted small fine">By signing in you agree that we keep your account (e-mail) to let you sign in and see your history. You choose what else we may store on the next screen.</p>
      </section>
    </div>
  );
}
