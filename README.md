# INF 601 - Scheduled Check-In Bot

Gage Giffin · Assigned Week 4, due end of Week 6

A Python bot that GitHub Actions runs on a cron schedule. It talks to the FHSU Practice
Hub REST API and does two things every run:

1. **Collects** every post the instructor has made - title, full body, tags, timestamps,
   and every attached file downloaded - into an `artifact/` folder.
2. **Replies** to each of the instructor's daily check-in posts, inside the one-day window
   the server allows.

The point of the assignment is the automation: the code runs itself on a schedule and acts
on my behalf, without me being at the keyboard.

## Status

Project scaffolding and documentation only so far. The bot itself is not written yet.

- [x] Repo initialized, `.gitignore` in place
- [x] Assignment and rubric documented under `docs/`
- [x] GitHub repository secrets and variables configured
- [ ] `requirements.txt`
- [ ] Task 1 - collection
- [ ] Task 2 - check-in replies
- [ ] GitHub Actions workflow

See [docs/RUBRIC.md](docs/RUBRIC.md) for the full checklist.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/GagePi-Dev/checkinbotGageGiffin.git
cd checkinbotGageGiffin

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

The bot reads three settings from the environment. It reads them the same way whether it
is running on your machine or inside GitHub Actions, so there is no separate "local mode".

| Name | Sensitive | Value | What it's for |
| --- | --- | --- | --- |
| `PRACTICE_API_TOKEN` | **Yes** | your Practice Hub API token | Authenticates every API call. |
| `PRACTICE_API_URL` | No | `https://practice.fhsucyber.com` | Base URL of the Practice Hub API. |
| `INSTRUCTOR_ID` | No | `7` | The instructor's user id - tells the bot whose posts to collect and whose check-ins to answer. |

For a local run, create a `.env` file in the project root:

```
PRACTICE_API_TOKEN=your_token_here
PRACTICE_API_URL=https://practice.fhsucyber.com
INSTRUCTOR_ID=7
```

`.env` is listed in `.gitignore` and is never committed. Get your own token from your
Practice Hub account - do not reuse someone else's.

> **Never commit the token.** If it is ever pasted into a file, printed to a log, or
> pushed, rotate it on the Practice Hub immediately.

### 3. Run it

```bash
python checkin.py
```

## Running it on your own GitHub Actions

If you fork or clone this repo and want the schedule running under your own account:

### Add the secrets and variables

In your repo: **Settings → Secrets and variables → Actions**. Use the **repository**
level, not environment level - environment secrets are only injected into jobs that
declare `environment:`, and without it they silently resolve to an empty string.

- **Secrets** tab → `PRACTICE_API_TOKEN`
- **Variables** tab → `PRACTICE_API_URL` and `INSTRUCTOR_ID`

The URL is kept as a variable rather than a secret so its value stays readable in the UI;
secrets are write-only once saved, which makes a typo in one invisible.

The workflow reads them to match where each one lives - `secrets.` for the token, `vars.`
for the other two:

```yaml
env:
  PRACTICE_API_TOKEN: ${{ secrets.PRACTICE_API_TOKEN }}
  PRACTICE_API_URL: ${{ vars.PRACTICE_API_URL }}
  INSTRUCTOR_ID: ${{ vars.INSTRUCTOR_ID }}
```

### Give the workflow write access

The workflow commits `artifact/` back to the repo, which the default workflow token cannot
do - `git push` fails with a 403 for `github-actions[bot]`. This goes at the **top level**
of the workflow file, not inside a step:

```yaml
permissions:
  contents: write
```

### A note on the schedule

GitHub cron is **UTC** and runs can be delayed under load. Each check-in is open
00:00-23:59 **Central** on the date in its title, so a run scheduled between **04:00 and
06:00 UTC** sits right on top of midnight Central during daylight time - a delayed run
there can slip into the next day and miss a check-in entirely. The schedule runs a few
times a day, well away from that band, so a failed run has a backup. The duplicate-reply
check makes the extra runs harmless.

You can also trigger a run by hand from the Actions tab - that is what the
`workflow_dispatch` trigger is for. Check the run log afterward and confirm the token
appears masked as `***`.

## Documentation

| File | What's in it |
| --- | --- |
| [docs/ASSIGNMENT.md](docs/ASSIGNMENT.md) | The assignment instructions as given - tasks, timing rules, points. |
| [docs/RUBRIC.md](docs/RUBRIC.md) | The 100-point breakdown as a checklist. |

## AI Usage

### What I used Claude Code for

So far Claude Code (Opus 5) has written the project documentation: it took the assignment
instructions I pasted in and turned them into `docs/ASSIGNMENT.md`, `docs/RUBRIC.md`, and
this README. It also wrote the `.gitignore` and handled the git and GitHub setup - wiring
the repo to its remote and renaming it to the required format.

I am directing the build - Claude Code proposes what it intends to write and I approve it
before anything is created. This table is updated as the project goes.

| Date | Tool | What it did |
| --- | --- | --- |
| 2026-09-15 | Claude Code (Opus 5) | Wrote `docs/ASSIGNMENT.md` and `docs/RUBRIC.md` from the assignment instructions. |
| 2026-09-15 | Claude Code (Opus 5) | Wrote the base README and the `.gitignore`. |
| 2026-09-15 | Claude Code (Opus 5) | Connected the repo to its GitHub remote, renamed it to `checkinbotGageGiffin`, and verified the repository secrets and variables. |
| 2026-09-15 | Claude Code (Opus 5) | Folded the separate setup doc into the README as a setup section. |

### What I wrote myself

<!-- TODO: fill in as I write the bot. -->

The Week 3 Mini Project 1 API client is my own work, and it is the foundation this bot
builds on - the bearer-token auth, the `/api/v1/posts` calls, and the error handling
pattern all carry over from code I wrote by hand.

I set up the GitHub repository secrets and variables myself.

### What I changed in AI-generated code

<!-- TODO: fill in as I revise. -->
