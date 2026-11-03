import { useState, type ReactNode } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

function Mark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M5 12.5l4.5 4.5L19 7.5" stroke="#f3cd45" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}

export default function Layout({ children }: { children: ReactNode }) {
  const { signedIn, me, devMode, signOut, configError } = useAuth();
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const close = () => setOpen(false);

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand" onClick={close}>
            <Mark />
            <span>CiteCheck</span>
          </Link>
          <button className="menu-btn" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>
            <span /><span /><span />
          </button>
          <nav className={`nav ${open ? "open" : ""}`}>
            <NavLink to="/check" onClick={close}>Check a draft</NavLink>
            <NavLink to="/papers" onClick={close}>Find papers</NavLink>
            {signedIn && <NavLink to="/history" onClick={close}>History</NavLink>}
            <NavLink to="/about" onClick={close}>How it works</NavLink>
            <div className="nav-account">
              {signedIn ? (
                <>
                  <NavLink to="/account" onClick={close} className="account-link" title={me?.email}>
                    {devMode ? "Dev mode" : me?.email?.split("@")[0] || "Account"}
                  </NavLink>
                  {!devMode && (
                    <button className="quiet-btn" onClick={async () => { close(); await signOut(); nav("/"); }}>
                      Sign out
                    </button>
                  )}
                </>
              ) : (
                <Link to="/signin" className="btn btn-small" onClick={close}>Sign in</Link>
              )}
            </div>
          </nav>
        </div>
      </header>
      {configError && <div className="banner banner-bad">{configError}</div>}
      <main>{children}</main>
      <footer className="footer">
        <div className="footer-inner">
          <span>CiteCheck</span>
          <span>Read the evidence before you cite.</span>
        </div>
      </footer>
    </div>
  );
}
