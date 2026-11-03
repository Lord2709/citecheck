// Small fetch wrapper: adds the signed-in user's token and turns API errors into readable messages.
let tokenGetter: () => Promise<string | null> = async () => null;

export function setTokenGetter(fn: () => Promise<string | null>) {
  tokenGetter = fn;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function headers(json: boolean): Promise<HeadersInit> {
  const h: Record<string, string> = {};
  const token = await tokenGetter();
  if (token) h["Authorization"] = `Bearer ${token}`;
  if (json) h["Content-Type"] = "application/json";
  return h;
}

async function handle<T>(r: Response): Promise<T> {
  if (r.ok) return (await r.json()) as T;
  let msg = `Something went wrong (HTTP ${r.status}). Please try again.`;
  try {
    const j = await r.json();
    if (typeof j.detail === "string") msg = j.detail;
    else if (Array.isArray(j.detail)) msg = "Some of the input is not valid. Please check it and try again.";
  } catch {
    /* not JSON */
  }
  throw new ApiError(r.status, msg);
}

export async function get<T>(path: string): Promise<T> {
  return handle<T>(await fetch(path, { headers: await headers(false) }));
}

export async function post<T>(path: string, body: unknown): Promise<T> {
  return handle<T>(await fetch(path, { method: "POST", headers: await headers(true), body: JSON.stringify(body) }));
}

export async function postForm<T>(path: string, form: FormData): Promise<T> {
  return handle<T>(await fetch(path, { method: "POST", headers: await headers(false), body: form }));
}

export async function download(path: string, filename: string) {
  const r = await fetch(path, { headers: await headers(false) });
  if (!r.ok) throw new ApiError(r.status, "The download failed. Please try again.");
  const url = URL.createObjectURL(await r.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
