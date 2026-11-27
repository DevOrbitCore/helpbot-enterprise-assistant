"""Upload sample fictional CampusDesk knowledge documents to a running HelpBot service.

Usage:
    python scripts/seed_sample_knowledge.py --base-url http://127.0.0.1:8200
"""

from __future__ import annotations

import argparse
import mimetypes
from pathlib import Path

import httpx

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures"

SAMPLE_METADATA: dict[str, dict[str, str]] = {
    "course_registration_policy.md": {
        "module_id": "course-registration",
        "screen_id": "registration-overview",
        "title": "Course Registration & Add/Drop Policy",
    },
    "library_borrowing_guide.txt": {
        "module_id": "library-services",
        "screen_id": "borrowing-rules",
        "title": "Campus Library Borrowing Guide",
    },
    "examination_handbook.html": {
        "module_id": "examination-help",
        "screen_id": "exam-schedule",
        "title": "Examination Regulations & Makeup Policy",
    },
    "fee_schedule_overview.vtt": {
        "module_id": "fee-information",
        "screen_id": "tuition-summary",
        "title": "Orientation Transcript: Tuition & Fee Deadlines",
    },
    "campus_facilities_walkthrough.srt": {
        "module_id": "campus-facilities",
        "screen_id": "facility-booking",
        "title": "Campus Facilities & Study Room Booking Transcript",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed sample HelpBot knowledge files.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8200")
    parser.add_argument("--tenant-id", default="campusdesk-dev")
    parser.add_argument("--user-id", default="advisor-elena")
    args = parser.parse_args()

    headers = {
        "X-HelpBot-Tenant-Id": args.tenant_id,
        "X-HelpBot-User-Id": args.user_id,
        "X-HelpBot-User-Role": "advisor",
    }

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=20.0) as client:
        for filename, meta in SAMPLE_METADATA.items():
            file_path = FIXTURES_DIR / filename
            if not file_path.is_file():
                print(f"Skipping missing fixture: {filename}")
                continue
            mime, _ = mimetypes.guess_type(file_path.name)
            with file_path.open("rb") as handle:
                resp = client.post(
                    "/api/knowledge/documents",
                    headers=headers,
                    data={
                        "application_id": "campusdesk",
                        "module_id": meta["module_id"],
                        "screen_id": meta["screen_id"],
                        "title": meta["title"],
                    },
                    files={"file": (file_path.name, handle, mime or "text/plain")},
                )
            if resp.status_code == 201:
                doc = resp.json()
                print(f"Uploaded {filename} -> id={doc['id']}")
            else:
                print(f"Failed {filename}: HTTP {resp.status_code} {resp.text}")


if __name__ == "__main__":
    main()
