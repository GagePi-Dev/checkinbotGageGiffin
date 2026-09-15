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
- [x] Assignment, rubric, and setup documented under `docs/`
- [ ] `requirements.txt`
- [ ] Task 1 - collection
- [ ] Task 2 - check-in replies
- [ ] GitHub Actions workflow

See [docs/RUBRIC.md](docs/RUBRIC.md) for the full checklist.

## Documentation

| File | What's in it |
| --- | --- |
| [docs/ASSIGNMENT.md](docs/ASSIGNMENT.md) | The assignment instructions as given - tasks, timing rules, points. |
| [docs/RUBRIC.md](docs/RUBRIC.md) | The 100-point breakdown as a checklist. |
| [docs/SETUP.md](docs/SETUP.md) | Creating the repo, the secrets and variables, cron timing, local `.env` setup. |

## Configuration

Three settings, read from the environment in both GitHub Actions and local runs:

| Name | Kind | Value |
| --- | --- | --- |
| `PRACTICE_API_TOKEN` | Secret | my Practice Hub API token |
| `PRACTICE_API_URL` | Secret or variable | `https://practice.fhsucyber.com` |
| `INSTRUCTOR_ID` | Variable | `7` |

The token is stored as a GitHub repository secret and in a local `.env`. `.env` is listed
in `.gitignore` and is never committed. Full instructions are in
[docs/SETUP.md](docs/SETUP.md).

## Running

Locally:

```bash
pip install -r requirements.txt
python checkin.py
```

On GitHub: the workflow runs on its cron schedule, and can also be started by hand from
the Actions tab via `workflow_dispatch`.

## AI Usage

### What I used Claude Code for

So far Claude Code (Opus 5) has written the project documentation: it took the assignment
instructions I pasted in and turned them into `docs/ASSIGNMENT.md`, `docs/RUBRIC.md`, and
`docs/SETUP.md`, plus this README. It also wrote the `.gitignore`.

I am directing the build - Claude Code proposes what it intends to write and I approve it
before anything is created. This table is updated as the project goes.

| Date | Tool | What it did |
| --- | --- | --- |
| 2026-09-15 | Claude Code (Opus 5) | Wrote `docs/ASSIGNMENT.md`, `docs/RUBRIC.md`, and `docs/SETUP.md` from the assignment instructions. |
| 2026-09-15 | Claude Code (Opus 5) | Wrote the base README and the `.gitignore`. |

### What I wrote myself

<!-- TODO: fill in as I write the bot. -->

The Week 3 Mini Project 1 API client is my own work, and it is the foundation this bot
builds on - the bearer-token auth, the `/api/v1/posts` calls, and the error handling
pattern all carry over from code I wrote by hand.

### What I changed in AI-generated code

<!-- TODO: fill in as I revise. -->
