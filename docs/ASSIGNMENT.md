# Assignment: Scheduled Check-In Bot

> Source of truth for this project. Copied from the course instructions as given.
> Assigned Week 4 · due end of Week 6 · 100 points.

## Submission

- Submit a **link to the GitHub repository**. Name it `checkinbotYourFullName`.
- Due **Sunday at midnight Central at the end of Week 6**.
- The result of this assignment lives in the GitHub repo (a committed `artifact/` folder
  produced by the scheduled workflow). There is nothing to upload to Blackboard except
  the repo link.

## Required file header

Every `.py` file starts with:

```python
# INF601 - Advanced Programming in Python
# Your Name
# Scheduled Check-In Bot
```

## The idea

Write a Python program that a GitHub Actions schedule runs automatically, every day. It
talks to the Practice Hub REST API and does two jobs. This is a first taste of automation
as a harness: code that runs itself on a schedule and acts on your behalf.

You configure it once; GitHub runs it on a cron schedule for the rest of the assignment
window.

## Task 1 — Collect everything the instructor posts

Pull **every** piece of content from the instructor's posts (only the instructor's —
ignore other students' posts). For each post, capture:

- the **title**, **body** (long or short), **tags**, and **timestamps**, and
- **every attached file** — the program must *download* each attachment, not just note
  that it exists.

Save it all into an `artifact/` folder (`collected.json` plus a `files/` directory).

- If the instructor posts 3 paragraphs, the artifact must contain 3 paragraphs — not a
  truncated preview.
- If the instructor attaches two files, both files must be downloaded.

**The API paginates.** Page through *all* of the instructor's posts, not just the first
page.

## Task 2 — Reply to each daily check-in, on time

Every so often the instructor posts a check-in. It is recognizable because the title
contains the words "check-in" — but with other text around it, e.g. `"Aug 21th check-in"`
or `"check-in for Sept 8"`. The program must:

1. **Find** the instructor's check-in posts by matching that keyword in the title (and
   only those — do not reply to regular posts or to other people's posts), and
2. **Reply** to each one by posting a comment.

Each check-in only accepts replies during a limited time window. **The server enforces
this:** replying too early or too late returns **`423`** and the reply is not recorded.
That is why the schedule matters — the bot has to run while the window is open. Miss a
window (because of a bug, or because the schedule didn't catch it) and that check-in is
gone; its points are lost.

Because the server records the time, the **presence of the reply is the proof**. Task 2 is
graded by listing who replied to each check-in.

### When check-ins are open

Each check-in is open for **one full day, 00:00 to 23:59 Central**, on the date in its
title.

A schedule that runs once a day will catch every one, **as long as it does not run close
to midnight Central** — that is, avoid **04:00 to 06:00 UTC** while Central is on daylight
time, because a delayed run there can slip into the next day and miss one.

Running **two or three times a day** gives margin if a run fails; the duplicate-reply
check makes that safe.

## How it runs

- A GitHub Actions workflow (`.github/workflows/....yml`) with a `schedule:` (cron)
  trigger **and** `workflow_dispatch` (so it can also be run by hand).
- The Practice Hub token is stored as a repository secret (`PRACTICE_API_TOKEN`) —
  **never commit it**. The site URL and the instructor user id go in as a secret/variable
  too.
- The workflow runs the program, then saves `artifact/` into the repo (commit it back
  and/or upload it as an Actions artifact) so it is in the GitHub account for the
  instructor to review by the deadline.

## The three settings the workflow needs

In the repo: **Settings → Secrets and variables → Actions**.

| Name | Kind | Value |
| --- | --- | --- |
| `PRACTICE_API_TOKEN` | Secret | your own Practice Hub API token |
| `PRACTICE_API_URL` | Secret or variable | `https://practice.fhsucyber.com` |
| `INSTRUCTOR_ID` | Variable | `7` |

`INSTRUCTOR_ID` is the instructor's user id on the Practice Hub — it is how the bot knows
whose posts to collect and whose check-ins to answer. **It is not a secret; the token
is.** Read them in the workflow the usual way:

```yaml
env:
  PRACTICE_API_TOKEN: ${{ secrets.PRACTICE_API_TOKEN }}
  PRACTICE_API_URL: ${{ secrets.PRACTICE_API_URL }}
  INSTRUCTOR_ID: ${{ vars.INSTRUCTOR_ID }}
```

### Workflow write permission

If the workflow commits `artifact/` back to the repo, it needs write access. By default
the workflow's token can read the repo but not push to it, so the `git push` step fails
with a **403** for `github-actions[bot]`. Add this at the **top level** of the workflow
file:

```yaml
permissions:
  contents: write
```

## Requirements and points

| Pts | Requirement |
| --- | --- |
| 10 | **Repo set up correctly**: header comments, repo naming, `requirements.txt`, and a `README.md` with an `## AI Usage` section. |
| 15 | **A scheduled workflow**: a working `schedule:` cron trigger *and* `workflow_dispatch`, with the token stored as a secret (not in code or logs). |
| 25 | **Collection (Task 1)**: `artifact/` contains all of the instructor's posts with full bodies and every attachment downloaded. Graded with the instructor's `verify_artifact.py` — missing posts/files/bodies lose points. |
| 30 | **Check-ins (Task 2)**: replied to each check-in within its window, found by the keyword (no replies to non-check-ins or other authors). Graded by tallying replies across all the assignment's check-ins — each missed check-in loses points. |
| 10 | **The artifact is saved** to the GitHub repo and reviewable by the deadline. |
| 5 | **Robustness**: handles the closed-window `423` gracefully and does not post duplicate replies on re-runs. |
| 5 | **Frequent, meaningful commits (≥ 5)** — the workflow's own commits count. |

## AI Usage (required)

Use Claude Code to help build this — that is encouraged. Add a short `## AI Usage` section
to the README describing what was AI-assisted vs. hand-written. **You must be able to
explain every line, including the workflow YAML.**

## Tips

- Recognize a check-in with something like `"check-in" in title.lower()`.
- Avoid duplicate replies: before replying, check the post's existing comments for one
  authored by you.
- GitHub cron is UTC and can be delayed under load, so don't cut the timing fine — let the
  schedule run with margin inside the window.
- A reference solution exists; the acceptance behavior is exactly "collect all my posts +
  files, and reply to each open check-in within its window."

## Where this fits

Set this up in Week 4, right after the API client (Mini Project 1) — you already know how
to call the Practice Hub. It then runs on its schedule across Weeks 4–6 and is graded at
the deadline (~end of Week 6). That timing is deliberate: you will have just built a small
piece of scheduled automation that acts on your behalf, which is the lead-in to Week 7,
where the agentic foundations unit explains what an agent harness really is.
