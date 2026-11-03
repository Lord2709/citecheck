# Hosting the website on Google Cloud Run (free trial)

Owner: Engineering.  Live site: **https://citecheck-877770798089.us-east4.run.app** (project `citecheck-512817`,
service `citecheck`, region `us-east4`).  Supabase and the sign-in e-mail are set up as in `deploy/WEB.md`, part 1.

## Why Cloud Run, and what it costs

The site is one Docker container (`Dockerfile.web`: React site + FastAPI + the evaluated verifier) that needs about
2 GB of memory. Hugging Face Docker Spaces need a paid plan since 2026, and free web hosts such as Render give 512 MB,
so neither fits. Cloud Run runs the same image unchanged.

| Item | Cost |
|---|---|
| New-account free trial | $300 credit for 90 days (this project: until 2027-01-25) |
| The site, always on (2 vCPU, 4 GiB, one instance) | about $110 a month **of the credit** |
| Image builds (Cloud Build) | free (2,500 build-minutes a month) |
| Image storage (Artifact Registry, ~3 GB) | about $0.25 a month of the credit |
| Secret Manager (3 secrets) | free |

**Rules that keep it at $0:** never click **Upgrade** / **Activate full account**. On the trial the card is only
verified (a temporary authorization hold) and is never charged; when the credit or the 90 days run out, the site
stops. A budget alert (Billing → Budgets & alerts, $250, "Promotions and others" unticked) e-mails the billing
admins at 50 / 90 / 100 % of the credit.

## One-time setup

1. **Trial and project.** cloud.google.com/free with the team Google account (account type Individual; name and
   address must match the card). Create the project `citecheck`; the free-trial billing account is linked
   automatically when it is the only one (check under ☰ → Billing).
2. **Cloud Shell** (the `>_` icon; a free terminal in the browser):

```bash
gcloud config set project citecheck-512817
gcloud config set run/region us-east4
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com compute.googleapis.com
git clone https://github.com/Lord2709/citecheck.git && cd citecheck && cp Dockerfile.web Dockerfile
gcloud artifacts repositories create citecheck --repository-format=docker --location=us-east4
IMAGE=us-east4-docker.pkg.dev/citecheck-512817/citecheck/web:$(git rev-parse --short HEAD)
gcloud builds submit --tag $IMAGE --timeout=3600          # about 6 minutes
```

`cp Dockerfile.web Dockerfile` is needed because `gcloud builds submit --tag` always builds `./Dockerfile` (the older
Streamlit image). Do not commit that copy.

3. **Secrets.** `DATABASE_URL` is the Supabase session-pooler URI from `deploy/WEB.md` (starts with
   `postgresql+psycopg://`, password inserted without the `[ ]`). Paste it at the prompt; nothing is echoed.

```bash
read -rsp "Paste DATABASE_URL: " V && printf '%s' "$V" | gcloud secrets create DATABASE_URL --data-file=- && unset V; echo
psql "$(gcloud secrets versions access latest --secret=DATABASE_URL | sed 's/+psycopg//')" -c "select 1 as ok"   # must print ok / 1
openssl rand -hex 32 | tr -d '\n' | gcloud secrets create CITECHECK_EXPORT_SALT --data-file=-
printf '%s' 'admin1@example.edu,admin2@example.edu' | gcloud secrets create CITECHECK_ADMIN_EMAILS --data-file=-
gcloud iam service-accounts create citecheck-run --display-name="CiteCheck site"
SA=citecheck-run@citecheck-512817.iam.gserviceaccount.com
for s in DATABASE_URL CITECHECK_EXPORT_SALT CITECHECK_ADMIN_EMAILS; do
  gcloud secrets add-iam-policy-binding $s --member=serviceAccount:$SA --role=roles/secretmanager.secretAccessor --quiet
done
```

4. **Deploy** (fill in the publishable key and the team contact e-mail; no spaces in `--set-env-vars`):

