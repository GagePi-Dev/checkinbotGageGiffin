# INF601 - Advanced Programming in Python
# Gage Giffin
# Scheduled Check-In Bot

# Imports
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load PRACTICE_API_TOKEN / PRACTICE_API_URL / INSTRUCTOR_ID from a local .env when
# running by hand. On GitHub Actions the workflow supplies them as environment
# variables instead, so the code reads its settings the same way in both places.
load_dotenv()

# Configuration
API_URL = os.environ.get("PRACTICE_API_URL", "https://practice.fhsucyber.com").rstrip("/")
API_TOKEN = os.environ.get("PRACTICE_API_TOKEN")
INSTRUCTOR_ID = int(os.environ.get("INSTRUCTOR_ID", "7"))

ARTIFACT_DIR = Path("artifact")
FILES_DIR = ARTIFACT_DIR / "files"
COLLECTED_JSON = ARTIFACT_DIR / "collected.json"

PAGE_SIZE = 100  # the API rejects limit > 100 with a 422


# Error Handling
class ApiError(Exception):
    """A non-OK response from the Practice Hub API.

    Mini Project 1 raised SystemExit here, which was fine for a script I watched
    run. This bot runs unattended on a schedule and has two jobs, so a single bad
    request must not kill the whole run - the caller catches this and keeps going.
    """

    def __init__(self, status_code, message):
        super().__init__(f"Error {status_code}: {message}")
        self.status_code = status_code
        self.message = message


def check(resp):
    """Raise ApiError unless the response is OK, then hand the response back."""
    if not resp.ok:
        try:
            detail = resp.json()["detail"]
            if isinstance(detail, list):
                detail = detail[0]["msg"]  # 422 sends a list of validation errors
        except (ValueError, KeyError, IndexError):
            detail = resp.text[:200] or resp.reason
        raise ApiError(resp.status_code, detail)
    return resp


# API Client
class PracticeHubClient:
    """Wraps the Practice Hub endpoints this bot needs."""

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, path, **kwargs):
        return check(self.session.get(f"{self.base_url}{path}", timeout=30, **kwargs))

    def list_posts(self, author=None, limit=PAGE_SIZE, offset=0):
        """One page of posts. The API returns a bare JSON array, not an envelope."""
        params = {"limit": limit, "offset": offset}
        if author is not None:
            params["author"] = author
        return self.get("/api/v1/posts", params=params).json()

    def iter_author_posts(self, author_id):
        """Yield every post by one author, paging until a short page comes back.

        There is no 'total' or 'next' field to follow, so the stopping rule is:
        a page holding fewer than PAGE_SIZE posts is the last one.
        """
        offset = 0
        while True:
            page = self.list_posts(author=author_id, limit=PAGE_SIZE, offset=offset)
            for post in page:
                yield post
            if len(page) < PAGE_SIZE:
                return
            offset += len(page)

    def get_post(self, post_id):
        """One post by id, with its full body and attachments list."""
        return self.get(f"/api/v1/posts/{post_id}").json()

    def download_attachment(self, download_url):
        """The raw bytes of an attachment. download_url is relative, e.g. /api/v1/attachments/2."""
        return self.get(download_url).content


# Task 1 - Collection
class Collector:
    """Saves every one of the instructor's posts, and every attached file, to artifact/."""

    def __init__(self, client, instructor_id, artifact_dir=ARTIFACT_DIR):
        self.client = client
        self.instructor_id = instructor_id
        self.artifact_dir = Path(artifact_dir)
        self.files_dir = self.artifact_dir / "files"

    @staticmethod
    def safe_filename(attachment_id, filename):
        """Build a unique, safe name for a downloaded file.

        Path(...).name drops any directory part, so a filename from the API cannot
        escape artifact/files/. The attachment id is prefixed because two different
        posts may attach files with the same name, and the second would otherwise
        overwrite the first.
        """
        base = Path(filename or "").name
        base = re.sub(r"[^A-Za-z0-9._-]", "_", base) or "attachment"
        return f"{attachment_id}_{base}"

    def save_attachment(self, attachment):
        """Download one attachment and return its path relative to artifact/."""
        name = self.safe_filename(attachment["id"], attachment.get("filename"))
        destination = self.files_dir / name
        relative = f"files/{name}"
        expected = attachment.get("size")

        # Attachment contents do not change, so an already-correct file is not
        # re-downloaded. This keeps the scheduled runs cheap as the feed grows.
        if destination.exists() and expected is not None and destination.stat().st_size == expected:
            print(f"    have  {relative} ({expected} bytes)")
            return relative

        data = self.client.download_attachment(attachment["download_url"])
        destination.write_bytes(data)

        if expected is not None and len(data) != expected:
            print(f"    WARNING {relative}: expected {expected} bytes, got {len(data)}")
        else:
            print(f"    saved {relative} ({len(data)} bytes)")
        return relative

    def collect(self):
        """Run the collection and write artifact/collected.json. Returns the artifact."""
        self.files_dir.mkdir(parents=True, exist_ok=True)

        posts = []
        attachment_count = 0
        failures = 0

        for summary in self.client.iter_author_posts(self.instructor_id):
            post_id = summary["id"]
            try:
                # Re-read the post by id rather than trusting the list entry, so what
                # gets saved is always the authoritative full record.
                post = self.client.get_post(post_id)
            except ApiError as err:
                print(f"  post {post_id}: could not fetch ({err}) - using list entry")
                post = summary
                failures += 1

            print(f"  post {post_id}: {post.get('title', '')!r} "
                  f"({len(post.get('body') or '')} chars, "
                  f"{len(post.get('attachments') or [])} attachment(s))")

            for attachment in post.get("attachments") or []:
                try:
                    attachment["saved_path"] = self.save_attachment(attachment)
                    attachment_count += 1
                except (ApiError, OSError) as err:
                    print(f"    FAILED attachment {attachment.get('id')}: {err}")
                    attachment["saved_path"] = None
                    failures += 1

            posts.append(post)

        artifact = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "instructor_id": self.instructor_id,
            "post_count": len(posts),
            "attachment_count": attachment_count,
            "posts": posts,
        }

        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        COLLECTED_JSON.write_text(json.dumps(artifact, indent=2, ensure_ascii=False))

        print(f"\nCollected {len(posts)} post(s) and {attachment_count} file(s) "
              f"into {self.artifact_dir}/")
        if failures:
            print(f"{failures} item(s) failed - see the warnings above.")
        return artifact


# Entry point
def main():
    if not API_TOKEN:
        print("PRACTICE_API_TOKEN is not set. Add it to .env locally, or as a "
              "repository secret on GitHub.", file=sys.stderr)
        return 1

    client = PracticeHubClient(API_URL, API_TOKEN)

    print(f"Collecting posts by user {INSTRUCTOR_ID} from {API_URL}")
    try:
        Collector(client, INSTRUCTOR_ID).collect()
    except ApiError as err:
        print(f"Collection failed: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
