# Setup

Everything needed to get this project running, both on GitHub Actions and locally.

---

## 1. Create the GitHub repository

The assignment requires the repo be named `checkinbotYourFullName`, so:

```
checkinbotGageGiffin
```

This local folder is currently `Week4-6_Scheduled_Check_In_Bot/` and is its own git repo
(`git init` already run, branch `main`). Rename the folder to `checkinbotGageGiffin` when
the GitHub remote is created so the local and remote names match, then:

```bash
git remote add origin git@github.com:<username>/checkinbotGageGiffin.git
git push -u origin main
```

The repo must be reachable by the instructor — public, or with the instructor granted
access.

---

## 2. Repository secrets and variables

In the repo on GitHub: **Settings → Secrets and variables → Actions**.

| Name | Kind | Value | Why |
| --- | --- | --- | --- |
| `PRACTICE_API_TOKEN` | **Secret** | your Practice Hub API token | Authenticates every API call. Secret so GitHub masks it in logs. |
| `PRACTICE_API_URL` | Secret or variable | `https://practice.fhsucyber.com` | Base URL of the Practice Hub API. |
| `INSTRUCTOR_ID` | **Variable** | `7` | The instructor's user id. Tells the bot whose posts to collect and whose check-ins to answer. Not sensitive. |

Secrets go under the **Secrets** tab; variables go under the **Variables** tab. They are
different tabs on the same page, and the workflow reads them differently
(`secrets.NAME` vs `vars.NAME`).

> **Never commit the token.** It belongs only in GitHub Secrets and in a local `.env`
> that `.gitignore` excludes. If it is ever pasted into a file, printed to a log, or
> pushed, rotate it on the Practice Hub immediately.

---

## 3. Wiring them into the workflow

```yaml
env:
  PRACTICE_API_TOKEN: ${{ secrets.PRACTICE_API_TOKEN }}
  PRACTICE_API_URL: ${{ secrets.PRACTICE_API_URL }}
  INSTRUCTOR_ID: ${{ vars.INSTRUCTOR_ID }}
```

### Write permission

If the workflow commits `artifact/` back to the repo, it needs write access. By default
the workflow's token can read the repo but not push to it, and `git push` fails with a
**403** for `github-actions[bot]`. Add this at the **top level** of the workflow file
(not inside a step):

```yaml
permissions:
  contents: write
```

---

## 4. Schedule timing

GitHub cron is **UTC** and runs can be delayed under load.

Each check-in is open 00:00–23:59 **Central** on the date in its title. A run scheduled
between **04:00 and 06:00 UTC** sits right on top of midnight Central during daylight
time, so a delayed run can slip into the next day and miss a check-in entirely.

Plan: run **2–3 times a day**, well away from that band. The duplicate-reply guard makes
extra runs harmless, and a second run covers for the first one failing.

---

## 5. Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` in the project root (it is in `.gitignore` and is never committed):

```
PRACTICE_API_TOKEN=your_token_here
PRACTICE_API_URL=https://practice.fhsucyber.com
INSTRUCTOR_ID=7
```

Using the same three names locally as in Actions means the code reads its configuration
identically in both places — `os.environ.get(...)` — with no branching between "local" and
"CI".

---

## 6. Verifying it works

- **By hand:** Actions tab → select the workflow → **Run workflow** (this is what
  `workflow_dispatch` is for). Check the run log for errors and confirm the token is
  masked as `***`.
- **Task 1:** confirm `artifact/collected.json` and `artifact/files/` appear in the repo
  after a run, with full post bodies and the attachments actually downloaded.
- **Task 2:** open a check-in post on <https://practice.fhsucyber.com> and confirm the
  reply is there. The server records the time, so the reply's presence is the proof.
