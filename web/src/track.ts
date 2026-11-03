// Product activity events. The server stores them only for people who agreed to research use.
import { post } from "./api";

function sessionId(): string {
  try {
    let id = sessionStorage.getItem("cc_session");
    if (!id) {
      id = Math.random().toString(36).slice(2) + Date.now().toString(36);
      sessionStorage.setItem("cc_session", id);
    }
    return id;
  } catch {
    return "no-storage";
  }
}

let enabled = false;

export function setTracking(on: boolean) {
  enabled = on;
}

export function track(event: string, props: Record<string, string | number | boolean> = {}) {
  if (!enabled) return;
  post("/api/events", { event, props, session_id: sessionId() }).catch(() => undefined);
}
