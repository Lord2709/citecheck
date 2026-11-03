# The CiteCheck website (React + FastAPI + Supabase)

Owner: Engineering.  Everything here runs at no cost: Supabase free plan, a Gmail sender, and Google Cloud Run on the
free trial (`deploy/GCP.md`).

```
browser ── React site (web/) ──► FastAPI (api/) ──► the agent and the evaluated verifier (src/)
   │                                   │
   └── sign-in: e-mailed one-time code └── Postgres: users, checks, feedback, activity (schema "citecheck")
            (Supabase Auth)                    (Supabase database)
```

One Docker container serves the site and the API, so there is a single URL and no CORS setup. It runs on Google Cloud
Run (`deploy/GCP.md`). Hugging Face Docker Spaces need a paid plan since 2026, and free web services such as Render's
offer 512 MB of memory while the site needs about 2 GB (PyTorch plus the verifier), so neither is used.

## What is stored, and why

| Table | What | When |
|---|---|---|
| `users` | consent choices, first and last visit (no e-mail: Supabase Auth keeps that) | everyone who signs in |
| `runs` | each draft check or paper search: length of the input, options, summary counts, the report shown | everyone (it is their History) |
| `runs.input_text` | the pasted text, e-mails and phone numbers masked | only with "also keep the text I paste" |
| `feedback` | 👍/👎 per report or citation; comment text only with text consent | everyone |
| `events` | page views and clicks | only with "help us improve CiteCheck" |

`/api/admin/export` (button on the Account page, for e-mails in `CITECHECK_ADMIN_EMAILS`) downloads usage, outcomes and
feedback of consenting users, with salted-hash ids and no free text. Review an export before committing any of it to
`evidence/`.

## 1. Supabase (once, about 15 minutes)

1. Create a free project at supabase.com. Note the **Project URL** (Project Settings → Data API) and the
   **publishable key** (Project Settings → API Keys).
2. **Authentication → Providers → Email**: enabled (the default).
3. **Authentication → Email Templates**: in **Magic Link** *and* **Confirm signup**, make the e-mail show the code, e.g.
   `<p>Your CiteCheck code is <strong>{{ .Token }}</strong>. It expires in 1 hour.</p>`
   (without `{{ .Token }}` Supabase sends a link instead of a code). Under **Authentication → Email**, set
   **Email OTP Length** to 6; the sign-in page accepts 6 to 10 digits either way.
4. **Authentication → URL Configuration**: Site URL = the live site's URL (today
   `https://citecheck-877770798089.us-east4.run.app`); add it and `http://localhost:8000` under **Redirect URLs**.
5. **Custom SMTP (strongly recommended before user tests)**: Supabase's built-in mailer allows only a few e-mails per
   hour on the free plan. Project Settings → Authentication → SMTP: use a free sender (e.g. Resend, Brevo, or a Gmail
   app password).
6. **Database connection string**: Connect → **Session pooler** URI (works over IPv4; the direct connection is
   IPv6-only). Change the start from `postgresql://` to `postgresql+psycopg://`, and put the database password in place
   of `[YOUR-PASSWORD]` **without the square brackets**. Use a password of letters and digits: `@ : / ? # %` break the
   address unless written as `%40 %3A %2F %3F %23 %25`. The API creates its tables in a
   `citecheck` schema on first start; Supabase's public REST API does not expose that schema, so the publishable key in
   the browser cannot read them.

## 2. Hosting

**Google Cloud Run (what the live site uses):** follow `deploy/GCP.md`.

**Alternative, Hugging Face Space** (needs HF PRO, $9/month, since 2026). Create a Space (SDK **Docker**, blank, hardware **CPU basic**). In **Settings → Variables and secrets**:

| Name | Kind | Value |
|---|---|---|
| `SUPABASE_URL` | variable | Project URL |
| `SUPABASE_PUBLISHABLE_KEY` | variable | publishable key `sb_publishable_...` (public by design; the legacy anon key also works as `SUPABASE_ANON_KEY`) |
| `DATABASE_URL` | **secret** | `postgresql+psycopg://...` session-pooler URI with the password |
| `CITECHECK_ADMIN_EMAILS` | secret | team e-mails allowed to download the research export, comma-separated |
| `CITECHECK_EXPORT_SALT` | secret | any long random string |
| `CITECHECK_MAILTO` | variable | team contact e-mail (Crossref, Unpaywall) |
| `OPENALEX_API_KEY`, `S2_API_KEY` | secrets | optional free keys |

Deploy from an up-to-date `main` (PowerShell; same as `deploy/DEPLOY.md`, with the web Dockerfile and README):

```powershell
git clone https://huggingface.co/spaces/<hf-user>/citecheck ..\citecheck-space
git archive --format=zip -o ..\citecheck-main.zip HEAD
Expand-Archive ..\citecheck-main.zip -DestinationPath ..\citecheck-space -Force
Copy-Item Dockerfile.web ..\citecheck-space\Dockerfile -Force
Copy-Item deploy\hf_space_web\README.md ..\citecheck-space\README.md -Force
Get-ChildItem ..\citecheck-space -Recurse -Include *.png,*.pdf,*.mp4 | Remove-Item
cd ..\citecheck-space
git add -A; git commit -m "Deploy CiteCheck website"; git push
```

The build (React, Python, model) takes about 15 minutes. Then check:

- [ ] the landing page loads; **Sign in** e-mails a 6-digit code and the code signs you in
- [ ] the welcome screen asks for consent (boxes unticked)
- [ ] *Check a draft* → *Try an example* → citations appear one by one, then the summary
- [ ] *Find papers* returns results; *History* lists both; *Account* shows the export button for admins
- [ ] Supabase → Table editor → schema `citecheck` shows the rows

## Local development

```powershell
pip install -r requirements.txt
$env:CITECHECK_AUTH = "off"                      # no sign-in locally; data goes to data/cache/citecheck_web.db
uvicorn --factory api.main:create_app --reload --port 8000
# second terminal
cd web; npm ci; npm run dev                      # http://localhost:5173 (forwards /api to :8000)
```

To test real sign-in locally, set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` instead of `CITECHECK_AUTH=off`.

## Security notes

- Sign-in is passwordless (an e-mailed one-time code). Every API call carries the Supabase session token, verified with
  Supabase on the server (cached 5 minutes).
- Rate limits per user: draft checks 6/min, searches 20/min. Inputs are capped (60,000 characters; 15 MB PDFs).
- People only ever see their own history (`runs` are filtered by user id on the server).
- Secrets live in Space secrets, never in the repo. The publishable key and the project URL are public by design.
