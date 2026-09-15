# INF601 - Advanced Programming in Python
# Gage Giffin
# Scheduled Check-In Bot

# Imports
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load PRACTICE_API_TOKEN / PRACTICE_API_URL / INSTRUCTOR_ID from a local .env when
# running by hand. On GitHub Actions the workflow supplies the same three names as
# environment variables, so the settings are read the same way in both places.
load_dotenv()

# Configuration
API_URL = os.environ.get("PRACTICE_API_URL", "https://practice.fhsucyber.com").rstrip("/")
API_TOKEN = os.environ.get("PRACTICE_API_TOKEN")
INSTRUCTOR_ID = int(os.environ.get("INSTRUCTOR_ID", "7"))

ARTIFACT_DIR = Path("artifact")
FILES_DIR = ARTIFACT_DIR / "files"
COLLECTED_JSON = ARTIFACT_DIR / "collected.json"

PAGE_SIZE = 100          # the API rejects limit > 100 with a 422
CHECKIN_KEYWORD = "check-in"
REPLY_BODY = "Checking in - Gage Giffin"


# Error Handling
def check(resp):
    if not resp.ok:
        detail = resp.json()["detail"]
        if isinstance(detail, list):
            detail = detail[0]["msg"]  # 422 sends a list of validation errors
        raise SystemExit(f"Error {resp.status_code}: {detail}")
    return resp


# API Client
class PracticeHubClient:
    ENDPOINT = API_URL
    HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

    def me(self):
        """The account that owns the token."""
        return check(requests.get(
            f"{self.ENDPOINT}/api/v1/me",
            headers=self.HEADERS,
        )).json()

    def posts(self, author, limit=PAGE_SIZE, offset=0):
        """One page of posts by one author. The API returns a bare JSON array."""
        return check(requests.get(
            f"{self.ENDPOINT}/api/v1/posts",
            headers=self.HEADERS,
            params={"author": author, "limit": limit, "offset": offset},
        )).json()

    def allPosts(self, author):
        """Every post by one author, paging until a short page comes back.

        There is no "total" or "next" field to follow, so the stopping rule is that
        a page holding fewer than PAGE_SIZE posts must be the last one.
        """
        collected = []
        offset = 0
        while True:
            page = self.posts(author, PAGE_SIZE, offset)
            collected.extend(page)
            if len(page) < PAGE_SIZE:
                return collected
            offset += len(page)

    def attachment(self, download_url):
        """The raw bytes of an attachment. download_url is relative to the endpoint."""
        return check(requests.get(
            f"{self.ENDPOINT}{download_url}",
            headers=self.HEADERS,
        )).content

    def comments(self, post_id):
        """A post's comments, oldest first."""
        return check(requests.get(
            f"{self.ENDPOINT}/api/v1/posts/{post_id}/comments",
            headers=self.HEADERS,
        )).json()

    def addComment(self, post_id, body):
        """Post a comment. Returns the status code without raising.

        check() is deliberately not used here: a closed check-in answers 423, which
        is a normal outcome for this bot and must not stop the run.
        """
        resp = requests.post(
            f"{self.ENDPOINT}/api/v1/posts/{post_id}/comments",
            headers=self.HEADERS,
            json={"body": body},
        )
        return resp.status_code


# Task 1 - Collect the instructor's posts and files
class Collector:
    def __init__(self, client, instructor_id):
        self.client = client
        self.instructor_id = instructor_id

    def saveAttachment(self, attachment):
        """Download one attachment and return its path relative to artifact/."""
        # Path(...).name keeps a filename from the server out of other directories,
        # and the id prefix keeps two posts from overwriting each other's files.
        name = f"{attachment['id']}_{Path(attachment['filename']).name}"
        (FILES_DIR / name).write_bytes(self.client.attachment(attachment["download_url"]))
        print(f"    saved files/{name} ({attachment['size']} bytes)")
        return f"files/{name}"

    def collect(self):
        """Write artifact/collected.json and artifact/files/. Returns the posts."""
        FILES_DIR.mkdir(parents=True, exist_ok=True)

        posts = self.client.allPosts(self.instructor_id)
        files = 0

        for post in posts:
            print(f"  post {post['id']}: {post['title']!r} "
                  f"({len(post['body'])} chars, {len(post['attachments'])} attachment(s))")
            for attachment in post["attachments"]:
                attachment["saved_path"] = self.saveAttachment(attachment)
                files += 1

        COLLECTED_JSON.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "instructor_id": self.instructor_id,
            "post_count": len(posts),
            "attachment_count": files,
            "posts": posts,
        }, indent=2, ensure_ascii=False))

        print(f"\nCollected {len(posts)} post(s) and {files} file(s) into {ARTIFACT_DIR}/")
        return posts


# Task 2 - Reply to the instructor's check-in posts
class Replier:
    def __init__(self, client, my_id):
        self.client = client
        self.my_id = my_id

    def isCheckin(self, post):
        """A check-in is any of the instructor's posts with the keyword in its title."""
        return CHECKIN_KEYWORD in post["title"].lower()

    def alreadyReplied(self, post_id):
        """True if one of my own comments is already on the post.

        This is what makes running several times a day safe: the second run of the
        day sees the first run's comment and leaves the post alone.
        """
        return any(c["author_id"] == self.my_id for c in self.client.comments(post_id))

    def reply(self, posts):
        """Reply once to every open check-in. posts are the instructor's only."""
        replied = 0

        for post in posts:
            if not self.isCheckin(post):
                continue  # a regular post of the instructor's - never reply to it

            if self.alreadyReplied(post["id"]):
                print(f"  post {post['id']}: {post['title']!r} - already replied")
                continue

            status = self.client.addComment(post["id"], REPLY_BODY)
            if status == 201:
                print(f"  post {post['id']}: {post['title']!r} - REPLIED")
                replied += 1
            elif status == 423:
                # The window for this check-in is closed. Expected for past and
                # future dates, so it is reported and the run carries on.
                print(f"  post {post['id']}: {post['title']!r} - window closed (423)")
            else:
                print(f"  post {post['id']}: {post['title']!r} - failed ({status})")

        print(f"\nReplied to {replied} check-in(s) this run.")
        return replied


# Entry point
def main():
    if not API_TOKEN:
        raise SystemExit("PRACTICE_API_TOKEN is not set. Add it to .env locally, "
                         "or as a repository secret on GitHub.")

    client = PracticeHubClient()
    me = client.me()
    print(f"Running as {me['name']} (id {me['id']}) against {API_URL}\n")

    print(f"Task 1 - collecting posts by user {INSTRUCTOR_ID}")
    posts = Collector(client, INSTRUCTOR_ID).collect()

    print(f"\nTask 2 - replying to check-ins")
    Replier(client, me["id"]).reply(posts)


if __name__ == "__main__":
    main()