```bash
gcloud run deploy citecheck --image $IMAGE --service-account $SA \
  --port 7860 --cpu 2 --memory 4Gi --no-cpu-throttling --cpu-boost \
  --min-instances 1 --max-instances 1 --timeout 300 --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=https://podznxaqniiocrmdoccm.supabase.co,SUPABASE_PUBLISHABLE_KEY=sb_publishable_...,CITECHECK_MAILTO=team@example.com \
  --set-secrets DATABASE_URL=DATABASE_URL:latest,CITECHECK_EXPORT_SALT=CITECHECK_EXPORT_SALT:latest,CITECHECK_ADMIN_EMAILS=CITECHECK_ADMIN_EMAILS:latest
```

| Flag | Why |
|---|---|
| `--port 7860` | the port `Dockerfile.web` listens on |
| `--no-cpu-throttling` | instance-based billing: CPU stays on between requests, which the background draft checks need |
| `--min-instances 1` | always warm, so testers never wait 30–60 s for the model to load (uses credit; set 0 to save it) |
| `--max-instances 1` | running checks live in the memory of one server; a second instance would not know them |
| `--cpu 2 --memory 4Gi` | the verifier on 2 CPUs; PyTorch + DeBERTa need about 2 GB |

5. **Supabase → Authentication → URL Configuration:** Site URL = the service URL; add it and
   `http://localhost:8000` under Redirect URLs.

## After a change is merged to `main`

```bash
cd ~/citecheck && git checkout -- Dockerfile && git pull && cp Dockerfile.web Dockerfile
IMAGE=us-east4-docker.pkg.dev/citecheck-512817/citecheck/web:$(git rev-parse --short HEAD)
gcloud builds submit --tag $IMAGE --timeout=3600 && gcloud run deploy citecheck --image $IMAGE
```

The other settings (secrets, flags) carry over from the previous revision.

## Everyday operations

| Task | Command |
|---|---|
| Recent logs | `gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="citecheck"' --freshness=15m --limit=60 --format='value(textPayload)' \| tac` |
| Change a secret | `... \| gcloud secrets versions add NAME --data-file=-`, then `gcloud run services update citecheck --update-secrets NAME=NAME:latest` (a new revision reads it) |
| Add an admin | add a new version of `CITECHECK_ADMIN_EMAILS` (comma-separated, no spaces), then the update above |
| Roll back | `gcloud run revisions list --service citecheck`, then `gcloud run services update-traffic citecheck --to-revisions=REVISION=100` |
| Save credit | `gcloud run services update citecheck --min-instances 0` (first visit after idle then waits 30–60 s) |
| Old secret versions | `gcloud secrets versions list DATABASE_URL`, then `gcloud secrets versions destroy N --secret=DATABASE_URL --quiet` |

## At the end of the semester (Dec 20)

Download the research export (Account page) first. Then either stop spending
(`gcloud run services update citecheck --min-instances 0`), delete the site
(`gcloud run services delete citecheck --region us-east4`), or shut the project down (IAM & Admin → Settings →
Shut down). The trial ends by itself on 2027-01-25 and never charges the card.

## Problems we hit, and the fix

| Symptom | Cause | Fix |
|---|---|---|
| Build: `PyTorch was not found` / `requires the PyTorch library` | unpinned `transformers` installed 5.x, which needs torch >= 2.6 | `requirements.txt` pins torch 2.8.0, transformers 4.57.6, sentence-transformers 5.1.2 (the evaluated versions) |
| Deploy: `failed to start and listen on the port` | the server exits at start-up; usually the database connection | read the logs (table above) |
| Logs: `password authentication failed` | wrong password in `DATABASE_URL` | reset it in Supabase (letters and digits), add a new secret version, redeploy |
| `psql`: host name like `abc]@aws-0-...` or `007@aws-0-...` | `[ ]` left around the password, or an `@` inside it | remove the brackets; write `@` as `%40` or choose a password without symbols |
| The e-mail has an 8-digit code | Supabase "Email OTP Length" set to 8 | the site accepts 6–10 digits; set it to 6 for consistency |
| Replacement search finds no candidates on the live site, but does locally | the free paper APIs rate-limit shared cloud addresses without a key | add free `S2_API_KEY` / `OPENALEX_API_KEY` as secrets |
