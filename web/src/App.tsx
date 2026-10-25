import { useEffect, type ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import About from "./pages/About";
import Account from "./pages/Account";
import CheckDraft from "./pages/CheckDraft";
import Consent from "./pages/Consent";
import FindPapers from "./pages/FindPapers";
import History from "./pages/History";
import Landing from "./pages/Landing";
import RunView from "./pages/RunView";
import SignIn from "./pages/SignIn";
import { track } from "./track";

function Protected({ children }: { children: ReactNode }) {
  const { ready, signedIn, me } = useAuth();
  const loc = useLocation();
  if (!ready) return <div className="page center"><span className="spinner" aria-label="Loading" /></div>;
  if (!signedIn) return <Navigate to={`/signin?next=${encodeURIComponent(loc.pathname)}`} replace />;
  if (me?.needs_consent && loc.pathname !== "/welcome") return <Navigate to={`/welcome?next=${encodeURIComponent(loc.pathname)}`} replace />;
  return <>{children}</>;
}

export default function App() {
  const loc = useLocation();
  useEffect(() => {
    track("page_view", { page: loc.pathname.split("/")[1] || "home" });
  }, [loc.pathname]);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/about" element={<About />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/welcome" element={<Protected><Consent /></Protected>} />
        <Route path="/check" element={<Protected><CheckDraft /></Protected>} />
        <Route path="/papers" element={<Protected><FindPapers /></Protected>} />
        <Route path="/history" element={<Protected><History /></Protected>} />
        <Route path="/runs/:id" element={<Protected><RunView /></Protected>} />
        <Route path="/account" element={<Protected><Account /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
