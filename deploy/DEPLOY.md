# Deploying CiteCheck (Hugging Face Spaces, free)

Owner: Engineering.  The Space runs the same code and the same evaluated model as `main`
(`eval/results/deployed_config.json`); the sidebar must say **Validated configuration**.

Why Hugging Face Spaces: the free "CPU basic" hardware has enough memory for the DeBERTa verifier (~0.7 GB of weights),
and the Docker SDK lets us bake the data and the model into the image. Limits: the Space sleeps after a period without
visitors (the first visit then takes a minute or two), and **files written at run time, including the usage log, are lost
on every restart**: use the researcher panel's "Download this session's log" right after each user session.

## Once: create the Space

1. Sign in at huggingface.co → **New Space**. Name `citecheck`, SDK **Docker** (blank template), hardware **CPU basic
   (free)**, visibility **Public**.
2. Space → **Settings → Variables and secrets**:
   - variable `CITECHECK_MAILTO` = a team e-mail (Crossref polite pool; needed for Unpaywall full text)
   - secret `OPENALEX_API_KEY` = free key from openalex.org (optional; without it OpenAlex allows very few searches a day)
   - secret `S2_API_KEY` = Semantic Scholar key (optional)
3. huggingface.co → **Settings → Access Tokens** → new token with **write** access. Git asks for it as the password.

## Every deploy (Windows PowerShell, from the repo, on an up-to-date `main`)

```powershell
git checkout main; git pull
git clone https://huggingface.co/spaces/<hf-user>/citecheck ..\citecheck-space
git archive --format=zip -o ..\citecheck-main.zip HEAD
Expand-Archive ..\citecheck-main.zip -DestinationPath ..\citecheck-space -Force
Copy-Item deploy\hf_space\README.md ..\citecheck-space\README.md -Force
# Spaces refuse binary files pushed without LFS: the plots are not needed by the app
Get-ChildItem ..\citecheck-space -Recurse -Include *.png,*.pdf,*.mp4 | Remove-Item
cd ..\citecheck-space
git add -A
git commit -m "Deploy CiteCheck main $(git -C ..\citecheck rev-parse --short HEAD)"
git push
```
(Adjust `..\citecheck` to your repo folder name.) The build takes about 10-15 minutes; watch **Logs → Build**.

## Check it before telling anyone

- [ ] Sidebar: **Validated configuration `zero_shot_nli`** (not DEMO, not UNVALIDATED)
- [ ] *Check a citation* → *Demo examples* → *Load* → *Check citation* gives the recorded verdict
- [ ] *Check a draft* → *Load an example* → *Check every citation*: four rows, at least one supported
- [ ] *Find papers* with a one-line direction returns papers (an info box names any source that did not answer)
- [ ] Note the commit you deployed in the PR / report (`git rev-parse --short HEAD`)

Link for user sessions: `https://<hf-user>-citecheck.hf.space/?p=P01` (one code per participant).

## If the build fails

Read the first error in **Logs → Build**. A library version that no longer installs: pin it in `requirements.txt` to
the version on a laptop where everything works (`pip freeze | findstr <name>`), commit through a PR, deploy again.
