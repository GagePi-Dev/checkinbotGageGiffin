# Rubric Checklist — 100 points

Progress tracker for the grading criteria in [ASSIGNMENT.md](ASSIGNMENT.md).
Check items off as they are finished. Nothing here is done yet.

---

## 1. Repo set up correctly — 10 pts

- [x] Repo named `checkinbotGageGiffin` on GitHub
- [x] Every `.py` file starts with the three-line header
      (`# INF601 - Advanced Programming in Python` / `# Gage Giffin` / `# Scheduled Check-In Bot`)
- [x] `requirements.txt` present and accurate
- [x] `README.md` present with an `## AI Usage` section
- [x] `.gitignore` keeps `.env`, `.venv/`, `__pycache__/` out of the repo

## 2. A scheduled workflow — 15 pts

- [ ] `.github/workflows/*.yml` exists
- [ ] `schedule:` cron trigger, running 2–3× per day
- [ ] Cron avoids **04:00–06:00 UTC** (too close to midnight Central; a delayed run
      can slip into the next day and miss a check-in)
- [ ] `workflow_dispatch` trigger so it can be run by hand
- [ ] `permissions: contents: write` at the top level (required to push `artifact/` back)
- [ ] Token read from `secrets.PRACTICE_API_TOKEN` — never in code, never printed to logs
- [ ] Verified working by an actual run in the Actions tab

## 3. Collection — Task 1 — 25 pts

Graded with the instructor's `verify_artifact.py`.

- [x] Fetches only the instructor's posts (`INSTRUCTOR_ID`, currently `7`)
- [x] **Pages through every page** of results, not just the first
- [x] Captures title, **full body** (no truncation), tags, timestamps
- [x] **Downloads every attachment** to `artifact/files/`
- [x] Writes `artifact/collected.json`
- [x] Spot-checked: a multi-paragraph post keeps all paragraphs; a post with two
      attachments yields two downloaded files

## 4. Check-ins — Task 2 — 30 pts

Highest-value item, and the only one that **cannot be made up later** — a missed window
is permanently lost.

- [ ] Identifies check-ins via `"check-in" in title.lower()`
- [ ] Replies **only** to the instructor's check-in posts
- [ ] Does **not** reply to the instructor's regular posts
- [ ] Does **not** reply to other students' posts
- [ ] Posts an actual comment on each check-in
- [ ] Confirmed at least one reply was accepted by the server

## 5. Artifact saved to the repo — 10 pts

- [ ] Workflow commits `artifact/` back to the repo (and/or uploads it as an Actions artifact)
- [x] `artifact/` is visible on GitHub and reviewable before the deadline

## 6. Robustness — 5 pts

- [ ] A `423` (window closed) is handled gracefully — logged, run does not crash
- [ ] Duplicate-reply guard: checks a post's existing comments for one authored by me
      before replying, so 2–3 runs per day are safe
- [x] Other HTTP errors do not take down the whole run

## 7. Commits — 5 pts

- [ ] At least 5 frequent, meaningful commits (the workflow's own artifact commits count)

---

## Deadline

Sunday at midnight Central, end of Week 6. Submit the repo link only.
