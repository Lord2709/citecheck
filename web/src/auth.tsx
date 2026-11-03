// Sign-in with an e-mailed one-time code (Supabase Auth; 6 to 10 digits, set in Supabase), and the current user's profile from our API.
import { createClient, type Session, type SupabaseClient } from "@supabase/supabase-js";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { get, setTokenGetter } from "./api";
import { setTracking } from "./track";
import type { Me } from "./types";

interface Config {
  auth: "supabase" | "off";
  supabase_url: string;
  supabase_anon_key: string;
}

interface AuthState {
  ready: boolean;
  configError: string;
  devMode: boolean;
  signedIn: boolean;
  me: Me | null;
  sendCode: (email: string) => Promise<void>;
  verifyCode: (email: string, code: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshMe: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<Config | null>(null);
  const [configError, setConfigError] = useState("");
  const [client, setClient] = useState<SupabaseClient | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    get<Config>("/api/config")
      .then((c) => {
        setConfig(c);
        if (c.auth === "supabase") {
          const sb = createClient(c.supabase_url, c.supabase_anon_key, {
            auth: { persistSession: true, autoRefreshToken: true },
          });
          setClient(sb);
          setTokenGetter(async () => (await sb.auth.getSession()).data.session?.access_token ?? null);
          sb.auth.getSession().then(({ data }) => setSession(data.session));
          sb.auth.onAuthStateChange((_e, s) => setSession(s));
        } else {
          setReady(true);
        }
      })
      .catch(() => {
        setConfigError("CiteCheck's server is not reachable right now. Please try again in a minute.");
        setReady(true);
      });
  }, []);

  const devMode = config?.auth === "off";
  const signedIn = devMode || !!session;

  const refreshMe = useCallback(async () => {
    try {
      const m = await get<Me>("/api/me");
      setMe(m);
      setTracking(!!m.consent.research);
    } catch {
      setMe(null);
    }
  }, []);

  useEffect(() => {
    if (!config) return;
    if (signedIn) {
      refreshMe().finally(() => setReady(true));
    } else {
      setMe(null);
      setTracking(false);
      if (config.auth === "supabase" && client) setReady(true);
    }
  }, [config, client, signedIn, refreshMe]);

  const sendCode = useCallback(
    async (email: string) => {
      if (!client) throw new Error("Sign-in is not available.");
      const { error } = await client.auth.signInWithOtp({ email, options: { shouldCreateUser: true } });
      if (error) throw new Error(friendly(error.message));
    },
    [client],
  );

  const verifyCode = useCallback(
    async (email: string, code: string) => {
      if (!client) throw new Error("Sign-in is not available.");
      const { error } = await client.auth.verifyOtp({ email, token: code, type: "email" });
      if (error) throw new Error(friendly(error.message));
    },
    [client],
  );

  const signOut = useCallback(async () => {
    if (client) await client.auth.signOut();
    setMe(null);
  }, [client]);

  const value = useMemo(
    () => ({ ready, configError, devMode, signedIn, me, sendCode, verifyCode, signOut, refreshMe }),
    [ready, configError, devMode, signedIn, me, sendCode, verifyCode, signOut, refreshMe],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

function friendly(msg: string): string {
  const m = msg.toLowerCase();
  if (m.includes("rate limit") || m.includes("too many")) return "Too many codes were requested. Please wait a few minutes and try again.";
  if (m.includes("expired") || m.includes("invalid")) return "That code is not valid or has expired. Request a new one.";
  if (m.includes("email")) return "Please enter a valid e-mail address.";
  return msg;
}

export function useAuth(): AuthState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}
